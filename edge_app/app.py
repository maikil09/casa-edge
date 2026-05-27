from flask import Flask, render_template, jsonify, send_from_directory, request, Response
from flask_cors import CORS
import paho.mqtt.client as mqtt
import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import cv2
import numpy as np
import time
import threading
import requests

app = Flask(__name__)
CORS(app)

DATA_DIR = "data"
CAPTURAS_DIR = os.path.join(DATA_DIR, "capturas")
DB_PATH = os.path.join(DATA_DIR, "historial.db")
os.makedirs(CAPTURAS_DIR, exist_ok=True)

MQTT_HOST = "10.118.61.219"
MQTT_PORT = 1883
CAMERA_STREAM_URL = "http://10.118.61.1:81/stream"

estado = {
    "alarma": "OFF",
    "ultimo_evento": "Sistema iniciado",
    "ultima_imagen": None,
    "autenticacion": "SIN PROCESO",
    "camara": "SIN DATOS",
    "movimiento_detectado": False,
    "ultimo_movimiento": "Sin movimiento",
    "porcentaje_movimiento": 0,
    "fecha_movimiento": None,
    "stream_url": "/video_feed"
}

frame_anterior = None
ultimo_frame = None
ultimo_evento_movimiento = 0
movimiento_hasta = 0
lock = threading.Lock()


def fecha_actual():
    return datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S")


def db():
    return sqlite3.connect(DB_PATH)


def crear_tablas():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo TEXT,
            descripcion TEXT,
            imagen TEXT,
            resultado TEXT
        )
    """)
    conn.commit()
    conn.close()


def guardar_evento(tipo, descripcion, imagen=None, resultado=None):
    conn = db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO eventos (fecha, tipo, descripcion, imagen, resultado)
        VALUES (?, ?, ?, ?, ?)
    """, (fecha_actual(), tipo, descripcion, imagen, resultado))
    conn.commit()
    conn.close()

    estado["ultimo_evento"] = descripcion
    if imagen:
        estado["ultima_imagen"] = imagen


def mqtt_publicar(topic, payload):
    try:
        mqtt_client.publish(topic, payload)
    except Exception as e:
        print("Error publicando MQTT:", topic, payload, e)


def detectar_movimiento(frame):
    global frame_anterior

    frame_pequeno = cv2.resize(frame, (320, 240))
    gris = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (21, 21), 0)

    if frame_anterior is None:
        frame_anterior = gris
        return False, "Primer frame recibido. Esperando comparacion.", 0

    diferencia = cv2.absdiff(frame_anterior, gris)
    frame_anterior = gris

    _, umbral = cv2.threshold(diferencia, 25, 255, cv2.THRESH_BINARY)
    umbral = cv2.dilate(umbral, None, iterations=2)

    contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    area_total = gris.shape[0] * gris.shape[1]
    area_movimiento = 0

    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area > 700:
            area_movimiento += area

    porcentaje = area_movimiento / area_total

    if porcentaje > 0.035:
        return True, f"Movimiento detectado por camara. Area: {porcentaje:.2%}", porcentaje

    return False, f"Sin movimiento importante. Area: {porcentaje:.2%}", porcentaje


def guardar_captura(frame):
    nombre = f"puerta_{datetime.now(ZoneInfo('America/Bogota')).strftime('%Y%m%d_%H%M%S')}.jpg"
    ruta = os.path.join(CAPTURAS_DIR, nombre)
    cv2.imwrite(ruta, frame)
    return f"/capturas/{nombre}"


def procesar_frame(frame):
    global ultimo_frame, ultimo_evento_movimiento, movimiento_hasta

    with lock:
        ultimo_frame = frame.copy()

    movimiento, resultado, porcentaje = detectar_movimiento(frame)
    ahora = time.time()

    if movimiento:
        movimiento_hasta = ahora + 8

    movimiento_activo = ahora < movimiento_hasta

    estado["camara"] = "Camara conectada"
    estado["movimiento_detectado"] = movimiento_activo
    estado["ultimo_movimiento"] = resultado
    estado["porcentaje_movimiento"] = round(porcentaje * 100, 2)
    estado["fecha_movimiento"] = fecha_actual()

    if movimiento and ahora - ultimo_evento_movimiento > 10:
        ultimo_evento_movimiento = ahora
        imagen_publica = guardar_captura(frame)

        estado["alarma"] = "ON"
        estado["autenticacion"] = "ESPERANDO CLAVE"

        guardar_evento(
            "movimiento",
            "Movimiento detectado por la camara de la puerta",
            imagen_publica,
            resultado
        )

        mqtt_publicar("casa/luz/entrada", "ON")
        mqtt_publicar("casa/auth/start", "START")
        mqtt_publicar("casa/alarma/control", "ALARM_ON")


def leer_stream_camara():
    while True:
        try:
            print("Conectando al stream de camara:", CAMERA_STREAM_URL)
            respuesta = requests.get(CAMERA_STREAM_URL, stream=True, timeout=10)
            respuesta.raise_for_status()

            bytes_buffer = b""
            estado["camara"] = "Stream conectado"

            for chunk in respuesta.iter_content(chunk_size=2048):
                if not chunk:
                    continue

                bytes_buffer += chunk
                inicio = bytes_buffer.find(b"\xff\xd8")
                fin = bytes_buffer.find(b"\xff\xd9")

                if inicio != -1 and fin != -1 and fin > inicio:
                    jpg = bytes_buffer[inicio:fin + 2]
                    bytes_buffer = bytes_buffer[fin + 2:]

                    arreglo = np.frombuffer(jpg, dtype=np.uint8)
                    frame = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)

                    if frame is not None:
                        procesar_frame(frame)

        except Exception as e:
            print("Error leyendo camara:", e)
            estado["camara"] = "Error conectando camara"
            estado["movimiento_detectado"] = False
            time.sleep(5)


def generar_stream_local():
    while True:
        with lock:
            frame = None if ultimo_frame is None else ultimo_frame.copy()

        if frame is None:
            time.sleep(0.2)
            continue

        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

        time.sleep(0.05)


def on_connect(client, userdata, flags, rc, properties=None):
    print("MQTT conectado:", rc)
    client.subscribe("casa/entrada/movimiento")
    client.subscribe("casa/auth/ok")
    client.subscribe("casa/auth/fail")
    client.subscribe("casa/auth/timeout")
    client.subscribe("casa/estado")
    client.subscribe("casa/alarma/sensores")
    client.subscribe("casa/alarma/control")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    topic = msg.topic
    print(f"MQTT [{topic}]: {payload}")

    if topic == "casa/entrada/movimiento":
        estado["movimiento_detectado"] = True
        estado["ultimo_movimiento"] = "Movimiento recibido por ESP32"
        estado["fecha_movimiento"] = fecha_actual()
        guardar_evento("entrada", "Movimiento reportado por ESP32", None, payload)
        mqtt_publicar("casa/luz/entrada", "ON")
        mqtt_publicar("casa/auth/start", "START")

    elif topic == "casa/alarma/sensores":
        guardar_evento("sensor", f"Evento ESP32: {payload}", None, "SENSOR")

    elif topic == "casa/auth/ok":
        estado["autenticacion"] = "AUTORIZADO"
        estado["alarma"] = "OFF"
        estado["movimiento_detectado"] = False
        estado["ultimo_movimiento"] = "Acceso autorizado. Alarma apagada."
        guardar_evento("autenticacion", "Clave correcta. Acceso autorizado", None, "OK")
        mqtt_publicar("casa/alarma/control", "ALARM_OFF")
        mqtt_publicar("casa/luces/todas", "OFF")

    elif topic == "casa/auth/fail":
        estado["autenticacion"] = "FALLIDA"
        estado["alarma"] = "ON"
        guardar_evento("autenticacion", "Tres intentos incorrectos. Alarma activada", None, "FAIL")
        mqtt_publicar("casa/alarma/control", "ALARM_ON")
        mqtt_publicar("casa/luces/todas", "ON")

    elif topic == "casa/auth/timeout":
        estado["autenticacion"] = "TIEMPO AGOTADO"
        estado["alarma"] = "ON"
        guardar_evento("autenticacion", "Tiempo agotado para ingresar clave. Alarma activada", None, "TIMEOUT")
        mqtt_publicar("casa/alarma/control", "ALARM_ON")
        mqtt_publicar("casa/luces/todas", "ON")

    elif topic == "casa/alarma/control":
        if payload == "ALARM_ON":
            estado["alarma"] = "ON"
        elif payload == "ALARM_OFF":
            estado["alarma"] = "OFF"
            estado["movimiento_detectado"] = False

    elif topic == "casa/estado":
        guardar_evento("estado", payload, None, "INFO")


mqtt_client = mqtt.Client(client_id="Edge_Dashboard", protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


def conectar_mqtt():
    while True:
        try:
            mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
            mqtt_client.loop_start()
            print("Conectado al broker MQTT")
            break
        except Exception as e:
            print("Error conectando MQTT:", e)
            time.sleep(5)


@app.route("/")
def dashboard():
    return render_template("index.html", stream_url="/video_feed")


@app.route("/video_feed")
def video_feed():
    return Response(generar_stream_local(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/estado")
def api_estado():
    data = dict(estado)
    data["stream_url"] = "/video_feed"
    return jsonify(data)


@app.route("/api/camara/puerta", methods=["POST"])
def camara_puerta():
    raw = request.data
    if not raw:
        return jsonify({"error": "No llego imagen"}), 400

    arreglo = np.frombuffer(raw, np.uint8)
    frame = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "No se pudo decodificar la imagen"}), 400

    procesar_frame(frame)

    return jsonify({
        "recibido": True,
        "movimiento_detectado": estado["movimiento_detectado"],
        "resultado": estado["ultimo_movimiento"],
        "porcentaje_movimiento": estado["porcentaje_movimiento"],
        "imagen": estado["ultima_imagen"]
    })


@app.route("/api/eventos")
def api_eventos():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, fecha, tipo, descripcion, imagen, resultado
        FROM eventos
        ORDER BY id DESC
        LIMIT 50
    """)
    filas = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "fecha": r[1],
            "tipo": r[2],
            "descripcion": r[3],
            "imagen": r[4],
            "resultado": r[5]
        }
        for r in filas
    ])


@app.route("/api/alarma/on")
def encender_alarma():
    estado["alarma"] = "ON"
    mqtt_publicar("casa/alarma/control", "ALARM_ON")
    mqtt_publicar("casa/luces/todas", "ON")
    guardar_evento("alarma", "Alarma activada desde dashboard", None, "ON")
    return jsonify({"alarma": "ON"})


@app.route("/api/alarma/off")
def apagar_alarma():
    estado["alarma"] = "OFF"
    estado["movimiento_detectado"] = False
    estado["ultimo_movimiento"] = "Sin movimiento"
    estado["porcentaje_movimiento"] = 0
    estado["autenticacion"] = "SIN PROCESO"

    mqtt_publicar("casa/alarma/control", "ALARM_OFF")
    mqtt_publicar("casa/luces/todas", "OFF")
    guardar_evento("alarma", "Alarma apagada desde dashboard", None, "OFF")

    return jsonify({"alarma": "OFF"})


@app.route("/api/movimiento/reset")
def reset_movimiento():
    global movimiento_hasta
    movimiento_hasta = 0
    estado["movimiento_detectado"] = False
    estado["ultimo_movimiento"] = "Movimiento reiniciado desde dashboard"
    estado["porcentaje_movimiento"] = 0
    return jsonify({"movimiento_detectado": False})


@app.route("/capturas/<path:filename>")
def capturas(filename):
    return send_from_directory(CAPTURAS_DIR, filename)


if __name__ == "__main__":
    crear_tablas()
    guardar_evento("sistema", "Sistema Edge iniciado correctamente", None, "OK")

    hilo_camara = threading.Thread(target=leer_stream_camara, daemon=True)
    hilo_camara.start()

    conectar_mqtt()

    app.run(host="0.0.0.0", port=5000, threaded=True)
from flask import Flask, request, jsonify, send_from_directory, render_template
import paho.mqtt.client as mqtt
import sqlite3
import cv2
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)

DATA_DIR = "data"
CAPTURAS_DIR = os.path.join(DATA_DIR, "capturas")
DB_PATH = os.path.join(DATA_DIR, "historial.db")

os.makedirs(CAPTURAS_DIR, exist_ok=True)

MQTT_HOST = os.getenv("MQTT_HOST", "broker_mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
CAMERA_STREAM_URL = os.getenv("CAMERA_STREAM_URL", "")

estado = {
    "alarma": "OFF",
    "ultimo_evento": "Sistema iniciado",
    "ultima_imagen": None,
    "autenticacion": "SIN PROCESO",
    "camara": "SIN DATOS"
}


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

    cursor.execute("PRAGMA table_info(eventos)")
    columnas = [col[1] for col in cursor.fetchall()]

    if "resultado" not in columnas:
        cursor.execute("ALTER TABLE eventos ADD COLUMN resultado TEXT")

    conn.commit()
    conn.close()


def guardar_evento(tipo, descripcion, imagen=None, resultado=None):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO eventos (fecha, tipo, descripcion, imagen, resultado)
        VALUES (?, ?, ?, ?, ?)
    """, (fecha, tipo, descripcion, imagen, resultado))

    conn.commit()
    conn.close()

    estado["ultimo_evento"] = descripcion
    estado["ultima_imagen"] = imagen


def analizar_imagen(frame):
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gris, (5, 5), 0)

    _, thresh = cv2.threshold(blur, 45, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    alto, ancho = gris.shape
    area_total = alto * ancho
    mayor_area = 0

    for c in contornos:
        area = cv2.contourArea(c)
        if area > mayor_area:
            mayor_area = area

    porcentaje = mayor_area / area_total

    if porcentaje > 0.08:
        return True, f"Posible persona u objeto grande detectado. Área: {porcentaje:.2f}"

    return False, f"Movimiento leve o sin presencia clara. Área: {porcentaje:.2f}"


def on_connect(client, userdata, flags, rc):
    print("MQTT conectado:", rc)
    client.subscribe("casa/entrada/movimiento")
    client.subscribe("casa/auth/ok")
    client.subscribe("casa/auth/fail")
    client.subscribe("casa/auth/timeout")
    client.subscribe("casa/estado")


def on_message(client, userdata, msg):
    topic = msg.topic
    mensaje = msg.payload.decode()

    print(f"MQTT [{topic}]: {mensaje}")

    if topic == "casa/entrada/movimiento":
        guardar_evento("entrada", "Movimiento detectado en la entrada exterior", None, "LUZ_ENTRADA_ON")
        mqtt_client.publish("casa/luz/entrada", "ON")

    elif topic == "casa/auth/ok":
        estado["autenticacion"] = "AUTORIZADO"
        estado["alarma"] = "OFF"
        guardar_evento("autenticacion", "Clave correcta. Acceso autorizado", None, "OK")
        mqtt_client.publish("casa/alarma", "OFF")

    elif topic == "casa/auth/fail":
        estado["autenticacion"] = "FALLIDA"
        estado["alarma"] = "ON"
        guardar_evento("autenticacion", "Tres intentos incorrectos. Alarma activada", None, "FAIL")
        mqtt_client.publish("casa/alarma", "ON")
        mqtt_client.publish("casa/luces/todas", "ON")

    elif topic == "casa/auth/timeout":
        estado["autenticacion"] = "TIEMPO AGOTADO"
        estado["alarma"] = "ON"
        guardar_evento("autenticacion", "Tiempo agotado para ingresar clave. Alarma activada", None, "TIMEOUT")
        mqtt_client.publish("casa/alarma", "ON")
        mqtt_client.publish("casa/luces/todas", "ON")

    elif topic == "casa/estado":
        guardar_evento("estado", mensaje, None, "INFO")


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/estado")
def api_estado():
    data = dict(estado)
    data["stream_url"] = CAMERA_STREAM_URL
    return jsonify(data)


@app.route("/api/camara/ping")
def camara_ping():
    estado["camara"] = "ESP32-CAM conectada al Edge"
    guardar_evento("camara", "ESP32-CAM verificó conexión con el Edge", None, "ONLINE")
    return jsonify({"ok": True, "mensaje": "Edge disponible"})


@app.route("/api/camara/puerta", methods=["POST"])
def camara_puerta():
    raw = request.data

    if not raw:
        return jsonify({"error": "No llegó imagen"}), 400

    arreglo = np.frombuffer(raw, np.uint8)
    frame = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "No se pudo decodificar la imagen"}), 400

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"puerta_{fecha}.jpg"
    ruta = os.path.join(CAPTURAS_DIR, nombre)

    posible_persona, resultado = analizar_imagen(frame)

    cv2.imwrite(ruta, frame)

    imagen_publica = f"/capturas/{nombre}"

    guardar_evento(
        "puerta",
        "Movimiento detectado en la puerta. Se inicia validación por clave",
        imagen_publica,
        resultado
    )

    estado["camara"] = "Imagen recibida correctamente"
    estado["autenticacion"] = "ESPERANDO CLAVE"

    mqtt_client.publish("casa/auth/start", "START")

    return jsonify({
        "recibido": True,
        "imagen": imagen_publica,
        "posible_persona": posible_persona,
        "resultado": resultado,
        "accion": "VENTANA_CLAVE_INICIADA"
    })


@app.route("/api/eventos")
def eventos():
    conn = db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, fecha, tipo, descripcion, imagen, resultado
        FROM eventos
        ORDER BY id DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()
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
        for r in rows
    ])


@app.route("/api/alarma/on")
def encender_alarma():
    estado["alarma"] = "ON"
    mqtt_client.publish("casa/alarma", "ON")
    mqtt_client.publish("casa/luces/todas", "ON")
    guardar_evento("alarma", "Alarma activada desde dashboard", None, "ON")
    return jsonify({"alarma": "ON"})


@app.route("/api/alarma/off")
def apagar_alarma():
    estado["alarma"] = "OFF"
    mqtt_client.publish("casa/alarma", "OFF")
    mqtt_client.publish("casa/luces/todas", "OFF")
    guardar_evento("alarma", "Alarma apagada desde dashboard", None, "OFF")
    return jsonify({"alarma": "OFF"})


@app.route("/capturas/<path:filename>")
def capturas(filename):
    return send_from_directory(CAPTURAS_DIR, filename)


if __name__ == "__main__":
    crear_tablas()

    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
    mqtt_client.loop_start()

    guardar_evento("sistema", "Sistema Edge iniciado correctamente", None, "OK")

    app.run(host="0.0.0.0", port=5000)
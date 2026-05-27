from flask import Flask, render_template, jsonify, send_from_directory
import paho.mqtt.client as mqtt
import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Ajuste de zona horaria
import cv2
import numpy as np
import time

app = Flask(__name__)

# Carpetas y base de datos
DATA_DIR = "data"
CAPTURAS_DIR = os.path.join(DATA_DIR, "capturas")
DB_PATH = os.path.join(DATA_DIR, "historial.db")
os.makedirs(CAPTURAS_DIR, exist_ok=True)

# Configuración MQTT
MQTT_HOST = "10.118.61.219"  # IP del broker MQTT
MQTT_PORT = 1883

# Streaming de la cámara ESP32-CAM
CAMERA_STREAM_URL = os.getenv("CAMERA_STREAM_URL", "http://192.168.1.80:81/stream")

# Estado global
estado = {
    "alarma": "OFF",
    "ultimo_evento": "Sistema iniciado",
    "ultima_imagen": None,
    "autenticacion": "SIN PROCESO",
    "camara": "SIN DATOS"
}

# --- Base de datos ---
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
    # Hora en Bogotá
    fecha = datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S")
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

# --- Análisis de imagen ESP32-CAM ---
def analizar_imagen(frame):
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gris, (5,5), 0)
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

# --- MQTT ---
def on_connect(client, userdata, flags, reasonCode, properties=None):
    print("MQTT conectado con reasonCode:", reasonCode)
    client.subscribe("casa/entrada/movimiento")
    client.subscribe("casa/auth/ok")
    client.subscribe("casa/auth/fail")
    client.subscribe("casa/auth/timeout")
    client.subscribe("casa/estado")
    client.subscribe("casa/alarma/sensores")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    topic = msg.topic
    print(f"MQTT [{topic}]: {payload}")
    if topic == "casa/entrada/movimiento":
        guardar_evento("entrada", "Movimiento detectado por ESP32-CAM", None, "LUZ_ENTRADA_ON")
        client.publish("casa/luz/entrada", "ON")
    elif topic == "casa/alarma/sensores":
        guardar_evento("sensor", f"Evento ESP32: {payload}")
        if payload == "MOVIMIENTO PIR DETECTADO":
            client.publish("casa/luz/entrada", "ON")
    elif topic == "casa/auth/ok":
        estado["autenticacion"] = "AUTORIZADO"
        estado["alarma"] = "OFF"
        guardar_evento("autenticacion", "Clave correcta. Acceso autorizado", None, "OK")
        client.publish("casa/alarma", "OFF")
    elif topic == "casa/auth/fail":
        estado["autenticacion"] = "FALLIDA"
        estado["alarma"] = "ON"
        guardar_evento("autenticacion", "Tres intentos incorrectos. Alarma activada", None, "FAIL")
        client.publish("casa/alarma", "ON")
        client.publish("casa/luces/todas", "ON")
    elif topic == "casa/auth/timeout":
        estado["autenticacion"] = "TIEMPO AGOTADO"
        estado["alarma"] = "ON"
        guardar_evento("autenticacion", "Tiempo agotado para ingresar clave. Alarma activada", None, "TIMEOUT")
        client.publish("casa/alarma", "ON")
        client.publish("casa/luces/todas", "ON")
    elif topic == "casa/estado":
        guardar_evento("estado", payload, None, "INFO")

# --- Cliente MQTT moderno con reconexión ---
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

# --- Flask endpoints ---
@app.route("/")
def dashboard():
    return render_template("index.html", stream_url=CAMERA_STREAM_URL)

@app.route("/api/estado")
def api_estado():
    data = dict(estado)
    data["stream_url"] = CAMERA_STREAM_URL
    return jsonify(data)

@app.route("/api/camara/puerta", methods=["POST"])
def camara_puerta():
    raw = request.data
    if not raw:
        return jsonify({"error": "No llegó imagen"}), 400
    arreglo = np.frombuffer(raw, np.uint8)
    frame = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({"error": "No se pudo decodificar la imagen"}), 400
    fecha = datetime.now(ZoneInfo("America/Bogota")).strftime("%Y%m%d_%H%M%S")
    nombre = f"puerta_{fecha}.jpg"
    ruta = os.path.join(CAPTURAS_DIR, nombre)
    posible_persona, resultado = analizar_imagen(frame)
    cv2.imwrite(ruta, frame)
    imagen_publica = f"/capturas/{nombre}"
    guardar_evento("puerta", "Movimiento detectado en la puerta. Validación por clave",
                   imagen_publica, resultado)
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
        {"id": r[0], "fecha": r[1], "tipo": r[2], "descripcion": r[3],
         "imagen": r[4], "resultado": r[5]}
        for r in filas
    ])

@app.route("/api/alarma/on")
def encender_alarma():
    estado["alarma"] = "ON"
    mqtt_client.publish("casa/alarma/control", "ALARM_ON")
    mqtt_client.publish("casa/luces/todas", "ON")
    guardar_evento("alarma", "Alarma activada desde dashboard", None, "ON")
    return jsonify({"alarma": "ON"})

@app.route("/api/alarma/off")
def apagar_alarma():
    estado["alarma"] = "OFF"
    mqtt_client.publish("casa/alarma/control", "ALARM_OFF")
    mqtt_client.publish("casa/luces/todas", "OFF")
    guardar_evento("alarma", "Alarma apagada desde dashboard", None, "OFF")
    return jsonify({"alarma": "OFF"})

@app.route("/capturas/<path:filename>")
def capturas(filename):
    return send_from_directory(CAPTURAS_DIR, filename)

if __name__ == "__main__":
    crear_tablas()
    guardar_evento("sistema", "Sistema Edge iniciado correctamente", None, "OK")
    conectar_mqtt()
    app.run(host="0.0.0.0", port=5000)
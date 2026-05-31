# 🏠 Casa-Edge

> Plataforma de Computación en el Borde (Edge Computing) para entornos IoT inteligentes.

## 📖 Descripción

**Casa-Edge** es un proyecto académico desarrollado para la asignatura de **Computación en el Borde**, enfocado en el diseño e implementación de una arquitectura IoT capaz de procesar información localmente mediante tecnologías Edge Computing.

La solución busca reducir la latencia, optimizar el uso de recursos de red y mejorar la disponibilidad de los servicios mediante el procesamiento de datos cerca de la fuente donde son generados.

Además del desarrollo de software, el proyecto fue validado utilizando una **maqueta funcional de una casa inteligente**, permitiendo demostrar el comportamiento real de la arquitectura propuesta.

---

## 🎯 Objetivos

* Implementar una arquitectura IoT basada en Edge Computing.
* Reducir la dependencia de servicios cloud centralizados.
* Mejorar los tiempos de respuesta en eventos críticos.
* Facilitar la comunicación entre dispositivos mediante MQTT.
* Permitir una solución escalable y fácilmente desplegable mediante contenedores Docker.

---

## 🏠 Prototipo Físico

El proyecto incluye una maqueta funcional de una vivienda inteligente utilizada para validar:

* 🔹 Comunicación entre sensores y actuadores.
* 🔹 Procesamiento local de eventos.
* 🔹 Automatización de dispositivos.
* 🔹 Escalabilidad del sistema.
* 🔹 Operación en tiempo real.

---

## ⚙️ Arquitectura del Sistema

```text
┌─────────────────────┐
│   Sensores IoT      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Broker MQTT      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Edge App       │
│ Procesamiento Local │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Interfaz Web      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Usuario        │
└─────────────────────┘
```

---

## 🛠️ Tecnologías Utilizadas

### Backend

* Python

### Frontend

* HTML5
* CSS3
* JavaScript

### Comunicación IoT

* MQTT

### Contenedorización

* Docker
* Docker Compose

### Computación en el Borde

* Edge Computing

---

## 📂 Estructura del Proyecto

```text
Casa-Edge/
│
├── edge_app/
│   ├── static/
│   ├── templates/
│   └── app.py
│
├── mqtt/
│
├── docker-compose.yml
│
└── README.md
```

| Carpeta              | Descripción                                  |
| -------------------- | -------------------------------------------- |
| `edge_app/`          | Aplicación principal del nodo Edge           |
| `mqtt/`              | Configuración del sistema de mensajería MQTT |
| `docker-compose.yml` | Orquestación de contenedores                 |
| `README.md`          | Documentación del proyecto                   |

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/maikil09/casa-edge.git
cd casa-edge
```

### 2. Iniciar los servicios

Docker Compose moderno:

```bash
docker compose up -d
```

Docker Compose clásico:

```bash
docker-compose up -d
```

### 3. Verificar contenedores

```bash
docker ps
```

---

## 🌐 Acceso a la Aplicación

Una vez iniciado el entorno:

```text
http://localhost
```

o la dirección IP del dispositivo Edge:

```text
http://IP_DEL_DISPOSITIVO
```

---

## 📡 Comunicación MQTT

El sistema utiliza MQTT como protocolo principal de comunicación debido a:

* Bajo consumo de ancho de banda.
* Comunicación ligera y eficiente.
* Arquitectura Publish/Subscribe.
* Alta compatibilidad con dispositivos IoT.

---

## 🔥 Ventajas del Edge Computing Implementadas

### Menor Latencia

Los datos son procesados localmente sin necesidad de enviarlos constantemente a la nube.

### Mayor Disponibilidad

El sistema puede continuar funcionando incluso ante fallas de conectividad externa.

### Optimización de Recursos

Reducción del tráfico de red y menor consumo de recursos cloud.

### Escalabilidad

Nuevos dispositivos pueden agregarse fácilmente a la arquitectura.

---

## 🎓 Contexto Académico

Proyecto desarrollado para la asignatura:

**Computación en el Borde (Edge Computing)**

Temáticas aplicadas:

* Internet de las Cosas (IoT)
* Arquitecturas Distribuidas
* Edge Computing
* Docker
* MQTT
* Sistemas Inteligentes
* Automatización

---

## 📸 Evidencias

```markdown
![Maqueta](images/maqueta.jpg)
```

---

## 👨‍💻 Autores

Proyecto académico desarrollado por:

- Ana Maria Chaves Perez
- Gabriela Reyes Gonzalez
- Michael Steven Medina Fernandez
- Maria Alejandra Cabrera Arauz

del curso de Computación en el Borde.

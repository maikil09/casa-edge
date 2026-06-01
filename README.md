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

<img width="733" height="364" alt="image" src="https://github.com/user-attachments/assets/3f07222c-02ff-407b-a94e-0ebc1c99510b" />


---

## 🧩 Diagrama de Arquitectura

Explicación detallada de los componentes del sistema y su interacción a traves de MQTT.

- Sensores IoT capturan información del entorno.
- Los datos son enviados mediante MQTT.
- El broker MQTT distribuye los mensajes.
- La Edge App procesa los eventos localmente.
- La interfaz web permite monitoreo y control en tiempo real.
- El usuario interactúa con el sistema desde la red local.

```text
                           ┌───────────────────────┐
                           │       Usuario         │
                           │  PC / Celular / Web   │
                           └───────────┬───────────┘
                                       │
                                       ▼
                           ┌───────────────────────┐
                           │    Interfaz Web UI    │
                           │ HTML • CSS • JS       │
                           └───────────┬───────────┘
                                       │
                                       ▼
                    ┌────────────────────────────────────┐
                    │           Edge Application         │
                    │              Python               │
                    │ Procesamiento Local de Eventos    │
                    │ Lógica de Automatización          │
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────────┐
                    │           Broker MQTT             │
                    │ Comunicación Publish/Subscribe    │
                    └───────┬───────────────┬───────────┘
                            │               │
                            │               │
              ┌─────────────▼───┐     ┌────▼────────────┐
              │    Sensores      │     │   Actuadores    │
              │                  │     │                 │
              │ • Temperatura    │     │ • Luces         │
              │ • Movimiento     │     │ • Alarmas       │
              │ • Humedad        │     │ • Ventilación   │
              │ • Presencia      │     │ • Puertas       │
              └──────────────────┘     └─────────────────┘

                           Infraestructura Docker
        ┌──────────────────────────────────────────────────────┐
        │                                                      │
        │  ┌──────────────┐      ┌─────────────────────────┐   │
        │  │ MQTT Broker  │◄────►│      Edge App           │   │
        │  │  Container   │      │      Container          │   │
        │  └──────────────┘      └─────────────────────────┘   │
        │                                                      │
        └──────────────────────────────────────────────────────┘
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

## 🐳 Descripción de la Imagen Docker

El proyecto utiliza contenedores Docker para garantizar portabilidad, reproducibilidad y facilidad de despliegue.

Funciones principales de la imagen:

- Ejecutar la aplicación Edge de forma aislada.
- Gestionar dependencias automáticamente.
- Facilitar el despliegue en dispositivos como Raspberry Pi o servidores Linux.
- Permitir escalabilidad mediante Docker Compose.

Beneficios:

- Entorno consistente en cualquier dispositivo.
- Menor tiempo de configuración.
- Fácil mantenimiento y actualización.

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

## ⚠️ Limitaciones

A pesar de los beneficios obtenidos, el proyecto presenta algunas limitaciones:

- Dependencia de la infraestructura local.
- Capacidad limitada de procesamiento en dispositivos Edge de bajo costo.
- Escalabilidad restringida frente a arquitecturas cloud de gran tamaño.
- Ausencia de mecanismos avanzados de tolerancia a fallos.
- Seguridad básica en las comunicaciones MQTT.

Estas limitaciones son comunes en entornos académicos y prototipos funcionales.

---

## 🚀 Posibilidades de Mejora

Trabajos futuros que pueden ampliar el alcance del proyecto:

- Implementar inteligencia artificial en el nodo Edge.
- Incorporar análisis predictivo mediante Machine Learning.
- Agregar autenticación y cifrado avanzado para MQTT.
- Integrar servicios híbridos Edge-Cloud.
- Implementar monitoreo centralizado.
- Incorporar balanceo de carga entre múltiples nodos Edge.
- Añadir sensores y actuadores adicionales para nuevas funcionalidades domóticas.

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

<table align="center">
  <tr>
    <td align="center">
      <img width="360" height="480" alt="Imagen 1" src="https://github.com/user-attachments/assets/d9d14ef6-22a0-4a9b-98e6-af081858ba26" />
    </td>
    <td align="center">
      <img width="360" height="480" alt="image" src="https://github.com/user-attachments/assets/52899d77-7480-49fc-9e67-afd74a2ca88e" />
    </td>
  </tr>
  <tr>
    <td align="center">
     <img width="360" height="480" alt="image" src="https://github.com/user-attachments/assets/00c688f7-ab2f-4d69-9502-5611c2f201b7" />
    </td>
    <td align="center">
      <img width="360" height="480" alt="image" src="https://github.com/user-attachments/assets/5ef20742-f198-4eef-bf87-3a6aae4002de" />
    </td>
  </tr>
</table>

---

## 👨‍💻 Autores

Proyecto académico desarrollado por:

- Ana Maria Chaves Perez
- Gabriela Reyes Gonzalez
- Michael Steven Medina Fernandez
- Maria Alejandra Cabrera Arauz

del curso de Computación en el Borde.

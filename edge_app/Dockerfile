FROM python:3.11-slim

WORKDIR /app

# Instala dependencias necesarias para OpenCV si es que luego se usa análisis de imágenes
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copia y instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código principal
COPY app.py .

# Copia templates (HTML) y static (CSS/JS)
COPY templates ./templates
COPY static ./static

# Expone el puerto para acceder al dashboard
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
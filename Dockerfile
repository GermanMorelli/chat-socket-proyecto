# Usamos una imagen de Python ligera
FROM python:3.9-slim

# Configuraciones básicas para que Python no guarde caché
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro de la nube
WORKDIR /app

# Instalamos las herramientas necesarias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todos tus códigos (.py) a la nube
COPY . .

# Damos permisos para ejecutar el script de arranque
RUN chmod +x start.sh

# El puerto que Render nos asignará (Streamlit lo usará)
EXPOSE 8501

# Comando para iniciar todo
CMD ["./start.sh"]
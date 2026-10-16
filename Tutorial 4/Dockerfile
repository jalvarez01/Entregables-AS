# Receta de la imagen del monolito Django (Tutorial 04).

# 1. Imagen base oficial de Python, ligera
FROM python:3.11-slim

# 2. Sin archivos .pyc y con logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Dependencias primero: si requirements.txt no cambia, Docker reutiliza esta capa
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Resto del código fuente
COPY . /app/

EXPOSE 8000

# 6. Comando por defecto. Escucha en 0.0.0.0 para ser accesible desde fuera del contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

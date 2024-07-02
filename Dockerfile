# Usa una imagen base de Selenium con Chrome y ChromeDriver preinstalados
FROM selenium/standalone-chrome:112.0-chromedriver-112.0

# Usuario root para instalar dependencias adicionales
USER root

# Instala Python y pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos a la imagen
COPY requirements.txt .

# Instala las dependencias
RUN pip3 install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio actual en el contenedor
COPY . .

# Asegura permisos en el directorio de trabajo
RUN chown -R root:root /app

# Copia el script de inicio y asegura permisos de ejecución
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Exponer el puerto de la aplicación
EXPOSE 5000

# Comando para iniciar el script de inicio
CMD ["/app/start.sh"]


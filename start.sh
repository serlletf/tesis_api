#!/bin/sh
# Ajustar las opciones de Chrome para evitar bloqueos
export DBUS_SESSION_BUS_ADDRESS=/dev/null
# Ejecutar el script de scraping en segundo plano
python3 scraping.py &

# Ejecutar la aplicación Flask
python3 app.py
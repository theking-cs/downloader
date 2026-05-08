#!/bin/bash

# Configuración de usuario theking-cs
GITHUB_USER="theking-cs"
PLUGIN_DIR="downloader"
VERSION="1.0"
URL_RAW="https://raw.githubusercontent.com/$GITHUB_USER/downloader/main"

echo "================================================="
echo "   INSTALADOR $PLUGIN_DIR v$VERSION"
echo "   Creado por: $GITHUB_USER"
echo "================================================="

# 1. Crear directorios necesarios
echo "> Preparando entorno..."
mkdir -p /usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_DIR
mkdir -p /media/hdd/Mp3

# 2. Descarga de archivos
echo "> Descargando archivos v$VERSION..."
curl -kLs $URL_RAW/plugin.py -o /usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_DIR/plugin.py
curl -kLs $URL_RAW/descargador.sh -o /usr/bin/descargador.sh

# 3. Permisos Críticos
echo "> Aplicando permisos 755..."
# Permisos para el script de descarga
chmod 755 /usr/bin/descargador.sh
# Permisos para la carpeta del plugin y sus archivos
chmod -R 755 /usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_DIR

# 4. Instalación de dependencias
echo "> Instalando paquetes necesarios..."
opkg update
opkg install python3-core python3-twisted-web python3-netclient curl yt-dlp

# Limpieza de posibles archivos compilados viejos
rm -f /usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_DIR/*.pyc

echo "================================================="
echo "   INSTALACIÓN v$VERSION COMPLETADA"
echo "   REINICIANDO ENIGMA2..."
echo "================================================="
killall -9 enigma2

#!/bin/bash
# =================================================
#   INSTALADOR downloader v1.0
#   Creado por: theking-cs
# =================================================

GITHUB_USER="theking-cs"
REPO_NAME="downloader"
URL_RAW="https://raw.githubusercontent.com/$GITHUB_USER/$REPO_NAME/main"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/descargador"

echo "================================================="
echo "   INSTALADOR $REPO_NAME v1.0"
echo "   Creado por: $GITHUB_USER"
echo "================================================="

# 1. Crear carpetas necesarias
echo "> Preparando entorno y carpetas..."
mkdir -p $PLUGIN_PATH
mkdir -p /media/hdd/Mp3
chmod 777 /media/hdd/Mp3

# 2. Descargar archivos del plugin desde GitHub
echo "> Descargando archivos del plugin..."
curl -kLs $URL_RAW/plugin.py -o $PLUGIN_PATH/plugin.py
curl -kLs $URL_RAW/__init__.py -o $PLUGIN_PATH/__init__.py
curl -kLs $URL_RAW/plugin.png -o $PLUGIN_PATH/plugin.png
curl -kLs $URL_RAW/descargador.sh -o /usr/bin/descargador.sh

# 3. Aplicar permisos de ejecución
echo "> Aplicando permisos..."
chmod 755 /usr/bin/descargador.sh
chmod -R 755 $PLUGIN_PATH

# 4. Instalar dependencias del sistema
echo "> Instalando paquetes necesarios (Python & Curl)..."
opkg update
opkg install python3-twisted-web python3-core curl

# 5. Instalación inteligente de yt-dlp
if ! command -v yt-dlp &> /dev/null; then
    echo "> yt-dlp no detectado, intentando instalar desde feeds..."
    if ! opkg install yt-dlp; then
        echo "> Error en feeds: Instalando yt-dlp binario manualmente..."
        curl -kLs https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/bin/yt-dlp
        chmod 755 /usr/bin/yt-dlp
    fi
fi

echo "================================================="
echo "   INSTALACIÓN COMPLETADA EXITOSAMENTE"
echo "   REINICIANDO ENIGMA2 PARA CARGAR EL PLUGIN..."
echo "================================================="

# Reiniciar la interfaz para que aparezca el plugin en el menú
killall -9 enigma2

exit 0

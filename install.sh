#!/bin/bash

# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias del sistema
sudo apt-get install -y python3-pip python3-venv python3-dev build-essential libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev shared-mime-info

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p reports data

# Configurar permisos
chmod +x run.sh

echo "Instalación completada. Por favor, configura el archivo .env con tus claves de API." 
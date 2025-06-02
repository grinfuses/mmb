#!/bin/bash

# Activar entorno virtual
source venv/bin/activate

# Configurar variables de entorno
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Ejecutar el análisis
python3 example.py

# Comprimir el informe generado
timestamp=$(date +%Y%m%d_%H%M%S)
cd reports
zip -r "report_${timestamp}.zip" .

# Limpiar informes antiguos (mantener solo los últimos 6 meses)
find . -name "report_*.zip" -mtime +180 -delete
find . -name "metadata_quality_report_*.pdf" -mtime +180 -delete
find . -name "metadata_quality_report_*.html" -mtime +180 -delete 
# Madrid Metadata Booster

Herramienta para analizar y mejorar la calidad de los metadatos de las APIs del portal de datos abiertos de Madrid.

## Características

- Análisis automático de la calidad de los metadatos de las APIs
- Generación de informes HTML interactivos con visualizaciones
- Estadísticas de actualización y uso de las APIs
- Filtros por sector, frecuencia y formato
- Identificación de APIs que necesitan mejoras en sus metadatos

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone git@github.com:grinfuses/mmb.git
cd mmb
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Descargar el catálogo de datos de Madrid:
```bash
curl -o catalogo.csv https://datos.madrid.es/egob/catalogo/catalogo.csv
```

2. Generar el informe:
```bash
python generate_api_report.py
```

3. Abrir el informe generado:
```bash
python -m http.server 8000
```
Luego abre http://localhost:8000/api_catalog.html en tu navegador.

## Estructura del Proyecto

```
mmb/
├── README.md
├── requirements.txt
├── generate_api_report.py
├── catalogo.csv
└── api_catalog.html
```

## Características del Informe

- **Panel de Resumen**: Muestra estadísticas generales del catálogo
- **Visualizaciones**: Gráficos de distribución por sector y frecuencia
- **Tabla Interactiva**: Lista completa de APIs con filtros
- **Métricas de Actualización**: Seguimiento de la frescura de los datos

## Contribuir

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Javier Naranjo - [@grinfuses](https://github.com/grinfuses)

Link del Proyecto: [https://github.com/grinfuses/mmb](https://github.com/grinfuses/mmb)

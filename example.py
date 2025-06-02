import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from src import MadridMetadataBooster

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metadata_booster.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Verificar API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY no encontrada en el archivo .env")
        
        # Inicializar el booster
        logging.info("Iniciando Madrid Metadata Booster...")
        booster = MadridMetadataBooster(
            catalog_url=os.getenv('CATALOG_URL', 'https://datos.madrid.es/api/v2/catalog/datasets'),
            openai_api_key=api_key,
            output_dir='reports'
        )
        
        # Analizar el catálogo
        logging.info("Analizando catálogo...")
        results = booster.analyze_catalog()
        
        # Registrar resumen
        logging.info("\nResumen de Calidad:")
        logging.info(f"Total datasets: {results['quality_summary']['total_datasets']}")
        logging.info(f"Puntuación media: {results['quality_summary']['average_score']:.2%}")
        
        logging.info("\nResumen de Mejoras:")
        logging.info(f"Total mejorados: {results['enhancement_summary']['total_enhanced']}")
        logging.info(f"Confianza media: {results['enhancement_summary']['average_confidence']:.2%}")
        
        logging.info("\nInformes generados:")
        for format, path in results['report_paths'].items():
            logging.info(f"- {format}: {path}")
        
        # Ejemplo: Obtener recomendaciones por texto
        logging.info("\nObteniendo recomendaciones por texto...")
        text_recommendations = booster.get_dataset_recommendations(
            text="transporte público madrid",
            n_recommendations=3
        )
        
        logging.info("\nTop 3 datasets relevantes:")
        for rec in text_recommendations:
            logging.info(f"- {rec['title']} (similitud: {rec['similarity_score']:.2%})")
        
        logging.info("Proceso completado exitosamente")
        
    except Exception as e:
        logging.error(f"Error durante la ejecución: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 
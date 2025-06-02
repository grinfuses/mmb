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
        logging.FileHandler('metadata_analysis.log'),
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
        logging.info("Iniciando análisis de datasets problemáticos...")
        booster = MadridMetadataBooster(
            catalog_url=os.getenv('CATALOG_URL', 'https://datos.madrid.es/api/v2/catalog/datasets'),
            openai_api_key=api_key,
            output_dir='reports'
        )
        
        # Analizar el catálogo
        logging.info("Analizando catálogo...")
        results = booster.analyze_catalog()
        
        # Mostrar resumen de calidad
        logging.info("\n=== RESUMEN DE CALIDAD ===")
        logging.info(f"Total datasets analizados: {results['quality_summary']['total_datasets']}")
        logging.info(f"Puntuación media: {results['quality_summary']['average_score']:.2%}")
        
        # Mostrar distribución de calidad
        logging.info("\n=== DISTRIBUCIÓN DE CALIDAD ===")
        dist = results['quality_summary']['score_distribution']
        logging.info(f"Excelente (≥80%): {dist['excellent']} datasets")
        logging.info(f"Bueno (60-79%): {dist['good']} datasets")
        logging.info(f"Regular (40-59%): {dist['fair']} datasets")
        logging.info(f"Pobre (<40%): {dist['poor']} datasets")
        
        # Mostrar problemas comunes
        logging.info("\n=== PROBLEMAS COMUNES ===")
        for issue, count in results['quality_summary']['common_issues'].items():
            logging.info(f"- {issue}: {count} datasets")
        
        # Mostrar datasets mejorados
        logging.info("\n=== DATASETS MEJORADOS ===")
        logging.info(f"Total mejorados: {results['enhancement_summary']['total_enhanced']}")
        logging.info(f"Confianza media de las mejoras: {results['enhancement_summary']['average_confidence']:.2%}")
        
        # Mostrar rutas de los informes
        logging.info("\n=== INFORMES GENERADOS ===")
        for format, path in results['report_paths'].items():
            logging.info(f"- {format}: {path}")
        
        logging.info("\nAnálisis completado exitosamente")
        
    except Exception as e:
        logging.error(f"Error durante la ejecución: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 
import requests
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DatasetMetadata:
    id: str
    title: str
    description: str
    format: str
    license: str
    frequency: str
    category: str
    tags: List[str]
    last_updated: datetime
    url: str

class MetadataAnalyzer:
    def __init__(self, catalog_url: str):
        self.catalog_url = catalog_url
        self.datasets: List[DatasetMetadata] = []
        
    def fetch_catalog(self) -> Dict:
        """Fetch the catalog from datos.madrid.es"""
        try:
            # Lista de endpoints de datasets conocidos
            dataset_endpoints = [
                '300396-12600740-mobiliario-urbano-deportivos',
                '300680-12600968-servicios-sociales-problematicas',
                '300584-2083621-rrhh_efectivos',
                '300392-12751124-meteorologia-tiempo-real',
                '300468-12600980-tarjeta-azul',
                '212411-12601927-madrid-avisa',
                '212411-12601936-madrid-avisa',
                '300217-12600700-mobiliario-mesas',
                '210980-2083617-cita-previa-linea-madrid',
                '300395-12600760-mobiliario-urbano-mayores'
            ]
            
            all_datasets = []
            for endpoint in dataset_endpoints:
                url = f'https://datos.madrid.es/egob/catalogo/{endpoint}.json'
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()
                    if isinstance(data, dict):
                        all_datasets.append(data)
                except Exception as e:
                    print(f"Error fetching dataset {endpoint}: {str(e)}")
                    continue
            
            return {'datasets': all_datasets}
                
        except Exception as e:
            raise Exception(f"Error fetching catalog: {str(e)}")
    
    def parse_dataset(self, dataset_data: Dict) -> DatasetMetadata:
        """Parse a single dataset's metadata"""
        # Extraer datos del formato específico de datos.madrid.es
        title = dataset_data.get('title', '')
        description = dataset_data.get('description', '')
        
        # Intentar extraer la fecha de actualización
        try:
            last_updated = datetime.fromisoformat(dataset_data.get('modified', ''))
        except (ValueError, TypeError):
            last_updated = datetime.now()
            
        # Extraer categoría y tags
        category = dataset_data.get('category', '')
        tags = dataset_data.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',')]
            
        # Extraer formato y licencia
        format_type = dataset_data.get('format', '')
        license_type = dataset_data.get('license', '')
        
        # Extraer frecuencia (si está disponible)
        frequency = dataset_data.get('frequency', '')
        
        # Construir URL
        url = dataset_data.get('url', '')
        if not url and 'id' in dataset_data:
            url = f"https://datos.madrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid={dataset_data['id']}"
            
        return DatasetMetadata(
            id=dataset_data.get('id', ''),
            title=title,
            description=description,
            format=format_type,
            license=license_type,
            frequency=frequency,
            category=category,
            tags=tags,
            last_updated=last_updated,
            url=url
        )
    
    def analyze_metadata(self) -> pd.DataFrame:
        """Analyze all datasets in the catalog"""
        catalog = self.fetch_catalog()
        self.datasets = [self.parse_dataset(dataset) for dataset in catalog.get('datasets', [])]
        
        analysis_results = []
        for dataset in self.datasets:
            analysis = {
                'id': dataset.id,
                'title_length': len(dataset.title),
                'description_length': len(dataset.description),
                'has_description': bool(dataset.description.strip()),
                'has_category': bool(dataset.category),
                'num_tags': len(dataset.tags),
                'format_score': self._score_format(dataset.format),
                'license_score': self._score_license(dataset.license),
                'frequency_score': self._score_frequency(dataset.frequency),
                'days_since_update': (datetime.now() - dataset.last_updated).days
            }
            analysis_results.append(analysis)
        
        return pd.DataFrame(analysis_results)
    
    def _score_format(self, format_str: str) -> float:
        """Score the dataset format (higher is better)"""
        format_scores = {
            'CSV': 1.0,
            'JSON': 1.0,
            'XML': 0.8,
            'XLSX': 0.7,
            'PDF': 0.5,
            'HTML': 0.6
        }
        return format_scores.get(format_str.upper(), 0.3)
    
    def _score_license(self, license_str: str) -> float:
        """Score the dataset license (higher is better)"""
        license_scores = {
            'CC0': 1.0,
            'CC-BY': 1.0,
            'CC-BY-SA': 0.9,
            'ODC-BY': 1.0,
            'ODC-ODbL': 0.9
        }
        return license_scores.get(license_str, 0.5)
    
    def _score_frequency(self, frequency: str) -> float:
        """Score the update frequency (higher is better)"""
        frequency_scores = {
            'daily': 1.0,
            'weekly': 0.9,
            'monthly': 0.8,
            'quarterly': 0.7,
            'annually': 0.6,
            'never': 0.1
        }
        return frequency_scores.get(frequency.lower(), 0.5)
    
    def get_problematic_datasets(self) -> List[Dict]:
        """Identify datasets with common metadata problems"""
        problems = []
        for dataset in self.datasets:
            dataset_problems = []
            
            if not dataset.description.strip():
                dataset_problems.append("Sin descripción")
            elif len(dataset.description) < 50:
                dataset_problems.append("Descripción demasiado corta")
                
            if not dataset.category:
                dataset_problems.append("Sin categoría")
                
            if len(dataset.tags) < 3:
                dataset_problems.append("Pocas etiquetas")
                
            if dataset.format.upper() not in ['CSV', 'JSON', 'XML']:
                dataset_problems.append("Formato poco reutilizable")
                
            if dataset_problems:
                problems.append({
                    'id': dataset.id,
                    'title': dataset.title,
                    'problems': dataset_problems
                })
                
        return problems 
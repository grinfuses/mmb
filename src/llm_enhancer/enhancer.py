import os
from typing import Dict, List, Optional
from openai import OpenAI
from dataclasses import dataclass

@dataclass
class EnhancedMetadata:
    dataset_id: str
    improved_description: str
    suggested_tags: List[str]
    suggested_category: str
    usage_examples: List[str]
    confidence_score: float

class LLMEnhancer:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4-turbo-preview"  # Using the latest GPT-4 model
        
    def enhance_metadata(self, dataset: Dict) -> EnhancedMetadata:
        """Enhance dataset metadata using LLM"""
        prompt = self._create_enhancement_prompt(dataset)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            enhanced_data = self._parse_llm_response(response.choices[0].message.content)
            return EnhancedMetadata(
                dataset_id=dataset['id'],
                improved_description=enhanced_data['description'],
                suggested_tags=enhanced_data['tags'],
                suggested_category=enhanced_data['category'],
                usage_examples=enhanced_data['examples'],
                confidence_score=enhanced_data['confidence']
            )
            
        except Exception as e:
            raise Exception(f"Error enhancing metadata: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM"""
        return """Eres un experto en metadatos de datos abiertos. Tu tarea es mejorar la calidad de los metadatos 
        de conjuntos de datos, proporcionando:
        1. Descripciones más detalladas y útiles
        2. Etiquetas relevantes y específicas
        3. Categorización precisa
        4. Ejemplos de uso práctico
        
        Responde en formato JSON con las siguientes claves:
        {
            "description": "descripción mejorada",
            "tags": ["tag1", "tag2", ...],
            "category": "categoría sugerida",
            "examples": ["ejemplo1", "ejemplo2", ...],
            "confidence": 0.95  // puntuación de confianza (0-1)
        }"""
    
    def _create_enhancement_prompt(self, dataset: Dict) -> str:
        """Create the prompt for metadata enhancement"""
        return f"""Por favor, mejora los metadatos del siguiente conjunto de datos:
        
        Título: {dataset.get('title', '')}
        Descripción actual: {dataset.get('description', '')}
        Formato: {dataset.get('format', '')}
        Categoría actual: {dataset.get('category', '')}
        Etiquetas actuales: {', '.join(dataset.get('tags', []))}
        
        Considera:
        1. El contexto de datos abiertos de Madrid
        2. Posibles casos de uso
        3. Relevancia para ciudadanos y empresas
        4. Mejores prácticas en metadatos"""
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse the LLM response into structured data"""
        try:
            import json
            data = json.loads(response)
            return {
                'description': data.get('description', ''),
                'tags': data.get('tags', []),
                'category': data.get('category', ''),
                'examples': data.get('examples', []),
                'confidence': float(data.get('confidence', 0.0))
            }
        except Exception as e:
            raise Exception(f"Error parsing LLM response: {str(e)}")
    
    def batch_enhance(self, datasets: List[Dict]) -> List[EnhancedMetadata]:
        """Enhance metadata for multiple datasets"""
        return [self.enhance_metadata(dataset) for dataset in datasets]
    
    def get_enhancement_summary(self, enhanced_metadata: List[EnhancedMetadata]) -> Dict:
        """Generate a summary of metadata enhancements"""
        return {
            'total_enhanced': len(enhanced_metadata),
            'average_confidence': sum(m.confidence_score for m in enhanced_metadata) / len(enhanced_metadata),
            'categories_suggested': len(set(m.suggested_category for m in enhanced_metadata)),
            'total_tags_suggested': sum(len(m.suggested_tags) for m in enhanced_metadata),
            'total_examples_generated': sum(len(m.usage_examples) for m in enhanced_metadata)
        } 
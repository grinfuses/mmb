import os
from typing import Dict, List, Optional
from datetime import datetime
from .metadata_analyzer.analyzer import MetadataAnalyzer
from .quality_scorer.scorer import QualityScorer
from .llm_enhancer.enhancer import LLMEnhancer
from .report_generator.generator import ReportGenerator
from .dataset_recommender.recommender import DatasetRecommender

class MadridMetadataBooster:
    def __init__(self, 
                 catalog_url: str,
                 openai_api_key: Optional[str] = None,
                 output_dir: str = 'reports'):
        """
        Initialize the Madrid Metadata Booster
        
        Args:
            catalog_url: URL of the Madrid open data catalog
            openai_api_key: OpenAI API key (optional, can be set via environment variable)
            output_dir: Directory for generated reports
        """
        self.catalog_url = catalog_url
        self.output_dir = output_dir
        
        # Initialize components
        self.metadata_analyzer = MetadataAnalyzer(catalog_url)
        self.quality_scorer = QualityScorer()
        self.llm_enhancer = LLMEnhancer(api_key=openai_api_key)
        self.report_generator = ReportGenerator()
        self.dataset_recommender = DatasetRecommender()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def analyze_catalog(self) -> Dict:
        """Analyze the entire catalog and generate reports"""
        # Analyze metadata
        analysis_df = self.metadata_analyzer.analyze_metadata()
        
        # Calculate quality scores
        quality_scores = self.quality_scorer.calculate_scores(analysis_df)
        quality_summary = self.quality_scorer.get_quality_summary(quality_scores)
        
        # Get problematic datasets
        problematic_datasets = self.metadata_analyzer.get_problematic_datasets()
        
        # Enhance metadata for problematic datasets
        enhanced_metadata = self.llm_enhancer.batch_enhance(problematic_datasets)
        enhancement_summary = self.llm_enhancer.get_enhancement_summary(enhanced_metadata)
        
        # Generate report
        report_paths = self.report_generator.generate_monthly_report(
            quality_scores=[vars(score) for score in quality_scores],
            enhanced_metadata=[vars(metadata) for metadata in enhanced_metadata],
            problematic_datasets=problematic_datasets,
            quality_summary=quality_summary,
            enhancement_summary=enhancement_summary,
            output_dir=self.output_dir,
            format='both'
        )
        
        # Train recommender
        self.dataset_recommender.fit(self.metadata_analyzer.datasets)
        
        return {
            'quality_summary': quality_summary,
            'enhancement_summary': enhancement_summary,
            'report_paths': report_paths
        }
    
    def get_dataset_recommendations(self, 
                                  dataset_id: Optional[str] = None,
                                  text: Optional[str] = None,
                                  category: Optional[str] = None,
                                  n_recommendations: int = 5) -> List[Dict]:
        """Get dataset recommendations based on different criteria"""
        if dataset_id:
            recommendations = self.dataset_recommender.get_recommendations(
                dataset_id, n_recommendations=n_recommendations
            )
        elif text:
            recommendations = self.dataset_recommender.get_recommendations_by_text(
                text, n_recommendations=n_recommendations
            )
        elif category:
            recommendations = self.dataset_recommender.get_recommendations_by_category(
                category, n_recommendations=n_recommendations
            )
        else:
            raise ValueError("Must provide either dataset_id, text, or category")
            
        return [vars(rec) for rec in recommendations]
    
    def enhance_single_dataset(self, dataset_id: str) -> Dict:
        """Enhance metadata for a single dataset"""
        dataset = next(
            (d for d in self.metadata_analyzer.datasets if d.id == dataset_id),
            None
        )
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found")
            
        enhanced = self.llm_enhancer.enhance_metadata(vars(dataset))
        return vars(enhanced)

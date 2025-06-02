import os
from datetime import datetime
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass

@dataclass
class ReportData:
    quality_scores: List[Dict]
    enhanced_metadata: List[Dict]
    problematic_datasets: List[Dict]
    quality_summary: Dict
    enhancement_summary: Dict
    generation_date: datetime

class ReportGenerator:
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
    def generate_html_report(self, data: ReportData, output_path: str) -> str:
        """Generate an HTML report"""
        template = self.env.get_template('report_template.html')
        html_content = template.render(
            quality_scores=data.quality_scores,
            enhanced_metadata=data.enhanced_metadata,
            problematic_datasets=data.problematic_datasets,
            quality_summary=data.quality_summary,
            enhancement_summary=data.enhancement_summary,
            generation_date=data.generation_date.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return output_path
    
    def generate_monthly_report(self, 
                              quality_scores: List[Dict],
                              enhanced_metadata: List[Dict],
                              problematic_datasets: List[Dict],
                              quality_summary: Dict,
                              enhancement_summary: Dict,
                              output_dir: str,
                              format: str = 'html') -> Dict[str, str]:
        """Generate monthly report in HTML format"""
        data = ReportData(
            quality_scores=quality_scores,
            enhanced_metadata=enhanced_metadata,
            problematic_datasets=problematic_datasets,
            quality_summary=quality_summary,
            enhancement_summary=enhancement_summary,
            generation_date=datetime.now()
        )
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with current month and year
        timestamp = datetime.now().strftime('%Y%m')
        base_filename = f'metadata_quality_report_{timestamp}'
        
        output_paths = {}
        
        if format in ['html', 'both']:
            html_path = os.path.join(output_dir, f'{base_filename}.html')
            output_paths['html'] = self.generate_html_report(data, html_path)
            
        return output_paths 
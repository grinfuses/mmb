from typing import Dict, List
import pandas as pd
from dataclasses import dataclass

@dataclass
class QualityScore:
    dataset_id: str
    overall_score: float
    metadata_score: float
    format_score: float
    license_score: float
    frequency_score: float
    description_score: float
    category_score: float
    tags_score: float
    issues: List[str]

class QualityScorer:
    def __init__(self):
        self.weights = {
            'metadata': 0.3,
            'format': 0.2,
            'license': 0.15,
            'frequency': 0.15,
            'description': 0.1,
            'category': 0.05,
            'tags': 0.05
        }
    
    def calculate_scores(self, analysis_df: pd.DataFrame) -> List[QualityScore]:
        """Calculate quality scores for all datasets"""
        scores = []
        
        for _, row in analysis_df.iterrows():
            # Calculate individual component scores
            metadata_score = self._calculate_metadata_score(row)
            format_score = row['format_score']
            license_score = row['license_score']
            frequency_score = row['frequency_score']
            description_score = self._calculate_description_score(row)
            category_score = 1.0 if row['has_category'] else 0.0
            tags_score = min(row['num_tags'] / 5, 1.0)  # Normalize to 1.0
            
            # Calculate weighted overall score
            overall_score = (
                metadata_score * self.weights['metadata'] +
                format_score * self.weights['format'] +
                license_score * self.weights['license'] +
                frequency_score * self.weights['frequency'] +
                description_score * self.weights['description'] +
                category_score * self.weights['category'] +
                tags_score * self.weights['tags']
            )
            
            # Collect issues
            issues = self._collect_issues(row)
            
            scores.append(QualityScore(
                dataset_id=row['id'],
                overall_score=overall_score,
                metadata_score=metadata_score,
                format_score=format_score,
                license_score=license_score,
                frequency_score=frequency_score,
                description_score=description_score,
                category_score=category_score,
                tags_score=tags_score,
                issues=issues
            ))
        
        return scores
    
    def _calculate_metadata_score(self, row: pd.Series) -> float:
        """Calculate score for metadata completeness"""
        score = 0.0
        if row['title_length'] > 0:
            score += 0.2
        if row['description_length'] > 0:
            score += 0.2
        if row['has_category']:
            score += 0.2
        if row['num_tags'] > 0:
            score += 0.2
        if row['format_score'] > 0:
            score += 0.2
        return score
    
    def _calculate_description_score(self, row: pd.Series) -> float:
        """Calculate score for description quality"""
        if not row['has_description']:
            return 0.0
        length = row['description_length']
        if length < 50:
            return 0.3
        elif length < 100:
            return 0.6
        elif length < 200:
            return 0.8
        else:
            return 1.0
    
    def _collect_issues(self, row: pd.Series) -> List[str]:
        """Collect quality issues for the dataset"""
        issues = []
        
        if row['title_length'] < 10:
            issues.append("Título demasiado corto")
        if row['description_length'] < 50:
            issues.append("Descripción insuficiente")
        if not row['has_category']:
            issues.append("Falta categoría")
        if row['num_tags'] < 3:
            issues.append("Pocas etiquetas")
        if row['format_score'] < 0.7:
            issues.append("Formato no óptimo")
        if row['license_score'] < 0.8:
            issues.append("Licencia restrictiva")
        if row['frequency_score'] < 0.6:
            issues.append("Baja frecuencia de actualización")
        if row['days_since_update'] > 365:
            issues.append("Dataset desactualizado")
            
        return issues
    
    def get_quality_summary(self, scores: List[QualityScore]) -> Dict:
        """Generate a summary of quality scores"""
        return {
            'total_datasets': len(scores),
            'average_score': sum(s.overall_score for s in scores) / len(scores),
            'score_distribution': {
                'excellent': len([s for s in scores if s.overall_score >= 0.8]),
                'good': len([s for s in scores if 0.6 <= s.overall_score < 0.8]),
                'fair': len([s for s in scores if 0.4 <= s.overall_score < 0.6]),
                'poor': len([s for s in scores if s.overall_score < 0.4])
            },
            'common_issues': self._get_common_issues(scores)
        }
    
    def _get_common_issues(self, scores: List[QualityScore]) -> Dict[str, int]:
        """Count frequency of common issues"""
        issue_counts = {}
        for score in scores:
            for issue in score.issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        return dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)) 
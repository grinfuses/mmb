from typing import Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass

@dataclass
class DatasetRecommendation:
    dataset_id: str
    title: str
    similarity_score: float
    common_tags: List[str]
    common_categories: List[str]

class DatasetRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.datasets = []
        self.tfidf_matrix = None
        
    def fit(self, datasets: List[Dict]):
        """Fit the recommender with the dataset catalog"""
        self.datasets = datasets
        
        # Prepare text for vectorization
        texts = []
        for dataset in datasets:
            text = f"{dataset.get('title', '')} {dataset.get('description', '')} "
            text += ' '.join(dataset.get('tags', []))
            text += f" {dataset.get('category', '')}"
            texts.append(text)
            
        # Create TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        
    def get_recommendations(self, 
                          dataset_id: str, 
                          n_recommendations: int = 5,
                          min_similarity: float = 0.1) -> List[DatasetRecommendation]:
        """Get recommendations for a specific dataset"""
        # Find the index of the target dataset
        target_idx = next((i for i, d in enumerate(self.datasets) if d['id'] == dataset_id), None)
        if target_idx is None:
            raise ValueError(f"Dataset with ID {dataset_id} not found")
            
        # Calculate similarity scores
        target_vector = self.tfidf_matrix[target_idx]
        similarity_scores = cosine_similarity(target_vector, self.tfidf_matrix).flatten()
        
        # Get indices of most similar datasets (excluding the target)
        similar_indices = np.argsort(similarity_scores)[::-1][1:n_recommendations+1]
        
        recommendations = []
        target_dataset = self.datasets[target_idx]
        
        for idx in similar_indices:
            score = similarity_scores[idx]
            if score < min_similarity:
                continue
                
            dataset = self.datasets[idx]
            
            # Find common tags and categories
            common_tags = list(set(target_dataset.get('tags', [])) & 
                             set(dataset.get('tags', [])))
            common_categories = []
            if target_dataset.get('category') == dataset.get('category'):
                common_categories.append(target_dataset['category'])
                
            recommendations.append(DatasetRecommendation(
                dataset_id=dataset['id'],
                title=dataset['title'],
                similarity_score=float(score),
                common_tags=common_tags,
                common_categories=common_categories
            ))
            
        return recommendations
    
    def get_recommendations_by_text(self,
                                  text: str,
                                  n_recommendations: int = 5,
                                  min_similarity: float = 0.1) -> List[DatasetRecommendation]:
        """Get recommendations based on a text query"""
        # Transform the query text
        query_vector = self.vectorizer.transform([text])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get indices of most similar datasets
        similar_indices = np.argsort(similarity_scores)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in similar_indices:
            score = similarity_scores[idx]
            if score < min_similarity:
                continue
                
            dataset = self.datasets[idx]
            recommendations.append(DatasetRecommendation(
                dataset_id=dataset['id'],
                title=dataset['title'],
                similarity_score=float(score),
                common_tags=dataset.get('tags', []),
                common_categories=[dataset.get('category', '')] if dataset.get('category') else []
            ))
            
        return recommendations
    
    def get_recommendations_by_category(self,
                                      category: str,
                                      n_recommendations: int = 5) -> List[DatasetRecommendation]:
        """Get recommendations based on a category"""
        # Filter datasets by category
        category_datasets = [d for d in self.datasets if d.get('category') == category]
        
        if not category_datasets:
            return []
            
        # Calculate average similarity within category
        category_indices = [i for i, d in enumerate(self.datasets) if d.get('category') == category]
        category_matrix = self.tfidf_matrix[category_indices]
        similarity_matrix = cosine_similarity(category_matrix)
        
        # Calculate average similarity for each dataset
        avg_similarities = np.mean(similarity_matrix, axis=1)
        
        # Get top recommendations
        top_indices = np.argsort(avg_similarities)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_indices:
            dataset = category_datasets[idx]
            recommendations.append(DatasetRecommendation(
                dataset_id=dataset['id'],
                title=dataset['title'],
                similarity_score=float(avg_similarities[idx]),
                common_tags=dataset.get('tags', []),
                common_categories=[category]
            ))
            
        return recommendations 
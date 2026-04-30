"""Recommendation service for finding similar poems."""

from typing import Optional
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationService:
    """Service for content-based poem recommendations."""
    
    def __init__(self):
        self._state = None
    
    @property
    def state(self):
        """Lazy load app state."""
        if self._state is None:
            from ..core import app_state
            self._state = app_state
        return self._state
    
    def get_recommendations(self, text: str, limit: int = 5) -> list[dict]:
        """
        Get poem recommendations based on input text.
        
        Uses clustering and cosine similarity to find similar poems.
        
        Args:
            text: Input poem text to find similar poems for
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended poems with metadata
        """
        if not self.state.models_loaded:
            return [{"poem": "Model not loaded", "similarity": 0}]
        
        if not text or not isinstance(text, str) or not text.strip():
            return [{"poem": "Invalid Input", "similarity": 0}]
        
        try:
            # Encode input text
            poem_vector = self.state.embedding_model.encode([text])
            
            # Find cluster
            cluster_label = self.state.kmeans.predict(poem_vector)[0]
            
            # Filter poems in same cluster
            cluster_df = self.state.poem_df[self.state.poem_df['labels'] == cluster_label]
            
            if cluster_df.empty:
                return [{"poem": "No similar poems found", "similarity": 0}]
            
            # Get embeddings columns (assuming 768-dimensional embeddings)
            embedding_columns = [str(i) for i in range(768)]
            cluster_embeddings = cluster_df[embedding_columns].values
            
            # Compute similarities
            similarity_scores = cosine_similarity(poem_vector, cluster_embeddings).flatten()
            
            # Get top similar poems
            top_indices = similarity_scores.argsort()[-limit:][::-1]
            
            recommendations = []
            for idx in top_indices:
                poem_data = cluster_df.iloc[idx]
                recommendations.append({
                    "poem": poem_data.get('poem', 'Unknown'),
                    "similarity": float(similarity_scores[idx]),
                    "label": int(cluster_label)
                })
            
            return recommendations
            
        except Exception as e:
            return [{"poem": f"Recommendation error: {str(e)}", "similarity": 0}]
    
    def get_clusters(self) -> list[int]:
        """Get available cluster labels."""
        if not self.state.models_loaded or self.state.poem_df is None:
            return []
        
        try:
            return sorted(self.state.poem_df['labels'].unique().tolist())
        except Exception:
            return []


recommendation_service = RecommendationService()

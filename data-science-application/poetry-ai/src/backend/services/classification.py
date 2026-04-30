"""Classification service for poem categorization."""

from typing import Optional


class ClassificationService:
    """Service for classifying poems using trained ML models."""
    
    def __init__(self):
        self._state = None
    
    @property
    def state(self):
        """Lazy load app state."""
        if self._state is None:
            from ..core import app_state
            self._state = app_state
        return self._state
    
    def classify(self, text: str) -> str:
        """
        Classify a poem or text into a category.
        
        Args:
            text: The text to classify
            
        Returns:
            Classification label/category
        """
        if not self.state.models_loaded:
            return "Model not loaded"
        
        if not text or not isinstance(text, str) or not text.strip():
            return "Invalid Input"
        
        try:
            embedding = self.state.embedding_model.encode([text])
            prediction = self.state.svm_classifier.predict(embedding)[0]
            return f"Class {prediction}"
        except Exception as e:
            return f"Classification error: {str(e)}"
    
    def get_classification_labels(self) -> list[str]:
        """Get available classification labels."""
        if not self.state.models_loaded or self.state.svm_classifier is None:
            return []
        
        try:
            return list(self.state.svm_classifier.classes_)
        except Exception:
            return []


classification_service = ClassificationService()

import os
from pathlib import Path
import torch
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # --- Configuration ---

    # API Keys / Models
    PINECONE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/embedding-001"
    TEMPERATURE: float = 0.1

    PINECONE_INDEX_NAME: str = "poetryqa"
    POET_NAMESPACE: str = "poet"
    POEM_NAMESPACE: str = "poem"

    # Paths (resolved from repo root)
    _REPO_ROOT: Path = Path(__file__).resolve().parents[3]
    EMBEDDING_MODEL_PATH: str = str(_REPO_ROOT / 'models' / 'embedding')
    CLASSIFICATION_MODEL_PATH: str = str(_REPO_ROOT / 'models' / 'classification' / 'svm_model.pkl')
    CLUSTER_MODEL_PATH: str = str(_REPO_ROOT / 'models' / 'clustering' / 'kmeans.pkl')
    DATA_PATH: str = str(_REPO_ROOT / 'data' / 'poem_embedding_and_label.csv')

settings = Settings()
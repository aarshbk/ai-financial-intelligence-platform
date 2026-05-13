"""
Configuration Module
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"
    
    # LLM Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Document Processing
    PDF_UPLOAD_DIR = os.getenv("PDF_UPLOAD_DIR", "uploads")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
    
    # Embeddings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Vector Store
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "data/vector_store.json")
    
    # Create necessary directories
    os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)


def get_config():
    """Get configuration instance"""
    return Config()

"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

import torch
from pathlib import Path

class Settings:
    """Configuration settings for Latent-FS backend"""
    
    # Embedding configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    # ChromaDB configuration
    CHROMA_PERSIST_DIR = "./data/chroma"
    
    # Clustering configuration
    N_CLUSTERS = 5
    
    # Re-embedding configuration
    RE_EMBED_ALPHA = 0.3
    
    # LLM configuration
    LLM_MODEL_PATH = "./models/llama-7b.gguf"
    
    # Debouncing configuration
    DEBOUNCE_WINDOW_SECONDS = 2.0  # Minimum time between re-clustering operations
    
    # API configuration
    API_HOST = "0.0.0.0"
    API_PORT = 9999
    
    def __init__(self):
        """Initialize settings and create necessary directories"""
        Path(self.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        Path("./models").mkdir(parents=True, exist_ok=True)
        
        # Log device information
        if self.DEVICE == "cuda":
            print(f"GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
        else:
            print("No GPU detected, using CPU")

settings = Settings()

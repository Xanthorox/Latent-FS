"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

import torch
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating vector embeddings from text using GPU-accelerated transformer models.
    
    This service uses sentence-transformers library with CUDA support for efficient
    embedding generation. It automatically falls back to CPU if GPU is unavailable.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cuda"):
        """
        Initialize the embedding service with a sentence-transformer model.
        
        Args:
            model_name: Name of the sentence-transformer model to use
            device: Device to run the model on ('cuda' or 'cpu')
        
        Raises:
            RuntimeError: If GPU is requested but CUDA is not available
            Exception: If model loading fails
        """
        self.model_name = model_name
        self.device = self._validate_device(device)
        
        try:
            logger.info(f"Loading embedding model '{model_name}' on device '{self.device}'")
            self.model = SentenceTransformer(model_name, device=self.device)
            logger.info(f"Successfully loaded model on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _validate_device(self, requested_device: str) -> str:
        """
        Validate and configure the device for model execution.
        
        Args:
            requested_device: The requested device ('cuda' or 'cpu')
        
        Returns:
            The actual device to use ('cuda' or 'cpu')
        """
        if requested_device == "cuda":
            if torch.cuda.is_available():
                logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
                logger.info(f"CUDA version: {torch.version.cuda}")
                return "cuda"
            else:
                logger.warning(
                    "CUDA requested but not available. Falling back to CPU. "
                    "Performance will be significantly slower."
                )
                return "cpu"
        return "cpu"
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text string.
        
        Args:
            text: The text to embed
        
        Returns:
            A list of floats representing the embedding vector
        
        Raises:
            RuntimeError: If GPU memory is insufficient
            ValueError: If text is empty or invalid
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty or whitespace-only")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.error(
                    "GPU out of memory. Try using a smaller model or reducing batch size. "
                    "Consider using CPU mode or freeing GPU memory."
                )
                raise RuntimeError(
                    "Insufficient GPU memory for embedding generation. "
                    "Recommendations: 1) Use CPU mode, 2) Use a smaller model, "
                    "3) Free GPU memory from other processes"
                ) from e
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently using batch processing.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors, one for each input text
        
        Raises:
            RuntimeError: If GPU memory is insufficient
            ValueError: If any text is empty or invalid
        """
        if not texts:
            return []
        
        # Validate all texts
        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise ValueError(f"Text at index {i} cannot be empty or whitespace-only")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            return embeddings.tolist()
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                logger.error(
                    f"GPU out of memory while processing batch of {len(texts)} texts. "
                    "Try reducing batch size or using CPU mode."
                )
                raise RuntimeError(
                    f"Insufficient GPU memory for batch of {len(texts)} texts. "
                    "Recommendations: 1) Reduce batch size, 2) Use CPU mode, "
                    "3) Use a smaller model, 4) Free GPU memory from other processes"
                ) from e
            raise
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get information about the device being used for embeddings.
        
        Returns:
            Dictionary containing device information
        """
        info = {
            "device": self.device,
            "model_name": self.model_name,
            "cuda_available": torch.cuda.is_available(),
        }
        
        if torch.cuda.is_available():
            info.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "cuda_version": torch.version.cuda,
                "gpu_memory_allocated": torch.cuda.memory_allocated(0),
                "gpu_memory_reserved": torch.cuda.memory_reserved(0),
            })
        
        return info

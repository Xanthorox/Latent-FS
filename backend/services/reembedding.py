"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)


class ReEmbeddingEngine:
    """
    Engine for modifying document embeddings based on user drag-and-drop actions.
    
    This class implements the "drag-to-train" functionality by computing weighted
    averages between current embeddings and target cluster centroids. The alpha
    parameter controls the strength of the nudge toward the target.
    """
    
    def __init__(self, alpha: float = 0.3):
        """
        Initialize the re-embedding engine with blending weight.
        
        Args:
            alpha: Blending weight for weighted average (0.0 to 1.0)
                  Higher values = stronger nudge toward target
                  Recommended range: 0.2 - 0.4
        
        Raises:
            ValueError: If alpha is not in valid range [0.0, 1.0]
        """
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"Alpha must be between 0.0 and 1.0, got {alpha}")
        
        self.alpha = alpha
        logger.info(f"Initialized ReEmbeddingEngine with alpha={alpha}")
    
    def nudge_embedding(
        self,
        current_embedding: List[float],
        target_centroid: List[float]
    ) -> List[float]:
        """
        Compute weighted average between current embedding and target centroid.
        
        This method implements the core re-embedding logic:
        new_embedding = (1 - alpha) * current + alpha * target
        
        The resulting vector is normalized to unit length to maintain
        consistency with the original embedding space.
        
        Args:
            current_embedding: The document's current embedding vector
            target_centroid: The target cluster's centroid vector
        
        Returns:
            New embedding vector as a list of floats
        
        Raises:
            ValueError: If embeddings are invalid or have mismatched dimensions
        """
        # Validate inputs
        if not current_embedding or len(current_embedding) == 0:
            raise ValueError("Current embedding cannot be empty")
        
        if not target_centroid or len(target_centroid) == 0:
            raise ValueError("Target centroid cannot be empty")
        
        if len(current_embedding) != len(target_centroid):
            raise ValueError(
                f"Embedding dimension mismatch: current has {len(current_embedding)} "
                f"dimensions, target has {len(target_centroid)} dimensions"
            )
        
        # Convert to numpy arrays for efficient computation
        current = np.array(current_embedding)
        target = np.array(target_centroid)
        
        # Compute weighted average
        new_embedding = (1 - self.alpha) * current + self.alpha * target
        
        # Normalize to unit length
        norm = np.linalg.norm(new_embedding)
        if norm > 0:
            new_embedding = new_embedding / norm
        else:
            logger.warning("Normalized embedding has zero norm, returning unnormalized")
        
        # Validate that nudge moves toward target
        similarity_before = self.calculate_similarity(current_embedding, target_centroid)
        similarity_after = self.calculate_similarity(new_embedding.tolist(), target_centroid)
        
        if similarity_after <= similarity_before:
            logger.warning(
                f"Nudge did not increase similarity: before={similarity_before:.4f}, "
                f"after={similarity_after:.4f}"
            )
        else:
            logger.debug(
                f"Nudge successful: similarity increased from {similarity_before:.4f} "
                f"to {similarity_after:.4f}"
            )
        
        return new_embedding.tolist()
    
    def calculate_similarity(
        self,
        emb1: List[float],
        emb2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embedding vectors.
        
        Cosine similarity measures the cosine of the angle between two vectors,
        ranging from -1 (opposite) to 1 (identical). Higher values indicate
        greater semantic similarity.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
        
        Returns:
            Cosine similarity as a float between -1 and 1
        
        Raises:
            ValueError: If embeddings are invalid or have mismatched dimensions
        """
        # Validate inputs
        if not emb1 or len(emb1) == 0:
            raise ValueError("First embedding cannot be empty")
        
        if not emb2 or len(emb2) == 0:
            raise ValueError("Second embedding cannot be empty")
        
        if len(emb1) != len(emb2):
            raise ValueError(
                f"Embedding dimension mismatch: first has {len(emb1)} dimensions, "
                f"second has {len(emb2)} dimensions"
            )
        
        # Convert to numpy arrays
        vec1 = np.array(emb1)
        vec2 = np.array(emb2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            logger.warning("One or both embeddings have zero norm")
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Clamp to valid range due to floating point errors
        similarity = np.clip(similarity, -1.0, 1.0)
        
        return float(similarity)

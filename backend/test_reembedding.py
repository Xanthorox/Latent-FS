"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Tests for the re-embedding engine.
"""

import pytest
import numpy as np
from backend.services.reembedding import ReEmbeddingEngine


def test_reembedding_engine_initialization():
    """Test that ReEmbeddingEngine initializes correctly with valid alpha."""
    engine = ReEmbeddingEngine(alpha=0.3)
    assert engine.alpha == 0.3


def test_reembedding_engine_invalid_alpha():
    """Test that ReEmbeddingEngine raises error for invalid alpha values."""
    with pytest.raises(ValueError, match="Alpha must be between 0.0 and 1.0"):
        ReEmbeddingEngine(alpha=1.5)
    
    with pytest.raises(ValueError, match="Alpha must be between 0.0 and 1.0"):
        ReEmbeddingEngine(alpha=-0.1)


def test_calculate_similarity_identical_vectors():
    """Test that identical vectors have similarity of 1.0."""
    engine = ReEmbeddingEngine()
    vec = [1.0, 2.0, 3.0, 4.0]
    similarity = engine.calculate_similarity(vec, vec)
    assert abs(similarity - 1.0) < 1e-6


def test_calculate_similarity_orthogonal_vectors():
    """Test that orthogonal vectors have similarity close to 0.0."""
    engine = ReEmbeddingEngine()
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [0.0, 1.0, 0.0]
    similarity = engine.calculate_similarity(vec1, vec2)
    assert abs(similarity) < 1e-6


def test_calculate_similarity_opposite_vectors():
    """Test that opposite vectors have similarity of -1.0."""
    engine = ReEmbeddingEngine()
    vec1 = [1.0, 2.0, 3.0]
    vec2 = [-1.0, -2.0, -3.0]
    similarity = engine.calculate_similarity(vec1, vec2)
    assert abs(similarity - (-1.0)) < 1e-6


def test_calculate_similarity_dimension_mismatch():
    """Test that mismatched dimensions raise ValueError."""
    engine = ReEmbeddingEngine()
    vec1 = [1.0, 2.0, 3.0]
    vec2 = [1.0, 2.0]
    
    with pytest.raises(ValueError, match="dimension mismatch"):
        engine.calculate_similarity(vec1, vec2)


def test_calculate_similarity_empty_vectors():
    """Test that empty vectors raise ValueError."""
    engine = ReEmbeddingEngine()
    
    with pytest.raises(ValueError, match="cannot be empty"):
        engine.calculate_similarity([], [1.0, 2.0])
    
    with pytest.raises(ValueError, match="cannot be empty"):
        engine.calculate_similarity([1.0, 2.0], [])


def test_nudge_embedding_moves_toward_target():
    """Test that nudge_embedding moves the vector toward the target."""
    engine = ReEmbeddingEngine(alpha=0.3)
    
    # Create current and target vectors
    current = [1.0, 0.0, 0.0]
    target = [0.0, 1.0, 0.0]
    
    # Calculate similarity before nudge
    similarity_before = engine.calculate_similarity(current, target)
    
    # Nudge the embedding
    new_embedding = engine.nudge_embedding(current, target)
    
    # Calculate similarity after nudge
    similarity_after = engine.calculate_similarity(new_embedding, target)
    
    # Verify that similarity increased
    assert similarity_after > similarity_before


def test_nudge_embedding_weighted_average():
    """Test that nudge_embedding computes correct weighted average."""
    engine = ReEmbeddingEngine(alpha=0.5)
    
    current = [2.0, 0.0, 0.0]
    target = [0.0, 2.0, 0.0]
    
    new_embedding = engine.nudge_embedding(current, target)
    
    # With alpha=0.5, the unnormalized result should be [1.0, 1.0, 0.0]
    # After normalization, it should be approximately [0.707, 0.707, 0.0]
    expected = np.array([1.0, 1.0, 0.0])
    expected = expected / np.linalg.norm(expected)
    
    np.testing.assert_array_almost_equal(new_embedding, expected, decimal=5)


def test_nudge_embedding_dimension_mismatch():
    """Test that mismatched dimensions raise ValueError."""
    engine = ReEmbeddingEngine()
    current = [1.0, 2.0, 3.0]
    target = [1.0, 2.0]
    
    with pytest.raises(ValueError, match="dimension mismatch"):
        engine.nudge_embedding(current, target)


def test_nudge_embedding_empty_vectors():
    """Test that empty vectors raise ValueError."""
    engine = ReEmbeddingEngine()
    
    with pytest.raises(ValueError, match="cannot be empty"):
        engine.nudge_embedding([], [1.0, 2.0])
    
    with pytest.raises(ValueError, match="cannot be empty"):
        engine.nudge_embedding([1.0, 2.0], [])


def test_nudge_embedding_normalization():
    """Test that nudge_embedding returns normalized vectors."""
    engine = ReEmbeddingEngine(alpha=0.3)
    
    current = [3.0, 4.0, 0.0]
    target = [0.0, 5.0, 12.0]
    
    new_embedding = engine.nudge_embedding(current, target)
    
    # Check that the result is normalized (unit length)
    norm = np.linalg.norm(new_embedding)
    assert abs(norm - 1.0) < 1e-6


def test_nudge_embedding_with_different_alphas():
    """Test that different alpha values produce different nudge strengths."""
    current = [1.0, 0.0, 0.0]
    target = [0.0, 1.0, 0.0]
    
    # Small alpha (weak nudge)
    engine_weak = ReEmbeddingEngine(alpha=0.1)
    new_weak = engine_weak.nudge_embedding(current, target)
    similarity_weak = engine_weak.calculate_similarity(new_weak, target)
    
    # Large alpha (strong nudge)
    engine_strong = ReEmbeddingEngine(alpha=0.5)
    new_strong = engine_strong.nudge_embedding(current, target)
    similarity_strong = engine_strong.calculate_similarity(new_strong, target)
    
    # Stronger alpha should result in higher similarity to target
    assert similarity_strong > similarity_weak


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

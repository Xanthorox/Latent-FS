"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Quick test script for the embedding service
"""

from services.embedding import EmbeddingService
from config import settings

def test_embedding_service():
    print("Testing Embedding Service...")
    print(f"Device: {settings.DEVICE}")
    
    # Initialize service
    service = EmbeddingService(model_name=settings.EMBEDDING_MODEL, device=settings.DEVICE)
    
    # Test device info
    print("\nDevice Info:")
    info = service.get_device_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test single embedding
    print("\nTesting single text embedding...")
    text = "This is a test document about machine learning."
    embedding = service.embed_text(text)
    print(f"  Text: {text}")
    print(f"  Embedding dimension: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")
    
    # Test batch embedding
    print("\nTesting batch embedding...")
    texts = [
        "Space exploration and astronomy",
        "Cooking recipes and culinary arts",
        "Python programming and software development"
    ]
    embeddings = service.embed_batch(texts)
    print(f"  Number of texts: {len(texts)}")
    print(f"  Number of embeddings: {len(embeddings)}")
    print(f"  Each embedding dimension: {len(embeddings[0])}")
    
    # Test error handling
    print("\nTesting error handling...")
    try:
        service.embed_text("")
        print("  ERROR: Should have raised ValueError for empty text")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}")
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_embedding_service()

"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Test script to verify GPU usage during embedding generation
"""

import torch
from backend.services.embedding import EmbeddingService
from backend.config import settings

def test_gpu_usage():
    """Test that embeddings are generated on GPU"""
    print("\n" + "="*60)
    print("Testing GPU Usage During Embedding Generation")
    print("="*60 + "\n")
    
    # Initialize embedding service
    print(f"1. Initializing EmbeddingService with device: {settings.DEVICE}")
    service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    
    # Check device info
    device_info = service.get_device_info()
    print(f"\n2. Device Information:")
    print(f"   - Device: {device_info['device']}")
    if 'gpu_name' in device_info:
        print(f"   - GPU Name: {device_info['gpu_name']}")
    print(f"   - CUDA Available: {device_info['cuda_available']}")
    
    # Generate embeddings
    print(f"\n3. Generating embeddings...")
    test_texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is transforming artificial intelligence",
        "Python is a versatile programming language"
    ]
    
    embeddings = service.embed_batch(test_texts)
    
    print(f"   ✓ Generated {len(embeddings)} embeddings")
    print(f"   ✓ Embedding dimension: {len(embeddings[0])}")
    
    # Verify model is on correct device
    model_device = next(service.model.parameters()).device
    print(f"\n4. Model Device Verification:")
    print(f"   - Model is on: {model_device}")
    print(f"   - Expected device: {settings.DEVICE}")
    
    if str(model_device).startswith('cuda'):
        print(f"\n✓ SUCCESS: Model is using GPU acceleration!")
    else:
        print(f"\n⚠ WARNING: Model is using CPU (expected GPU)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_gpu_usage()

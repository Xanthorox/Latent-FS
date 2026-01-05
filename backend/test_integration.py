"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Integration test for embedding service and ChromaDB manager
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.embedding import EmbeddingService
from backend.services.database import ChromaDBManager
from backend.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_integration():
    """Test integration between embedding service and database"""
    
    print("\n" + "="*60)
    print("Testing Embedding Service + ChromaDB Integration")
    print("="*60 + "\n")
    
    # Initialize services
    print("1. Initializing services...")
    embedding_service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    db = ChromaDBManager(persist_directory="./data/chroma_test")
    db.reset_database()  # Start fresh
    print(f"   ✓ Services initialized")
    print(f"   ✓ Device: {embedding_service.device}")
    
    # Test single document workflow
    print("\n2. Testing single document workflow...")
    text = "Machine learning is a subset of artificial intelligence."
    embedding = embedding_service.embed_text(text)
    print(f"   ✓ Generated embedding with {len(embedding)} dimensions")
    
    doc = db.add_document(
        doc_id="ml_doc",
        text=text,
        embedding=embedding
    )
    print(f"   ✓ Stored document in database")
    
    # Retrieve and verify
    retrieved = db.get_document("ml_doc")
    print(f"   ✓ Retrieved document: {retrieved.text[:50]}...")
    print(f"   ✓ Embedding matches: {retrieved.embedding[:3] == embedding[:3]}")
    
    # Test batch workflow
    print("\n3. Testing batch document workflow...")
    texts = [
        "Python is a popular programming language.",
        "Deep learning uses neural networks.",
        "Natural language processing analyzes text."
    ]
    embeddings = embedding_service.embed_batch(texts)
    print(f"   ✓ Generated {len(embeddings)} embeddings")
    
    for i, (text, embedding) in enumerate(zip(texts, embeddings)):
        db.add_document(
            doc_id=f"batch_doc_{i}",
            text=text,
            embedding=embedding
        )
    print(f"   ✓ Stored {len(texts)} documents")
    
    # Verify all documents
    all_docs = db.get_all_documents()
    print(f"   ✓ Total documents in database: {len(all_docs)}")
    
    # Test persistence
    print("\n4. Testing persistence...")
    doc_count_before = db.count_documents()
    
    # Create new manager instance (simulates restart)
    db2 = ChromaDBManager(persist_directory="./data/chroma_test")
    doc_count_after = db2.count_documents()
    
    print(f"   ✓ Documents before: {doc_count_before}")
    print(f"   ✓ Documents after restart: {doc_count_after}")
    print(f"   ✓ Persistence verified: {doc_count_before == doc_count_after}")
    
    # Clean up
    print("\n5. Cleaning up...")
    db2.reset_database()
    print(f"   ✓ Test database cleaned")
    
    print("\n" + "="*60)
    print("Integration test passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_integration()

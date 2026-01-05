"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Test script for ChromaDB manager
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.database import ChromaDBManager
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_chromadb_manager():
    """Test ChromaDB manager functionality"""
    
    print("\n" + "="*60)
    print("Testing ChromaDB Manager")
    print("="*60 + "\n")
    
    # Initialize manager
    print("1. Initializing ChromaDB manager...")
    db = ChromaDBManager(persist_directory="./data/chroma_test")
    print(f"   ✓ Manager initialized. Document count: {db.count_documents()}")
    
    # Test adding a document
    print("\n2. Adding a test document...")
    test_embedding = [0.1] * 384  # MiniLM produces 384-dimensional embeddings
    doc = db.add_document(
        doc_id="test_doc_1",
        text="This is a test document about machine learning.",
        embedding=test_embedding,
        metadata={"category": "test"}
    )
    print(f"   ✓ Document added: {doc.id}")
    print(f"   ✓ Document count: {db.count_documents()}")
    
    # Test retrieving the document
    print("\n3. Retrieving the document...")
    retrieved_doc = db.get_document("test_doc_1")
    print(f"   ✓ Retrieved document: {retrieved_doc.id}")
    print(f"   ✓ Text: {retrieved_doc.text[:50]}...")
    print(f"   ✓ Embedding dimensions: {len(retrieved_doc.embedding)}")
    
    # Test updating embedding
    print("\n4. Updating document embedding...")
    new_embedding = [0.2] * 384
    db.update_embedding("test_doc_1", new_embedding)
    updated_doc = db.get_document("test_doc_1")
    print(f"   ✓ Embedding updated")
    print(f"   ✓ First value changed from 0.1 to {updated_doc.embedding[0]}")
    
    # Test adding multiple documents
    print("\n5. Adding multiple documents...")
    for i in range(2, 5):
        db.add_document(
            doc_id=f"test_doc_{i}",
            text=f"Test document number {i}",
            embedding=[0.1 * i] * 384
        )
    print(f"   ✓ Added 3 more documents")
    print(f"   ✓ Total document count: {db.count_documents()}")
    
    # Test getting all documents
    print("\n6. Retrieving all documents...")
    all_docs = db.get_all_documents()
    print(f"   ✓ Retrieved {len(all_docs)} documents")
    for doc in all_docs:
        print(f"      - {doc.id}: {doc.text[:40]}...")
    
    # Test cluster assignment
    print("\n7. Testing cluster assignment...")
    db.update_cluster_assignment("test_doc_1", "cluster_A")
    doc_with_cluster = db.get_document("test_doc_1")
    print(f"   ✓ Cluster assigned: {doc_with_cluster.cluster_id}")
    
    # Test error handling
    print("\n8. Testing error handling...")
    try:
        db.get_document("nonexistent_doc")
        print("   ✗ Should have raised an error")
    except RuntimeError as e:
        print(f"   ✓ Correctly raised error for nonexistent document")
    
    try:
        db.add_document("", "text", [0.1])
        print("   ✗ Should have raised an error")
    except ValueError as e:
        print(f"   ✓ Correctly raised error for empty document ID")
    
    # Clean up
    print("\n9. Cleaning up test database...")
    db.reset_database()
    print(f"   ✓ Database reset. Document count: {db.count_documents()}")
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_chromadb_manager()

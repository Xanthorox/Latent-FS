"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Test script for mock data generation
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.mock_data import get_mock_documents, populate_database_with_mock_data
from backend.services.database import ChromaDBManager
from backend.services.embedding import EmbeddingService
from backend.config import settings

def test_mock_data_structure():
    """Test that mock data has the correct structure"""
    print("Testing mock data structure...")
    docs = get_mock_documents()
    
    assert len(docs) == 20, f"Expected 20 documents, got {len(docs)}"
    
    # Check categories
    categories = {}
    for doc in docs:
        assert 'text' in doc, "Document missing 'text' field"
        assert 'category' in doc, "Document missing 'category' field"
        assert len(doc['text']) > 0, "Document text is empty"
        
        category = doc['category']
        categories[category] = categories.get(category, 0) + 1
    
    print(f"Found {len(docs)} documents across {len(categories)} categories:")
    for category, count in sorted(categories.items()):
        print(f"  - {category}: {count} documents")
    
    # Verify expected categories
    expected_categories = {'Space', 'Cooking', 'Coding', 'History', 'Finance', 'Sports'}
    actual_categories = set(categories.keys())
    assert actual_categories == expected_categories, \
        f"Category mismatch. Expected {expected_categories}, got {actual_categories}"
    
    print("✓ Mock data structure is correct\n")


def test_database_population():
    """Test populating database with mock data"""
    print("Testing database population...")
    
    # Use a test database directory
    test_db_path = "./data/chroma_test"
    
    try:
        # Initialize services
        db_manager = ChromaDBManager(persist_directory=test_db_path)
        
        # Reset database to ensure it's empty
        db_manager.reset_database()
        
        # Verify it's empty
        count_before = db_manager.count_documents()
        assert count_before == 0, f"Database should be empty, but has {count_before} documents"
        
        # Initialize embedding service
        embedding_service = EmbeddingService(
            model_name=settings.EMBEDDING_MODEL,
            device=settings.DEVICE
        )
        
        # Populate with mock data
        num_added = populate_database_with_mock_data(db_manager, embedding_service)
        print(f"Added {num_added} documents to database")
        
        # Verify documents were added
        count_after = db_manager.count_documents()
        assert count_after == 20, f"Expected 20 documents, got {count_after}"
        assert num_added == 20, f"Expected to add 20 documents, but added {num_added}"
        
        # Retrieve and verify documents
        all_docs = db_manager.get_all_documents()
        assert len(all_docs) == 20, f"Expected 20 documents, retrieved {len(all_docs)}"
        
        # Verify embeddings exist and have correct dimensions
        for doc in all_docs:
            assert doc.embedding is not None, f"Document {doc.id} has no embedding"
            assert len(doc.embedding) > 0, f"Document {doc.id} has empty embedding"
            assert doc.text is not None and len(doc.text) > 0, f"Document {doc.id} has no text"
        
        print(f"✓ Successfully populated database with {count_after} documents")
        print(f"✓ All documents have valid embeddings (dimension: {len(all_docs[0].embedding)})\n")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Mock Data Generation Tests")
    print("=" * 60 + "\n")
    
    test_mock_data_structure()
    test_database_population()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)

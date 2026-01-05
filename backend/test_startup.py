"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Test script for startup mock data initialization
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.database import ChromaDBManager
from backend.services.embedding import EmbeddingService
from backend.services.mock_data import populate_database_with_mock_data
from backend.config import settings

def test_startup_with_empty_database():
    """Test startup behavior when database is empty"""
    print("Test 1: Startup with empty database")
    print("-" * 60)
    
    # Use a test database directory
    test_db_path = "./data/chroma_startup_test"
    
    try:
        # Initialize database
        db_manager = ChromaDBManager(persist_directory=test_db_path)
        
        # Reset to ensure it's empty
        db_manager.reset_database()
        
        # Simulate startup logic
        doc_count = db_manager.count_documents()
        print(f"Initial document count: {doc_count}")
        
        if doc_count == 0:
            print("Database is empty. Populating with mock data...")
            embedding_service = EmbeddingService(
                model_name=settings.EMBEDDING_MODEL,
                device=settings.DEVICE
            )
            
            num_docs = populate_database_with_mock_data(db_manager, embedding_service)
            print(f"Successfully added {num_docs} mock documents to the database")
            
            # Verify
            final_count = db_manager.count_documents()
            assert final_count == 20, f"Expected 20 documents, got {final_count}"
            print(f"✓ Database now contains {final_count} documents")
        else:
            print(f"Database already contains {doc_count} documents")
        
        print()
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise


def test_startup_with_existing_data():
    """Test startup behavior when database already has data"""
    print("Test 2: Startup with existing data")
    print("-" * 60)
    
    # Use the same test database (should now have data)
    test_db_path = "./data/chroma_startup_test"
    
    try:
        # Initialize database (should have data from previous test)
        db_manager = ChromaDBManager(persist_directory=test_db_path)
        
        # Simulate startup logic
        doc_count = db_manager.count_documents()
        print(f"Initial document count: {doc_count}")
        
        if doc_count == 0:
            print("Database is empty. Populating with mock data...")
            embedding_service = EmbeddingService(
                model_name=settings.EMBEDDING_MODEL,
                device=settings.DEVICE
            )
            
            num_docs = populate_database_with_mock_data(db_manager, embedding_service)
            print(f"Successfully added {num_docs} mock documents to the database")
        else:
            print(f"✓ Database already contains {doc_count} documents (skipping mock data)")
            assert doc_count == 20, f"Expected 20 documents from previous test, got {doc_count}"
        
        print()
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Startup Mock Data Initialization Tests")
    print("=" * 60 + "\n")
    
    test_startup_with_empty_database()
    test_startup_with_existing_data()
    
    print("=" * 60)
    print("All startup tests passed! ✓")
    print("=" * 60)

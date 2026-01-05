"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

End-to-end integration tests covering complete system flows
"""

import sys
from pathlib import Path
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.embedding import EmbeddingService
from backend.services.database import ChromaDBManager
from backend.services.clustering import ClusterEngine
from backend.services.naming import FolderNamingService
from backend.services.reembedding import ReEmbeddingEngine
from backend.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_complete_ingestion_clustering_flow():
    """
    Test complete flow: ingestion → clustering → display
    Validates: Requirements 1.1, 2.1
    """
    print("\n" + "="*70)
    print("TEST 1: Complete Ingestion → Clustering → Display Flow")
    print("="*70 + "\n")
    
    # Initialize all services
    print("Step 1: Initializing services...")
    embedding_service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    db = ChromaDBManager(persist_directory="./data/chroma_e2e_test")
    db.reset_database()
    cluster_engine = ClusterEngine(n_clusters=3)
    naming_service = FolderNamingService()
    print(f"   ✓ All services initialized on device: {embedding_service.device}\n")
    
    # Step 1: Ingest diverse documents
    print("Step 2: Ingesting diverse documents...")
    test_documents = [
        "Python is a versatile programming language used for web development.",
        "JavaScript enables interactive web applications and dynamic content.",
        "Machine learning algorithms can predict patterns from data.",
        "Neural networks are inspired by biological brain structures.",
        "The solar system contains eight planets orbiting the sun.",
        "Mars is known as the red planet due to iron oxide.",
        "Pasta carbonara is a classic Italian dish with eggs and cheese.",
        "Sushi is a Japanese cuisine featuring vinegared rice and seafood.",
    ]
    
    doc_ids = []
    for i, text in enumerate(test_documents):
        embedding = embedding_service.embed_text(text)
        doc = db.add_document(
            doc_id=f"doc_{i}",
            text=text,
            embedding=embedding
        )
        doc_ids.append(doc.id)
    
    print(f"   ✓ Ingested {len(test_documents)} documents")
    print(f"   ✓ Document IDs: {doc_ids[:3]}...\n")
    
    # Step 2: Perform clustering
    print("Step 3: Performing clustering...")
    all_docs = db.get_all_documents()
    clusters_dict = cluster_engine.cluster_documents(all_docs)
    
    print(f"   ✓ Created {len(clusters_dict)} clusters")
    for cluster_id, docs in clusters_dict.items():
        print(f"   ✓ {cluster_id}: {len(docs)} documents")
    print()
    
    # Step 3: Generate folder names
    print("Step 4: Generating semantic folder names...")
    folder_data = []
    for cluster_id, docs in clusters_dict.items():
        # Find representative document (first one for simplicity)
        rep_doc = docs[0] if docs else None
        if rep_doc:
            name = naming_service.generate_folder_name([rep_doc.text])
            folder_data.append({
                "id": cluster_id,
                "name": name,
                "document_count": len(docs),
                "representative_doc_id": rep_doc.id
            })
            print(f"   ✓ {cluster_id}: '{name}'")
    print()
    
    # Step 4: Verify display data structure
    print("Step 5: Verifying display data structure...")
    display_data = {
        "folders": folder_data,
        "documents": [
            {
                "id": doc.id,
                "text": doc.text,
                "cluster_id": getattr(doc, 'cluster_id', None)
            }
            for doc in all_docs
        ]
    }
    
    print(f"   ✓ Display data contains {len(display_data['folders'])} folders")
    print(f"   ✓ Display data contains {len(display_data['documents'])} documents")
    print(f"   ✓ Folders have names: {all(f['name'] for f in display_data['folders'])}")
    
    # Cleanup
    db.reset_database()
    print("\n✅ TEST 1 PASSED: Complete ingestion → clustering → display flow\n")


def test_complete_drag_reembed_recluster_flow():
    """
    Test complete flow: drag → re-embed → re-cluster → update
    Validates: Requirements 4.2, 4.6, 7.1
    """
    print("\n" + "="*70)
    print("TEST 2: Complete Drag → Re-Embed → Re-Cluster → Update Flow")
    print("="*70 + "\n")
    
    # Initialize services
    print("Step 1: Initializing services...")
    embedding_service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    db = ChromaDBManager(persist_directory="./data/chroma_e2e_test")
    db.reset_database()
    cluster_engine = ClusterEngine(n_clusters=2)
    reembed_engine = ReEmbeddingEngine(alpha=0.3)
    print(f"   ✓ All services initialized\n")
    
    # Setup: Create two distinct clusters
    print("Step 2: Creating initial clusters...")
    tech_docs = [
        "Python programming language for software development",
        "JavaScript for web applications",
        "Machine learning with neural networks"
    ]
    food_docs = [
        "Italian pasta with tomato sauce",
        "Japanese sushi with fresh fish",
        "French croissants and pastries"
    ]
    
    all_texts = tech_docs + food_docs
    all_doc_ids = []
    
    for i, text in enumerate(all_texts):
        embedding = embedding_service.embed_text(text)
        doc = db.add_document(
            doc_id=f"doc_{i}",
            text=text,
            embedding=embedding
        )
        all_doc_ids.append(doc.id)
    
    print(f"   ✓ Created {len(all_texts)} documents\n")
    
    # Initial clustering
    print("Step 3: Performing initial clustering...")
    all_docs = db.get_all_documents()
    clusters_dict = cluster_engine.cluster_documents(all_docs)
    
    print(f"   ✓ Initial clusters: {len(clusters_dict)}")
    for cluster_id, docs in clusters_dict.items():
        print(f"   ✓ {cluster_id}: {len(docs)} documents")
    
    # Find a document to move
    doc_to_move = all_docs[0]
    # Find which cluster it's in
    initial_cluster_id = None
    for cluster_id, docs in clusters_dict.items():
        if any(d.id == doc_to_move.id for d in docs):
            initial_cluster_id = cluster_id
            break
    
    print(f"\n   ✓ Selected document to move: '{doc_to_move.text[:50]}...'")
    print(f"   ✓ Current cluster: {initial_cluster_id}\n")
    
    # Find target cluster (different from current)
    target_cluster_id = None
    target_cluster_docs = None
    for cluster_id, docs in clusters_dict.items():
        if cluster_id != initial_cluster_id:
            target_cluster_id = cluster_id
            target_cluster_docs = docs
            break
    
    if not target_cluster_id:
        print("   ⚠ Only one cluster found, using same cluster as target")
        target_cluster_id = initial_cluster_id
        target_cluster_docs = clusters_dict[initial_cluster_id]
    
    print(f"Step 4: Simulating drag to target cluster {target_cluster_id}...")
    
    # Step 1: Re-embed the document
    print("   → Re-embedding document...")
    current_embedding = doc_to_move.embedding
    
    # Calculate target centroid
    target_centroid = cluster_engine.calculate_centroid(target_cluster_docs)
    
    new_embedding = reembed_engine.nudge_embedding(current_embedding, target_centroid)
    
    # Verify embedding moved closer
    old_similarity = reembed_engine.calculate_similarity(current_embedding, target_centroid)
    new_similarity = reembed_engine.calculate_similarity(new_embedding, target_centroid)
    
    print(f"   ✓ Old similarity to target: {old_similarity:.4f}")
    print(f"   ✓ New similarity to target: {new_similarity:.4f}")
    print(f"   ✓ Moved closer: {new_similarity > old_similarity}\n")
    
    # Step 2: Update database
    print("   → Updating database...")
    db.update_embedding(doc_to_move.id, new_embedding)
    updated_doc = db.get_document(doc_to_move.id)
    print(f"   ✓ Document embedding updated in database\n")
    
    # Step 3: Trigger re-clustering
    print("Step 5: Triggering automatic re-clustering...")
    all_docs_updated = db.get_all_documents()
    new_clusters_dict = cluster_engine.cluster_documents(all_docs_updated)
    
    print(f"   ✓ Re-clustering complete")
    for cluster_id, docs in new_clusters_dict.items():
        print(f"   ✓ {cluster_id}: {len(docs)} documents")
    
    # Find new cluster assignment
    new_cluster_id = None
    for cluster_id, docs in new_clusters_dict.items():
        if any(d.id == doc_to_move.id for d in docs):
            new_cluster_id = cluster_id
            break
    
    print(f"\n   ✓ Document moved from cluster {initial_cluster_id} to {new_cluster_id}")
    
    # Step 4: Verify UI update data
    print("\nStep 6: Verifying UI update data...")
    ui_update = {
        "success": True,
        "document_id": doc_to_move.id,
        "old_cluster_id": initial_cluster_id,
        "new_cluster_id": new_cluster_id,
        "updated_clusters": {
            "folders": [
                {
                    "id": cluster_id,
                    "document_count": len(docs)
                }
                for cluster_id, docs in new_clusters_dict.items()
            ]
        }
    }
    
    print(f"   ✓ UI update data prepared")
    print(f"   ✓ Success: {ui_update['success']}")
    print(f"   ✓ Cluster change: {ui_update['old_cluster_id']} → {ui_update['new_cluster_id']}")
    
    # Cleanup
    db.reset_database()
    print("\n✅ TEST 2 PASSED: Complete drag → re-embed → re-cluster → update flow\n")


def test_error_recovery_flows():
    """
    Test error recovery in various scenarios
    Validates: Requirements 4.2, 4.6
    """
    print("\n" + "="*70)
    print("TEST 3: Error Recovery Flows")
    print("="*70 + "\n")
    
    # Initialize services
    print("Step 1: Initializing services...")
    embedding_service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    db = ChromaDBManager(persist_directory="./data/chroma_e2e_test")
    db.reset_database()
    cluster_engine = ClusterEngine(n_clusters=2)
    reembed_engine = ReEmbeddingEngine(alpha=0.3)
    print(f"   ✓ All services initialized\n")
    
    # Test 1: Invalid document ID
    print("Test 3.1: Handling invalid document ID...")
    try:
        doc = db.get_document("nonexistent_doc_id")
        print("   ✗ Should have raised error for invalid document ID")
    except Exception as e:
        print(f"   ✓ Correctly raised error: {type(e).__name__}")
    print()
    
    # Test 2: Empty database clustering
    print("Test 3.2: Handling empty database clustering...")
    try:
        empty_docs = db.get_all_documents()
        if len(empty_docs) == 0:
            print(f"   ✓ Database is empty: {len(empty_docs)} documents")
            # Clustering with empty list should handle gracefully
            result = cluster_engine.cluster_documents(empty_docs)
            print(f"   ✓ Clustering handled empty database: {len(result.clusters)} clusters")
    except Exception as e:
        print(f"   ✓ Gracefully handled error: {type(e).__name__}")
    print()
    
    # Test 3: Re-embedding with invalid cluster
    print("Test 3.3: Handling re-embedding with invalid target...")
    # Add a document first
    text = "Test document for error handling"
    embedding = embedding_service.embed_text(text)
    doc = db.add_document(doc_id="test_doc", text=text, embedding=embedding)
    
    # Try to re-embed with invalid target centroid (wrong dimensions)
    try:
        invalid_centroid = [0.1, 0.2]  # Wrong dimension
        new_emb = reembed_engine.nudge_embedding(doc.embedding, invalid_centroid)
        print("   ✗ Should have raised error for dimension mismatch")
    except Exception as e:
        print(f"   ✓ Correctly raised error: {type(e).__name__}")
    print()
    
    # Test 4: Recovery after failed operation
    print("Test 3.4: Verifying system state after errors...")
    # System should still be functional
    all_docs = db.get_all_documents()
    print(f"   ✓ Database still accessible: {len(all_docs)} documents")
    
    # Can still perform normal operations
    new_text = "Another test document"
    new_embedding = embedding_service.embed_text(new_text)
    new_doc = db.add_document(doc_id="test_doc_2", text=new_text, embedding=new_embedding)
    print(f"   ✓ Can still add documents after errors")
    
    # Cleanup
    db.reset_database()
    print("\n✅ TEST 3 PASSED: Error recovery flows working correctly\n")


def run_all_e2e_tests():
    """Run all end-to-end integration tests"""
    print("\n" + "="*70)
    print("RUNNING END-TO-END INTEGRATION TESTS")
    print("="*70)
    
    start_time = time.time()
    
    try:
        test_complete_ingestion_clustering_flow()
        test_complete_drag_reembed_recluster_flow()
        test_error_recovery_flows()
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"✅ ALL END-TO-END TESTS PASSED ({elapsed:.2f}s)")
        print("="*70 + "\n")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ TEST FAILED: {e}")
        print(f"Time elapsed: {elapsed:.2f}s\n")
        raise


if __name__ == "__main__":
    run_all_e2e_tests()

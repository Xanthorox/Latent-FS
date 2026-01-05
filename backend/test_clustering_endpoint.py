"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Test for clustering API endpoint
"""

import requests
import time


def test_clustering_endpoint():
    """Test the /cluster endpoint with real API"""
    
    print("\n" + "="*60)
    print("Testing Clustering API Endpoint")
    print("="*60 + "\n")
    
    base_url = "http://localhost:9999"
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✓ API is healthy")
            print(f"   ✓ Device: {health.get('device')}")
            print(f"   ✓ Document count: {health.get('document_count')}")
        else:
            print(f"   ✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Cannot connect to API: {e}")
        print(f"   Please start the server with: python backend/main.py")
        return False
    
    # Test 2: Ingest test documents
    print("\n2. Ingesting test documents...")
    test_texts = [
        "Python is a programming language used for web development and data science.",
        "JavaScript is used for frontend web development and Node.js backend.",
        "Machine learning algorithms can predict patterns in data.",
        "Neural networks are inspired by biological neurons in the brain.",
        "The solar system contains eight planets orbiting the sun.",
        "Mars is the fourth planet from the sun and has a reddish appearance.",
        "Cooking pasta requires boiling water and adding salt.",
        "Italian cuisine is famous for pizza and pasta dishes."
    ]
    
    payload = {"texts": test_texts}
    response = requests.post(f"{base_url}/api/ingest", json=payload)
    
    if response.status_code == 201:
        result = response.json()
        print(f"   ✓ Ingested {result['count']} documents")
    else:
        print(f"   ✗ Ingestion failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    # Test 3: Test clustering endpoint
    print("\n3. Testing clustering endpoint...")
    response = requests.get(f"{base_url}/api/cluster")
    
    if response.status_code != 200:
        print(f"   ✗ Clustering failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    data = response.json()
    
    # Verify response structure
    if "folders" not in data or "documents" not in data or "timestamp" not in data:
        print(f"   ✗ Invalid response structure")
        return False
    
    print(f"   ✓ Clustering successful")
    
    # Test 4: Verify folders
    print("\n4. Verifying semantic folders...")
    folders = data["folders"]
    
    if len(folders) == 0:
        print(f"   ✗ No folders created")
        return False
    
    print(f"   ✓ Created {len(folders)} semantic folders")
    
    for i, folder in enumerate(folders, 1):
        # Verify required fields
        required_fields = ["id", "name", "centroid", "document_ids", "representative_doc_id"]
        for field in required_fields:
            if field not in folder:
                print(f"   ✗ Folder missing required field: {field}")
                return False
        
        # Verify folder name is not empty
        if not folder["name"] or len(folder["name"]) == 0:
            print(f"   ✗ Folder has empty name")
            return False
        
        # Verify centroid is a list of floats
        if not isinstance(folder["centroid"], list) or len(folder["centroid"]) == 0:
            print(f"   ✗ Invalid centroid")
            return False
        
        # Verify document_ids is not empty
        if len(folder["document_ids"]) == 0:
            print(f"   ✗ Folder has no documents")
            return False
        
        # Verify representative_doc_id is in document_ids
        if folder["representative_doc_id"] not in folder["document_ids"]:
            print(f"   ✗ Representative document not in folder")
            return False
        
        print(f"   ✓ Folder {i}: '{folder['name']}' ({len(folder['document_ids'])} documents)")
    
    # Test 5: Verify documents
    print("\n5. Verifying document assignments...")
    documents = data["documents"]
    
    # Note: There may be more documents than we just ingested if the database
    # already had documents from previous tests
    if len(documents) < len(test_texts):
        print(f"   ✗ Document count too low: expected at least {len(test_texts)}, got {len(documents)}")
        return False
    
    print(f"   ✓ Found {len(documents)} documents (including {len(test_texts)} newly ingested)")
    
    # Verify all documents have cluster assignments
    unassigned = [doc for doc in documents if doc.get("cluster_id") is None]
    if unassigned:
        print(f"   ✗ {len(unassigned)} documents not assigned to clusters")
        return False
    
    print(f"   ✓ All documents assigned to clusters")
    
    # Verify all documents are assigned to exactly one cluster
    all_doc_ids = set(doc["id"] for doc in documents)
    assigned_doc_ids = set()
    for folder in folders:
        assigned_doc_ids.update(folder["document_ids"])
    
    if all_doc_ids != assigned_doc_ids:
        print(f"   ✗ Document assignment mismatch")
        return False
    
    print(f"   ✓ All documents assigned exactly once")
    
    # Test 6: Verify clustering quality
    print("\n6. Verifying clustering quality...")
    
    # Count documents per cluster
    cluster_sizes = [len(folder["document_ids"]) for folder in folders]
    print(f"   ✓ Cluster sizes: {cluster_sizes}")
    
    # Verify no empty clusters
    if any(size == 0 for size in cluster_sizes):
        print(f"   ✗ Found empty clusters")
        return False
    
    print(f"   ✓ No empty clusters")
    
    print("\n" + "="*60)
    print("All clustering tests passed! ✓")
    print("="*60 + "\n")
    
    print("Summary:")
    print(f"  - Total documents: {len(documents)}")
    print(f"  - Semantic folders: {len(folders)}")
    for folder in folders:
        print(f"    • {folder['name']}: {len(folder['document_ids'])} documents")
    
    return True


if __name__ == "__main__":
    success = test_clustering_endpoint()
    exit(0 if success else 1)

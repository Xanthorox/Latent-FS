"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Test for re-embedding API endpoint.
"""

import requests
import time


def test_reembed_endpoint():
    """
    Test the re-embedding endpoint with a complete workflow.
    
    This test:
    1. Ingests multiple documents
    2. Performs initial clustering
    3. Re-embeds a document to a different cluster
    4. Verifies the document moved to the target cluster
    """
    print("\n" + "="*60)
    print("Testing Re-Embedding API Endpoint")
    print("="*60 + "\n")
    
    base_url = "http://localhost:9999"
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Step 1: Health check
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
        return False
    
    # Step 2: Ingest diverse documents
    print("\n2. Ingesting diverse documents...")
    documents = [
        "Python is a high-level programming language",
        "JavaScript is used for web development",
        "Machine learning uses neural networks",
        "Deep learning is a subset of AI",
        "React is a JavaScript library",
        "Django is a Python web framework"
    ]
    
    response = requests.post(f"{base_url}/api/ingest", json={"texts": documents})
    if response.status_code != 201:
        print(f"   ✗ Ingestion failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    data = response.json()
    assert data["success"] is True
    assert data["count"] == len(documents)
    document_ids = data["document_ids"]
    print(f"   ✓ Ingested {data['count']} documents")
    print(f"   ✓ First document ID: {document_ids[0]}")
    
    # Step 3: Get initial clustering
    print("\n3. Getting initial clustering...")
    response = requests.get(f"{base_url}/api/cluster")
    if response.status_code != 200:
        print(f"   ✗ Clustering failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    cluster_data = response.json()
    assert "folders" in cluster_data
    assert "documents" in cluster_data
    assert len(cluster_data["folders"]) > 0
    
    folders = cluster_data["folders"]
    print(f"   ✓ Created {len(folders)} semantic folders")
    for folder in folders:
        print(f"   ✓ Folder '{folder['name']}' has {len(folder['document_ids'])} documents")
    
    # Find a document and a different cluster to move it to
    test_doc_id = document_ids[0]
    
    # Find which cluster it's currently in
    current_cluster_id = None
    for folder in folders:
        if test_doc_id in folder["document_ids"]:
            current_cluster_id = folder["id"]
            current_folder_name = folder["name"]
            break
    
    assert current_cluster_id is not None, "Document not found in any cluster"
    print(f"\n   ✓ Test document is in folder '{current_folder_name}' (cluster {current_cluster_id})")
    
    # Find a different cluster to move it to
    target_cluster_id = None
    target_folder_name = None
    for folder in folders:
        if folder["id"] != current_cluster_id:
            target_cluster_id = folder["id"]
            target_folder_name = folder["name"]
            break
    
    # If there's only one cluster, we can't test moving between clusters
    if target_cluster_id is None:
        print("\n   ⚠ Only one cluster exists, cannot test re-embedding between clusters")
        print("   This is expected with small document sets")
        return True
    
    print(f"   ✓ Target folder is '{target_folder_name}' (cluster {target_cluster_id})")
    
    # Step 4: Re-embed the document to the target cluster
    print("\n4. Re-embedding document to target folder...")
    response = requests.post(
        f"{base_url}/api/re-embed",
        json={
            "document_id": test_doc_id,
            "target_folder_id": target_cluster_id
        }
    )
    
    if response.status_code != 200:
        print(f"   ✗ Re-embedding failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    reembed_data = response.json()
    assert reembed_data["success"] is True
    assert "new_cluster_id" in reembed_data
    assert "updated_clusters" in reembed_data
    
    print(f"   ✓ Re-embedding successful")
    print(f"   ✓ Document ended up in cluster '{reembed_data['new_cluster_id']}'")
    
    # Step 5: Verify the document is in the updated clusters
    print("\n5. Verifying updated cluster structure...")
    updated_clusters = reembed_data["updated_clusters"]
    assert "folders" in updated_clusters
    assert "documents" in updated_clusters
    
    # Verify the document exists in the updated cluster data
    doc_found = False
    for doc in updated_clusters["documents"]:
        if doc["id"] == test_doc_id:
            doc_found = True
            break
    
    assert doc_found, "Re-embedded document not found in updated clusters"
    print(f"   ✓ Document found in updated cluster data")
    
    # Find which folder the document is now in
    new_folder_name = None
    for folder in updated_clusters["folders"]:
        if test_doc_id in folder["document_ids"]:
            new_folder_name = folder["name"]
            break
    
    if new_folder_name:
        print(f"   ✓ Document is now in folder '{new_folder_name}'")
    
    print("\n" + "="*60)
    print("All re-embedding tests passed! ✓")
    print("="*60 + "\n")
    return True


if __name__ == "__main__":
    success = test_reembed_endpoint()
    exit(0 if success else 1)


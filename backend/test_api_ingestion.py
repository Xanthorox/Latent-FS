"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Test script for API ingestion endpoint
"""

import sys
from pathlib import Path
import requests
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ingestion_endpoint():
    """Test the /api/ingest endpoint"""
    
    print("\n" + "="*60)
    print("Testing API Ingestion Endpoint")
    print("="*60 + "\n")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✓ API is healthy")
            print(f"   ✓ Device: {health.get('device')}")
            print(f"   ✓ Model: {health.get('model')}")
            print(f"   ✓ Document count: {health.get('document_count')}")
        else:
            print(f"   ✗ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Cannot connect to API: {e}")
        print("   Make sure the server is running: python backend/main.py")
        return
    
    # Test 2: Single document ingestion
    print("\n2. Testing single document ingestion...")
    payload = {
        "texts": ["Machine learning is a subset of artificial intelligence."]
    }
    
    response = requests.post(f"{base_url}/api/ingest", json=payload)
    if response.status_code == 201:
        result = response.json()
        print(f"   ✓ Ingestion successful")
        print(f"   ✓ Document ID: {result['document_ids'][0]}")
        print(f"   ✓ Count: {result['count']}")
        print(f"   ✓ Message: {result['message']}")
    else:
        print(f"   ✗ Ingestion failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 3: Batch document ingestion
    print("\n3. Testing batch document ingestion...")
    payload = {
        "texts": [
            "Python is a popular programming language.",
            "Deep learning uses neural networks.",
            "Natural language processing analyzes text.",
            "Computer vision enables machines to see.",
            "Reinforcement learning trains agents through rewards."
        ]
    }
    
    response = requests.post(f"{base_url}/api/ingest", json=payload)
    if response.status_code == 201:
        result = response.json()
        print(f"   ✓ Batch ingestion successful")
        print(f"   ✓ Documents ingested: {result['count']}")
        print(f"   ✓ First document ID: {result['document_ids'][0]}")
    else:
        print(f"   ✗ Batch ingestion failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 4: Retrieve all documents
    print("\n4. Testing document retrieval...")
    response = requests.get(f"{base_url}/api/documents")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Retrieved {result['count']} documents")
        if result['documents']:
            first_doc = result['documents'][0]
            print(f"   ✓ First document text: {first_doc['text'][:50]}...")
            print(f"   ✓ Embedding dimensions: {len(first_doc['embedding'])}")
    else:
        print(f"   ✗ Retrieval failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 5: Error handling - empty text
    print("\n5. Testing error handling (empty text)...")
    payload = {
        "texts": [""]
    }
    
    response = requests.post(f"{base_url}/api/ingest", json=payload)
    if response.status_code == 400:
        print(f"   ✓ Correctly rejected empty text")
        print(f"   ✓ Error message: {response.json()['detail']}")
    else:
        print(f"   ✗ Should have rejected empty text")
        return
    
    # Test 6: Error handling - whitespace only
    print("\n6. Testing error handling (whitespace only)...")
    payload = {
        "texts": ["   \n\t  "]
    }
    
    response = requests.post(f"{base_url}/api/ingest", json=payload)
    if response.status_code == 400:
        print(f"   ✓ Correctly rejected whitespace-only text")
    else:
        print(f"   ✗ Should have rejected whitespace-only text")
        return
    
    print("\n" + "="*60)
    print("All API tests passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\nNote: Make sure the API server is running before running this test.")
    print("Start the server with: python backend/main.py\n")
    
    input("Press Enter to start tests...")
    test_ingestion_endpoint()

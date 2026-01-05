"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Manual verification script for error handling
Run the server first with: python backend/main.py
Then run this script to verify error handling works correctly
"""

import requests
import json

BASE_URL = "http://localhost:9999"


def test_validation_error():
    """Test that validation errors return 422 with proper structure"""
    print("\n1. Testing validation error handling...")
    
    # Send invalid data (texts should be a list, not a string)
    response = requests.post(
        f"{BASE_URL}/api/ingest",
        json={"texts": "not a list"}
    )
    
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 422, "Should return 422 for validation error"
    assert "error" in data, "Response should have 'error' field"
    assert data["error"]["type"] == "validation_error", "Error type should be 'validation_error'"
    assert "details" in data["error"], "Should include validation details"
    print("   ✓ Validation error handling works correctly")


def test_missing_field():
    """Test that missing required fields return 422"""
    print("\n2. Testing missing field error...")
    
    response = requests.post(
        f"{BASE_URL}/api/ingest",
        json={}  # Missing 'texts' field
    )
    
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 422, "Should return 422 for missing field"
    assert "error" in data, "Response should have 'error' field"
    print("   ✓ Missing field error handling works correctly")


def test_not_found_error():
    """Test that 404 errors are handled properly"""
    print("\n3. Testing 404 error handling...")
    
    response = requests.post(
        f"{BASE_URL}/api/re-embed",
        json={
            "document_id": "non-existent-id-12345",
            "target_folder_id": "cluster_0"
        }
    )
    
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 404, "Should return 404 for non-existent document"
    assert "error" in data, "Response should have 'error' field"
    assert data["error"]["status_code"] == 404, "Error status_code should be 404"
    print("   ✓ 404 error handling works correctly")


def test_error_response_structure():
    """Test that all error responses have consistent structure"""
    print("\n4. Testing error response structure...")
    
    response = requests.post(
        f"{BASE_URL}/api/ingest",
        json={"texts": 123}  # Invalid type
    )
    
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    assert "error" in data, "Response should have 'error' field"
    error = data["error"]
    assert "type" in error, "Error should have 'type' field"
    assert "status_code" in error, "Error should have 'status_code' field"
    assert "message" in error, "Error should have 'message' field"
    assert "path" in error, "Error should have 'path' field"
    assert error["path"] == "/api/ingest", "Path should match request path"
    print("   ✓ Error response structure is consistent")


def test_invalid_endpoint():
    """Test that invalid endpoints return 404"""
    print("\n5. Testing invalid endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/invalid-endpoint-xyz")
    
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 404, "Should return 404 for invalid endpoint"
    assert "error" in data, "Response should have 'error' field"
    print("   ✓ Invalid endpoint error handling works correctly")


def test_health_endpoint():
    """Test that health endpoint works"""
    print("\n6. Testing health endpoint...")
    
    response = requests.get(f"{BASE_URL}/")
    
    print(f"   Status Code: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200, "Health endpoint should return 200"
    assert data["status"] == "healthy", "Status should be 'healthy'"
    print("   ✓ Health endpoint works correctly")


def main():
    """Run all error handling tests"""
    print("="*60)
    print("Error Handling Verification")
    print("="*60)
    print("\nMake sure the server is running on http://localhost:9999")
    print("Start it with: python backend/main.py")
    print()
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 9999")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server connection timed out")
        return False
    
    try:
        test_health_endpoint()
        test_validation_error()
        test_missing_field()
        test_not_found_error()
        test_error_response_structure()
        test_invalid_endpoint()
        
        print("\n" + "="*60)
        print("✓ All error handling tests passed!")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

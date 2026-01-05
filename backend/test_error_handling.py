"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Test error handling and validation
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def test_validation_error_returns_422(client):
    """Test that invalid request data returns 422 with validation details"""
    # Send invalid data (texts should be a list, not a string)
    response = client.post(
        "/api/ingest",
        json={"texts": "not a list"}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["type"] == "validation_error"
    assert data["error"]["status_code"] == 422
    assert "details" in data["error"]


def test_validation_error_missing_field(client):
    """Test that missing required field returns 422"""
    response = client.post(
        "/api/ingest",
        json={}  # Missing 'texts' field
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["type"] == "validation_error"


def test_not_found_error_returns_404(client):
    """Test that requesting non-existent document returns 404"""
    response = client.post(
        "/api/re-embed",
        json={
            "document_id": "non-existent-id",
            "target_folder_id": "cluster_0"
        }
    )
    
    # Should return 404 when document not found
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["status_code"] == 404


def test_error_response_structure(client):
    """Test that error responses have consistent structure"""
    response = client.post(
        "/api/ingest",
        json={"texts": 123}  # Invalid type
    )
    
    assert response.status_code == 422
    data = response.json()
    
    # Verify error structure
    assert "error" in data
    error = data["error"]
    assert "type" in error
    assert "status_code" in error
    assert "message" in error
    assert "path" in error
    assert error["path"] == "/api/ingest"


def test_health_endpoint_success(client):
    """Test that health endpoint returns success"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "device" in data


def test_invalid_endpoint_returns_404(client):
    """Test that invalid endpoint returns 404"""
    response = client.get("/api/invalid-endpoint")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["status_code"] == 404


def test_empty_texts_list(client):
    """Test that empty texts list is handled properly"""
    response = client.post(
        "/api/ingest",
        json={"texts": []}
    )
    
    # Should reject empty list with validation error
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["type"] == "validation_error"


def test_cluster_endpoint_with_no_documents(client):
    """Test clustering endpoint when database might be empty"""
    # This test depends on database state, but should handle gracefully
    response = client.get("/api/cluster")
    
    # Should either return clusters or 404 if no documents
    assert response.status_code in [200, 404]
    
    if response.status_code == 404:
        data = response.json()
        assert "error" in data
        assert data["error"]["status_code"] == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

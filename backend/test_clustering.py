"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Tests for the clustering service.
"""

import pytest
import numpy as np
from datetime import datetime

from backend.services.clustering import ClusterEngine
from backend.models.schemas import Document


def test_cluster_engine_initialization():
    """Test that ClusterEngine initializes correctly."""
    engine = ClusterEngine(n_clusters=5)
    assert engine.n_clusters == 5


def test_cluster_documents_basic():
    """Test basic clustering functionality with simple documents."""
    # Create test documents with known embeddings
    docs = [
        Document(
            id=f"doc_{i}",
            text=f"Document {i}",
            embedding=[float(i), float(i * 2), float(i * 3)],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for i in range(10)
    ]
    
    engine = ClusterEngine(n_clusters=3)
    clusters = engine.cluster_documents(docs)
    
    # Verify all documents are assigned to clusters
    total_docs = sum(len(cluster_docs) for cluster_docs in clusters.values())
    assert total_docs == len(docs)
    
    # Verify we have at most 3 clusters
    assert len(clusters) <= 3


def test_cluster_documents_adjusts_for_small_dataset():
    """Test that clustering adjusts cluster count for small datasets."""
    # Create only 2 documents
    docs = [
        Document(
            id="doc_1",
            text="Document 1",
            embedding=[1.0, 2.0, 3.0],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Document(
            id="doc_2",
            text="Document 2",
            embedding=[4.0, 5.0, 6.0],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    engine = ClusterEngine(n_clusters=5)
    clusters = engine.cluster_documents(docs)
    
    # Should have at most 2 clusters (adjusted from 5)
    assert len(clusters) <= 2
    
    # All documents should be assigned
    total_docs = sum(len(cluster_docs) for cluster_docs in clusters.values())
    assert total_docs == 2


def test_cluster_documents_empty_list():
    """Test clustering with empty document list."""
    engine = ClusterEngine(n_clusters=3)
    clusters = engine.cluster_documents([])
    
    assert clusters == {}


def test_calculate_centroid():
    """Test centroid calculation."""
    docs = [
        Document(
            id="doc_1",
            text="Document 1",
            embedding=[1.0, 2.0, 3.0],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Document(
            id="doc_2",
            text="Document 2",
            embedding=[3.0, 4.0, 5.0],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    engine = ClusterEngine()
    centroid = engine.calculate_centroid(docs)
    
    # Centroid should be the mean: [(1+3)/2, (2+4)/2, (3+5)/2] = [2.0, 3.0, 4.0]
    expected = [2.0, 3.0, 4.0]
    assert len(centroid) == len(expected)
    for i in range(len(centroid)):
        assert abs(centroid[i] - expected[i]) < 0.001


def test_calculate_centroid_empty_cluster():
    """Test that calculating centroid for empty cluster raises error."""
    engine = ClusterEngine()
    
    with pytest.raises(ValueError, match="Cannot calculate centroid for empty cluster"):
        engine.calculate_centroid([])


def test_find_representative_doc():
    """Test finding representative document closest to centroid."""
    docs = [
        Document(
            id="doc_1",
            text="Document 1",
            embedding=[1.0, 1.0, 1.0],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Document(
            id="doc_2",
            text="Document 2",
            embedding=[2.0, 2.0, 2.0],  # Closest to centroid [2.0, 2.0, 2.0]
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Document(
            id="doc_3",
            text="Document 3",
            embedding=[5.0, 5.0, 5.0],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    centroid = [2.0, 2.0, 2.0]
    
    engine = ClusterEngine()
    representative = engine.find_representative_doc(docs, centroid)
    
    # doc_2 should be the representative as it's closest to the centroid
    assert representative.id == "doc_2"


def test_find_representative_doc_empty_cluster():
    """Test that finding representative for empty cluster raises error."""
    engine = ClusterEngine()
    centroid = [1.0, 2.0, 3.0]
    
    with pytest.raises(ValueError, match="Cannot find representative document for empty cluster"):
        engine.find_representative_doc([], centroid)


def test_cluster_documents_with_invalid_embedding():
    """Test that clustering validates embeddings properly."""
    # Note: Pydantic validates empty embeddings at model creation,
    # so we test with a document that has a valid embedding initially
    # but we'll verify the validation logic exists in the clustering code
    
    # This test verifies the clustering engine has validation logic
    # even though Pydantic catches it first
    engine = ClusterEngine()
    
    # Create a document with valid embedding
    doc = Document(
        id="doc_1",
        text="Document 1",
        embedding=[1.0, 2.0, 3.0],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Manually set embedding to empty to bypass Pydantic (for testing validation)
    doc.embedding = []
    
    with pytest.raises(ValueError, match="has invalid or empty embedding"):
        engine.cluster_documents([doc])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

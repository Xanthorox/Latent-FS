"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


class Document(BaseModel):
    """Represents a document with its embedding and metadata."""
    id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., min_length=1, description="Document text content")
    embedding: List[float] = Field(..., description="Vector embedding of the document")
    cluster_id: Optional[str] = Field(None, description="ID of the cluster this document belongs to")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    @validator('text')
    def text_not_empty(cls, v):
        """Validate that text is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Document text cannot be empty or whitespace only')
        return v

    @validator('embedding')
    def embedding_not_empty(cls, v):
        """Validate that embedding is not empty."""
        if not v or len(v) == 0:
            raise ValueError('Embedding vector cannot be empty')
        return v


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    texts: List[str] = Field(..., min_items=1, description="List of document texts to ingest")

    @validator('texts')
    def texts_not_empty(cls, v):
        """Validate that all texts are non-empty."""
        if not v:
            raise ValueError('Must provide at least one document to ingest')
        for i, text in enumerate(v):
            if not text or not text.strip():
                raise ValueError(f'Document at index {i} cannot be empty or whitespace only')
        return v


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    success: bool = Field(..., description="Whether ingestion was successful")
    document_ids: List[str] = Field(..., description="IDs of ingested documents")
    count: int = Field(..., description="Number of documents ingested")
    message: str = Field(..., description="Status message")


class Cluster(BaseModel):
    """Represents a semantic cluster (folder)."""
    id: str = Field(..., description="Unique cluster identifier")
    name: str = Field(..., description="Semantic name for the cluster")
    centroid: List[float] = Field(..., description="Centroid vector of the cluster")
    document_ids: List[str] = Field(..., description="IDs of documents in this cluster")
    representative_doc_id: str = Field(..., description="ID of the most representative document")


class ClusterResponse(BaseModel):
    """Response model for clustering operations."""
    folders: List[Cluster] = Field(..., description="List of semantic folders")
    documents: List[Document] = Field(..., description="List of all documents")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ReEmbedRequest(BaseModel):
    """Request model for re-embedding a document."""
    document_id: str = Field(..., description="ID of document to re-embed")
    target_folder_id: str = Field(..., description="ID of target folder/cluster")

    @validator('document_id', 'target_folder_id')
    def ids_not_empty(cls, v):
        """Validate that IDs are not empty."""
        if not v or not v.strip():
            raise ValueError('ID cannot be empty')
        return v


class ReEmbedResponse(BaseModel):
    """Response model for re-embedding operations."""
    success: bool = Field(..., description="Whether re-embedding was successful")
    new_cluster_id: str = Field(..., description="New cluster ID after re-embedding")
    updated_clusters: ClusterResponse = Field(..., description="Updated cluster data")


class DocumentResponse(BaseModel):
    """Response model for document retrieval."""
    documents: List[Document] = Field(..., description="List of documents")
    count: int = Field(..., description="Number of documents")

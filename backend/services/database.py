"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json
from pathlib import Path

from backend.models.schemas import Document

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """
    Manager for ChromaDB vector database with persistent storage.
    
    This class handles all interactions with ChromaDB, including document storage,
    retrieval, and embedding updates. It uses persistent storage to maintain data
    across application restarts.
    """
    
    def __init__(self, persist_directory: str = "./data/chroma"):
        """
        Initialize ChromaDB manager with persistent storage.
        
        Args:
            persist_directory: Path to the directory for persistent storage
        
        Raises:
            RuntimeError: If ChromaDB initialization fails
            PermissionError: If persist_directory is not writable
        """
        self.persist_directory = persist_directory
        self.collection_name = "latent_fs_documents"
        
        # Ensure persist directory exists and is writable
        try:
            persist_path = Path(persist_directory)
            persist_path.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = persist_path / ".write_test"
            test_file.touch()
            test_file.unlink()
            
        except PermissionError as e:
            logger.error(f"Persist directory '{persist_directory}' is not writable")
            raise PermissionError(
                f"Cannot write to persist directory '{persist_directory}'. "
                "Please check directory permissions."
            ) from e
        except Exception as e:
            logger.error(f"Failed to create persist directory: {e}")
            raise RuntimeError(f"Failed to initialize persist directory: {e}") from e
        
        # Initialize ChromaDB client
        try:
            logger.info(f"Initializing ChromaDB with persistent storage at '{persist_directory}'")
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self._initialize_collection()
            logger.info(f"ChromaDB initialized successfully. Collection: '{self.collection_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError(
                f"ChromaDB initialization failed: {e}. "
                "Check if the database is corrupted or if another process is using it."
            ) from e
    
    def _initialize_collection(self):
        """
        Initialize or retrieve the document collection.
        
        Returns:
            ChromaDB collection object
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection '{self.collection_name}' with {collection.count()} documents")
            return collection
        except Exception:
            # Collection doesn't exist, create it
            logger.info(f"Creating new collection '{self.collection_name}'")
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Latent-FS document embeddings"}
            )
    
    def add_document(
        self,
        doc_id: str,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Store a document with its embedding in the database.
        
        Args:
            doc_id: Unique identifier for the document
            text: The document text content
            embedding: The embedding vector for the document
            metadata: Optional additional metadata
        
        Returns:
            Document object representing the stored document
        
        Raises:
            ValueError: If doc_id, text, or embedding is invalid
            RuntimeError: If database operation fails
        """
        if not doc_id or not doc_id.strip():
            raise ValueError("Document ID cannot be empty")
        
        if not text or not text.strip():
            raise ValueError("Document text cannot be empty")
        
        if not embedding or len(embedding) == 0:
            raise ValueError("Embedding cannot be empty")
        
        try:
            now = datetime.utcnow()
            
            # Prepare metadata (ChromaDB only accepts str, int, float, bool)
            doc_metadata = metadata or {}
            doc_metadata.update({
                "text": text,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            })
            # Only add cluster_id if it's not None
            # ChromaDB doesn't accept None values
            
            # Add to ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[doc_metadata]
            )
            
            logger.info(f"Added document '{doc_id}' to database")
            
            # Return Document object
            return Document(
                id=doc_id,
                text=text,
                embedding=embedding,
                cluster_id=None,
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            
        except Exception as e:
            logger.error(f"Failed to add document '{doc_id}': {e}")
            raise RuntimeError(f"Failed to add document to database: {e}") from e
    
    def update_embedding(self, doc_id: str, new_embedding: List[float]) -> None:
        """
        Update an existing document's embedding.
        
        Args:
            doc_id: ID of the document to update
            new_embedding: The new embedding vector
        
        Raises:
            ValueError: If doc_id or new_embedding is invalid
            RuntimeError: If document doesn't exist or update fails
        """
        if not doc_id or not doc_id.strip():
            raise ValueError("Document ID cannot be empty")
        
        if not new_embedding or len(new_embedding) == 0:
            raise ValueError("Embedding cannot be empty")
        
        try:
            # Check if document exists
            result = self.collection.get(ids=[doc_id])
            if not result['ids']:
                raise RuntimeError(f"Document '{doc_id}' not found in database")
            
            # Get existing metadata and update timestamp
            existing_metadata = result['metadatas'][0]
            existing_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            # Update the embedding
            self.collection.update(
                ids=[doc_id],
                embeddings=[new_embedding],
                metadatas=[existing_metadata]
            )
            
            logger.info(f"Updated embedding for document '{doc_id}'")
            
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to update embedding for document '{doc_id}': {e}")
            raise RuntimeError(f"Failed to update document embedding: {e}") from e
    
    def get_all_documents(self) -> List[Document]:
        """
        Retrieve all documents from the database.
        
        Returns:
            List of Document objects
        
        Raises:
            RuntimeError: If database query fails
        """
        try:
            # Get all documents from collection
            result = self.collection.get(
                include=["embeddings", "metadatas"]
            )
            
            if not result['ids']:
                logger.info("No documents found in database")
                return []
            
            # Convert to Document objects
            documents = []
            for i, doc_id in enumerate(result['ids']):
                metadata = result['metadatas'][i]
                
                doc = Document(
                    id=doc_id,
                    text=metadata.get('text', ''),
                    embedding=result['embeddings'][i],
                    cluster_id=metadata.get('cluster_id'),
                    metadata={k: v for k, v in metadata.items() 
                             if k not in ['text', 'created_at', 'updated_at', 'cluster_id']},
                    created_at=datetime.fromisoformat(metadata.get('created_at', datetime.utcnow().isoformat())),
                    updated_at=datetime.fromisoformat(metadata.get('updated_at', datetime.utcnow().isoformat()))
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents from database")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            raise RuntimeError(f"Failed to retrieve documents from database: {e}") from e
    
    def get_document(self, doc_id: str) -> Document:
        """
        Retrieve a single document by ID.
        
        Args:
            doc_id: ID of the document to retrieve
        
        Returns:
            Document object
        
        Raises:
            ValueError: If doc_id is invalid
            RuntimeError: If document doesn't exist or query fails
        """
        if not doc_id or not doc_id.strip():
            raise ValueError("Document ID cannot be empty")
        
        try:
            result = self.collection.get(
                ids=[doc_id],
                include=["embeddings", "metadatas"]
            )
            
            if not result['ids']:
                raise RuntimeError(f"Document '{doc_id}' not found in database")
            
            metadata = result['metadatas'][0]
            
            doc = Document(
                id=doc_id,
                text=metadata.get('text', ''),
                embedding=result['embeddings'][0],
                cluster_id=metadata.get('cluster_id'),
                metadata={k: v for k, v in metadata.items() 
                         if k not in ['text', 'created_at', 'updated_at', 'cluster_id']},
                created_at=datetime.fromisoformat(metadata.get('created_at', datetime.utcnow().isoformat())),
                updated_at=datetime.fromisoformat(metadata.get('updated_at', datetime.utcnow().isoformat()))
            )
            
            logger.info(f"Retrieved document '{doc_id}' from database")
            return doc
            
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve document '{doc_id}': {e}")
            raise RuntimeError(f"Failed to retrieve document from database: {e}") from e
    
    def update_cluster_assignment(self, doc_id: str, cluster_id: str) -> None:
        """
        Update a document's cluster assignment.
        
        Args:
            doc_id: ID of the document to update
            cluster_id: ID of the cluster to assign
        
        Raises:
            ValueError: If doc_id or cluster_id is invalid
            RuntimeError: If document doesn't exist or update fails
        """
        if not doc_id or not doc_id.strip():
            raise ValueError("Document ID cannot be empty")
        
        if not cluster_id or not cluster_id.strip():
            raise ValueError("Cluster ID cannot be empty")
        
        try:
            # Check if document exists
            result = self.collection.get(ids=[doc_id])
            if not result['ids']:
                raise RuntimeError(f"Document '{doc_id}' not found in database")
            
            # Get existing metadata and update cluster assignment
            existing_metadata = result['metadatas'][0]
            existing_metadata['cluster_id'] = cluster_id
            existing_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            # Update metadata
            self.collection.update(
                ids=[doc_id],
                metadatas=[existing_metadata]
            )
            
            logger.info(f"Updated cluster assignment for document '{doc_id}' to cluster '{cluster_id}'")
            
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to update cluster assignment for document '{doc_id}': {e}")
            raise RuntimeError(f"Failed to update cluster assignment: {e}") from e
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the database.
        
        Args:
            doc_id: ID of the document to delete
        
        Raises:
            ValueError: If doc_id is invalid
            RuntimeError: If deletion fails
        """
        if not doc_id or not doc_id.strip():
            raise ValueError("Document ID cannot be empty")
        
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document '{doc_id}' from database")
            
        except Exception as e:
            logger.error(f"Failed to delete document '{doc_id}': {e}")
            raise RuntimeError(f"Failed to delete document from database: {e}") from e
    
    def count_documents(self) -> int:
        """
        Get the total number of documents in the database.
        
        Returns:
            Number of documents
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
            return 0
    
    def reset_database(self) -> None:
        """
        Delete all documents and reset the database.
        
        Warning: This operation cannot be undone!
        
        Raises:
            RuntimeError: If reset fails
        """
        try:
            logger.warning("Resetting database - all documents will be deleted")
            self.client.delete_collection(name=self.collection_name)
            self.collection = self._initialize_collection()
            logger.info("Database reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            raise RuntimeError(f"Failed to reset database: {e}") from e

"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple
import logging

from backend.models.schemas import Document

logger = logging.getLogger(__name__)


class ClusterEngine:
    """
    Engine for performing semantic clustering on document embeddings.
    
    This class uses K-Means clustering to group documents by semantic similarity
    in the embedding space. It dynamically adjusts cluster count for small document
    sets and provides methods for calculating centroids and finding representative
    documents.
    """
    
    def __init__(self, n_clusters: int = 5):
        """
        Initialize the cluster engine with target number of clusters.
        
        Args:
            n_clusters: Target number of clusters (will be adjusted for small datasets)
        """
        self.n_clusters = n_clusters
        logger.info(f"Initialized ClusterEngine with target {n_clusters} clusters")
    
    def cluster_documents(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """
        Perform K-Means clustering on document embeddings.
        
        This method groups documents into semantic clusters based on their
        embedding vectors. It automatically adjusts the number of clusters
        if there are fewer documents than the target cluster count.
        
        Args:
            documents: List of Document objects with embeddings
        
        Returns:
            Dictionary mapping cluster IDs to lists of documents in each cluster
        
        Raises:
            ValueError: If documents list is empty or embeddings are invalid
        """
        if not documents:
            logger.warning("No documents provided for clustering")
            return {}
        
        # Validate that all documents have embeddings
        for doc in documents:
            if not doc.embedding or len(doc.embedding) == 0:
                raise ValueError(f"Document '{doc.id}' has invalid or empty embedding")
        
        # Extract embeddings as numpy array
        embeddings = np.array([doc.embedding for doc in documents])
        
        # Adjust cluster count for small document sets
        actual_n_clusters = min(self.n_clusters, len(documents))
        
        if actual_n_clusters < self.n_clusters:
            logger.info(
                f"Adjusting cluster count from {self.n_clusters} to {actual_n_clusters} "
                f"due to small document set ({len(documents)} documents)"
            )
        
        # Perform K-Means clustering
        logger.info(f"Clustering {len(documents)} documents into {actual_n_clusters} clusters")
        
        try:
            kmeans = KMeans(
                n_clusters=actual_n_clusters,
                random_state=42,
                n_init=10,
                max_iter=300
            )
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Group documents by cluster
            clusters: Dict[str, List[Document]] = {}
            for doc, label in zip(documents, cluster_labels):
                cluster_id = f"cluster_{label}"
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(doc)
            
            logger.info(
                f"Clustering complete. Created {len(clusters)} clusters with sizes: "
                f"{[len(docs) for docs in clusters.values()]}"
            )
            
            return clusters
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            raise RuntimeError(f"Failed to perform clustering: {e}") from e
    
    def calculate_centroid(self, cluster_docs: List[Document]) -> List[float]:
        """
        Calculate the centroid vector for a cluster of documents.
        
        The centroid is the mathematical mean of all embedding vectors in the cluster.
        
        Args:
            cluster_docs: List of documents in the cluster
        
        Returns:
            Centroid vector as a list of floats
        
        Raises:
            ValueError: If cluster is empty or embeddings are invalid
        """
        if not cluster_docs:
            raise ValueError("Cannot calculate centroid for empty cluster")
        
        # Validate embeddings
        for doc in cluster_docs:
            if not doc.embedding or len(doc.embedding) == 0:
                raise ValueError(f"Document '{doc.id}' has invalid or empty embedding")
        
        # Extract embeddings and calculate mean
        embeddings = np.array([doc.embedding for doc in cluster_docs])
        centroid = np.mean(embeddings, axis=0)
        
        logger.debug(f"Calculated centroid for cluster of {len(cluster_docs)} documents")
        
        return centroid.tolist()
    
    def find_representative_doc(
        self,
        cluster_docs: List[Document],
        centroid: List[float]
    ) -> Document:
        """
        Find the document closest to the cluster centroid.
        
        This document serves as the most representative example of the cluster's
        semantic content. Distance is measured using cosine similarity.
        
        Args:
            cluster_docs: List of documents in the cluster
            centroid: Centroid vector of the cluster
        
        Returns:
            The document closest to the centroid
        
        Raises:
            ValueError: If cluster is empty or centroid is invalid
        """
        if not cluster_docs:
            raise ValueError("Cannot find representative document for empty cluster")
        
        if not centroid or len(centroid) == 0:
            raise ValueError("Centroid vector cannot be empty")
        
        # Convert centroid to numpy array
        centroid_array = np.array(centroid)
        
        # Calculate cosine similarity for each document
        min_distance = float('inf')
        representative_doc = None
        
        for doc in cluster_docs:
            if not doc.embedding or len(doc.embedding) == 0:
                logger.warning(f"Skipping document '{doc.id}' with invalid embedding")
                continue
            
            doc_embedding = np.array(doc.embedding)
            
            # Calculate Euclidean distance (faster than cosine for finding closest)
            distance = np.linalg.norm(doc_embedding - centroid_array)
            
            if distance < min_distance:
                min_distance = distance
                representative_doc = doc
        
        if representative_doc is None:
            raise ValueError("No valid documents found in cluster")
        
        logger.debug(
            f"Found representative document '{representative_doc.id}' "
            f"with distance {min_distance:.4f} from centroid"
        )
        
        return representative_doc

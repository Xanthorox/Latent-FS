"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
import uuid
import time
from threading import Lock

from backend.models.schemas import (
    IngestRequest,
    IngestResponse,
    Document,
    DocumentResponse,
    Cluster,
    ClusterResponse,
    ReEmbedRequest,
    ReEmbedResponse
)
from backend.services.embedding import EmbeddingService
from backend.services.database import ChromaDBManager
from backend.services.clustering import ClusterEngine
from backend.services.naming import FolderNamingService
from backend.services.reembedding import ReEmbeddingEngine
from backend.config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services (these will be singletons)
embedding_service = None
db_manager = None
cluster_engine = None
naming_service = None
reembedding_engine = None

# Debouncing state
last_reclustering_time = 0.0
reclustering_lock = Lock()


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton."""
    global embedding_service
    if embedding_service is None:
        logger.info("Initializing embedding service")
        embedding_service = EmbeddingService(
            model_name=settings.EMBEDDING_MODEL,
            device=settings.DEVICE
        )
    return embedding_service


def get_db_manager() -> ChromaDBManager:
    """Get or create the database manager singleton."""
    global db_manager
    if db_manager is None:
        logger.info("Initializing database manager")
        db_manager = ChromaDBManager(persist_directory=settings.CHROMA_PERSIST_DIR)
    return db_manager


def get_cluster_engine() -> ClusterEngine:
    """Get or create the cluster engine singleton."""
    global cluster_engine
    if cluster_engine is None:
        logger.info("Initializing cluster engine")
        cluster_engine = ClusterEngine(n_clusters=settings.N_CLUSTERS)
    return cluster_engine


def get_naming_service() -> FolderNamingService:
    """Get or create the folder naming service singleton."""
    global naming_service
    if naming_service is None:
        logger.info("Initializing folder naming service")
        naming_service = FolderNamingService(llm_model_path=settings.LLM_MODEL_PATH)
    return naming_service


def get_reembedding_engine() -> ReEmbeddingEngine:
    """Get or create the re-embedding engine singleton."""
    global reembedding_engine
    if reembedding_engine is None:
        logger.info("Initializing re-embedding engine")
        reembedding_engine = ReEmbeddingEngine(alpha=settings.RE_EMBED_ALPHA)
    return reembedding_engine


def should_perform_reclustering() -> bool:
    """
    Check if enough time has passed since the last re-clustering operation.
    
    This implements debouncing to prevent excessive re-clustering from rapid
    embedding modifications. Uses a thread-safe lock to handle concurrent requests.
    
    Returns:
        True if re-clustering should be performed, False if within debounce window
    """
    global last_reclustering_time
    
    with reclustering_lock:
        current_time = time.time()
        time_since_last = current_time - last_reclustering_time
        
        if time_since_last >= settings.DEBOUNCE_WINDOW_SECONDS:
            # Update the last re-clustering time
            last_reclustering_time = current_time
            logger.info(
                f"Re-clustering allowed (time since last: {time_since_last:.2f}s)"
            )
            return True
        else:
            logger.info(
                f"Re-clustering skipped due to debouncing "
                f"(time since last: {time_since_last:.2f}s, "
                f"window: {settings.DEBOUNCE_WINDOW_SECONDS}s)"
            )
            return False


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_documents(request: IngestRequest):
    """
    Ingest documents into the system.
    
    This endpoint accepts a list of text documents, generates embeddings for them
    using GPU-accelerated models, and stores them in the vector database.
    
    Args:
        request: IngestRequest containing list of document texts
    
    Returns:
        IngestResponse with success status, document IDs, and count
    
    Raises:
        HTTPException 400: If validation fails or texts are invalid
        HTTPException 500: If embedding generation or database storage fails
    """
    try:
        logger.info(f"Received ingestion request for {len(request.texts)} documents")
        
        # Get services
        embedder = get_embedding_service()
        db = get_db_manager()
        
        # Generate embeddings (batch processing for efficiency)
        try:
            embeddings = embedder.embed_batch(request.texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
        except ValueError as e:
            logger.error(f"Validation error during embedding: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document text: {str(e)}"
            )
        except RuntimeError as e:
            logger.error(f"Runtime error during embedding: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Embedding generation failed: {str(e)}"
            )
        
        # Store documents in database
        document_ids = []
        for i, (text, embedding) in enumerate(zip(request.texts, embeddings)):
            try:
                # Generate unique document ID
                doc_id = str(uuid.uuid4())
                
                # Store in database
                doc = db.add_document(
                    doc_id=doc_id,
                    text=text,
                    embedding=embedding,
                    metadata={"source": "api_ingest", "batch_index": i}
                )
                
                document_ids.append(doc_id)
                logger.debug(f"Stored document {i+1}/{len(request.texts)}: {doc_id}")
                
            except Exception as e:
                logger.error(f"Failed to store document {i}: {e}")
                # If we fail partway through, we still return the successful ones
                # but include an error message
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to store document at index {i}: {str(e)}"
                )
        
        logger.info(f"Successfully ingested {len(document_ids)} documents")
        
        return IngestResponse(
            success=True,
            document_ids=document_ids,
            count=len(document_ids),
            message=f"Successfully ingested {len(document_ids)} documents"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during ingestion: {str(e)}"
        )


@router.get("/documents", response_model=DocumentResponse)
async def get_all_documents():
    """
    Retrieve all documents from the database.
    
    Returns:
        DocumentResponse containing list of all documents and count
    
    Raises:
        HTTPException 500: If database query fails
    """
    try:
        logger.info("Retrieving all documents")
        
        # Get database manager
        db = get_db_manager()
        
        # Retrieve all documents
        documents = db.get_all_documents()
        
        logger.info(f"Retrieved {len(documents)} documents")
        
        return DocumentResponse(
            documents=documents,
            count=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/cluster", response_model=ClusterResponse)
async def get_clusters():
    """
    Perform clustering on all documents and return semantic folder structure.
    
    This endpoint retrieves all documents from the database, performs K-Means
    clustering on their embeddings, generates semantic folder names using LLM
    or fallback naming, and returns the complete folder hierarchy with document
    assignments.
    
    Returns:
        ClusterResponse with folders (clusters) and documents
    
    Raises:
        HTTPException 404: If no documents are found in the database
        HTTPException 500: If clustering or naming fails
    """
    try:
        logger.info("Starting clustering operation")
        
        # Get services
        db = get_db_manager()
        clusterer = get_cluster_engine()
        namer = get_naming_service()
        
        # Retrieve all documents
        documents = db.get_all_documents()
        
        if not documents:
            logger.warning("No documents found for clustering")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found in database. Please ingest documents first."
            )
        
        logger.info(f"Clustering {len(documents)} documents")
        
        # Perform clustering
        try:
            clusters_dict = clusterer.cluster_documents(documents)
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Clustering operation failed: {str(e)}"
            )
        
        # Build cluster response objects
        folders = []
        
        for cluster_id, cluster_docs in clusters_dict.items():
            try:
                # Calculate centroid
                centroid = clusterer.calculate_centroid(cluster_docs)
                
                # Find representative document
                representative_doc = clusterer.find_representative_doc(cluster_docs, centroid)
                
                # Generate folder name using representative documents
                # Use top 3 documents for naming (or all if fewer than 3)
                representative_texts = [doc.text for doc in cluster_docs[:3]]
                folder_name = namer.generate_folder_name(representative_texts)
                
                # Update cluster assignments in database
                for doc in cluster_docs:
                    doc.cluster_id = cluster_id
                    try:
                        db.update_cluster_assignment(doc.id, cluster_id)
                    except Exception as e:
                        logger.warning(f"Failed to update cluster assignment for doc {doc.id}: {e}")
                
                # Create Cluster object
                cluster = Cluster(
                    id=cluster_id,
                    name=folder_name,
                    centroid=centroid,
                    document_ids=[doc.id for doc in cluster_docs],
                    representative_doc_id=representative_doc.id
                )
                
                folders.append(cluster)
                logger.debug(
                    f"Created folder '{folder_name}' (cluster {cluster_id}) "
                    f"with {len(cluster_docs)} documents"
                )
                
            except Exception as e:
                logger.error(f"Failed to process cluster {cluster_id}: {e}")
                # Continue with other clusters even if one fails
                continue
        
        if not folders:
            logger.error("No valid clusters were created")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create any valid clusters"
            )
        
        logger.info(f"Successfully created {len(folders)} semantic folders")
        
        return ClusterResponse(
            folders=folders,
            documents=documents
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during clustering: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during clustering: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint with service status.
    
    Returns:
        Dictionary with service health information
    """
    try:
        embedder = get_embedding_service()
        db = get_db_manager()
        
        device_info = embedder.get_device_info()
        doc_count = db.count_documents()
        
        return {
            "status": "healthy",
            "services": {
                "embedding": "operational",
                "database": "operational"
            },
            "device": device_info["device"],
            "model": device_info["model_name"],
            "document_count": doc_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/re-embed", response_model=ReEmbedResponse)
async def re_embed_document(request: ReEmbedRequest):
    """
    Re-embed a document by nudging it toward a target folder's centroid.
    
    This endpoint implements the "drag-to-train" functionality. When a user
    drags a document to a different folder, this endpoint:
    1. Retrieves the document and target folder information
    2. Calculates the target folder's centroid
    3. Computes a weighted average between current embedding and target centroid
    4. Updates the document's embedding in the database
    5. Triggers automatic re-clustering
    6. Returns updated cluster assignments
    
    Args:
        request: ReEmbedRequest with document_id and target_folder_id
    
    Returns:
        ReEmbedResponse with success status, new cluster ID, and updated clusters
    
    Raises:
        HTTPException 404: If document or target folder not found
        HTTPException 500: If re-embedding or re-clustering fails
    """
    try:
        logger.info(
            f"Re-embedding document '{request.document_id}' "
            f"toward folder '{request.target_folder_id}'"
        )
        
        # Get services
        db = get_db_manager()
        reembedder = get_reembedding_engine()
        clusterer = get_cluster_engine()
        namer = get_naming_service()
        
        # Retrieve the document
        try:
            document = db.get_document(request.document_id)
        except RuntimeError as e:
            logger.error(f"Document not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{request.document_id}' not found"
            )
        
        # Get all documents to find the target folder
        all_documents = db.get_all_documents()
        
        if not all_documents:
            logger.error("No documents in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found in database"
            )
        
        # Perform clustering to get current folder structure
        try:
            clusters_dict = clusterer.cluster_documents(all_documents)
        except Exception as e:
            logger.error(f"Initial clustering failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve current clusters: {str(e)}"
            )
        
        # Find the target folder and calculate its centroid
        target_cluster_docs = clusters_dict.get(request.target_folder_id)
        
        if target_cluster_docs is None:
            logger.error(f"Target folder '{request.target_folder_id}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target folder '{request.target_folder_id}' not found"
            )
        
        # Calculate target centroid
        try:
            target_centroid = clusterer.calculate_centroid(target_cluster_docs)
        except Exception as e:
            logger.error(f"Failed to calculate target centroid: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to calculate target centroid: {str(e)}"
            )
        
        # Nudge the document's embedding toward the target
        try:
            new_embedding = reembedder.nudge_embedding(
                document.embedding,
                target_centroid
            )
        except Exception as e:
            logger.error(f"Re-embedding failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to re-embed document: {str(e)}"
            )
        
        # Update the document's embedding in the database
        try:
            db.update_embedding(request.document_id, new_embedding)
            logger.info(f"Updated embedding for document '{request.document_id}'")
        except Exception as e:
            logger.error(f"Failed to update embedding in database: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to persist updated embedding: {str(e)}"
            )
        
        # Trigger automatic re-clustering with updated embeddings
        # Check debouncing to prevent excessive re-clustering
        if should_perform_reclustering():
            logger.info("Triggering automatic re-clustering after embedding update")
            
            try:
                # Refresh documents from database (includes updated embedding)
                updated_documents = db.get_all_documents()
                
                # Perform re-clustering
                new_clusters_dict = clusterer.cluster_documents(updated_documents)
                
                # Build updated cluster response
                folders = []
                new_cluster_id = None
                
                for cluster_id, cluster_docs in new_clusters_dict.items():
                    # Calculate centroid
                    centroid = clusterer.calculate_centroid(cluster_docs)
                    
                    # Find representative document
                    representative_doc = clusterer.find_representative_doc(cluster_docs, centroid)
                    
                    # Generate folder name
                    representative_texts = [doc.text for doc in cluster_docs[:3]]
                    folder_name = namer.generate_folder_name(representative_texts)
                    
                    # Update cluster assignments in database
                    for doc in cluster_docs:
                        doc.cluster_id = cluster_id
                        try:
                            db.update_cluster_assignment(doc.id, cluster_id)
                        except Exception as e:
                            logger.warning(f"Failed to update cluster assignment for doc {doc.id}: {e}")
                        
                        # Track which cluster our re-embedded document ended up in
                        if doc.id == request.document_id:
                            new_cluster_id = cluster_id
                    
                    # Create Cluster object
                    cluster = Cluster(
                        id=cluster_id,
                        name=folder_name,
                        centroid=centroid,
                        document_ids=[doc.id for doc in cluster_docs],
                        representative_doc_id=representative_doc.id
                    )
                    
                    folders.append(cluster)
                
                if new_cluster_id is None:
                    logger.error(f"Document '{request.document_id}' not found in re-clustered results")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Document lost during re-clustering"
                    )
                
                logger.info(
                    f"Re-clustering complete. Document '{request.document_id}' "
                    f"now in cluster '{new_cluster_id}'"
                )
                
                # Build response
                updated_clusters = ClusterResponse(
                    folders=folders,
                    documents=updated_documents
                )
                
                return ReEmbedResponse(
                    success=True,
                    new_cluster_id=new_cluster_id,
                    updated_clusters=updated_clusters
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Re-clustering failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Re-clustering after embedding update failed: {str(e)}"
                )
        else:
            # Debouncing prevented re-clustering, return current cluster structure
            logger.info(
                "Re-clustering skipped due to debouncing. "
                "Returning current cluster structure."
            )
            
            try:
                # Get current documents (with updated embedding)
                updated_documents = db.get_all_documents()
                
                # Use the existing cluster structure (from before the embedding update)
                # The document's cluster_id in the database hasn't changed yet
                folders = []
                
                # Rebuild folders from current cluster assignments
                cluster_groups = {}
                for doc in updated_documents:
                    if doc.cluster_id:
                        if doc.cluster_id not in cluster_groups:
                            cluster_groups[doc.cluster_id] = []
                        cluster_groups[doc.cluster_id].append(doc)
                
                # If no cluster assignments exist, use the clusters we calculated earlier
                if not cluster_groups:
                    cluster_groups = clusters_dict
                
                for cluster_id, cluster_docs in cluster_groups.items():
                    # Calculate centroid
                    centroid = clusterer.calculate_centroid(cluster_docs)
                    
                    # Find representative document
                    representative_doc = clusterer.find_representative_doc(cluster_docs, centroid)
                    
                    # Generate folder name
                    representative_texts = [doc.text for doc in cluster_docs[:3]]
                    folder_name = namer.generate_folder_name(representative_texts)
                    
                    # Create Cluster object
                    cluster = Cluster(
                        id=cluster_id,
                        name=folder_name,
                        centroid=centroid,
                        document_ids=[doc.id for doc in cluster_docs],
                        representative_doc_id=representative_doc.id
                    )
                    
                    folders.append(cluster)
                
                # The document stays in its current cluster (no re-clustering)
                # Find which cluster the document is currently in
                current_cluster_id = document.cluster_id or request.target_folder_id
                
                updated_clusters = ClusterResponse(
                    folders=folders,
                    documents=updated_documents
                )
                
                return ReEmbedResponse(
                    success=True,
                    new_cluster_id=current_cluster_id,
                    updated_clusters=updated_clusters
                )
                
            except Exception as e:
                logger.error(f"Failed to build response during debouncing: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to build response: {str(e)}"
                )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during re-embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during re-embedding: {str(e)}"
        )

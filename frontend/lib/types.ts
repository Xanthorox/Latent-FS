/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

/**
 * Represents a document with its embedding and metadata.
 * Matches backend Document Pydantic model.
 */
export interface Document {
  id: string;
  text: string;
  embedding: number[];
  cluster_id: string | null;
  metadata: Record<string, any>;
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
}

/**
 * Represents a semantic cluster (folder).
 * Matches backend Cluster Pydantic model.
 */
export interface Cluster {
  id: string;
  name: string;
  centroid: number[];
  document_ids: string[];
  representative_doc_id: string;
}

/**
 * Semantic folder with additional UI properties.
 * Extended from Cluster for frontend use.
 */
export interface SemanticFolder {
  id: string;
  name: string;
  documentCount: number;
  color: string; // For visual distinction
  representativeDocId: string;
}

/**
 * Complete cluster data response.
 * Matches backend ClusterResponse Pydantic model.
 */
export interface ClusterData {
  folders: Cluster[];
  documents: Document[];
  timestamp: string; // ISO 8601 datetime string
}

/**
 * Request model for document ingestion.
 * Matches backend IngestRequest Pydantic model.
 */
export interface IngestRequest {
  texts: string[];
}

/**
 * Response model for document ingestion.
 * Matches backend IngestResponse Pydantic model.
 */
export interface IngestResponse {
  success: boolean;
  document_ids: string[];
  count: number;
  message: string;
}

/**
 * Request model for re-embedding a document.
 * Matches backend ReEmbedRequest Pydantic model.
 */
export interface ReEmbedRequest {
  document_id: string;
  target_folder_id: string;
}

/**
 * Response model for re-embedding operations.
 * Matches backend ReEmbedResponse Pydantic model.
 */
export interface ReEmbedResponse {
  success: boolean;
  new_cluster_id: string;
  updated_clusters: ClusterData;
}

/**
 * Response model for document retrieval.
 * Matches backend DocumentResponse Pydantic model.
 */
export interface DocumentResponse {
  documents: Document[];
  count: number;
}

/**
 * Drag state for drag-and-drop operations.
 */
export interface DragState {
  isDragging: boolean;
  documentId: string | null;
  sourceFolderId: string | null;
}

/**
 * API error response structure.
 */
export interface APIError {
  detail: string;
  status: number;
}

/**
 * Helper type for API responses that can fail.
 */
export type APIResult<T> = 
  | { success: true; data: T }
  | { success: false; error: APIError };

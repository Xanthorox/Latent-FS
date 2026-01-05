/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import { z } from 'zod';
import type {
  Document,
  Cluster,
  ClusterData,
  IngestRequest,
  IngestResponse,
  ReEmbedRequest,
  ReEmbedResponse,
  DocumentResponse,
  APIError,
  APIResult,
} from './types';

// Zod schemas for runtime validation
const DocumentSchema = z.object({
  id: z.string(),
  text: z.string(),
  embedding: z.array(z.number()),
  cluster_id: z.string().nullable(),
  metadata: z.record(z.string(), z.any()),
  created_at: z.string(),
  updated_at: z.string(),
});

const ClusterSchema = z.object({
  id: z.string(),
  name: z.string(),
  centroid: z.array(z.number()),
  document_ids: z.array(z.string()),
  representative_doc_id: z.string(),
});

const ClusterDataSchema = z.object({
  folders: z.array(ClusterSchema),
  documents: z.array(DocumentSchema),
  timestamp: z.string(),
});

const IngestResponseSchema = z.object({
  success: z.boolean(),
  document_ids: z.array(z.string()),
  count: z.number(),
  message: z.string(),
});

const ClusterResponseSchema = z.object({
  folders: z.array(ClusterSchema),
  documents: z.array(DocumentSchema),
  timestamp: z.string(),
});

const ReEmbedResponseSchema = z.object({
  success: z.boolean(),
  new_cluster_id: z.string(),
  updated_clusters: ClusterResponseSchema,
});

const DocumentResponseSchema = z.object({
  documents: z.array(DocumentSchema),
  count: z.number(),
});

/**
 * Configuration options for the API client.
 */
export interface LatentFSClientConfig {
  baseURL: string;
  maxRetries?: number;
  retryDelay?: number;
  timeout?: number;
}

/**
 * API client for Latent-FS backend.
 * Handles all communication with the FastAPI backend.
 */
export class LatentFSClient {
  private baseURL: string;
  private maxRetries: number;
  private retryDelay: number;
  private timeout: number;

  /**
   * Create a new Latent-FS API client.
   * @param config - Client configuration
   */
  constructor(config: LatentFSClientConfig) {
    this.baseURL = config.baseURL.replace(/\/$/, ''); // Remove trailing slash
    this.maxRetries = config.maxRetries ?? 3;
    this.retryDelay = config.retryDelay ?? 1000; // 1 second
    this.timeout = config.timeout ?? 30000; // 30 seconds
  }

  /**
   * Make an HTTP request with retry logic and error handling.
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    schema: z.ZodSchema<T>
  ): Promise<APIResult<T>> {
    const url = `${this.baseURL}${endpoint}`;
    let lastError: APIError | null = null;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });

        clearTimeout(timeoutId);

        // Handle non-OK responses
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({
            detail: `HTTP ${response.status}: ${response.statusText}`,
          }));

          lastError = {
            detail: errorData.detail || errorData.message || 'Unknown error',
            status: response.status,
          };

          // Don't retry on client errors (4xx)
          if (response.status >= 400 && response.status < 500) {
            return { success: false, error: lastError };
          }

          // Retry on server errors (5xx)
          if (attempt < this.maxRetries) {
            await this.sleep(this.retryDelay * Math.pow(2, attempt)); // Exponential backoff
            continue;
          }

          return { success: false, error: lastError };
        }

        // Parse and validate response
        const data = await response.json();
        const validated = schema.parse(data);

        return { success: true, data: validated };
      } catch (error) {
        // Handle network errors, timeouts, and validation errors
        if (error instanceof z.ZodError) {
          lastError = {
            detail: `Invalid response format: ${error.message}`,
            status: 0,
          };
          return { success: false, error: lastError };
        }

        if (error instanceof Error) {
          if (error.name === 'AbortError') {
            lastError = {
              detail: 'Request timeout',
              status: 0,
            };
          } else {
            lastError = {
              detail: error.message || 'Network error',
              status: 0,
            };
          }
        } else {
          lastError = {
            detail: 'Unknown error occurred',
            status: 0,
          };
        }

        // Retry on network errors
        if (attempt < this.maxRetries) {
          await this.sleep(this.retryDelay * Math.pow(2, attempt));
          continue;
        }

        return { success: false, error: lastError };
      }
    }

    // Should never reach here, but TypeScript needs it
    return {
      success: false,
      error: lastError || { detail: 'Max retries exceeded', status: 0 },
    };
  }

  /**
   * Sleep for a specified duration.
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Ingest documents into the system.
   * @param texts - Array of document texts to ingest
   * @returns Ingestion response with document IDs
   */
  async ingestDocuments(texts: string[]): Promise<APIResult<IngestResponse>> {
    const body: IngestRequest = { texts };

    return this.request<IngestResponse>(
      '/ingest',
      {
        method: 'POST',
        body: JSON.stringify(body),
      },
      IngestResponseSchema
    );
  }

  /**
   * Get current cluster data (semantic folders and documents).
   * @returns Cluster data with folders and documents
   */
  async getClusters(): Promise<APIResult<ClusterData>> {
    return this.request<ClusterData>(
      '/cluster',
      {
        method: 'GET',
      },
      ClusterDataSchema
    );
  }

  /**
   * Re-embed a document to move it toward a target folder.
   * @param documentId - ID of document to re-embed
   * @param targetFolderId - ID of target folder/cluster
   * @returns Re-embedding response with updated clusters
   */
  async reEmbedDocument(
    documentId: string,
    targetFolderId: string
  ): Promise<APIResult<ReEmbedResponse>> {
    const body: ReEmbedRequest = {
      document_id: documentId,
      target_folder_id: targetFolderId,
    };

    return this.request<ReEmbedResponse>(
      '/re-embed',
      {
        method: 'POST',
        body: JSON.stringify(body),
      },
      ReEmbedResponseSchema
    );
  }

  /**
   * Get all documents in the system.
   * @returns All documents with metadata
   */
  async getAllDocuments(): Promise<APIResult<DocumentResponse>> {
    return this.request<DocumentResponse>(
      '/documents',
      {
        method: 'GET',
      },
      DocumentResponseSchema
    );
  }

  /**
   * Health check endpoint.
   * @returns True if backend is reachable
   */
  async healthCheck(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${this.baseURL}/`, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch {
      return false;
    }
  }
}

/**
 * Create a default API client instance.
 * Uses environment variable or defaults to localhost.
 */
export function createAPIClient(): LatentFSClient {
  const baseURL =
    typeof window !== 'undefined'
      ? 'http://localhost:9999' // Always use localhost:9999 for backend in development
      : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9999';

  return new LatentFSClient({
    baseURL: `${baseURL}/api`, // Add /api prefix for backend routes
    maxRetries: 3,
    retryDelay: 1000,
    timeout: 30000,
  });
}

/**
 * Default API client instance.
 */
export const apiClient = createAPIClient();

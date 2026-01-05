/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';
import type { ClusterData, APIError } from '@/lib/types';

/**
 * State interface for cluster data hook.
 */
export interface UseClusterDataState {
  data: ClusterData | null;
  loading: boolean;
  error: APIError | null;
  refresh: () => Promise<void>;
}

/**
 * Hook options for configuring behavior.
 */
export interface UseClusterDataOptions {
  /**
   * Whether to fetch data immediately on mount.
   * @default true
   */
  fetchOnMount?: boolean;

  /**
   * Automatic refresh interval in milliseconds.
   * Set to 0 or undefined to disable auto-refresh.
   * @default undefined
   */
  refreshInterval?: number;
}

/**
 * Custom hook for fetching and managing cluster data.
 * 
 * Provides cluster data with loading and error states, plus manual refresh capability.
 * Supports automatic refresh at specified intervals.
 * 
 * @param options - Configuration options for the hook
 * @returns Cluster data state and refresh function
 * 
 * @example
 * ```tsx
 * const { data, loading, error, refresh } = useClusterData();
 * 
 * if (loading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage error={error} />;
 * if (!data) return null;
 * 
 * return <FileSystemView data={data} onRefresh={refresh} />;
 * ```
 * 
 * @example
 * ```tsx
 * // With auto-refresh every 5 seconds
 * const { data, loading, error } = useClusterData({
 *   refreshInterval: 5000
 * });
 * ```
 */
export function useClusterData(
  options: UseClusterDataOptions = {}
): UseClusterDataState {
  const { fetchOnMount = true, refreshInterval } = options;

  const [data, setData] = useState<ClusterData | null>(null);
  const [loading, setLoading] = useState<boolean>(fetchOnMount);
  const [error, setError] = useState<APIError | null>(null);

  /**
   * Fetch cluster data from the API.
   * Handles loading and error states.
   */
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.getClusters();

      if (result.success) {
        setData(result.data);
        setError(null);
      } else {
        setError(result.error);
        // Don't clear existing data on error - keep showing stale data
      }
    } catch (err) {
      // Catch any unexpected errors
      const apiError: APIError = {
        detail: err instanceof Error ? err.message : 'Unknown error occurred',
        status: 0,
      };
      setError(apiError);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Manual refresh function exposed to consumers.
   * Can be called to force a data refresh.
   */
  const refresh = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  // Initial fetch on mount
  useEffect(() => {
    if (fetchOnMount) {
      fetchData();
    }
  }, [fetchOnMount, fetchData]);

  // Auto-refresh interval
  useEffect(() => {
    if (!refreshInterval || refreshInterval <= 0) {
      return;
    }

    const intervalId = setInterval(() => {
      fetchData();
    }, refreshInterval);

    return () => {
      clearInterval(intervalId);
    };
  }, [refreshInterval, fetchData]);

  return {
    data,
    loading,
    error,
    refresh,
  };
}

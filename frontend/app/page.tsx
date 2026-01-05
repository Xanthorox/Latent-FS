/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

'use client';

import { useClusterData } from '@/hooks/useClusterData';
import { FileSystemView } from '@/components/FileSystemView';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { EmptyState } from '@/components/EmptyState';
import { AlertCircle, RefreshCw } from 'lucide-react';

/**
 * Error display component with retry button.
 */
function ErrorDisplay({ error, onRetry }: { error: { detail: string; status: number }; onRetry: () => void }) {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-950">
      <div className="flex max-w-md flex-col items-center gap-6 rounded-lg border border-red-500/20 bg-red-950/10 p-8 backdrop-blur-sm">
        <AlertCircle className="h-16 w-16 text-red-500" />
        <div className="text-center">
          <h2 className="mb-2 text-xl font-semibold text-red-400">
            Failed to Load Data
          </h2>
          <p className="text-gray-400">{error.detail}</p>
          {error.status > 0 && (
            <p className="mt-2 text-sm text-gray-500">Status: {error.status}</p>
          )}
        </div>
        <button
          onClick={onRetry}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Retry
        </button>
      </div>
    </div>
  );
}

/**
 * Main page component for Latent-FS.
 * Fetches cluster data and displays the file system interface.
 */
export default function Home() {
  const { data, loading, error, refresh } = useClusterData({
    fetchOnMount: true,
  });

  // Show loading state
  if (loading && !data) {
    return <LoadingSpinner size="lg" message="Loading cluster data..." fullScreen />;
  }

  // Show error state with retry option
  if (error && !data) {
    return <ErrorDisplay error={error} onRetry={refresh} />;
  }

  // Show empty state if no data
  if (!data) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-950">
        <EmptyState type="no-data" />
      </div>
    );
  }

  // Show file system view with data
  return <FileSystemView initialData={data} />;
}

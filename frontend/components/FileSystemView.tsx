/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

'use client';

import React, { useState } from 'react';
import { ClusterData, SemanticFolder } from '@/lib/types';
import { Sidebar } from './Sidebar';
import { GridView } from './GridView';
import { apiClient } from '@/lib/api-client';
import { ToastContainer } from './Toast';
import { useToast } from '@/hooks/useToast';
import { LoadingOverlay } from './LoadingSpinner';

interface FileSystemViewProps {
  initialData?: ClusterData;
}

// Helper function to generate colors for folders
const generateFolderColor = (index: number): string => {
  const colors = [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#06b6d4', // cyan
    '#f97316', // orange
  ];
  return colors[index % colors.length];
};

export function FileSystemView({ initialData }: FileSystemViewProps) {
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);
  const [clusterData, setClusterData] = useState<ClusterData | undefined>(initialData);
  const [isReEmbedding, setIsReEmbedding] = useState(false);
  const [updateCounter, setUpdateCounter] = useState(0); // Force re-render counter
  const { toasts, showError, showSuccess, dismissToast } = useToast();

  // Transform cluster data into semantic folders - force recalculation on every render
  const folders: SemanticFolder[] = clusterData?.folders.map((cluster, index) => ({
    id: cluster.id,
    name: cluster.name,
    documentCount: cluster.document_ids.length,
    color: generateFolderColor(index),
    representativeDocId: cluster.representative_doc_id,
  })) || [];

  const documents = clusterData?.documents || [];
  
  // Log folders on every render to debug
  React.useEffect(() => {
    console.log('🔄 Folders rendered:', folders.map(f => ({ name: f.name, count: f.documentCount })));
  });

  // Validate that selectedFolderId still exists in current folders
  // If not, clear the selection
  React.useEffect(() => {
    if (selectedFolderId && folders.length > 0) {
      const folderExists = folders.some(f => f.id === selectedFolderId);
      if (!folderExists) {
        console.log('Selected folder no longer exists, clearing selection');
        setSelectedFolderId(null);
      }
    }
  }, [selectedFolderId, folders]);

  const handleFolderSelect = (folderId: string) => {
    // Toggle selection: if already selected, deselect (show all)
    setSelectedFolderId(selectedFolderId === folderId ? null : folderId);
  };

  const handleFolderDrop = async (targetFolderId: string, documentId: string) => {
    // Prevent multiple simultaneous re-embedding operations
    if (isReEmbedding) {
      showError('Please wait for the current operation to complete');
      return;
    }

    setIsReEmbedding(true);

    try {
      console.log('🔄 Starting re-embed:', { documentId, targetFolderId });
      
      // Call API to re-embed the document
      const result = await apiClient.reEmbedDocument(documentId, targetFolderId);
      
      console.log('📦 API result:', result);

      if (result.success) {
        console.log('✅ Re-embed successful, updating UI');
        
        const newFolders = result.data.updated_clusters.folders;
        console.log('📊 New folders:', newFolders.map(f => ({
          id: f.id,
          name: f.name,
          count: f.document_ids.length,
          docIds: f.document_ids.slice(0, 3) // First 3 doc IDs
        })));
        
        console.log('📊 Current folders before update:', folders.map(f => ({
          id: f.id,
          name: f.name,
          count: f.documentCount
        })));
        
        // Create completely new object to force React re-render
        const newClusterData: ClusterData = {
          folders: [...result.data.updated_clusters.folders],
          documents: [...result.data.updated_clusters.documents],
          timestamp: new Date().toISOString(), // Force new timestamp
        };
        
        // Clear selection first
        setSelectedFolderId(null);
        
        // Update data immediately (no delay)
        setClusterData(newClusterData);
        
        // Force re-render by incrementing counter
        setUpdateCounter(prev => prev + 1);
        console.log('🎨 UI updated with new data, counter:', updateCounter + 1);
        
        // Log after update
        setTimeout(() => {
          console.log('📊 Folders after state update:', folders.map(f => ({
            id: f.id,
            name: f.name,
            count: f.documentCount
          })));
        }, 100);
        
        // Show success notification
        showSuccess('Document moved successfully!');
      } else {
        // Handle error with retry option
        showError(
          result.error.detail || 'Failed to move document',
          {
            canRetry: true,
            onRetry: () => handleFolderDrop(targetFolderId, documentId),
          }
        );
      }
    } catch (error) {
      // Handle unexpected errors
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'An unexpected error occurred';
      
      showError(errorMessage, {
        canRetry: true,
        onRetry: () => handleFolderDrop(targetFolderId, documentId),
      });
    } finally {
      setIsReEmbedding(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar
        key={`sidebar-${updateCounter}`}
        folders={folders}
        selectedFolderId={selectedFolderId}
        onFolderSelect={handleFolderSelect}
        onFolderDrop={handleFolderDrop}
      />
      <GridView
        documents={documents}
        selectedFolderId={selectedFolderId}
      />
      
      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
      
      {/* Loading overlay during re-embedding */}
      {isReEmbedding && (
        <LoadingOverlay message="Re-organizing documents..." />
      )}
    </div>
  );
}

/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import React from 'react';
import { Document } from '@/lib/types';
import { DocumentCardNative as DocumentCard } from './DocumentCardNative';
import { EmptyState } from './EmptyState';

interface GridViewProps {
  documents: Document[];
  selectedFolderId: string | null;
}

export function GridView({ documents, selectedFolderId }: GridViewProps) {
  // Filter documents based on selected folder
  const filteredDocuments = selectedFolderId
    ? documents.filter((doc) => doc.cluster_id === selectedFolderId)
    : documents;

  return (
    <div className="flex-1 h-screen overflow-y-auto p-6 bg-gray-950 relative z-10">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">
          {selectedFolderId ? 'Folder Contents' : 'All Documents'}
        </h1>
        <p className="text-gray-400 text-sm">
          {filteredDocuments.length} {filteredDocuments.length === 1 ? 'document' : 'documents'}
        </p>
      </div>

      {/* Empty state */}
      {filteredDocuments.length === 0 ? (
        <EmptyState
          type={selectedFolderId ? 'folder-empty' : 'no-documents'}
        />
      ) : (
        /* Document grid - Removed layout animations that interfere with drag */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredDocuments.map((document) => (
            <div key={document.id}>
              <DocumentCard document={document} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

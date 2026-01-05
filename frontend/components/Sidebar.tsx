/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SemanticFolder } from '@/lib/types';
import { CompactEmptyState } from './EmptyState';

interface SidebarProps {
  folders: SemanticFolder[];
  selectedFolderId: string | null;
  onFolderSelect: (folderId: string) => void;
  onFolderDrop: (folderId: string, documentId: string) => void;
}

export function Sidebar({ folders, selectedFolderId, onFolderSelect, onFolderDrop }: SidebarProps) {
  const [dragSourceFolderId, setDragSourceFolderId] = React.useState<string | null>(null);

  React.useEffect(() => {
    const handleDragActive = (e: Event) => {
      const customEvent = e as CustomEvent;
      setDragSourceFolderId(customEvent.detail.sourceFolderId);
    };

    const handleDragInactive = () => {
      setDragSourceFolderId(null);
    };

    window.addEventListener('document-drag-active', handleDragActive);
    window.addEventListener('document-drag-inactive', handleDragInactive);

    return () => {
      window.removeEventListener('document-drag-active', handleDragActive);
      window.removeEventListener('document-drag-inactive', handleDragInactive);
    };
  }, []);

  return (
    <aside className="w-64 h-screen bg-gray-900/50 backdrop-blur-xl border-r border-gray-700/50 p-4 overflow-y-auto relative z-50">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white mb-2">Semantic Folders</h2>
        <p className="text-sm text-gray-400">AI-organized categories</p>
      </div>

      <nav className="space-y-2">
        {folders.length === 0 ? (
          <CompactEmptyState
            icon={<div className="text-4xl">📂</div>}
            title="No Folders Yet"
            description="Folders will appear here once documents are clustered"
          />
        ) : (
          <AnimatePresence mode="popLayout">
            {folders.map((folder) => (
              <FolderItem
                key={folder.id}
                folder={folder}
                isSelected={selectedFolderId === folder.id}
                isDragActive={dragSourceFolderId !== null}
                canAcceptDrag={dragSourceFolderId !== null && dragSourceFolderId !== folder.id}
                onSelect={() => onFolderSelect(folder.id)}
                onDrop={(documentId) => onFolderDrop(folder.id, documentId)}
              />
            ))}
          </AnimatePresence>
        )}
      </nav>
    </aside>
  );
}

// Folder item component with native drop zone functionality
interface FolderItemProps {
  folder: SemanticFolder;
  isSelected: boolean;
  isDragActive: boolean;
  canAcceptDrag: boolean;
  onSelect: () => void;
  onDrop: (documentId: string) => void;
}

function FolderItem({ folder, isSelected, isDragActive, canAcceptDrag, onSelect, onDrop }: FolderItemProps) {
  const [dragOver, setDragOver] = React.useState(false);
  const [canAcceptDrop, setCanAcceptDrop] = React.useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    try {
      const data = e.dataTransfer.getData('application/json');
      if (data) {
        const { sourceFolderId } = JSON.parse(data);
        const canDrop = sourceFolderId !== folder.id;
        setCanAcceptDrop(canDrop);
        if (canDrop) {
          console.log('✨ Drag over folder:', folder.name, 'canDrop:', canDrop);
          setDragOver(true);
        }
      }
    } catch {
      // Data not available during dragover in some browsers
      // Assume it can be dropped
      console.log('✨ Drag over folder (no data):', folder.name);
      setDragOver(true);
      setCanAcceptDrop(true);
    }
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDragLeave = (e: React.DragEvent) => {
    // Only clear if we're actually leaving the element (not entering a child)
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;
    
    if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
      setDragOver(false);
      setCanAcceptDrop(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    setCanAcceptDrop(false);

    try {
      const data = e.dataTransfer.getData('application/json');
      const { documentId, sourceFolderId } = JSON.parse(data);
      
      // Only trigger drop if document is from a different folder
      if (sourceFolderId !== folder.id) {
        onDrop(documentId);
      }
    } catch (error) {
      console.error('Failed to parse drop data:', error);
    }
  };

  return (
    <motion.button
      onClick={onSelect}
      onDragOver={handleDragOver}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{
        layout: { duration: 0.3, ease: [0.4, 0, 0.2, 1] },
        opacity: { duration: 0.2 },
        x: { duration: 0.3, ease: [0.4, 0, 0.2, 1] }
      }}
      style={{
        position: 'relative',
        zIndex: dragOver ? 100 : 10,
        pointerEvents: 'auto',
      }}
      className={`
        w-full text-left px-4 py-3 rounded-lg
        transition-all duration-200
        backdrop-blur-sm
        relative
        ${
          isSelected
            ? 'bg-white/20 border border-white/30 shadow-lg'
            : 'bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20'
        }
        ${dragOver && canAcceptDrop 
          ? 'ring-4 ring-green-500 bg-green-500/40 scale-110 z-50 shadow-2xl border-green-500 brightness-125' 
          : ''
        }
        ${!dragOver && isDragActive && canAcceptDrag
          ? 'opacity-60'
          : ''
        }
      `}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: folder.color }}
          />
          <span className="text-white font-medium">{folder.name}</span>
          {dragOver && <span className="text-xs text-green-400">DROP HERE</span>}
        </div>
        <span
          className={`
            text-xs px-2 py-1 rounded-full
            ${
              isSelected
                ? 'bg-white/30 text-white'
                : 'bg-white/10 text-gray-300'
            }
          `}
        >
          {folder.documentCount}
        </span>
      </div>
    </motion.button>
  );
}

/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import React from 'react';
import { Document } from '@/lib/types';

interface DocumentCardProps {
  document: Document;
}

export function DocumentCardNative({ document: doc }: DocumentCardProps) {
  const [isDragging, setIsDragging] = React.useState(false);

  const handleDragStart = (e: React.DragEvent) => {
    setIsDragging(true);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('application/json', JSON.stringify({
      documentId: doc.id,
      sourceFolderId: doc.cluster_id,
    }));
    
    console.log('🎯 Drag started:', doc.id);
    
    // Dispatch event to notify sidebar that drag started
    window.dispatchEvent(new CustomEvent('document-drag-active', { 
      detail: { sourceFolderId: doc.cluster_id } 
    }));
    
    // Create a semi-transparent drag image
    const dragImage = e.currentTarget.cloneNode(true) as HTMLElement;
    dragImage.style.opacity = '0.5';
    dragImage.style.transform = 'rotate(5deg)';
    dragImage.style.pointerEvents = 'none'; // Critical: don't block events
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 50, 50);
    setTimeout(() => {
      if (document.body.contains(dragImage)) {
        document.body.removeChild(dragImage);
      }
    }, 0);
  };

  const handleDragEnd = () => {
    setIsDragging(false);
    // Notify sidebar that drag ended
    window.dispatchEvent(new CustomEvent('document-drag-inactive'));
  };

  const docPreview = doc.text.length > 150 
    ? doc.text.substring(0, 150) + '...' 
    : doc.text;

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return 'Unknown date';
    }
  };

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      className={`
        group bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-4
        hover:bg-white/10 hover:border-white/20 
        transition-all duration-300 ease-out
        cursor-grab active:cursor-grabbing 
        shadow-lg hover:shadow-xl select-none
        ${isDragging ? 'opacity-50 scale-95 rotate-2 shadow-2xl' : 'hover:scale-105'}
      `}
      style={{ 
        touchAction: 'none', 
        userSelect: 'none', 
        WebkitUserSelect: 'none',
        transform: isDragging ? 'translateY(-8px)' : 'translateY(0)',
      }}
    >
      <div className="mb-3 select-none">
        <p className="text-gray-200 text-sm leading-relaxed line-clamp-4 select-none">
          {docPreview}
        </p>
      </div>

      <div className="flex items-center justify-between text-xs text-gray-400 pt-3 border-t border-white/5 select-none">
        <div className="flex items-center gap-2">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{formatDate(doc.created_at)}</span>
        </div>

        {doc.metadata && Object.keys(doc.metadata).length > 0 && (
          <div className="flex items-center gap-1">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
            <span>{Object.keys(doc.metadata).length} tags</span>
          </div>
        )}
      </div>

      <div className="mt-2 text-xs text-gray-500 font-mono truncate">
        {doc.id.substring(0, 8)}...
      </div>
    </div>
  );
}

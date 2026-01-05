/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import React from 'react';
import { useDragLayer } from 'react-dnd';

interface DragItem {
  type: string;
  documentId: string;
  sourceFolderId: string | null;
}

/**
 * Custom drag layer that renders a preview without blocking pointer events.
 * This solves the React DnD HTML5Backend hover detection issue.
 */
export function CustomDragLayer() {
  const { isDragging, item, currentOffset } = useDragLayer((monitor) => ({
    item: monitor.getItem() as DragItem | null,
    currentOffset: monitor.getSourceClientOffset(),
    isDragging: monitor.isDragging(),
  }));

  if (!isDragging || !currentOffset) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        pointerEvents: 'none',
        zIndex: 100,
        left: 0,
        top: 0,
        width: '100%',
        height: '100%',
      }}
    >
      <div
        style={{
          transform: `translate(${currentOffset.x}px, ${currentOffset.y}px)`,
        }}
      >
        <div
          className="
            bg-blue-500/20 backdrop-blur-md
            border-2 border-blue-500
            rounded-lg p-4
            shadow-2xl
            w-64
          "
        >
          <div className="text-white font-medium text-sm">
            📄 Dragging document...
          </div>
          <div className="text-blue-200 text-xs mt-1">
            Drop on a folder to move
          </div>
        </div>
      </div>
    </div>
  );
}

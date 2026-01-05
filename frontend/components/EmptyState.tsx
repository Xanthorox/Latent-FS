/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import React from 'react';
import { FileText, Folder, Database, AlertCircle } from 'lucide-react';

export type EmptyStateType = 'no-documents' | 'no-folders' | 'no-data' | 'folder-empty';

interface EmptyStateProps {
  type: EmptyStateType;
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

/**
 * Reusable empty state component.
 * Displays helpful messages when there's no data to show.
 */
export function EmptyState({ type, title, description, icon, action }: EmptyStateProps) {
  // Default configurations for each type
  const configs = {
    'no-documents': {
      icon: <FileText className="w-16 h-16 text-gray-600" />,
      title: 'No Documents Found',
      description: 'Get started by ingesting documents into the system. They will be automatically organized into semantic folders.',
      tip: 'Use the /ingest API endpoint to add documents',
    },
    'no-folders': {
      icon: <Folder className="w-16 h-16 text-gray-600" />,
      title: 'No Folders Yet',
      description: 'Folders will appear here once documents are clustered. Add some documents to get started.',
      tip: null,
    },
    'no-data': {
      icon: <Database className="w-16 h-16 text-gray-600" />,
      title: 'No Data Available',
      description: 'The system has no documents or clusters to display. Start by ingesting some documents.',
      tip: null,
    },
    'folder-empty': {
      icon: <Folder className="w-16 h-16 text-gray-600" />,
      title: 'This Folder is Empty',
      description: 'This semantic folder doesn\'t contain any documents yet. Try dragging documents here to organize them.',
      tip: null,
    },
  };

  const config = configs[type];
  const displayTitle = title || config.title;
  const displayDescription = description || config.description;
  const displayIcon = icon || config.icon;

  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      {/* Icon */}
      <div className="mb-6 opacity-50">
        {displayIcon}
      </div>

      {/* Title */}
      <h3 className="text-xl font-semibold text-gray-300 mb-3">
        {displayTitle}
      </h3>

      {/* Description */}
      <p className="text-sm text-gray-500 max-w-md leading-relaxed mb-6">
        {displayDescription}
      </p>

      {/* Tip */}
      {config.tip && (
        <div className="px-6 py-3 bg-blue-600/10 border border-blue-500/20 rounded-lg">
          <p className="text-xs text-blue-400">
            💡 Tip: {config.tip}
          </p>
        </div>
      )}

      {/* Action button */}
      {action && (
        <button
          onClick={action.onClick}
          className="mt-6 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

/**
 * Compact empty state for smaller spaces (like sidebar).
 */
export function CompactEmptyState({ 
  icon, 
  title, 
  description 
}: { 
  icon?: React.ReactNode; 
  title: string; 
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
      {icon && (
        <div className="mb-3 opacity-50">
          {icon}
        </div>
      )}
      <h4 className="text-sm font-medium text-gray-400 mb-1">
        {title}
      </h4>
      {description && (
        <p className="text-xs text-gray-500 leading-relaxed">
          {description}
        </p>
      )}
    </div>
  );
}

/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  fullScreen?: boolean;
}

/**
 * Reusable loading spinner component.
 * Can be used inline or as a full-screen overlay.
 */
export function LoadingSpinner({ 
  size = 'md', 
  message, 
  fullScreen = false 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  const spinner = (
    <div className="flex flex-col items-center gap-3">
      <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-500`} />
      {message && (
        <p className={`${textSizeClasses[size]} text-gray-400`}>
          {message}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-950">
        {spinner}
      </div>
    );
  }

  return spinner;
}

interface LoadingOverlayProps {
  message?: string;
  transparent?: boolean;
}

/**
 * Full-screen loading overlay with backdrop blur.
 * Used for blocking operations like re-embedding.
 */
export function LoadingOverlay({ 
  message = 'Loading...', 
  transparent = false 
}: LoadingOverlayProps) {
  return (
    <div 
      className={`
        fixed inset-0 z-50 
        flex items-center justify-center
        ${transparent ? 'bg-black/30' : 'bg-black/50'} 
        backdrop-blur-sm
      `}
    >
      <div className="bg-gray-900/90 border border-white/10 rounded-lg p-6 flex items-center gap-4 shadow-2xl">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        <span className="text-white text-lg">{message}</span>
      </div>
    </div>
  );
}

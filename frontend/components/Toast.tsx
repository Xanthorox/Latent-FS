/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle, Info, X, RefreshCw } from 'lucide-react';

export type ToastType = 'error' | 'success' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  canRetry?: boolean;
  onRetry?: () => void;
  duration?: number; // Auto-dismiss duration in ms (0 = no auto-dismiss)
}

interface ToastProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

/**
 * Individual toast notification component.
 */
function ToastItem({ toast, onDismiss }: ToastProps) {
  const { id, type, message, canRetry, onRetry, duration = 5000 } = toast;

  // Auto-dismiss after duration
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onDismiss(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onDismiss]);

  // Icon based on type
  const Icon = type === 'error' ? AlertCircle : type === 'success' ? CheckCircle : Info;

  // Colors based on type
  const colors = {
    error: {
      bg: 'bg-red-950/90',
      border: 'border-red-500/30',
      icon: 'text-red-400',
      text: 'text-red-100',
    },
    success: {
      bg: 'bg-green-950/90',
      border: 'border-green-500/30',
      icon: 'text-green-400',
      text: 'text-green-100',
    },
    info: {
      bg: 'bg-blue-950/90',
      border: 'border-blue-500/30',
      icon: 'text-blue-400',
      text: 'text-blue-100',
    },
  };

  const colorScheme = colors[type];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.95 }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 30,
      }}
      className={`
        ${colorScheme.bg} ${colorScheme.border}
        border backdrop-blur-xl
        rounded-lg shadow-2xl
        p-4 min-w-[320px] max-w-md
      `}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <Icon className={`${colorScheme.icon} w-5 h-5 flex-shrink-0 mt-0.5`} />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className={`${colorScheme.text} text-sm leading-relaxed`}>
            {message}
          </p>

          {/* Retry button for recoverable errors */}
          {canRetry && onRetry && (
            <button
              onClick={() => {
                onRetry();
                onDismiss(id);
              }}
              className="mt-3 flex items-center gap-2 text-xs font-medium text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              Retry
            </button>
          )}
        </div>

        {/* Dismiss button */}
        <button
          onClick={() => onDismiss(id)}
          className="text-gray-400 hover:text-white transition-colors flex-shrink-0"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

/**
 * Container for all toast notifications.
 * Positioned at top-right of screen.
 */
export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastItem toast={toast} onDismiss={onDismiss} />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
}

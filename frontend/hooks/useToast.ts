/**
 * Latent-FS - The Vector File System
 * Author: Gary Dev of Xanthorox
 * Copyright © 2026 Xanthorox
 */

import { useState, useCallback } from 'react';
import type { Toast, ToastType } from '@/components/Toast';

/**
 * Hook for managing toast notifications.
 * Provides methods to show and dismiss toasts.
 */
export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  /**
   * Show a new toast notification.
   */
  const showToast = useCallback(
    (
      type: ToastType,
      message: string,
      options?: {
        canRetry?: boolean;
        onRetry?: () => void;
        duration?: number;
      }
    ) => {
      const id = `toast-${Date.now()}-${Math.random()}`;
      const newToast: Toast = {
        id,
        type,
        message,
        canRetry: options?.canRetry,
        onRetry: options?.onRetry,
        duration: options?.duration,
      };

      setToasts((prev) => [...prev, newToast]);
      return id;
    },
    []
  );

  /**
   * Dismiss a toast by ID.
   */
  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  /**
   * Dismiss all toasts.
   */
  const dismissAll = useCallback(() => {
    setToasts([]);
  }, []);

  /**
   * Show an error toast.
   */
  const showError = useCallback(
    (message: string, options?: { canRetry?: boolean; onRetry?: () => void }) => {
      return showToast('error', message, {
        ...options,
        duration: options?.canRetry ? 0 : 7000, // Don't auto-dismiss if retry is available
      });
    },
    [showToast]
  );

  /**
   * Show a success toast.
   */
  const showSuccess = useCallback(
    (message: string, duration = 4000) => {
      return showToast('success', message, { duration });
    },
    [showToast]
  );

  /**
   * Show an info toast.
   */
  const showInfo = useCallback(
    (message: string, duration = 5000) => {
      return showToast('info', message, { duration });
    },
    [showToast]
  );

  return {
    toasts,
    showToast,
    showError,
    showSuccess,
    showInfo,
    dismissToast,
    dismissAll,
  };
}

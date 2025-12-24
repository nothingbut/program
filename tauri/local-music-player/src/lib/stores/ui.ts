/**
 * UI state management stores
 * Handles loading states, error states, success notifications, and user feedback
 */

import { writable, derived, type Readable } from 'svelte/store';
import type { AppError, RecoverableError } from '../errors';

/**
 * Store for global loading state
 */
export const isLoading = writable<boolean>(false);

/**
 * Store for loading message
 */
export const loadingMessage = writable<string>('');

/**
 * Enhanced error state with full error information
 */
export const errorState = writable<{
  hasError: boolean;
  error?: AppError | RecoverableError;
  message?: string;
  details?: string;
}>({
  hasError: false
});

/**
 * Store for success notifications
 */
export const successMessage = writable<{
  message: string;
  timestamp: number;
  id: string;
} | null>(null);

/**
 * Store for confirmation dialogs
 */
export const confirmationDialog = writable<{
  isOpen: boolean;
  title: string;
  message: string;
  confirmText: string;
  cancelText: string;
  onConfirm: () => void | Promise<void>;
  onCancel?: () => void | Promise<void>;
  destructive?: boolean;
} | null>(null);

/**
 * Store for directory scanning state
 */
export const isScanningDirectory = writable<boolean>(false);

/**
 * Store for scanning progress
 */
export const scanningProgress = writable<{
  current: number;
  total: number;
  message: string;
}>({
  current: 0,
  total: 0,
  message: ''
});

/**
 * Store for toast notifications
 */
export const toastNotifications = writable<Array<{
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  timestamp: number;
}>>([]);

/**
 * Derived store for scanning progress percentage
 */
export const scanningProgressPercent: Readable<number> = derived(
  scanningProgress,
  ($progress) => {
    if ($progress.total === 0) return 0;
    return Math.round(($progress.current / $progress.total) * 100);
  }
);

/**
 * Derived store that combines all loading states
 */
export const isAnyLoading: Readable<boolean> = derived(
  [isLoading, isScanningDirectory],
  ([$isLoading, $isScanningDirectory]) => $isLoading || $isScanningDirectory
);

/**
 * Utility functions for UI state management
 */
export const uiActions = {
  /**
   * Set loading state with optional message
   */
  setLoading: (loading: boolean, message: string = '') => {
    isLoading.set(loading);
    loadingMessage.set(message);
  },

  /**
   * Show error with full error object
   */
  showError: (error: AppError | RecoverableError) => {
    errorState.set({
      hasError: true,
      error,
      message: error.userMessage,
      details: error.message
    });
  },

  /**
   * Show simple error message (legacy support)
   */
  showSimpleError: (message: string, details?: string) => {
    errorState.set({
      hasError: true,
      message,
      details
    });
  },

  /**
   * Set error state (legacy support)
   */
  setError: (message: string, details?: string) => {
    errorState.set({
      hasError: true,
      message,
      details
    });
  },

  /**
   * Clear error state
   */
  clearError: () => {
    errorState.set({ hasError: false });
  },

  /**
   * Show success message with auto-clear
   */
  showSuccess: (message: string, duration: number = 3000) => {
    const notification = {
      message,
      timestamp: Date.now(),
      id: `success_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
    
    successMessage.set(notification);
    
    // Auto-clear success message
    setTimeout(() => {
      successMessage.update(current => {
        if (current?.id === notification.id) {
          return null;
        }
        return current;
      });
    }, duration);
  },

  /**
   * Show confirmation dialog
   */
  showConfirmation: (
    title: string,
    message: string,
    onConfirm: () => void | Promise<void>,
    options: {
      confirmText?: string;
      cancelText?: string;
      onCancel?: () => void | Promise<void>;
      destructive?: boolean;
    } = {}
  ) => {
    confirmationDialog.set({
      isOpen: true,
      title,
      message,
      confirmText: options.confirmText || 'Confirm',
      cancelText: options.cancelText || 'Cancel',
      onConfirm,
      onCancel: options.onCancel,
      destructive: options.destructive || false
    });
  },

  /**
   * Close confirmation dialog
   */
  closeConfirmation: () => {
    confirmationDialog.set(null);
  },

  /**
   * Add toast notification
   */
  addToast: (
    message: string,
    type: 'success' | 'error' | 'warning' | 'info' = 'info',
    duration: number = 5000
  ) => {
    const toast = {
      id: `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      message,
      type,
      duration,
      timestamp: Date.now()
    };

    toastNotifications.update(toasts => [...toasts, toast]);

    // Auto-remove toast after duration
    if (duration > 0) {
      setTimeout(() => {
        toastNotifications.update(toasts => 
          toasts.filter(t => t.id !== toast.id)
        );
      }, duration);
    }

    return toast.id;
  },

  /**
   * Remove specific toast
   */
  removeToast: (id: string) => {
    toastNotifications.update(toasts => 
      toasts.filter(t => t.id !== id)
    );
  },

  /**
   * Clear all toasts
   */
  clearToasts: () => {
    toastNotifications.set([]);
  },

  /**
   * Set directory scanning state
   */
  setScanningDirectory: (scanning: boolean) => {
    isScanningDirectory.set(scanning);
    if (!scanning) {
      // Reset progress when scanning stops
      scanningProgress.set({
        current: 0,
        total: 0,
        message: ''
      });
    }
  },

  /**
   * Update scanning progress
   */
  updateScanningProgress: (current: number, total: number, message: string = '') => {
    scanningProgress.set({
      current,
      total,
      message
    });
  },

  /**
   * Clear all UI states
   */
  clearAllStates: () => {
    isLoading.set(false);
    loadingMessage.set('');
    errorState.set({ hasError: false });
    successMessage.set(null);
    confirmationDialog.set(null);
    toastNotifications.set([]);
    isScanningDirectory.set(false);
    scanningProgress.set({
      current: 0,
      total: 0,
      message: ''
    });
  }
};
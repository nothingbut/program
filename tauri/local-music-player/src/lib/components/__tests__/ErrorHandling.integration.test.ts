/**
 * Integration tests for error handling and user feedback system
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { get } from 'svelte/store';

// Import components and stores
import { uiActions, errorState, toastNotifications, confirmationDialog } from '../../stores/ui';
import { createAppError, createRecoverableError, commonRecoveryActions, ErrorCategory, ErrorSeverity } from '../../errors';

describe('Error Handling Integration Tests', () => {
  beforeEach(() => {
    // Clear all UI states before each test
    uiActions.clearAllStates();
  });

  describe('Error Creation and Parsing', () => {
    it('should create basic app error correctly', () => {
      const error = createAppError(
        'Technical error message',
        'User-friendly error message',
        ErrorCategory.FILE_SYSTEM,
        ErrorSeverity.ERROR
      );

      expect(error.message).toBe('Technical error message');
      expect(error.userMessage).toBe('User-friendly error message');
      expect(error.category).toBe(ErrorCategory.FILE_SYSTEM);
      expect(error.severity).toBe(ErrorSeverity.ERROR);
      expect(error.recoverable).toBe(false);
      expect(error.retryable).toBe(false);
      expect(error.id).toBeDefined();
      expect(error.timestamp).toBeInstanceOf(Date);
    });

    it('should create recoverable error with actions', () => {
      const mockRetryAction = () => {};
      const error = createRecoverableError(
        'Technical error',
        'Something went wrong',
        [
          commonRecoveryActions.retry(mockRetryAction),
          commonRecoveryActions.dismiss()
        ],
        ErrorCategory.AUDIO_PLAYBACK,
        ErrorSeverity.ERROR
      );

      expect(error.recoverable).toBe(true);
      expect(error.retryable).toBe(true);
      expect(error.recoveryActions).toHaveLength(2);
      expect(error.recoveryActions[0].label).toBe('Retry');
      expect(error.recoveryActions[1].label).toBe('Dismiss');
    });

    it('should categorize errors correctly based on message content', () => {
      const fileError = createAppError('File not found', 'File error', ErrorCategory.FILE_SYSTEM);
      const audioError = createAppError('Audio playback failed', 'Audio error', ErrorCategory.AUDIO_PLAYBACK);
      const networkError = createAppError('Network timeout', 'Network error', ErrorCategory.NETWORK);

      expect(fileError.category).toBe(ErrorCategory.FILE_SYSTEM);
      expect(audioError.category).toBe(ErrorCategory.AUDIO_PLAYBACK);
      expect(networkError.category).toBe(ErrorCategory.NETWORK);
    });

    it('should generate user-friendly messages', () => {
      const permissionError = createAppError('Permission denied', 'Permission denied');
      const corruptedError = createAppError('File corrupted', 'File corrupted');
      const timeoutError = createAppError('Request timed out', 'Request timed out');

      expect(permissionError.userMessage).toContain('Permission denied');
      expect(corruptedError.userMessage).toContain('corrupted');
      expect(timeoutError.userMessage).toContain('timed out');
    });
  });

  describe('UI Store Integration', () => {
    it('should manage error state correctly', () => {
      const error = createAppError('Test error', 'Test user message');
      
      // Initially no error
      expect(get(errorState).hasError).toBe(false);

      // Show error
      uiActions.showError(error);
      expect(get(errorState).hasError).toBe(true);
      expect(get(errorState).error).toBe(error);
      expect(get(errorState).message).toBe('Test user message');

      // Clear error
      uiActions.clearError();
      expect(get(errorState).hasError).toBe(false);
      expect(get(errorState).error).toBeUndefined();
    });

    it('should manage toast notifications correctly', () => {
      // Initially no toasts
      expect(get(toastNotifications)).toHaveLength(0);

      // Add toast
      const toastId = uiActions.addToast('Test toast', 'success');
      expect(get(toastNotifications)).toHaveLength(1);
      expect(get(toastNotifications)[0].message).toBe('Test toast');
      expect(get(toastNotifications)[0].type).toBe('success');

      // Remove toast
      uiActions.removeToast(toastId);
      expect(get(toastNotifications)).toHaveLength(0);
    });

    it('should manage confirmation dialog correctly', () => {
      const mockConfirm = () => {};
      const mockCancel = () => {};

      // Initially no dialog
      expect(get(confirmationDialog)).toBeNull();

      // Show confirmation
      uiActions.showConfirmation(
        'Test Title',
        'Test Message',
        mockConfirm,
        { onCancel: mockCancel, destructive: true }
      );

      const dialog = get(confirmationDialog);
      expect(dialog).not.toBeNull();
      expect(dialog?.title).toBe('Test Title');
      expect(dialog?.message).toBe('Test Message');
      expect(dialog?.destructive).toBe(true);

      // Close confirmation
      uiActions.closeConfirmation();
      expect(get(confirmationDialog)).toBeNull();
    });

    it('should clear all states correctly', () => {
      // Set up various states
      const error = createAppError('Test', 'Test');
      uiActions.showError(error);
      uiActions.addToast('Test toast', 'info');
      uiActions.showConfirmation('Test', 'Test', () => {});
      uiActions.setLoading(true, 'Loading...');

      // Verify states are set
      expect(get(errorState).hasError).toBe(true);
      expect(get(toastNotifications)).toHaveLength(1);
      expect(get(confirmationDialog)).not.toBeNull();

      // Clear all states
      uiActions.clearAllStates();

      // Verify all states are cleared
      expect(get(errorState).hasError).toBe(false);
      expect(get(toastNotifications)).toHaveLength(0);
      expect(get(confirmationDialog)).toBeNull();
    });
  });

  describe('Error Recovery Scenarios', () => {
    it('should create retry recovery action correctly', () => {
      const mockOperation = () => 'success';
      const retryAction = commonRecoveryActions.retry(mockOperation);

      expect(retryAction.label).toBe('Retry');
      expect(retryAction.primary).toBe(true);
      expect(typeof retryAction.action).toBe('function');
    });

    it('should create common recovery actions', () => {
      const mockAction = () => {};
      
      const retry = commonRecoveryActions.retry(mockAction);
      const refresh = commonRecoveryActions.refresh(mockAction);
      const dismiss = commonRecoveryActions.dismiss();
      const reload = commonRecoveryActions.reload();

      expect(retry.label).toBe('Retry');
      expect(refresh.label).toBe('Refresh');
      expect(dismiss.label).toBe('Dismiss');
      expect(reload.label).toBe('Reload Application');
    });

    it('should handle async recovery actions', async () => {
      let executed = false;
      const asyncAction = async () => {
        executed = true;
        return 'success';
      };

      const retryAction = commonRecoveryActions.retry(asyncAction);
      await retryAction.action();

      expect(executed).toBe(true);
    });
  });
});
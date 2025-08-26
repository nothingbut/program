<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { _ } from 'svelte-i18n';
  import { open } from '@tauri-apps/plugin-dialog';
  import type { Directory } from '../types';
  import { directoryApi, handleApiError, safeApiCall } from '../api';
  import { createRecoverableError, commonRecoveryActions, ErrorCategory, ErrorSeverity } from '../errors';
  import { uiActions } from '../stores/ui';
  import ErrorDisplay from './ErrorDisplay.svelte';
  import ConfirmationDialog from './ConfirmationDialog.svelte';

  // Props
  interface Props {
    directories: Directory[];
    selectedDirectory: Directory | null;
    loading?: boolean;
  }

  let { directories, selectedDirectory, loading = false }: Props = $props();

  // Event dispatcher for parent communication
  const dispatch = createEventDispatcher<{
    directorySelect: { directory: Directory };
    directoryAdd: { directory: Directory };
    directoryRemove: { directory: Directory };
    error: { message: string };
  }>();

  // Local state
  let isAddingDirectory = $state(false);
  let errorMessage = $state<string | null>(null);
  let currentError = $state<any>(null);
  let confirmDialog = $state<{
    isOpen: boolean;
    directory: Directory | null;
    loading: boolean;
  }>({
    isOpen: false,
    directory: null,
    loading: false
  });

  /**
   * Handle adding a new directory with enhanced error handling
   */
  async function handleAddDirectory() {
    if (isAddingDirectory) return;

    try {
      isAddingDirectory = true;
      clearError();

      // Open folder selection dialog
      const selectedPath = await open({
        directory: true,
        multiple: false,
        title: 'Select Music Directory'
      });

      if (selectedPath && typeof selectedPath === 'string') {
        // Add directory via API with safe call
        const result = await safeApiCall(
          () => directoryApi.add(selectedPath),
          { operation: 'add_directory', path: selectedPath }
        );

        if (result.success) {
          // Success - dispatch event and show success message
          dispatch('directoryAdd', { directory: result.data });
          uiActions.addToast(`Directory "${result.data.name}" added successfully`, 'success');
        } else {
          // Handle error with recovery options
          const recoverableError = createRecoverableError(
            result.error.message,
            `Failed to add directory: ${result.error.userMessage}`,
            [
              commonRecoveryActions.retry(() => handleAddDirectory()),
              commonRecoveryActions.dismiss()
            ],
            ErrorCategory.FILE_SYSTEM,
            ErrorSeverity.ERROR,
            { path: selectedPath }
          );
          
          currentError = recoverableError;
          dispatch('error', { message: recoverableError.userMessage });
        }
      }
    } catch (error) {
      // Handle unexpected errors (like dialog cancellation)
      if (error && typeof error === 'object' && 'message' in error) {
        const appError = handleApiError(error, { operation: 'add_directory' });
        currentError = appError;
        errorMessage = appError.userMessage;
        dispatch('error', { message: appError.userMessage });
      }
    } finally {
      isAddingDirectory = false;
    }
  }

  /**
   * Handle directory selection
   */
  function handleDirectorySelect(directory: Directory) {
    if (selectedDirectory?.id === directory.id) return;
    
    dispatch('directorySelect', { directory });
  }

  /**
   * Handle directory removal with confirmation
   */
  function handleRemoveDirectory(directory: Directory, event: Event) {
    event.stopPropagation(); // Prevent directory selection
    
    // Show confirmation dialog
    confirmDialog = {
      isOpen: true,
      directory,
      loading: false
    };
  }

  /**
   * Confirm directory removal
   */
  async function confirmRemoveDirectory() {
    if (!confirmDialog.directory) return;

    const directory = confirmDialog.directory;
    
    try {
      confirmDialog.loading = true;
      
      const result = await safeApiCall(
        () => directoryApi.remove(directory.id),
        { operation: 'remove_directory', directoryId: directory.id, directoryName: directory.name }
      );

      if (result.success) {
        // Success
        dispatch('directoryRemove', { directory });
        uiActions.addToast(`Directory "${directory.name}" removed successfully`, 'success');
        closeConfirmDialog();
      } else {
        // Handle error with recovery options
        const recoverableError = createRecoverableError(
          result.error.message,
          `Failed to remove directory: ${result.error.userMessage}`,
          [
            commonRecoveryActions.retry(() => confirmRemoveDirectory()),
            commonRecoveryActions.dismiss()
          ],
          ErrorCategory.FILE_SYSTEM,
          ErrorSeverity.ERROR,
          { directoryId: directory.id, directoryName: directory.name }
        );
        
        currentError = recoverableError;
        dispatch('error', { message: recoverableError.userMessage });
        closeConfirmDialog();
      }
    } catch (error) {
      const appError = handleApiError(error, { operation: 'remove_directory', directoryId: directory.id });
      currentError = appError;
      errorMessage = appError.userMessage;
      dispatch('error', { message: appError.userMessage });
      closeConfirmDialog();
    } finally {
      confirmDialog.loading = false;
    }
  }

  /**
   * Close confirmation dialog
   */
  function closeConfirmDialog() {
    confirmDialog = {
      isOpen: false,
      directory: null,
      loading: false
    };
  }

  /**
   * Get display name for directory
   */
  function getDirectoryDisplayName(directory: Directory): string {
    return directory.name || directory.path.split('/').pop() || directory.path;
  }

  /**
   * Clear error message
   */
  function clearError() {
    errorMessage = null;
    currentError = null;
  }

  /**
   * Handle error dismissal
   */
  function handleErrorDismiss() {
    clearError();
  }

  /**
   * Handle error recovery
   */
  function handleErrorRecover() {
    clearError();
  }
</script>

<div class="directory-panel">
  <div class="panel-header">
    <h2>{$_('directory.title', { default: 'Music Directories' })}</h2>
    <button 
      class="add-button"
      onclick={handleAddDirectory}
      disabled={isAddingDirectory || loading}
      data-testid="add-directory-btn"
      title={$_('directory.add', { default: 'Add Directory' })}
    >
      {#if isAddingDirectory}
        <span class="loading-spinner"></span>
      {:else}
        +
      {/if}
    </button>
  </div>

  <!-- Enhanced Error Display -->
  {#if currentError}
    <ErrorDisplay
      error={currentError}
      compact={true}
      on:dismiss={handleErrorDismiss}
      on:recover={handleErrorRecover}
    />
  {:else if errorMessage}
    <div class="error-message" data-testid="error-message">
      <span>{errorMessage}</span>
      <button class="error-close" onclick={clearError}>×</button>
    </div>
  {/if}

  <div class="directory-list" data-testid="directory-list">
    {#if loading}
      <div class="loading-state">
        <span class="loading-spinner"></span>
        <span>Loading directories...</span>
      </div>
    {:else if directories.length === 0}
      <div class="empty-state" data-testid="empty-state">
        <p>No music directories added yet.</p>
        <p>Click the "+" button to add your first directory.</p>
      </div>
    {:else}
      {#each directories as directory (directory.id)}
        <div 
          class="directory-item"
          class:selected={selectedDirectory?.id === directory.id}
          onclick={() => handleDirectorySelect(directory)}
          data-testid="directory-item"
          data-directory-id={directory.id}
          role="button"
          tabindex="0"
          onkeydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              handleDirectorySelect(directory);
            }
          }}
        >
          <div class="directory-info">
            <div class="directory-name" title={directory.path}>
              {getDirectoryDisplayName(directory)}
            </div>
            <div class="directory-path">
              {directory.path}
            </div>
          </div>
          <button 
            class="remove-button"
            onclick={(e) => handleRemoveDirectory(directory, e)}
            title="Remove directory"
            data-testid="remove-directory-btn"
          >
            ×
          </button>
        </div>
      {/each}
    {/if}
  </div>
</div>

<!-- Confirmation Dialog -->
<ConfirmationDialog
  isOpen={confirmDialog.isOpen}
  title="Remove Directory"
  message="Are you sure you want to remove '{confirmDialog.directory?.name || 'this directory'}'? This will not delete the files, only remove it from the music player."
  confirmText="Remove"
  cancelText="Cancel"
  destructive={true}
  loading={confirmDialog.loading}
  on:confirm={confirmRemoveDirectory}
  on:cancel={closeConfirmDialog}
  on:close={closeConfirmDialog}
/>

<style>
  .directory-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--bg-secondary, #f8f9fa);
    border-right: 1px solid var(--border-color, #e0e0e0);
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--border-color, #e0e0e0);
    background-color: var(--bg-primary, #ffffff);
  }

  .panel-header h2 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary, #333333);
  }

  .add-button {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 50%;
    background-color: var(--accent-color, #007bff);
    color: white;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .add-button:hover:not(:disabled) {
    background-color: var(--accent-hover, #0056b3);
    transform: scale(1.05);
  }

  .add-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .error-message {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background-color: var(--error-bg, #fee);
    color: var(--error-text, #c33);
    border-bottom: 1px solid var(--error-border, #fcc);
    font-size: 0.9rem;
  }

  .error-close {
    background: none;
    border: none;
    color: var(--error-text, #c33);
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .directory-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
  }

  .loading-state, .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    text-align: center;
    color: var(--text-secondary, #666666);
  }

  .empty-state p {
    margin: 0.5rem 0;
  }

  .directory-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem;
    margin-bottom: 0.25rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    background-color: var(--bg-primary, #ffffff);
    border: 1px solid transparent;
  }

  .directory-item:hover {
    background-color: var(--bg-hover, #f0f0f0);
    border-color: var(--border-hover, #d0d0d0);
  }

  .directory-item.selected {
    background-color: var(--accent-light, #e3f2fd);
    border-color: var(--accent-color, #007bff);
    color: var(--accent-color, #007bff);
  }

  .directory-item:focus {
    outline: 2px solid var(--accent-color, #007bff);
    outline-offset: 2px;
  }

  .directory-info {
    flex: 1;
    min-width: 0; /* Allow text truncation */
  }

  .directory-name {
    font-weight: 500;
    font-size: 0.95rem;
    margin-bottom: 0.25rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .directory-path {
    font-size: 0.8rem;
    color: var(--text-secondary, #666666);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .remove-button {
    width: 24px;
    height: 24px;
    border: none;
    border-radius: 50%;
    background-color: var(--danger-color, #dc3545);
    color: white;
    font-size: 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: all 0.2s ease;
    margin-left: 0.5rem;
  }

  .directory-item:hover .remove-button {
    opacity: 1;
  }

  .remove-button:hover {
    background-color: var(--danger-hover, #c82333);
    transform: scale(1.1);
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .directory-panel {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --bg-hover: #4a5568;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --border-hover: #718096;
      --accent-color: #4299e1;
      --accent-hover: #3182ce;
      --accent-light: #2d3748;
      --error-bg: #742a2a;
      --error-text: #feb2b2;
      --error-border: #c53030;
      --danger-color: #e53e3e;
      --danger-hover: #c53030;
    }
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .panel-header {
      padding: 0.75rem;
    }
    
    .directory-item {
      padding: 0.5rem;
    }
    
    .directory-name {
      font-size: 0.9rem;
    }
    
    .directory-path {
      font-size: 0.75rem;
    }
  }
</style>
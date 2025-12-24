<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { AppError, RecoverableError } from '../errors';

  // Props
  interface Props {
    error: AppError | RecoverableError | null;
    showDetails?: boolean;
    compact?: boolean;
  }

  let {
    error = null,
    showDetails = false,
    compact = false
  }: Props = $props();

  // Events
  const dispatch = createEventDispatcher<{
    dismiss: void;
    retry: void;
    recover: { action: () => Promise<void> | void };
  }>();

  // Local state
  let showErrorDetails = $state(false);
  let isExecutingRecovery = $state(false);

  // Derived values
  const isRecoverable = $derived(error && 'recoveryActions' in error);
  const recoveryActions = $derived(isRecoverable ? (error as RecoverableError).recoveryActions : []);

  /**
   * Handle dismiss action
   */
  function handleDismiss() {
    dispatch('dismiss');
  }

  /**
   * Handle retry action
   */
  function handleRetry() {
    dispatch('retry');
  }

  /**
   * Handle recovery action
   */
  async function handleRecoveryAction(action: () => Promise<void> | void) {
    if (isExecutingRecovery) return;

    try {
      isExecutingRecovery = true;
      await action();
      dispatch('recover', { action });
    } catch (recoveryError) {
      console.error('Recovery action failed:', recoveryError);
      // The parent component should handle this error
    } finally {
      isExecutingRecovery = false;
    }
  }

  /**
   * Toggle error details
   */
  function toggleDetails() {
    showErrorDetails = !showErrorDetails;
  }

  /**
   * Get severity icon
   */
  function getSeverityIcon(severity: string): string {
    switch (severity) {
      case 'critical': return '🚨';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '❌';
    }
  }

  /**
   * Get severity color class
   */
  function getSeverityClass(severity: string): string {
    switch (severity) {
      case 'critical': return 'critical';
      case 'error': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'error';
    }
  }

  /**
   * Format timestamp
   */
  function formatTimestamp(timestamp: Date): string {
    return timestamp.toLocaleTimeString();
  }
</script>

{#if error}
  <div 
    class="error-display"
    class:compact
    class:recoverable={isRecoverable}
    class:executing-recovery={isExecutingRecovery}
    data-testid="error-display"
    data-severity={error.severity}
  >
    <!-- Main Error Content -->
    <div class="error-content">
      <!-- Error Header -->
      <div class="error-header">
        <div class="error-icon-message">
          <span class="error-icon" aria-hidden="true">
            {getSeverityIcon(error.severity)}
          </span>
          <div class="error-text">
            <div class="error-message">{error.userMessage}</div>
            {#if !compact}
              <div class="error-meta">
                <span class="error-category">{error.category}</span>
                <span class="error-time">{formatTimestamp(error.timestamp)}</span>
              </div>
            {/if}
          </div>
        </div>

        <div class="error-actions">
          {#if showDetails || error.context}
            <button
              class="details-toggle"
              onclick={toggleDetails}
              aria-expanded={showErrorDetails}
              title="Toggle error details"
              data-testid="details-toggle"
            >
              {showErrorDetails ? '▼' : '▶'}
            </button>
          {/if}
          
          <button
            class="dismiss-button"
            onclick={handleDismiss}
            title="Dismiss error"
            data-testid="dismiss-button"
          >
            ×
          </button>
        </div>
      </div>

      <!-- Error Details (Expandable) -->
      {#if showErrorDetails && (showDetails || error.context)}
        <div class="error-details" data-testid="error-details">
          {#if error.message !== error.userMessage}
            <div class="detail-section">
              <strong>Technical Details:</strong>
              <pre class="technical-message">{error.message}</pre>
            </div>
          {/if}

          {#if error.context}
            <div class="detail-section">
              <strong>Context:</strong>
              <pre class="context-data">{JSON.stringify(error.context, null, 2)}</pre>
            </div>
          {/if}

          <div class="detail-section">
            <strong>Error ID:</strong> <code>{error.id}</code>
          </div>
        </div>
      {/if}

      <!-- Recovery Actions -->
      {#if isRecoverable && recoveryActions.length > 0}
        <div class="recovery-actions" data-testid="recovery-actions">
          <div class="recovery-label">Available actions:</div>
          <div class="recovery-buttons">
            {#each recoveryActions as action, index}
              <button
                class="recovery-button"
                class:primary={action.primary}
                onclick={() => handleRecoveryAction(action.action)}
                disabled={isExecutingRecovery}
                data-testid="recovery-action-{index}"
              >
                {#if isExecutingRecovery}
                  <span class="loading-spinner"></span>
                {/if}
                {action.label}
              </button>
            {/each}
          </div>
        </div>
      {:else if error.retryable}
        <div class="recovery-actions">
          <button
            class="recovery-button primary"
            onclick={handleRetry}
            disabled={isExecutingRecovery}
            data-testid="retry-button"
          >
            {#if isExecutingRecovery}
              <span class="loading-spinner"></span>
            {/if}
            Retry
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .error-display {
    border-radius: 6px;
    border-left: 4px solid;
    background-color: var(--error-bg, #fee);
    color: var(--error-text, #c33);
    border-left-color: var(--error-border, #fcc);
    margin-bottom: 1rem;
    overflow: hidden;
    transition: all 0.2s ease;
  }

  .error-display.compact {
    margin-bottom: 0.5rem;
  }

  .error-display.executing-recovery {
    opacity: 0.8;
    pointer-events: none;
  }

  /* Severity-based styling */
  .error-display[data-severity="critical"] {
    background-color: var(--critical-bg, #4a0e0e);
    color: var(--critical-text, #ff6b6b);
    border-left-color: var(--critical-border, #ff0000);
  }

  .error-display[data-severity="error"] {
    background-color: var(--error-bg, #fee);
    color: var(--error-text, #c33);
    border-left-color: var(--error-border, #fcc);
  }

  .error-display[data-severity="warning"] {
    background-color: var(--warning-bg, #fff3cd);
    color: var(--warning-text, #856404);
    border-left-color: var(--warning-border, #ffc107);
  }

  .error-display[data-severity="info"] {
    background-color: var(--info-bg, #d1ecf1);
    color: var(--info-text, #0c5460);
    border-left-color: var(--info-border, #17a2b8);
  }

  .error-content {
    padding: 1rem;
  }

  .error-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }

  .error-icon-message {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    flex: 1;
    min-width: 0;
  }

  .error-icon {
    font-size: 1.2rem;
    flex-shrink: 0;
    margin-top: 0.1rem;
  }

  .error-text {
    flex: 1;
    min-width: 0;
  }

  .error-message {
    font-weight: 500;
    line-height: 1.4;
    margin-bottom: 0.25rem;
    word-break: break-word;
  }

  .error-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.8rem;
    opacity: 0.8;
  }

  .error-category {
    text-transform: capitalize;
    font-weight: 500;
  }

  .error-time {
    font-family: monospace;
  }

  .error-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-shrink: 0;
  }

  .details-toggle,
  .dismiss-button {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 3px;
    font-size: 1rem;
    line-height: 1;
    transition: background-color 0.2s ease;
  }

  .details-toggle:hover,
  .dismiss-button:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }

  .dismiss-button {
    font-size: 1.2rem;
  }

  .error-details {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
  }

  .detail-section {
    margin-bottom: 0.75rem;
  }

  .detail-section:last-child {
    margin-bottom: 0;
  }

  .detail-section strong {
    display: block;
    margin-bottom: 0.25rem;
    font-size: 0.9rem;
  }

  .technical-message,
  .context-data {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-family: monospace;
    white-space: pre-wrap;
    word-break: break-word;
    margin: 0;
    overflow-x: auto;
  }

  .recovery-actions {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
  }

  .recovery-label {
    font-size: 0.9rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
  }

  .recovery-buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .recovery-button {
    padding: 0.5rem 1rem;
    border: 1px solid rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    background-color: rgba(255, 255, 255, 0.8);
    color: inherit;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .recovery-button:hover:not(:disabled) {
    background-color: rgba(255, 255, 255, 0.9);
    border-color: rgba(0, 0, 0, 0.3);
  }

  .recovery-button.primary {
    background-color: var(--accent-color, #007bff);
    color: white;
    border-color: var(--accent-color, #007bff);
  }

  .recovery-button.primary:hover:not(:disabled) {
    background-color: var(--accent-hover, #0056b3);
    border-color: var(--accent-hover, #0056b3);
  }

  .recovery-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .loading-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Compact mode */
  .error-display.compact .error-content {
    padding: 0.75rem;
  }

  .error-display.compact .error-message {
    font-size: 0.9rem;
  }

  .error-display.compact .recovery-actions {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .error-display {
      --error-bg: #2d1b1b;
      --error-text: #feb2b2;
      --error-border: #c53030;
      --warning-bg: #2d2a1b;
      --warning-text: #fbd38d;
      --warning-border: #ed8936;
      --info-bg: #1b2d2d;
      --info-text: #81e6d9;
      --info-border: #4fd1c7;
      --critical-bg: #1a0a0a;
      --critical-text: #ff9999;
      --critical-border: #ff4444;
      --accent-color: #4299e1;
      --accent-hover: #3182ce;
    }

    .technical-message,
    .context-data {
      background-color: rgba(255, 255, 255, 0.05);
    }

    .recovery-button {
      background-color: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .recovery-button:hover:not(:disabled) {
      background-color: rgba(255, 255, 255, 0.15);
      border-color: rgba(255, 255, 255, 0.3);
    }

    .details-toggle:hover,
    .dismiss-button:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }
  }

  /* Responsive design */
  @media (max-width: 480px) {
    .error-header {
      flex-direction: column;
      align-items: stretch;
      gap: 0.75rem;
    }

    .error-actions {
      justify-content: flex-end;
    }

    .recovery-buttons {
      flex-direction: column;
    }

    .recovery-button {
      width: 100%;
      justify-content: center;
    }
  }

  /* High contrast mode */
  @media (prefers-contrast: high) {
    .error-display {
      border: 2px solid;
      border-left-width: 6px;
    }

    .recovery-button {
      border-width: 2px;
    }
  }

  /* Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    .error-display {
      transition: none;
    }

    .loading-spinner {
      animation: none;
    }

    .recovery-button,
    .details-toggle,
    .dismiss-button {
      transition: none;
    }
  }
</style>
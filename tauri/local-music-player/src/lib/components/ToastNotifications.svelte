<script lang="ts">
  import { toastNotifications, uiActions } from '../stores/ui';
  import { fly } from 'svelte/transition';

  // Reactive values
  const toasts = $derived($toastNotifications);

  /**
   * Remove a toast notification
   */
  function removeToast(id: string) {
    uiActions.removeToast(id);
  }

  /**
   * Get icon for toast type
   */
  function getToastIcon(type: string): string {
    switch (type) {
      case 'success': return '✓';
      case 'error': return '✕';
      case 'warning': return '⚠';
      case 'info': return 'ℹ';
      default: return 'ℹ';
    }
  }

  /**
   * Handle toast click (dismiss)
   */
  function handleToastClick(id: string) {
    removeToast(id);
  }

  /**
   * Handle keyboard interaction
   */
  function handleKeydown(event: KeyboardEvent, id: string) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      removeToast(id);
    }
  }
</script>

<div class="toast-container" data-testid="toast-container">
  {#each toasts as toast (toast.id)}
    <div
      class="toast toast-{toast.type}"
      role="button"
      aria-live="polite"
      onclick={() => handleToastClick(toast.id)}
      onkeydown={(e) => handleKeydown(e, toast.id)}
      transition:fly={{ y: -50, duration: 300 }}
      tabindex="0"
      aria-label="Dismiss notification"
      data-testid="toast-{toast.type}"
    >
      <div class="toast-content">
        <span class="toast-icon" aria-hidden="true">
          {getToastIcon(toast.type)}
        </span>
        <span class="toast-message">{toast.message}</span>
      </div>
      <button
        class="toast-close"
        onclick={(e) => {
          e.stopPropagation();
          removeToast(toast.id);
        }}
        aria-label="Dismiss notification"
        data-testid="toast-close"
      >
        ×
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-width: 400px;
    pointer-events: none;
  }

  .toast {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    pointer-events: auto;
    transition: all 0.2s ease;
    border-left: 4px solid;
    background-color: var(--bg-primary, #ffffff);
    color: var(--text-primary, #333333);
    min-width: 300px;
  }

  .toast:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  .toast:focus {
    outline: 2px solid var(--accent-color, #007bff);
    outline-offset: 2px;
  }

  .toast-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
    min-width: 0;
  }

  .toast-icon {
    font-size: 1.1rem;
    font-weight: bold;
    flex-shrink: 0;
    width: 20px;
    text-align: center;
  }

  .toast-message {
    flex: 1;
    font-size: 0.9rem;
    line-height: 1.4;
    word-break: break-word;
  }

  .toast-close {
    background: none;
    border: none;
    color: inherit;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 3px;
    line-height: 1;
    opacity: 0.7;
    transition: opacity 0.2s ease;
    flex-shrink: 0;
    margin-left: 0.5rem;
  }

  .toast-close:hover {
    opacity: 1;
    background-color: rgba(0, 0, 0, 0.1);
  }

  /* Toast type styles */
  .toast-success {
    border-left-color: var(--success-color, #28a745);
    background-color: var(--success-bg, #d4edda);
    color: var(--success-text, #155724);
  }

  .toast-success .toast-icon {
    color: var(--success-color, #28a745);
  }

  .toast-error {
    border-left-color: var(--danger-color, #dc3545);
    background-color: var(--error-bg, #f8d7da);
    color: var(--error-text, #721c24);
  }

  .toast-error .toast-icon {
    color: var(--danger-color, #dc3545);
  }

  .toast-warning {
    border-left-color: var(--warning-color, #ffc107);
    background-color: var(--warning-bg, #fff3cd);
    color: var(--warning-text, #856404);
  }

  .toast-warning .toast-icon {
    color: var(--warning-color, #ffc107);
  }

  .toast-info {
    border-left-color: var(--info-color, #17a2b8);
    background-color: var(--info-bg, #d1ecf1);
    color: var(--info-text, #0c5460);
  }

  .toast-info .toast-icon {
    color: var(--info-color, #17a2b8);
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .toast {
      --bg-primary: #2d3748;
      --text-primary: #f7fafc;
      --success-bg: #1a2e1a;
      --success-text: #68d391;
      --success-color: #48bb78;
      --error-bg: #2d1b1b;
      --error-text: #feb2b2;
      --danger-color: #e53e3e;
      --warning-bg: #2d2a1b;
      --warning-text: #fbd38d;
      --warning-color: #ed8936;
      --info-bg: #1b2d2d;
      --info-text: #81e6d9;
      --info-color: #4fd1c7;
    }

    .toast-close:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }
  }

  /* Responsive design */
  @media (max-width: 480px) {
    .toast-container {
      top: 0.5rem;
      right: 0.5rem;
      left: 0.5rem;
      max-width: none;
    }

    .toast {
      min-width: 0;
      width: 100%;
    }

    .toast-message {
      font-size: 0.85rem;
    }
  }

  /* High contrast mode */
  @media (prefers-contrast: high) {
    .toast {
      border: 2px solid;
      border-left-width: 6px;
    }

    .toast-success {
      border-color: var(--success-color, #28a745);
    }

    .toast-error {
      border-color: var(--danger-color, #dc3545);
    }

    .toast-warning {
      border-color: var(--warning-color, #ffc107);
    }

    .toast-info {
      border-color: var(--info-color, #17a2b8);
    }
  }

  /* Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    .toast {
      transition: none;
    }

    .toast:hover {
      transform: none;
    }

    .toast-close {
      transition: none;
    }
  }

  /* Print styles */
  @media print {
    .toast-container {
      display: none;
    }
  }
</style>
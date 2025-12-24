<script lang="ts">
  import { createEventDispatcher } from "svelte";

  // Props
  interface Props {
    isOpen: boolean;
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    destructive?: boolean;
    loading?: boolean;
  }

  let {
    isOpen = false,
    title,
    message,
    confirmText = "Confirm",
    cancelText = "Cancel",
    destructive = false,
    loading = false,
  }: Props = $props();

  // Events
  const dispatch = createEventDispatcher<{
    confirm: void;
    cancel: void;
    close: void;
  }>();

  // Local state
  let dialogElement = $state<HTMLDialogElement>();

  // Handle dialog open/close
  $effect(() => {
    if (dialogElement) {
      if (isOpen && !dialogElement.open) {
        dialogElement.showModal();
      } else if (!isOpen && dialogElement.open) {
        dialogElement.close();
      }
    }
  });

  /**
   * Handle confirm action
   */
  function handleConfirm() {
    if (loading) return;
    dispatch("confirm");
  }

  /**
   * Handle cancel action
   */
  function handleCancel() {
    if (loading) return;
    dispatch("cancel");
  }

  /**
   * Handle dialog close (backdrop click or ESC)
   */
  function handleClose() {
    if (loading) return;
    dispatch("close");
  }

  /**
   * Handle keyboard events
   */
  function handleKeydown(event: KeyboardEvent) {
    if (loading) return;

    if (event.key === "Escape") {
      event.preventDefault();
      handleCancel();
    } else if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      handleConfirm();
    }
  }

  /**
   * Handle backdrop click
   */
  function handleBackdropClick(event: MouseEvent) {
    if (loading) return;

    if (event.target === dialogElement) {
      handleClose();
    }
  }
</script>

<dialog
  bind:this={dialogElement}
  class="confirmation-dialog"
  class:destructive
  class:loading
  onclose={handleClose}
  onkeydown={handleKeydown}
  onclick={handleBackdropClick}
  data-testid="confirmation-dialog"
>
  <div
    class="dialog-content"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => {
      if (e.key === "Escape") {
        handleCancel();
      }
    }}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
  >
    <!-- Header -->
    <div class="dialog-header">
      <h2 class="dialog-title">{title}</h2>
      {#if !loading}
        <button
          class="close-button"
          onclick={handleCancel}
          aria-label="Close dialog"
          data-testid="close-button"
        >
          ×
        </button>
      {/if}
    </div>

    <!-- Body -->
    <div class="dialog-body">
      <p class="dialog-message">{message}</p>
    </div>

    <!-- Footer -->
    <div class="dialog-footer">
      <button
        class="cancel-button"
        onclick={handleCancel}
        disabled={loading}
        data-testid="cancel-button"
      >
        {cancelText}
      </button>
      <button
        class="confirm-button"
        class:destructive
        onclick={handleConfirm}
        disabled={loading}
        data-testid="confirm-button"
      >
        {#if loading}
          <span class="loading-spinner"></span>
        {/if}
        {confirmText}
      </button>
    </div>
  </div>
</dialog>

<style>
  .confirmation-dialog {
    padding: 0;
    border: none;
    border-radius: 8px;
    background: transparent;
    max-width: 500px;
    width: 90vw;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }

  .confirmation-dialog::backdrop {
    background-color: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(2px);
  }

  .dialog-content {
    background-color: var(--bg-primary, #ffffff);
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .dialog-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 1.5rem 0;
  }

  .dialog-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary, #333333);
  }

  .close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: var(--text-secondary, #666666);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    line-height: 1;
    transition: all 0.2s ease;
  }

  .close-button:hover {
    background-color: var(--bg-hover, #f0f0f0);
    color: var(--text-primary, #333333);
  }

  .dialog-body {
    padding: 1rem 1.5rem;
  }

  .dialog-message {
    margin: 0;
    color: var(--text-primary, #333333);
    line-height: 1.5;
  }

  .dialog-footer {
    display: flex;
    gap: 0.75rem;
    padding: 0 1.5rem 1.5rem;
    justify-content: flex-end;
  }

  .cancel-button,
  .confirm-button {
    padding: 0.75rem 1.5rem;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 80px;
    justify-content: center;
  }

  .cancel-button {
    background-color: var(--bg-secondary, #f8f9fa);
    color: var(--text-primary, #333333);
  }

  .cancel-button:hover:not(:disabled) {
    background-color: var(--bg-hover, #f0f0f0);
    border-color: var(--border-hover, #d0d0d0);
  }

  .confirm-button {
    background-color: var(--accent-color, #007bff);
    color: white;
    border-color: var(--accent-color, #007bff);
  }

  .confirm-button:hover:not(:disabled) {
    background-color: var(--accent-hover, #0056b3);
    border-color: var(--accent-hover, #0056b3);
  }

  .confirm-button.destructive {
    background-color: var(--danger-color, #dc3545);
    border-color: var(--danger-color, #dc3545);
  }

  .confirm-button.destructive:hover:not(:disabled) {
    background-color: var(--danger-hover, #c82333);
    border-color: var(--danger-hover, #c82333);
  }

  .cancel-button:disabled,
  .confirm-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  /* Destructive dialog styling */
  .confirmation-dialog.destructive .dialog-title {
    color: var(--danger-color, #dc3545);
  }

  /* Loading state */
  .confirmation-dialog.loading {
    pointer-events: none;
  }

  .confirmation-dialog.loading .dialog-content {
    opacity: 0.8;
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .confirmation-dialog {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --bg-hover: #4a5568;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --border-hover: #718096;
      --accent-color: #4299e1;
      --accent-hover: #3182ce;
      --danger-color: #e53e3e;
      --danger-hover: #c53030;
    }

    .confirmation-dialog::backdrop {
      background-color: rgba(0, 0, 0, 0.7);
    }
  }

  /* Responsive design */
  @media (max-width: 480px) {
    .confirmation-dialog {
      width: 95vw;
      max-width: none;
    }

    .dialog-header,
    .dialog-body,
    .dialog-footer {
      padding-left: 1rem;
      padding-right: 1rem;
    }

    .dialog-footer {
      flex-direction: column-reverse;
    }

    .cancel-button,
    .confirm-button {
      width: 100%;
    }
  }

  /* High contrast mode */
  @media (prefers-contrast: high) {
    .confirmation-dialog {
      --border-color: #000000;
      --border-hover: #333333;
    }

    .dialog-content {
      border: 2px solid var(--border-color);
    }
  }

  /* Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    .loading-spinner {
      animation: none;
    }

    .cancel-button,
    .confirm-button,
    .close-button {
      transition: none;
    }
  }
</style>

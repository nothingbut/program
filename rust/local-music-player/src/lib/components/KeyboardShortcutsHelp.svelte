<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { shortcutsByCategory, formatShortcut } from '../stores/keyboard';

  // Props
  interface Props {
    isOpen: boolean;
  }

  let { isOpen }: Props = $props();

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    close: void;
  }>();

  /**
   * Handle close button click
   */
  function handleClose() {
    dispatch('close');
  }

  /**
   * Handle overlay click
   */
  function handleOverlayClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  }

  /**
   * Handle escape key
   */
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      handleClose();
    }
  }
</script>

{#if isOpen}
  <div 
    class="shortcuts-overlay"
    onclick={handleOverlayClick}
    onkeydown={handleKeyDown}
    data-testid="shortcuts-overlay"
    role="dialog"
    aria-modal="true"
    aria-labelledby="shortcuts-title"
  >
    <div class="shortcuts-modal">
      <div class="modal-header">
        <h2 id="shortcuts-title">Keyboard Shortcuts</h2>
        <button 
          class="close-button"
          onclick={handleClose}
          aria-label="Close shortcuts help"
          data-testid="close-shortcuts-button"
        >
          ×
        </button>
      </div>

      <div class="modal-content">
        {#each Object.entries($shortcutsByCategory) as [category, shortcuts]}
          {#if shortcuts.length > 0}
            <div class="shortcut-category">
              <h3 class="category-title">
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </h3>
              
              <div class="shortcuts-list">
                {#each shortcuts as shortcut}
                  <div class="shortcut-item">
                    <div class="shortcut-keys">
                      {formatShortcut(shortcut)}
                    </div>
                    <div class="shortcut-description">
                      {shortcut.description}
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        {/each}
      </div>

      <div class="modal-footer">
        <p class="footer-note">
          Press <kbd>?</kbd> or <kbd>F1</kbd> to toggle this help
        </p>
      </div>
    </div>
  </div>
{/if}

<style>
  .shortcuts-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(3px);
  }

  .shortcuts-modal {
    background-color: var(--bg-primary, #ffffff);
    border-radius: 8px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    max-width: 600px;
    width: 90vw;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--border-color, #e0e0e0);
    background-color: var(--bg-secondary, #f8f9fa);
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary, #333333);
  }

  .close-button {
    background: none;
    border: none;
    font-size: 2rem;
    color: var(--text-secondary, #666666);
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s ease;
  }

  .close-button:hover {
    background-color: var(--bg-hover, #f0f0f0);
    color: var(--text-primary, #333333);
  }

  .modal-content {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem 2rem;
  }

  .shortcut-category {
    margin-bottom: 2rem;
  }

  .shortcut-category:last-child {
    margin-bottom: 0;
  }

  .category-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent-color, #007bff);
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent-light, #e3f2fd);
  }

  .shortcuts-list {
    display: grid;
    gap: 0.75rem;
  }

  .shortcut-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem;
    background-color: var(--bg-secondary, #f8f9fa);
    border-radius: 6px;
    border: 1px solid var(--border-light, #f0f0f0);
    transition: all 0.2s ease;
  }

  .shortcut-item:hover {
    background-color: var(--bg-hover, #e9ecef);
    border-color: var(--border-color, #e0e0e0);
  }

  .shortcut-keys {
    font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--accent-color, #007bff);
    background-color: var(--bg-primary, #ffffff);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    border: 1px solid var(--border-color, #e0e0e0);
    min-width: 80px;
    text-align: center;
  }

  .shortcut-description {
    flex: 1;
    margin-left: 1rem;
    color: var(--text-primary, #333333);
    font-size: 0.95rem;
  }

  .modal-footer {
    padding: 1rem 2rem;
    border-top: 1px solid var(--border-color, #e0e0e0);
    background-color: var(--bg-secondary, #f8f9fa);
    text-align: center;
  }

  .footer-note {
    margin: 0;
    font-size: 0.85rem;
    color: var(--text-secondary, #666666);
  }

  .footer-note kbd {
    background-color: var(--bg-primary, #ffffff);
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 3px;
    padding: 0.1rem 0.3rem;
    font-family: inherit;
    font-size: 0.8rem;
    color: var(--text-primary, #333333);
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .shortcuts-modal {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --bg-hover: #4a5568;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --border-light: #2d3748;
      --accent-color: #4299e1;
      --accent-light: #2d3748;
    }
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .shortcuts-modal {
      width: 95vw;
      max-height: 90vh;
    }

    .modal-header {
      padding: 1rem 1.5rem;
    }

    .modal-header h2 {
      font-size: 1.25rem;
    }

    .modal-content {
      padding: 1rem 1.5rem;
    }

    .shortcut-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .shortcut-description {
      margin-left: 0;
    }

    .shortcut-keys {
      min-width: auto;
      align-self: flex-end;
    }
  }

  @media (max-width: 480px) {
    .modal-header {
      padding: 0.75rem 1rem;
    }

    .modal-content {
      padding: 0.75rem 1rem;
    }

    .modal-footer {
      padding: 0.75rem 1rem;
    }

    .shortcut-category {
      margin-bottom: 1.5rem;
    }

    .category-title {
      font-size: 1rem;
    }
  }
</style>
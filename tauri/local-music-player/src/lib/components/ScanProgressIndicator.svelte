<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  // Props
  interface Props {
    isScanning: boolean;
    progress: number;
    currentFile?: string;
    totalFiles?: number;
    scannedFiles?: number;
    directoryName?: string;
  }

  let { 
    isScanning, 
    progress, 
    currentFile, 
    totalFiles, 
    scannedFiles, 
    directoryName 
  }: Props = $props();

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    cancel: void;
  }>();

  // Computed values
  const progressPercent = $derived(Math.round(progress * 100));
  const hasFileInfo = $derived(totalFiles !== undefined && scannedFiles !== undefined);
  const progressText = $derived(() => {
    if (hasFileInfo) {
      return `${scannedFiles}/${totalFiles} files`;
    }
    return `${progressPercent}%`;
  });

  /**
   * Handle cancel button click
   */
  function handleCancel() {
    dispatch('cancel');
  }

  /**
   * Get truncated file name for display
   */
  function getTruncatedFileName(filePath: string, maxLength: number = 50): string {
    if (!filePath) return '';
    
    const fileName = filePath.split('/').pop() || filePath;
    if (fileName.length <= maxLength) return fileName;
    
    const extension = fileName.split('.').pop();
    const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
    const truncatedName = nameWithoutExt.substring(0, maxLength - extension!.length - 4) + '...';
    
    return `${truncatedName}.${extension}`;
  }
</script>

{#if isScanning}
  <div class="scan-progress-overlay" data-testid="scan-progress-overlay">
    <div class="progress-modal">
      <div class="progress-header">
        <h3>Scanning Directory</h3>
        {#if directoryName}
          <p class="directory-name">{directoryName}</p>
        {/if}
      </div>

      <div class="progress-content">
        <!-- Progress Bar -->
        <div class="progress-bar-container">
          <div class="progress-bar">
            <div 
              class="progress-fill"
              style="width: {progressPercent}%"
            ></div>
          </div>
          <div class="progress-text">
            {progressText}
          </div>
        </div>

        <!-- Current File Info -->
        {#if currentFile}
          <div class="current-file">
            <div class="file-label">Processing:</div>
            <div class="file-name" title={currentFile}>
              {getTruncatedFileName(currentFile)}
            </div>
          </div>
        {/if}

        <!-- Detailed Progress Info -->
        {#if hasFileInfo}
          <div class="progress-details">
            <div class="detail-item">
              <span class="detail-label">Files found:</span>
              <span class="detail-value">{totalFiles}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Processed:</span>
              <span class="detail-value">{scannedFiles}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Remaining:</span>
              <span class="detail-value">{totalFiles! - scannedFiles!}</span>
            </div>
          </div>
        {/if}
      </div>

      <div class="progress-actions">
        <button 
          class="cancel-button"
          onclick={handleCancel}
          data-testid="cancel-scan-button"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .scan-progress-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
  }

  .progress-modal {
    background-color: var(--bg-primary, #ffffff);
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    padding: 2rem;
    min-width: 400px;
    max-width: 500px;
    width: 90vw;
    max-height: 80vh;
    overflow-y: auto;
  }

  .progress-header {
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .progress-header h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary, #333333);
  }

  .directory-name {
    margin: 0;
    font-size: 0.9rem;
    color: var(--text-secondary, #666666);
    word-break: break-all;
  }

  .progress-content {
    margin-bottom: 1.5rem;
  }

  .progress-bar-container {
    margin-bottom: 1rem;
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background-color: var(--border-color, #e0e0e0);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-color, #007bff), var(--accent-hover, #0056b3));
    border-radius: 4px;
    transition: width 0.3s ease;
    position: relative;
  }

  .progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.3),
      transparent
    );
    animation: shimmer 2s infinite;
  }

  @keyframes shimmer {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(100%);
    }
  }

  .progress-text {
    text-align: center;
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--text-primary, #333333);
  }

  .current-file {
    background-color: var(--bg-secondary, #f8f9fa);
    border-radius: 4px;
    padding: 0.75rem;
    margin-bottom: 1rem;
  }

  .file-label {
    font-size: 0.8rem;
    color: var(--text-secondary, #666666);
    margin-bottom: 0.25rem;
    font-weight: 500;
  }

  .file-name {
    font-size: 0.9rem;
    color: var(--text-primary, #333333);
    font-family: monospace;
    word-break: break-all;
  }

  .progress-details {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
    padding: 1rem;
    background-color: var(--bg-secondary, #f8f9fa);
    border-radius: 4px;
    border: 1px solid var(--border-color, #e0e0e0);
  }

  .detail-item {
    text-align: center;
  }

  .detail-label {
    display: block;
    font-size: 0.8rem;
    color: var(--text-secondary, #666666);
    margin-bottom: 0.25rem;
  }

  .detail-value {
    display: block;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary, #333333);
  }

  .progress-actions {
    display: flex;
    justify-content: center;
  }

  .cancel-button {
    padding: 0.75rem 1.5rem;
    background-color: var(--error-bg, #dc3545);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .cancel-button:hover {
    background-color: var(--error-hover, #c82333);
    transform: translateY(-1px);
  }

  .cancel-button:active {
    transform: translateY(0);
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .progress-modal {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --accent-color: #4299e1;
      --accent-hover: #3182ce;
      --error-bg: #e53e3e;
      --error-hover: #c53030;
    }
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .progress-modal {
      min-width: 300px;
      padding: 1.5rem;
    }

    .progress-details {
      grid-template-columns: 1fr;
      gap: 0.75rem;
    }

    .detail-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      text-align: left;
    }

    .detail-label {
      margin-bottom: 0;
    }
  }

  @media (max-width: 480px) {
    .progress-modal {
      min-width: 280px;
      padding: 1rem;
    }

    .progress-header h3 {
      font-size: 1.1rem;
    }

    .directory-name {
      font-size: 0.8rem;
    }
  }
</style>
<script lang="ts">
  import { validateAudioFile, formatAudioDiagnostics, type AudioFileInfo } from '../utils/audioDebug';
  import type { Track } from '../types';

  interface Props {
    track: Track | null;
    visible?: boolean;
  }

  let { track, visible = false }: Props = $props();

  let diagnostics = $state<AudioFileInfo | null>(null);
  let isValidating = $state(false);

  /**
   * Validate the current track
   */
  async function validateTrack() {
    if (!track) return;

    isValidating = true;
    try {
      diagnostics = await validateAudioFile(track.filePath);
    } catch (error) {
      diagnostics = {
        path: track.filePath,
        exists: false,
        isValid: false,
        error: error instanceof Error ? error.message : String(error),
      };
    } finally {
      isValidating = false;
    }
  }

  /**
   * Clear diagnostics
   */
  function clearDiagnostics() {
    diagnostics = null;
  }

  // Auto-validate when track changes
  $effect(() => {
    if (track && visible) {
      validateTrack();
    } else {
      clearDiagnostics();
    }
  });
</script>

{#if visible && track}
  <div class="debug-panel">
    <div class="debug-header">
      <h3>Audio Debug Information</h3>
      <button class="close-btn" onclick={() => (visible = false)}>×</button>
    </div>

    <div class="track-info">
      <h4>Track: {track.title}</h4>
      <p><strong>File:</strong> {track.filePath}</p>
      <p><strong>Artist:</strong> {track.artist}</p>
      <p><strong>Album:</strong> {track.album}</p>
      {#if track.trackNumber}
        <p><strong>Track Number:</strong> {track.trackNumber}</p>
      {/if}
      <p><strong>Duration:</strong> {track.duration}s</p>
    </div>

    <div class="validation-section">
      <div class="validation-controls">
        <button onclick={validateTrack} disabled={isValidating}>
          {isValidating ? 'Validating...' : 'Validate Audio File'}
        </button>
        {#if diagnostics}
          <button onclick={clearDiagnostics}>Clear</button>
        {/if}
      </div>

      {#if isValidating}
        <div class="loading">
          <span class="spinner"></span>
          <span>Validating audio file...</span>
        </div>
      {/if}

      {#if diagnostics}
        <div class="diagnostics" class:error={!diagnostics.isValid} class:success={diagnostics.isValid}>
          <h4>Validation Results</h4>
          <pre>{formatAudioDiagnostics(diagnostics)}</pre>
          
          {#if !diagnostics.isValid}
            <div class="error-help">
              <h5>Possible Solutions:</h5>
              <ul>
                <li>Check if the file is corrupted</li>
                <li>Try converting to a supported format (MP3, FLAC, WAV, OGG)</li>
                <li>Ensure the file is not empty or truncated</li>
                <li>Check file permissions</li>
              </ul>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .debug-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    background: var(--bg-primary, #ffffff);
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    overflow-y: auto;
  }

  .debug-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--border-color, #e0e0e0);
    background: var(--bg-secondary, #f8f9fa);
  }

  .debug-header h3 {
    margin: 0;
    color: var(--text-primary, #333);
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--text-secondary, #666);
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
  }

  .close-btn:hover {
    background: var(--bg-hover, #f0f0f0);
  }

  .track-info {
    padding: 1rem;
    border-bottom: 1px solid var(--border-light, #f0f0f0);
  }

  .track-info h4 {
    margin: 0 0 0.5rem 0;
    color: var(--text-primary, #333);
  }

  .track-info p {
    margin: 0.25rem 0;
    color: var(--text-secondary, #666);
    font-size: 0.9rem;
  }

  .validation-section {
    padding: 1rem;
  }

  .validation-controls {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .validation-controls button {
    padding: 0.5rem 1rem;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 4px;
    background: var(--bg-primary, #ffffff);
    color: var(--text-primary, #333);
    cursor: pointer;
    font-size: 0.9rem;
  }

  .validation-controls button:hover:not(:disabled) {
    background: var(--bg-hover, #f0f0f0);
  }

  .validation-controls button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .loading {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary, #666);
    font-size: 0.9rem;
  }

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid var(--border-light, #f0f0f0);
    border-top: 2px solid var(--accent-color, #007bff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .diagnostics {
    border-radius: 4px;
    padding: 1rem;
  }

  .diagnostics.success {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
  }

  .diagnostics.error {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
  }

  .diagnostics h4 {
    margin: 0 0 0.5rem 0;
  }

  .diagnostics pre {
    background: rgba(0, 0, 0, 0.05);
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    white-space: pre-wrap;
    margin: 0.5rem 0;
  }

  .error-help {
    margin-top: 1rem;
  }

  .error-help h5 {
    margin: 0 0 0.5rem 0;
  }

  .error-help ul {
    margin: 0;
    padding-left: 1.5rem;
  }

  .error-help li {
    margin: 0.25rem 0;
    font-size: 0.9rem;
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .debug-panel {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --bg-hover: #4a5568;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --border-light: #2d3748;
      --accent-color: #4299e1;
    }

    .diagnostics.success {
      background: #1e4620;
      border-color: #2d5a2f;
      color: #9ae6b4;
    }

    .diagnostics.error {
      background: #4a1e1e;
      border-color: #5a2d2d;
      color: #feb2b2;
    }
  }
</style>
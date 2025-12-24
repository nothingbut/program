<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { _ } from "svelte-i18n";
  import type { Track } from "../types";
  import { formatDuration } from "../types";
  import AudioDebugPanel from "./AudioDebugPanel.svelte";

  // Props
  interface Props {
    tracks: Track[];
    selectedTrack: Track | null;
    loading?: boolean;
  }

  let { tracks, selectedTrack, loading = false }: Props = $props();

  // Event dispatcher for parent communication
  const dispatch = createEventDispatcher<{
    trackSelect: { track: Track };
    trackPlay: { track: Track };
    error: { message: string };
  }>();

  // Local state
  let errorMessage = $state<string | null>(null);
  let showDebugPanel = $state(false);
  let debugTrack = $state<Track | null>(null);

  /**
   * Handle track selection (single click)
   */
  function handleTrackSelect(track: Track) {
    if (selectedTrack?.id === track.id) return;

    dispatch("trackSelect", { track });
  }

  /**
   * Handle track play (double click)
   */
  function handleTrackPlay(track: Track) {
    dispatch("trackPlay", { track });
  }

  /**
   * Handle keyboard navigation
   */
  function handleKeyDown(event: KeyboardEvent, track: Track) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (event.detail === 2 || event.key === "Enter") {
        // Double click or Enter key - play track
        handleTrackPlay(track);
      } else {
        // Single click or Space key - select track
        handleTrackSelect(track);
      }
    }
  }

  /**
   * Get display value for track number
   */
  function getTrackNumberDisplay(trackNumber?: number): string {
    return trackNumber ? trackNumber.toString() : "-";
  }

  /**
   * Get display value for missing metadata
   */
  function getDisplayValue(
    value: string | undefined,
    fallback: string = "Unknown"
  ): string {
    return value && value.trim() ? value : fallback;
  }

  /**
   * Clear error message
   */
  function clearError() {
    errorMessage = null;
  }

  /**
   * Show debug panel for a track
   */
  function showDebugInfo(track: Track) {
    debugTrack = track;
    showDebugPanel = true;
  }

  /**
   * Handle right-click context menu
   */
  function handleContextMenu(event: MouseEvent, track: Track) {
    event.preventDefault();
    showDebugInfo(track);
  }
</script>

<div class="playlist-panel">
  <div class="panel-header">
    <h2>{$_("playlist.title", { default: "Playlist" })}</h2>
    <div class="header-controls">
      {#if tracks.length > 0}
        <div class="track-count" data-testid="track-count">
          {tracks.length} track{tracks.length !== 1 ? "s" : ""}
        </div>
      {/if}
      {#if selectedTrack}
        <button
          class="debug-btn"
          onclick={() => showDebugInfo(selectedTrack)}
          title="Debug selected track"
        >
          🔧
        </button>
      {/if}
    </div>
  </div>

  {#if errorMessage}
    <div class="error-message" data-testid="error-message">
      <span>{errorMessage}</span>
      <button class="error-close" onclick={clearError}>×</button>
    </div>
  {/if}

  <div class="playlist-content" data-testid="playlist-content">
    {#if loading}
      <div class="loading-state" data-testid="loading-state">
        <span class="loading-spinner"></span>
        <span
          >{$_("playlist.loading", { default: "Loading music files..." })}</span
        >
      </div>
    {:else if tracks.length === 0}
      <div class="empty-state" data-testid="empty-state">
        <div class="empty-icon">♪</div>
        <p>{$_("playlist.empty", { default: "No music files found" })}</p>
        <p>
          {$_("directory.select", {
            default: "Select a directory to view music files",
          })}
        </p>
      </div>
    {:else}
      <div class="playlist-table">
        <div class="table-header">
          <div class="header-cell track-number">#</div>
          <div class="header-cell title">
            {$_("playlist.columns.title", { default: "Title" })}
          </div>
          <div class="header-cell artist">
            {$_("playlist.columns.artist", { default: "Artist" })}
          </div>
          <div class="header-cell album">
            {$_("playlist.columns.album", { default: "Album" })}
          </div>
          <div class="header-cell duration">
            {$_("playlist.columns.duration", { default: "Duration" })}
          </div>
        </div>

        <div class="table-body" data-testid="playlist-table">
          {#each tracks as track, index (track.id)}
            <div
              class="track-row"
              class:selected={selectedTrack?.id === track.id}
              onclick={() => handleTrackSelect(track)}
              ondblclick={() => handleTrackPlay(track)}
              oncontextmenu={(e) => handleContextMenu(e, track)}
              onkeydown={(e) => handleKeyDown(e, track)}
              data-testid="track-row"
              data-track-id={track.id}
              role="button"
              tabindex="0"
              title="Click to select, double-click to play, right-click for debug info"
            >
              <div class="cell track-number">
                {getTrackNumberDisplay(track.trackNumber)}
              </div>
              <div class="cell title" title={track.title}>
                {getDisplayValue(track.title, "Untitled")}
              </div>
              <div class="cell artist" title={track.artist}>
                {getDisplayValue(track.artist)}
              </div>
              <div class="cell album" title={track.album}>
                {getDisplayValue(track.album)}
              </div>
              <div class="cell duration">
                {formatDuration(track.duration)}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>

  <!-- Audio Debug Panel -->
  <AudioDebugPanel track={debugTrack} bind:visible={showDebugPanel} />
</div>

<style>
  .playlist-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--bg-primary, #ffffff);
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--border-color, #e0e0e0);
    background-color: var(--bg-primary, #ffffff);
  }

  .header-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .panel-header h2 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary, #333333);
  }

  .track-count {
    font-size: 0.9rem;
    color: var(--text-secondary, #666666);
    font-weight: 500;
  }

  .debug-btn {
    background: none;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    cursor: pointer;
    font-size: 0.9rem;
    color: var(--text-secondary, #666);
    transition: all 0.2s ease;
  }

  .debug-btn:hover {
    background: var(--bg-hover, #f0f0f0);
    border-color: var(--accent-color, #007bff);
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

  .playlist-content {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .loading-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    padding: 2rem 1rem;
    text-align: center;
    color: var(--text-secondary, #666666);
  }

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  .empty-state p {
    margin: 0.5rem 0;
  }

  .playlist-table {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .table-header {
    display: flex;
    padding: 0.75rem 1rem;
    background-color: var(--bg-secondary, #f8f9fa);
    border-bottom: 1px solid var(--border-color, #e0e0e0);
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-secondary, #666666);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .table-body {
    flex: 1;
    overflow-y: auto;
  }

  .header-cell,
  .cell {
    padding: 0 0.5rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .track-number {
    width: 60px;
    flex-shrink: 0;
    text-align: center;
  }

  .title {
    flex: 2;
    min-width: 150px;
  }

  .artist {
    flex: 1.5;
    min-width: 120px;
  }

  .album {
    flex: 1.5;
    min-width: 120px;
  }

  .duration {
    width: 80px;
    flex-shrink: 0;
    text-align: right;
  }

  .track-row {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    border-bottom: 1px solid var(--border-light, #f0f0f0);
  }

  .track-row:hover {
    background-color: var(--bg-hover, #f8f9fa);
  }

  .track-row.selected {
    background-color: var(--accent-light, #e3f2fd);
    color: var(--accent-color, #007bff);
    border-color: var(--accent-color, #007bff);
  }

  .track-row:focus {
    outline: 2px solid var(--accent-color, #007bff);
    outline-offset: -2px;
  }

  .track-row:last-child {
    border-bottom: none;
  }

  .loading-spinner {
    width: 24px;
    height: 24px;
    border: 3px solid var(--border-light, #f0f0f0);
    border-top: 3px solid var(--accent-color, #007bff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .playlist-panel {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --bg-hover: #4a5568;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --border-light: #2d3748;
      --accent-color: #4299e1;
      --accent-light: #2d3748;
      --error-bg: #742a2a;
      --error-text: #feb2b2;
      --error-border: #c53030;
    }
  }

  /* Responsive design */
  @media (max-width: 1024px) {
    .album {
      display: none;
    }

    .artist {
      flex: 2;
    }
  }

  @media (max-width: 768px) {
    .panel-header {
      padding: 0.75rem;
    }

    .table-header,
    .track-row {
      padding: 0.5rem 0.75rem;
    }

    .track-number {
      width: 40px;
    }

    .duration {
      width: 60px;
    }

    .header-cell,
    .cell {
      font-size: 0.9rem;
    }
  }

  @media (max-width: 480px) {
    .artist {
      display: none;
    }

    .title {
      flex: 3;
    }

    .track-number {
      width: 30px;
    }
  }
</style>

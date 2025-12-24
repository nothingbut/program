<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import type { Track } from "../types";
  import { formatDuration } from "../types";

  // Props
  interface Props {
    currentTrack: Track | null;
    isPlaying: boolean;
    currentTime: number;
    duration: number;
    isShuffleMode: boolean;
    volume?: number;
  }

  let {
    currentTrack,
    isPlaying,
    currentTime,
    duration,
    isShuffleMode,
    volume = 1.0,
  }: Props = $props();

  // Event dispatcher for parent communication
  const dispatch = createEventDispatcher<{
    playPause: void;
    previous: void;
    next: void;
    seek: { time: number };
    volumeChange: { volume: number };
    shuffleToggle: void;
    showNotification: { message: string; type: string };
  }>();

  // Progress bar element reference (for potential future use)
  let progressBarElement: HTMLElement;

  // Computed values
  const progress = $derived((): number => {
    return duration > 0 ? currentTime / duration : 0;
  });

  const formattedCurrentTime = $derived(() => formatDuration(currentTime));
  const formattedDuration = $derived(() => formatDuration(duration));

  const trackDisplayInfo = $derived(() => {
    if (!currentTrack) return "";

    const trackNum = currentTrack.trackNumber
      ? `(${currentTrack.trackNumber})`
      : "";
    return `${currentTrack.album}${trackNum}: ${currentTrack.title} - ${currentTrack.artist}`;
  });

  /**
   * Handle play/pause button click
   */
  function handlePlayPause() {
    dispatch("playPause");
  }

  /**
   * Handle previous track button click
   */
  function handlePrevious() {
    dispatch("previous");
  }

  /**
   * Handle next track button click
   */
  function handleNext() {
    dispatch("next");
  }

  /**
   * Handle shuffle toggle button click
   */
  function handleShuffleToggle() {
    dispatch("shuffleToggle");
  }

  // Note: Seeking functionality has been disabled due to Rodio library limitations
  // The progress bar now serves as a read-only indicator of playback progress

  /**
   * Handle volume change
   */
  function handleVolumeChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const newVolume = parseFloat(target.value);
    dispatch("volumeChange", { volume: newVolume });
  }

  /**
   * Handle keyboard shortcuts
   */
  function handleKeyDown(event: KeyboardEvent) {
    // Only handle if not focused on an input element
    if (event.target instanceof HTMLInputElement) return;

    switch (event.code) {
      case "Space":
        event.preventDefault();
        handlePlayPause();
        break;
      case "ArrowLeft":
        event.preventDefault();
        handlePrevious();
        break;
      case "ArrowRight":
        event.preventDefault();
        handleNext();
        break;
    }
  }

  /**
   * Show notification about seeking not being supported
   */
  function showSeekingNotSupported() {
    // Dispatch a custom event to show a toast notification
    dispatch("showNotification", {
      message: "Seeking is not supported with the current audio engine",
      type: "info",
    });
  }
</script>

<svelte:window onkeydown={handleKeyDown} />

<div class="player-controls" data-testid="player-controls">
  <!-- Track Information -->
  <div class="track-info">
    {#if currentTrack}
      <div class="cover-art">
        {#if currentTrack.coverArt}
          <img
            src="data:image/jpeg;base64,{currentTrack.coverArt}"
            alt="Album cover"
            class="cover-image"
          />
        {:else}
          <div class="cover-placeholder">
            <span class="music-icon">♪</span>
          </div>
        {/if}
      </div>

      <div class="track-details">
        <div class="track-title" title={trackDisplayInfo()}>
          {trackDisplayInfo()}
        </div>
        <div class="track-file" title={currentTrack.filePath}>
          {currentTrack.filePath.split("/").pop()}
        </div>
      </div>
    {:else}
      <div class="no-track">
        <div class="cover-placeholder">
          <span class="music-icon">♪</span>
        </div>
        <div class="track-details">
          <div class="track-title">No track selected</div>
          <div class="track-file">Select a track to start playing</div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Playback Controls -->
  <div class="playback-controls">
    <!-- Control Buttons -->
    <div class="control-buttons">
      <button
        class="control-button shuffle-button"
        class:active={isShuffleMode}
        onclick={handleShuffleToggle}
        title="Toggle shuffle mode"
        aria-label="Toggle shuffle mode"
        data-testid="shuffle-button"
      >
        <svg viewBox="0 0 24 24" class="button-icon">
          <path
            d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"
          />
        </svg>
      </button>

      <button
        class="control-button previous-button"
        onclick={handlePrevious}
        disabled={!currentTrack}
        title="Previous track"
        aria-label="Previous track"
        data-testid="previous-button"
      >
        <svg viewBox="0 0 24 24" class="button-icon">
          <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" />
        </svg>
      </button>

      <button
        class="control-button play-pause-button"
        onclick={handlePlayPause}
        disabled={!currentTrack}
        title={isPlaying ? "Pause" : "Play"}
        aria-label={isPlaying ? "Pause" : "Play"}
        data-testid="play-pause-button"
      >
        {#if isPlaying}
          <svg viewBox="0 0 24 24" class="button-icon">
            <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
          </svg>
        {:else}
          <svg viewBox="0 0 24 24" class="button-icon">
            <path d="M8 5v14l11-7z" />
          </svg>
        {/if}
      </button>

      <button
        class="control-button next-button"
        onclick={handleNext}
        disabled={!currentTrack}
        title="Next track"
        aria-label="Next track"
        data-testid="next-button"
      >
        <svg viewBox="0 0 24 24" class="button-icon">
          <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
        </svg>
      </button>
    </div>

    <!-- Progress Bar -->
    <div class="progress-section">
      <div class="time-display current-time" data-testid="current-time">
        {formattedCurrentTime()}
      </div>

      <div
        class="progress-bar-container"
        bind:this={progressBarElement}
        role="progressbar"
        aria-valuemin="0"
        aria-valuemax={duration}
        aria-valuenow={currentTime}
        aria-label="Playback progress (seeking not supported)"
        title="Seeking is not supported with the current audio engine"
        data-testid="progress-bar"
      >
        <div class="progress-bar">
          <div class="progress-fill" style="width: {progress() * 100}%"></div>
          <div class="progress-handle" style="left: {progress() * 100}%"></div>
        </div>
      </div>

      <div class="time-display duration-time" data-testid="duration-time">
        {formattedDuration()}
      </div>
    </div>
  </div>

  <!-- Volume Control -->
  <div class="volume-control">
    <svg viewBox="0 0 24 24" class="volume-icon">
      {#if volume === 0}
        <path
          d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"
        />
      {:else if volume < 0.5}
        <path
          d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"
        />
      {:else}
        <path
          d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"
        />
      {/if}
    </svg>

    <input
      type="range"
      min="0"
      max="1"
      step="0.01"
      value={volume}
      onchange={handleVolumeChange}
      class="volume-slider"
      title="Volume"
      data-testid="volume-slider"
    />
  </div>
</div>

<style>
  .player-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background-color: var(--bg-primary, #ffffff);
    border-top: 1px solid var(--border-color, #e0e0e0);
    min-height: 80px;
  }

  /* Track Information */
  .track-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 0 0 300px;
    min-width: 0;
  }

  .cover-art {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
    border-radius: 4px;
    overflow: hidden;
    background-color: var(--bg-secondary, #f8f9fa);
  }

  .cover-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .cover-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--bg-secondary, #f8f9fa);
    color: var(--text-secondary, #666666);
  }

  .music-icon {
    font-size: 1.5rem;
  }

  .track-details {
    flex: 1;
    min-width: 0;
  }

  .track-title {
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--text-primary, #333333);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 0.25rem;
  }

  .track-file {
    font-size: 0.8rem;
    color: var(--text-secondary, #666666);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .no-track .track-title {
    color: var(--text-secondary, #666666);
  }

  /* Playback Controls */
  .playback-controls {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    max-width: 600px;
  }

  .control-buttons {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .control-button {
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 50%;
    background-color: transparent;
    color: var(--text-primary, #333333);
    cursor: pointer;
    transition: all 0.2s ease;
    padding: 0.5rem;
  }

  .control-button:hover:not(:disabled) {
    background-color: var(--bg-hover, #f0f0f0);
    transform: scale(1.05);
  }

  .control-button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
  }

  .play-pause-button {
    width: 48px;
    height: 48px;
    background-color: var(--accent-color, #007bff);
    color: white;
  }

  .play-pause-button:hover:not(:disabled) {
    background-color: var(--accent-hover, #0056b3);
  }

  .shuffle-button.active {
    color: var(--accent-color, #007bff);
    background-color: var(--accent-light, #e3f2fd);
  }

  .button-icon {
    width: 20px;
    height: 20px;
    fill: currentColor;
  }

  .play-pause-button .button-icon {
    width: 24px;
    height: 24px;
  }

  /* Progress Bar */
  .progress-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    width: 100%;
  }

  .time-display {
    font-size: 0.8rem;
    color: var(--text-secondary, #666666);
    font-variant-numeric: tabular-nums;
    min-width: 40px;
  }

  .current-time {
    text-align: right;
  }

  .duration-time {
    text-align: left;
  }

  .progress-bar-container {
    flex: 1;
    height: 20px;
    display: flex;
    align-items: center;
    cursor: not-allowed;
    padding: 8px 0;
    opacity: 0.7;
  }

  .progress-bar {
    position: relative;
    width: 100%;
    height: 4px;
    background-color: var(--border-color, #e0e0e0);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background-color: var(--accent-color, #007bff);
    border-radius: 2px;
    transition: width 0.1s ease;
  }

  .progress-handle {
    position: absolute;
    top: 50%;
    width: 12px;
    height: 12px;
    background-color: var(--accent-color, #007bff);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    opacity: 0;
    transition: opacity 0.2s ease;
    display: none; /* Hide handle since seeking is disabled */
  }

  /* Disabled hover effects since seeking is not supported */
  /* .progress-bar-container:hover .progress-handle,
  .progress-handle.dragging {
    opacity: 1;
  }

  .progress-handle.dragging {
    transform: translate(-50%, -50%) scale(1.2);
  } */

  /* Volume Control */
  .volume-control {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 0 0 120px;
  }

  .volume-icon {
    width: 20px;
    height: 20px;
    fill: var(--text-secondary, #666666);
    flex-shrink: 0;
  }

  .volume-slider {
    flex: 1;
    height: 4px;
    background: transparent;
    outline: none;
    -webkit-appearance: none;
    appearance: none;
  }

  .volume-slider::-webkit-slider-track {
    height: 4px;
    background-color: var(--border-color, #e0e0e0);
    border-radius: 2px;
  }

  .volume-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 12px;
    height: 12px;
    background-color: var(--accent-color, #007bff);
    border-radius: 50%;
    cursor: pointer;
  }

  .volume-slider::-moz-range-track {
    height: 4px;
    background-color: var(--border-color, #e0e0e0);
    border-radius: 2px;
    border: none;
  }

  .volume-slider::-moz-range-thumb {
    width: 12px;
    height: 12px;
    background-color: var(--accent-color, #007bff);
    border-radius: 50%;
    border: none;
    cursor: pointer;
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .player-controls {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --bg-hover: #4a5568;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --accent-color: #4299e1;
      --accent-hover: #3182ce;
      --accent-light: #2d3748;
    }
  }

  /* Responsive design */
  @media (max-width: 1024px) {
    .track-info {
      flex: 0 0 250px;
    }

    .volume-control {
      flex: 0 0 100px;
    }
  }

  @media (max-width: 768px) {
    .player-controls {
      flex-direction: column;
      gap: 0.75rem;
      padding: 0.75rem;
      min-height: auto;
    }

    .track-info {
      flex: none;
      width: 100%;
      max-width: none;
    }

    .playback-controls {
      width: 100%;
      max-width: none;
    }

    .volume-control {
      flex: none;
      width: 100%;
      max-width: 200px;
    }
  }

  @media (max-width: 480px) {
    .control-buttons {
      gap: 0.25rem;
    }

    .control-button {
      padding: 0.375rem;
    }

    .play-pause-button {
      width: 40px;
      height: 40px;
    }

    .button-icon {
      width: 16px;
      height: 16px;
    }

    .play-pause-button .button-icon {
      width: 20px;
      height: 20px;
    }
  }
</style>

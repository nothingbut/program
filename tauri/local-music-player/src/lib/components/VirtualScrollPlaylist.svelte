<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import type { Track } from '../types';
  import { formatDuration } from '../types';

  // Props
  interface Props {
    tracks: Track[];
    selectedTrack: Track | null;
    loading?: boolean;
    itemHeight?: number;
    overscan?: number;
  }

  let { 
    tracks, 
    selectedTrack, 
    loading = false,
    itemHeight = 48,
    overscan = 5
  }: Props = $props();

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    trackSelect: { track: Track };
    trackPlay: { track: Track };
    error: { message: string };
  }>();

  // Virtual scrolling state
  let containerElement: HTMLElement;
  let scrollTop = $state(0);
  let containerHeight = $state(0);
  let isScrolling = $state(false);
  let scrollTimeout: number;

  // Computed values for virtual scrolling
  const totalHeight = $derived(tracks.length * itemHeight);
  const startIndex = $derived(Math.max(0, Math.floor(scrollTop / itemHeight) - overscan));
  const endIndex = $derived(Math.min(tracks.length - 1, Math.floor((scrollTop + containerHeight) / itemHeight) + overscan));
  const visibleTracks = $derived(tracks.slice(startIndex, endIndex + 1));
  const offsetY = $derived(startIndex * itemHeight);

  // Resize observer for container height
  let resizeObserver: ResizeObserver;

  onMount(() => {
    if (containerElement) {
      // Initialize container height
      containerHeight = containerElement.clientHeight;

      // Set up resize observer
      resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          containerHeight = entry.contentRect.height;
        }
      });
      resizeObserver.observe(containerElement);
    }

    return () => {
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
      if (scrollTimeout) {
        clearTimeout(scrollTimeout);
      }
    };
  });

  /**
   * Handle scroll events
   */
  function handleScroll(event: Event) {
    const target = event.target as HTMLElement;
    scrollTop = target.scrollTop;
    
    // Set scrolling state
    isScrolling = true;
    
    // Clear existing timeout
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }
    
    // Set timeout to clear scrolling state
    scrollTimeout = setTimeout(() => {
      isScrolling = false;
    }, 150);
  }

  /**
   * Scroll to specific track
   */
  function scrollToTrack(trackIndex: number) {
    if (!containerElement) return;
    
    const targetScrollTop = trackIndex * itemHeight;
    containerElement.scrollTop = targetScrollTop;
  }

  /**
   * Handle track selection
   */
  function handleTrackSelect(track: Track) {
    if (selectedTrack?.id === track.id) return;
    dispatch('trackSelect', { track });
  }

  /**
   * Handle track play
   */
  function handleTrackPlay(track: Track) {
    dispatch('trackPlay', { track });
  }

  /**
   * Handle keyboard navigation
   */
  function handleKeyDown(event: KeyboardEvent, track: Track) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (event.key === 'Enter') {
        handleTrackPlay(track);
      } else {
        handleTrackSelect(track);
      }
    }
  }

  /**
   * Get display value for track number
   */
  function getTrackNumberDisplay(trackNumber?: number): string {
    return trackNumber ? trackNumber.toString() : '-';
  }

  /**
   * Get display value for missing metadata
   */
  function getDisplayValue(value: string | undefined, fallback: string = 'Unknown'): string {
    return value && value.trim() ? value : fallback;
  }

  // Auto-scroll to selected track when it changes
  $effect(() => {
    if (selectedTrack && tracks.length > 0) {
      const trackIndex = tracks.findIndex(t => t.id === selectedTrack.id);
      if (trackIndex >= 0) {
        // Check if selected track is visible
        const isVisible = trackIndex >= startIndex && trackIndex <= endIndex;
        if (!isVisible && !isScrolling) {
          scrollToTrack(trackIndex);
        }
      }
    }
  });
</script>

<div class="virtual-playlist" data-testid="virtual-playlist">
  <div class="panel-header">
    <h2>Playlist</h2>
    {#if tracks.length > 0}
      <div class="track-count" data-testid="track-count">
        {tracks.length} track{tracks.length !== 1 ? 's' : ''}
      </div>
    {/if}
  </div>

  <div class="playlist-content" data-testid="playlist-content">
    {#if loading}
      <div class="loading-state" data-testid="loading-state">
        <span class="loading-spinner"></span>
        <span>Loading tracks...</span>
      </div>
    {:else if tracks.length === 0}
      <div class="empty-state" data-testid="empty-state">
        <div class="empty-icon">♪</div>
        <p>No tracks found</p>
        <p>Select a directory with MP3 files to see your music here.</p>
      </div>
    {:else}
      <div class="playlist-table">
        <!-- Table Header -->
        <div class="table-header">
          <div class="header-cell track-number">#</div>
          <div class="header-cell title">Title</div>
          <div class="header-cell artist">Artist</div>
          <div class="header-cell album">Album</div>
          <div class="header-cell duration">Duration</div>
        </div>
        
        <!-- Virtual Scroll Container -->
        <div 
          class="virtual-scroll-container"
          bind:this={containerElement}
          onscroll={handleScroll}
          data-testid="virtual-scroll-container"
        >
          <!-- Total height spacer -->
          <div class="scroll-spacer" style="height: {totalHeight}px;"></div>
          
          <!-- Visible items container -->
          <div 
            class="visible-items"
            style="transform: translateY({offsetY}px);"
          >
            {#each visibleTracks as track, index (track.id)}
              {@const actualIndex = startIndex + index}
              <div 
                class="track-row"
                class:selected={selectedTrack?.id === track.id}
                onclick={() => handleTrackSelect(track)}
                ondblclick={() => handleTrackPlay(track)}
                onkeydown={(e) => handleKeyDown(e, track)}
                data-testid="track-row"
                data-track-id={track.id}
                data-index={actualIndex}
                role="button"
                tabindex="0"
                title="Click to select, double-click to play"
                style="height: {itemHeight}px;"
              >
                <div class="cell track-number">
                  {getTrackNumberDisplay(track.trackNumber)}
                </div>
                <div class="cell title" title={track.title}>
                  {getDisplayValue(track.title, 'Untitled')}
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
      </div>
    {/if}
  </div>
</div>

<style>
  .virtual-playlist {
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
    flex-shrink: 0;
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

  .playlist-content {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .loading-state, .empty-state {
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
    min-height: 0;
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
    flex-shrink: 0;
  }

  .virtual-scroll-container {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    position: relative;
    min-height: 0;
  }

  .scroll-spacer {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    pointer-events: none;
  }

  .visible-items {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
  }

  .header-cell, .cell {
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
    transition: background-color 0.2s ease;
    border-bottom: 1px solid var(--border-light, #f0f0f0);
    box-sizing: border-box;
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

  /* Custom scrollbar */
  .virtual-scroll-container::-webkit-scrollbar {
    width: 8px;
  }

  .virtual-scroll-container::-webkit-scrollbar-track {
    background: var(--bg-secondary, #f8f9fa);
  }

  .virtual-scroll-container::-webkit-scrollbar-thumb {
    background: var(--border-color, #e0e0e0);
    border-radius: 4px;
  }

  .virtual-scroll-container::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary, #666666);
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .virtual-playlist {
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
    
    .table-header, .track-row {
      padding: 0.5rem 0.75rem;
    }
    
    .track-number {
      width: 40px;
    }
    
    .duration {
      width: 60px;
    }
    
    .header-cell, .cell {
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
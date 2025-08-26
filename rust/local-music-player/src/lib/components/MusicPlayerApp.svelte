<script lang="ts">
  import { onMount } from 'svelte';
  import DirectoryPanel from './DirectoryPanel.svelte';
  import PlaylistPanel from './PlaylistPanel.svelte';
  import VirtualScrollPlaylist from './VirtualScrollPlaylist.svelte';
  import PlayerControls from './PlayerControls.svelte';
  import ScanProgressIndicator from './ScanProgressIndicator.svelte';
  import KeyboardShortcutsHelp from './KeyboardShortcutsHelp.svelte';
  import { 
    directories, 
    selectedDirectory, 
    directoryActions,
    currentPlaylist,
    selectedTrack,
    playlistActions,
    playbackState,
    isShuffleMode,
    playbackActions,
    shuffleActions,
    playlistManager,
    navigationState,
    uiActions,
    isLoading,
    errorState,
    isScanningDirectory,
    scanningProgress,
    scanningProgressPercent
  } from '../stores';
  import { 
    handleGlobalKeyboard, 
    registerKeyboardHandler, 
    unregisterKeyboardHandler,
    keyboardActions 
  } from '../stores/keyboard';
  import { playbackApi, directoryApi, handleApiError } from '../api';
  import type { Directory, Track } from '../types';

  // Component state
  let errorMessage = $state<string | null>(null);
  let isInitialized = $state(false);
  let showKeyboardHelp = $state(false);
  let useVirtualScrolling = $state(true);
  let windowWidth = $state(0);
  let windowHeight = $state(0);
  let isMobile = $derived(windowWidth < 768);
  let isTablet = $derived(windowWidth >= 768 && windowWidth < 1024);

  // Reactive values
  const currentTrack = $derived($playbackState.currentTrack);
  const isPlaying = $derived($playbackState.isPlaying);
  const currentTime = $derived($playbackState.currentTime);
  const duration = $derived($playbackState.duration);
  const volume = $derived($playbackState.volume);
  const navState = $derived($navigationState);

  /**
   * Initialize the application
   */
  onMount(async () => {
    try {
      uiActions.setLoading(true, 'Initializing application...');
      
      // Initialize window size tracking
      updateWindowSize();
      
      // Load saved directories
      await loadDirectories();
      
      // Initialize playlist manager
      playlistManager.setAutoPlay(true);
      
      // Setup keyboard shortcuts
      setupKeyboardShortcuts();
      
      // Enable virtual scrolling for large playlists
      useVirtualScrolling = $currentPlaylist.length > 100;
      
      isInitialized = true;
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    } finally {
      uiActions.setLoading(false);
    }
  });

  /**
   * Update window size
   */
  function updateWindowSize() {
    windowWidth = window.innerWidth;
    windowHeight = window.innerHeight;
  }

  /**
   * Setup keyboard shortcuts
   */
  function setupKeyboardShortcuts() {
    // Register keyboard handlers
    registerKeyboardHandler('playPause', () => {
      handlePlayPause();
      return true;
    });

    registerKeyboardHandler('previous', () => {
      handlePrevious();
      return true;
    });

    registerKeyboardHandler('next', () => {
      handleNext();
      return true;
    });

    registerKeyboardHandler('volumeUp', () => {
      const newVolume = Math.min(1, volume + 0.1);
      handleVolumeChange(new CustomEvent('volumeChange', { detail: { volume: newVolume } }));
      return true;
    });

    registerKeyboardHandler('volumeDown', () => {
      const newVolume = Math.max(0, volume - 0.1);
      handleVolumeChange(new CustomEvent('volumeChange', { detail: { volume: newVolume } }));
      return true;
    });

    registerKeyboardHandler('toggleShuffle', () => {
      handleShuffleToggle();
      return true;
    });

    registerKeyboardHandler('toggleMute', () => {
      const newVolume = volume > 0 ? 0 : 1;
      handleVolumeChange(new CustomEvent('volumeChange', { detail: { volume: newVolume } }));
      return true;
    });

    registerKeyboardHandler('escape', () => {
      if (showKeyboardHelp) {
        showKeyboardHelp = false;
        return true;
      }
      return false;
    });

    // Help shortcut
    const helpHandler = (event: KeyboardEvent) => {
      if (event.key === '?' || event.key === 'F1') {
        event.preventDefault();
        showKeyboardHelp = !showKeyboardHelp;
        return true;
      }
      return false;
    };

    // Add global keyboard listener
    document.addEventListener('keydown', (event) => {
      if (helpHandler(event)) return;
      handleGlobalKeyboard(event);
    });

    // Cleanup function
    return () => {
      document.removeEventListener('keydown', helpHandler);
      unregisterKeyboardHandler('playPause', handlePlayPause);
      unregisterKeyboardHandler('previous', handlePrevious);
      unregisterKeyboardHandler('next', handleNext);
    };
  }

  /**
   * Load directories from backend
   */
  async function loadDirectories() {
    try {
      const result = await directoryApi.getAll();
      directoryActions.setDirectories(result);
    } catch (error) {
      console.error('Failed to load directories:', error);
      throw error;
    }
  }

  /**
   * Handle directory addition
   */
  async function handleDirectoryAdd(event: CustomEvent<{ directory: Directory }>) {
    try {
      const { directory } = event.detail;
      directoryActions.addDirectory(directory);
      
      // Auto-select if it's the first directory
      if ($directories.length === 1) {
        await handleDirectorySelect(new CustomEvent('directorySelect', { 
          detail: { directory } 
        }));
      }
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Handle directory selection and scan
   */
  async function handleDirectorySelect(event: CustomEvent<{ directory: Directory }>) {
    try {
      const { directory } = event.detail;
      
      uiActions.setLoading(true, `Scanning ${directory.name}...`);
      directoryActions.selectDirectory(directory);
      
      // Scan directory for tracks
      const tracks = await directoryApi.scan(directory.id);
      playlistActions.setPlaylist(tracks);
      
      // Clear any previous error
      errorMessage = null;
      uiActions.clearError();
      
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    } finally {
      uiActions.setLoading(false);
    }
  }

  /**
   * Handle directory removal
   */
  async function handleDirectoryRemove(event: CustomEvent<{ directory: Directory }>) {
    try {
      const { directory } = event.detail;
      
      // Remove from backend
      await directoryApi.remove(directory.id);
      
      // Update local state
      directoryActions.removeDirectory(directory.id);
      
      // Clear playlist if this was the selected directory
      if ($selectedDirectory?.id === directory.id) {
        directoryActions.selectDirectory(null);
        playlistActions.clearPlaylist();
      }
      
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Handle track selection
   */
  function handleTrackSelect(event: CustomEvent<{ track: Track }>) {
    const { track } = event.detail;
    playlistActions.selectTrack(track);
  }

  /**
   * Handle track play (double-click)
   */
  async function handleTrackPlay(event: CustomEvent<{ track: Track }>) {
    try {
      const { track } = event.detail;
      
      // Select the track first
      playlistActions.selectTrack(track);
      
      // Start playback
      await playTrack(track);
      
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Play a specific track
   */
  async function playTrack(track: Track) {
    try {
      // Update playback state
      playbackActions.setCurrentTrack(track);
      playbackActions.setPlaying(true);
      
      // Call backend to start playback
      await playbackApi.playTrack(track);
      
    } catch (error) {
      playbackActions.setPlaying(false);
      throw error;
    }
  }

  /**
   * Handle play/pause toggle
   */
  async function handlePlayPause() {
    try {
      if (!currentTrack) {
        // No track selected, try to play first track in playlist
        const playlist = $currentPlaylist;
        if (playlist.length > 0) {
          await playTrack(playlist[0]);
        }
        return;
      }

      if (isPlaying) {
        await playbackApi.pause();
        playbackActions.setPlaying(false);
      } else {
        await playbackApi.resume();
        playbackActions.setPlaying(true);
      }
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Handle previous track
   */
  async function handlePrevious() {
    try {
      if (!navState.canGoPrevious) return;
      
      const success = playlistManager.playPrevious();
      if (success && $selectedTrack) {
        await playTrack($selectedTrack);
      }
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Handle next track
   */
  async function handleNext() {
    try {
      if (!navState.canGoNext) return;
      
      const success = playlistManager.playNext();
      if (success && $selectedTrack) {
        await playTrack($selectedTrack);
      }
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Handle seek
   */
  async function handleSeek(event: CustomEvent<{ time: number }>) {
    try {
      const { time } = event.detail;
      await playbackApi.seekTo(time);
      playbackActions.setCurrentTime(time);
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Handle volume change
   */
  async function handleVolumeChange(event: CustomEvent<{ volume: number }>) {
    try {
      const { volume } = event.detail;
      await playbackApi.setVolume(volume);
      playbackActions.setVolume(volume);
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Handle shuffle toggle
   */
  function handleShuffleToggle() {
    shuffleActions.toggleShuffle();
  }

  /**
   * Handle track end (auto-play next)
   */
  async function handleTrackEnd() {
    try {
      const success = playlistManager.onTrackEnd();
      if (success && $selectedTrack) {
        await playTrack($selectedTrack);
      } else {
        // No next track, stop playback
        playbackActions.setPlaying(false);
      }
    } catch (error) {
      const message = handleApiError(error);
      uiActions.setError(message);
      errorMessage = message;
    }
  }

  /**
   * Handle errors from child components
   */
  function handleError(event: CustomEvent<{ message: string }>) {
    const { message } = event.detail;
    uiActions.setError(message);
    errorMessage = message;
    
    // Clear error after 5 seconds
    setTimeout(() => {
      if (errorMessage === message) {
        errorMessage = null;
        uiActions.clearError();
      }
    }, 5000);
  }

  /**
   * Clear error message
   */
  function clearError() {
    errorMessage = null;
    uiActions.clearError();
  }

  // Listen for track end events (this would be implemented with proper event system)
  // For now, we'll simulate this with a timer-based approach
  let trackEndTimer: number | null = null;
  
  $effect(() => {
    if (isPlaying && currentTrack && duration > 0) {
      // Clear existing timer
      if (trackEndTimer) {
        clearTimeout(trackEndTimer);
      }
      
      // Set timer for track end
      const remainingTime = (duration - currentTime) * 1000;
      if (remainingTime > 0 && remainingTime < 300000) { // Max 5 minutes
        trackEndTimer = setTimeout(() => {
          handleTrackEnd();
        }, remainingTime);
      }
    } else if (trackEndTimer) {
      clearTimeout(trackEndTimer);
      trackEndTimer = null;
    }
  });

  // Window resize listener
  $effect(() => {
    const handleResize = () => updateWindowSize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  });

  // Auto-enable virtual scrolling for large playlists
  $effect(() => {
    useVirtualScrolling = $currentPlaylist.length > 100;
  });
</script>

<svelte:window onkeydown={handleGlobalKeyboard} />

<div class="music-player-app" data-testid="music-player-app">
  <!-- Global Error Display -->
  {#if errorMessage}
    <div class="global-error" data-testid="global-error">
      <div class="error-content">
        <strong>Error:</strong> {errorMessage}
        <button class="error-close" onclick={clearError} aria-label="Close error">×</button>
      </div>
    </div>
  {/if}

  <!-- Loading Overlay -->
  {#if $isLoading}
    <div class="loading-overlay" data-testid="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p class="loading-message">{$isLoading}</p>
      </div>
    </div>
  {/if}

  <!-- Main Application Layout -->
  <div class="app-layout" class:loading={$isLoading}>
    <!-- Top Panel: Directory and Playlist -->
    <div class="main-panels">
      <!-- Left Panel: Directory Management -->
      <div class="directory-panel">
        <DirectoryPanel
          directories={$directories}
          selectedDirectory={$selectedDirectory}
          loading={$isLoading}
          on:directoryAdd={handleDirectoryAdd}
          on:directorySelect={handleDirectorySelect}
          on:directoryRemove={handleDirectoryRemove}
          on:error={handleError}
        />
      </div>

      <!-- Right Panel: Playlist -->
      <div class="playlist-panel">
        {#if useVirtualScrolling}
          <VirtualScrollPlaylist
            tracks={$currentPlaylist}
            selectedTrack={$selectedTrack}
            loading={$isLoading}
            on:trackSelect={handleTrackSelect}
            on:trackPlay={handleTrackPlay}
            on:error={handleError}
          />
        {:else}
          <PlaylistPanel
            tracks={$currentPlaylist}
            selectedTrack={$selectedTrack}
            loading={$isLoading}
            on:trackSelect={handleTrackSelect}
            on:trackPlay={handleTrackPlay}
            on:error={handleError}
          />
        {/if}
      </div>
    </div>

    <!-- Bottom Panel: Player Controls -->
    <div class="player-panel">
      <PlayerControls
        currentTrack={currentTrack}
        isPlaying={isPlaying}
        currentTime={currentTime}
        duration={duration}
        isShuffleMode={$isShuffleMode}
        volume={volume}
        on:playPause={handlePlayPause}
        on:previous={handlePrevious}
        on:next={handleNext}
        on:seek={handleSeek}
        on:volumeChange={handleVolumeChange}
        on:shuffleToggle={handleShuffleToggle}
      />
    </div>
  </div>

  <!-- Scan Progress Indicator -->
  <ScanProgressIndicator
    isScanning={$isScanningDirectory}
    progress={$scanningProgressPercent / 100}
    currentFile={$scanningProgress.message}
    totalFiles={$scanningProgress.total}
    scannedFiles={$scanningProgress.current}
    directoryName={$selectedDirectory?.name}
  />

  <!-- Keyboard Shortcuts Help -->
  <KeyboardShortcutsHelp
    isOpen={showKeyboardHelp}
    on:close={() => showKeyboardHelp = false}
  />

  <!-- Debug Panel (development only) -->
  {#if import.meta.env.DEV}
    <details class="debug-panel">
      <summary>Debug Information</summary>
      <div class="debug-content">
        <div class="debug-section">
          <h4>Navigation State</h4>
          <pre>{JSON.stringify(navState, null, 2)}</pre>
        </div>
        <div class="debug-section">
          <h4>Playlist Manager State</h4>
          <pre>{JSON.stringify(playlistManager.getState(), null, 2)}</pre>
        </div>
        <div class="debug-section">
          <h4>Playback State</h4>
          <pre>{JSON.stringify($playbackState, null, 2)}</pre>
        </div>
      </div>
    </details>
  {/if}
</div>

<style>
  .music-player-app {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: var(--bg-primary, #ffffff);
    color: var(--text-primary, #333333);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  /* Global Error Display */
  .global-error {
    background-color: var(--error-bg, #fee);
    color: var(--error-text, #c33);
    border-bottom: 1px solid var(--error-border, #fcc);
    z-index: 1000;
  }

  .error-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .error-close {
    background: none;
    border: none;
    color: inherit;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    margin-left: 1rem;
    line-height: 1;
  }

  .error-close:hover {
    opacity: 0.7;
  }

  /* Loading Overlay */
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
  }

  .loading-content {
    text-align: center;
    padding: 2rem;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--border-color, #e0e0e0);
    border-top: 4px solid var(--accent-color, #007bff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .loading-message {
    color: var(--text-secondary, #666666);
    margin: 0;
  }

  /* Main Layout */
  .app-layout {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
  }

  .app-layout.loading {
    pointer-events: none;
    opacity: 0.7;
  }

  .main-panels {
    display: flex;
    flex: 1;
    min-height: 0;
    border-bottom: 1px solid var(--border-color, #e0e0e0);
  }

  .directory-panel {
    flex: 0 0 300px;
    border-right: 1px solid var(--border-color, #e0e0e0);
    background-color: var(--bg-secondary, #f8f9fa);
  }

  .playlist-panel {
    flex: 1;
    min-width: 0;
    background-color: var(--bg-primary, #ffffff);
  }

  .player-panel {
    flex: 0 0 auto;
    background-color: var(--bg-primary, #ffffff);
  }

  /* Debug Panel */
  .debug-panel {
    position: fixed;
    bottom: 10px;
    right: 10px;
    background-color: var(--bg-secondary, #f8f9fa);
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 4px;
    padding: 0.5rem;
    max-width: 400px;
    max-height: 300px;
    overflow: auto;
    font-size: 0.8rem;
    z-index: 100;
  }

  .debug-content {
    margin-top: 0.5rem;
  }

  .debug-section {
    margin-bottom: 1rem;
  }

  .debug-section h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
  }

  .debug-section pre {
    background-color: var(--bg-primary, #ffffff);
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid var(--border-color, #e0e0e0);
    overflow-x: auto;
    font-size: 0.7rem;
    margin: 0;
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .music-player-app {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --accent-color: #4299e1;
      --error-bg: #742a2a;
      --error-text: #feb2b2;
      --error-border: #9b2c2c;
    }

    .loading-overlay {
      background-color: rgba(45, 55, 72, 0.9);
    }
  }

  /* Responsive design */
  @media (max-width: 1024px) {
    .directory-panel {
      flex: 0 0 250px;
    }
  }

  @media (max-width: 768px) {
    .main-panels {
      flex-direction: column;
    }
    
    .directory-panel {
      flex: 0 0 200px;
      border-right: none;
      border-bottom: 1px solid var(--border-color, #e0e0e0);
    }
    
    .playlist-panel {
      flex: 1;
    }

    /* Mobile-specific optimizations */
    .app-layout {
      font-size: 0.9rem;
    }
  }

  @media (max-width: 480px) {
    .directory-panel {
      flex: 0 0 150px;
    }
    
    .debug-panel {
      position: relative;
      bottom: auto;
      right: auto;
      margin: 1rem;
      max-width: none;
    }

    /* Mobile-specific optimizations */
    .app-layout {
      font-size: 0.85rem;
    }

    .main-panels {
      min-height: calc(100vh - 120px); /* Account for smaller player controls */
    }
  }

  /* High DPI displays */
  @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    .app-layout {
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
  }

  /* Landscape orientation on mobile */
  @media (max-width: 768px) and (orientation: landscape) {
    .main-panels {
      flex-direction: row;
    }
    
    .directory-panel {
      flex: 0 0 200px;
      border-right: 1px solid var(--border-color, #e0e0e0);
      border-bottom: none;
    }
  }

  /* Touch device optimizations */
  @media (hover: none) and (pointer: coarse) {
    .app-layout {
      /* Increase touch targets */
      --touch-target-size: 44px;
    }
    
    /* Disable hover effects on touch devices */
    .shortcut-item:hover,
    .track-row:hover {
      background-color: inherit;
    }
  }
</style>
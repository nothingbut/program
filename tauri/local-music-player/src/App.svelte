<script lang="ts">
  import { onMount } from 'svelte';
  import { _, locale } from 'svelte-i18n';
  import { listen } from '@tauri-apps/api/event';
  import DirectoryPanel from './lib/components/DirectoryPanel.svelte';
  import PlaylistPanel from './lib/components/PlaylistPanel.svelte';
  import PlayerControls from './lib/components/PlayerControls.svelte';
  import LanguageSwitcher from './lib/components/LanguageSwitcher.svelte';
  import { setDynamicTitle } from './lib/utils/window';
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
    confirmationDialog,
    initializePersistence
  } from './lib/stores';
  import { playbackApi, directoryApi, stateApi, handleApiError, handleApiErrorLegacy } from './lib/api';
  import type { Directory, Track } from './lib/types';
  import { createAppError, ErrorCategory, ErrorSeverity } from './lib/errors';
  import ToastNotifications from './lib/components/ToastNotifications.svelte';
  import ConfirmationDialog from './lib/components/ConfirmationDialog.svelte';

  // Global application state
  let isInitialized = $state(false);
  let globalError = $state<string | null>(null);
  let showErrorDetails = $state(false);

  // Reactive values from stores
  const currentTrack = $derived($playbackState.currentTrack);
  const isPlaying = $derived($playbackState.isPlaying);
  const currentTime = $derived($playbackState.currentTime);
  const duration = $derived($playbackState.duration);
  const volume = $derived($playbackState.volume);
  const navState = $derived($navigationState);

  /**
   * Initialize the application on mount
   */
  onMount(async () => {
    // Set up audio event listeners
    setupAudioEventListeners();
    
    try {
      await initializeApp();
    } catch (error) {
      handleGlobalError(error, 'Failed to initialize application');
    }
  });

  /**
   * Initialize application with proper error handling
   */
  async function initializeApp() {
    uiActions.setLoading(true, 'Initializing MP3 Player...');
    
    try {
      // Initialize persistence system
      await initializePersistence();
      
      // Load saved application state
      await loadAppState();
      
      // Initialize playlist manager
      playlistManager.setAutoPlay(true);
      
      // Mark as initialized
      isInitialized = true;
      
      // Clear any previous errors
      clearGlobalError();
      
    } catch (error) {
      console.error('App initialization failed:', error);
      throw error;
    } finally {
      uiActions.setLoading(false);
    }
  }

  /**
   * Load application state from backend
   */
  async function loadAppState() {
    try {
      // Load directories
      const savedDirectories = await directoryApi.getAll();
      // Clear existing directories and add loaded ones
      directoryActions.clearDirectories();
      savedDirectories.forEach(dir => directoryActions.addDirectory(dir));
      
      // Try to load full app state
      try {
        const appState = await stateApi.load();
        
        // Restore selected directory if it still exists
        if (appState.selectedDirectory) {
          const selectedDir = savedDirectories.find(d => d.id === appState.selectedDirectory);
          if (selectedDir) {
            directoryActions.selectDirectory(selectedDir);
            
            // Restore playlist for selected directory
            if (appState.currentPlaylist.length > 0) {
              playlistActions.setPlaylist(appState.currentPlaylist);
            }
          }
        }
        
        // Restore shuffle mode
        if (appState.isShuffleMode) {
          shuffleActions.setShuffle(true);
        }
        
        // Restore playback state (but don't auto-play)
        if (appState.playbackState.currentTrack) {
          playbackActions.setCurrentTrack(appState.playbackState.currentTrack);
          playbackActions.setVolume(appState.playbackState.volume);
        }
        
      } catch (stateError) {
        // State loading failed, but that's okay - we'll start fresh
        console.warn('Could not load saved app state:', stateError);
      }
      
    } catch (error) {
      console.error('Failed to load app state:', error);
      throw error;
    }
  }

  /**
   * Save current application state
   */
  async function saveAppState() {
    try {
      const appState = {
        directories: $directories,
        selectedDirectory: $selectedDirectory?.id || null,
        currentPlaylist: $currentPlaylist,
        playbackState: $playbackState,
        isShuffleMode: $isShuffleMode,
        windowGeometry: {
          x: window.screenX || 0,
          y: window.screenY || 0,
          width: window.innerWidth,
          height: window.innerHeight
        }
      };
      
      await stateApi.save(appState);
    } catch (error) {
      console.warn('Failed to save app state:', error);
      // Don't throw - this shouldn't break the app
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
        await selectDirectory(directory);
      }
      
      // Save state
      await saveAppState();
      
    } catch (error) {
      handleGlobalError(error, 'Failed to add directory');
    }
  }

  /**
   * Handle directory selection and scanning
   */
  async function handleDirectorySelect(event: CustomEvent<{ directory: Directory }>) {
    const { directory } = event.detail;
    try {
      await selectDirectory(directory);
    } catch (error) {
      handleGlobalError(error, `Failed to scan directory: ${directory.name}`);
    }
  }

  /**
   * Select and scan a directory
   */
  async function selectDirectory(directory: Directory) {
    uiActions.setLoading(true, `Scanning ${directory.name}...`);
    
    try {
      // Update selected directory
      directoryActions.selectDirectory(directory);
      
      // Scan for tracks
      const tracks = await directoryApi.scan(directory.id);
      playlistActions.setPlaylist(tracks);
      
      // Clear any previous selection if tracks changed
      if ($selectedTrack && !tracks.find(t => t.id === $selectedTrack?.id)) {
        playlistActions.selectTrack(null);
      }
      
      // Save state
      await saveAppState();
      
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
      
      // Remove from local state first for immediate UI feedback
      directoryActions.removeDirectory(directory.id);
      
      // Clear playlist if this was the selected directory
      if ($selectedDirectory?.id === directory.id) {
        directoryActions.selectDirectory(null);
        playlistActions.clearPlaylist();
        playlistActions.selectTrack(null);
      }
      
      // Save state
      await saveAppState();
      
    } catch (error) {
      handleGlobalError(error, 'Failed to remove directory');
      // Reload directories to restore consistent state
      try {
        const dirs = await directoryApi.getAll();
        directoryActions.clearDirectories();
        dirs.forEach(dir => directoryActions.addDirectory(dir));
      } catch (reloadError) {
        console.error('Failed to reload directories:', reloadError);
      }
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
    const { track } = event.detail;
    try {
      // Select the track first
      playlistActions.selectTrack(track);
      
      // Start playback
      await startPlayback(track);
      
    } catch (error) {
      handleGlobalError(error, `Failed to play track: ${track.title}`);
    }
  }

  /**
   * Start playback for a specific track
   */
  async function startPlayback(track: Track) {
    try {
      // Update playback state optimistically
      playbackActions.setCurrentTrack(track);
      playbackActions.setPlaying(true);
      
      // Call backend to start playback
      await playbackApi.playTrack(track);
      
      // Save state
      await saveAppState();
      
    } catch (error) {
      // Revert optimistic update on failure
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
          const firstTrack = playlist[0];
          playlistActions.selectTrack(firstTrack);
          await startPlayback(firstTrack);
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
      
      // Save state
      await saveAppState();
      
    } catch (error) {
      handleGlobalError(error, 'Failed to toggle playback');
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
        await startPlayback($selectedTrack);
      }
    } catch (error) {
      handleGlobalError(error, 'Failed to play previous track');
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
        await startPlayback($selectedTrack);
      }
    } catch (error) {
      handleGlobalError(error, 'Failed to play next track');
    }
  }

  /**
   * Handle seek operation
   */
  async function handleSeek(event: CustomEvent<{ time: number }>) {
    try {
      const { time } = event.detail;
      
      // Update local state optimistically
      playbackActions.setCurrentTime(time);
      
      // Call backend
      await playbackApi.seekTo(time);
      
    } catch (error) {
      handleGlobalError(error, 'Failed to seek');
      // Revert optimistic update by getting current state
      try {
        const state = await playbackApi.getState();
        playbackActions.setCurrentTime(state.currentTime);
      } catch (stateError) {
        console.error('Failed to get playback state:', stateError);
      }
    }
  }

  /**
   * Handle volume change
   */
  async function handleVolumeChange(event: CustomEvent<{ volume: number }>) {
    try {
      const { volume } = event.detail;
      
      // Update local state optimistically
      playbackActions.setVolume(volume);
      
      // Call backend
      await playbackApi.setVolume(volume);
      
      // Save state
      await saveAppState();
      
    } catch (error) {
      handleGlobalError(error, 'Failed to change volume');
    }
  }

  /**
   * Handle shuffle toggle
   */
  function handleShuffleToggle() {
    try {
      shuffleActions.toggleShuffle();
      
      // Save state asynchronously
      saveAppState().catch(error => {
        console.warn('Failed to save shuffle state:', error);
      });
      
    } catch (error) {
      handleGlobalError(error, 'Failed to toggle shuffle mode');
    }
  }

  /**
   * Handle notification display
   */
  function handleShowNotification(event: CustomEvent<{ message: string; type: string }>) {
    const { message, type } = event.detail;
    uiActions.showToast(message, type as 'info' | 'success' | 'warning' | 'error');
  }

  /**
   * Handle track end (auto-play next)
   */
  async function handleTrackEnd() {
    try {
      const success = playlistManager.onTrackEnd();
      if (success && $selectedTrack) {
        await startPlayback($selectedTrack);
      } else {
        // No next track, stop playback
        playbackActions.setPlaying(false);
        await saveAppState();
      }
    } catch (error) {
      handleGlobalError(error, 'Failed to auto-play next track');
    }
  }

  /**
   * Set up audio event listeners from Tauri backend
   */
  async function setupAudioEventListeners() {
    try {
      // Listen for position changes
      await listen('position-changed', (event) => {
        const position = event.payload as number;
        playbackActions.setCurrentTime(position);
      });

      // Listen for track started events
      await listen('track-started', (event) => {
        const track = event.payload as Track;
        playbackActions.setCurrentTrack(track);
        playbackActions.setPlaying(true);
      });

      // Listen for track paused events
      await listen('track-paused', () => {
        playbackActions.setPlaying(false);
      });

      // Listen for track resumed events
      await listen('track-resumed', () => {
        playbackActions.setPlaying(true);
      });

      // Listen for track stopped events
      await listen('track-stopped', () => {
        playbackActions.setPlaying(false);
        playbackActions.setCurrentTime(0);
      });

      // Listen for track finished events
      await listen('track-finished', () => {
        playbackActions.setPlaying(false);
        // Auto-play next track if available
        handleNext();
      });

      // Listen for volume changed events
      await listen('volume-changed', (event) => {
        const volume = event.payload as number;
        playbackActions.setVolume(volume);
      });

      // Listen for playback errors
      await listen('playback-error', (event) => {
        const error = event.payload as string;
        handleGlobalError(new Error(error), 'Playback error');
      });

    } catch (error) {
      console.error('Failed to set up audio event listeners:', error);
    }
  }

  /**
   * Handle errors from child components
   */
  function handleComponentError(event: CustomEvent<{ message: string }>) {
    const { message } = event.detail;
    handleGlobalError(new Error(message), 'Component Error');
  }

  /**
   * Enhanced global error handler with structured error handling
   */
  function handleGlobalError(error: unknown, context?: string) {
    const appError = handleApiError(error, { context });
    const fullMessage = context ? `${context}: ${appError.userMessage}` : appError.userMessage;
    
    console.error('Global error:', fullMessage, appError);
    
    globalError = fullMessage;
    uiActions.showError(appError);
    
    // Also show as toast for better visibility
    uiActions.addToast(appError.userMessage, 'error', 8000);
    
    // Auto-clear error after 10 seconds
    setTimeout(() => {
      if (globalError === fullMessage) {
        clearGlobalError();
      }
    }, 10000);
  }

  /**
   * Legacy error handler for backward compatibility
   */
  function handleGlobalErrorLegacy(error: unknown, context?: string) {
    const message = handleApiErrorLegacy(error);
    const fullMessage = context ? `${context}: ${message}` : message;
    
    console.error('Global error:', fullMessage, error);
    
    globalError = fullMessage;
    uiActions.showSimpleError(fullMessage);
    
    // Auto-clear error after 8 seconds
    setTimeout(() => {
      if (globalError === fullMessage) {
        clearGlobalError();
      }
    }, 8000);
  }

  /**
   * Clear global error state
   */
  function clearGlobalError() {
    globalError = null;
    uiActions.clearError();
  }

  /**
   * Handle keyboard shortcuts
   */
  function handleGlobalKeydown(event: KeyboardEvent) {
    // Only handle if not focused on an input element
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
      return;
    }
    
    switch (event.code) {
      case 'Space':
        event.preventDefault();
        handlePlayPause();
        break;
      case 'ArrowLeft':
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          handlePrevious();
        }
        break;
      case 'ArrowRight':
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          handleNext();
        }
        break;
      case 'KeyS':
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          handleShuffleToggle();
        }
        break;
    }
  }

  // Auto-save state periodically
  let saveInterval: number;
  onMount(() => {
    saveInterval = setInterval(() => {
      if (isInitialized) {
        saveAppState().catch(error => {
          console.warn('Periodic state save failed:', error);
        });
      }
    }, 30000); // Save every 30 seconds
    
    return () => {
      if (saveInterval) {
        clearInterval(saveInterval);
      }
    };
  });

  // Save state before unload
  function handleBeforeUnload() {
    if (isInitialized) {
      // Use synchronous approach for beforeunload
      try {
        saveAppState();
      } catch (error) {
        console.warn('Failed to save state before unload:', error);
      }
    }
  }

  // Track end detection (simplified - in real implementation this would come from backend events)
  let trackEndTimer: number | null = null;
  
  $effect(() => {
    if (isPlaying && currentTrack && duration > 0) {
      // Clear existing timer
      if (trackEndTimer) {
        clearTimeout(trackEndTimer);
      }
      
      // Set timer for track end (with some buffer)
      const remainingTime = Math.max(0, (duration - currentTime - 1) * 1000);
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

  // Update window title when language or current track changes
  $effect(() => {
    if (isInitialized && $locale) {
      const appTitle = $_('app.title', { default: 'Local MP3 Player' });
      setDynamicTitle(appTitle, currentTrack).catch(error => {
        console.warn('Failed to update window title:', error);
      });
    }
  });
</script>

<svelte:window 
  onkeydown={handleGlobalKeydown} 
  onbeforeunload={handleBeforeUnload}
/>

<div class="app" data-testid="mp3-player-app">
  <!-- Global Error Banner -->
  {#if globalError}
    <div class="global-error-banner" data-testid="global-error">
      <div class="error-content">
        <div class="error-message">
          <strong>Error:</strong> {globalError}
        </div>
        <div class="error-actions">
          <button 
            class="error-toggle" 
            onclick={() => showErrorDetails = !showErrorDetails}
            title="Toggle error details"
          >
            {showErrorDetails ? '▼' : '▶'}
          </button>
          <button 
            class="error-close" 
            onclick={clearGlobalError}
            title="Dismiss error"
          >
            ×
          </button>
        </div>
      </div>
      {#if showErrorDetails}
        <div class="error-details">
          <pre>{JSON.stringify($errorState, null, 2)}</pre>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Loading Overlay -->
  {#if $isLoading}
    <div class="loading-overlay" data-testid="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p class="loading-message">{$isLoading || $_('app.loading', { default: 'Loading...' })}</p>
      </div>
    </div>
  {/if}

  <!-- Main Application Layout -->
  <div class="app-layout" class:disabled={$isLoading}>
    <!-- Main Content Area: Left-Right Split Layout -->
    <div class="main-content">
      <!-- Left Panel: Directory Management -->
      <div class="left-panel">
        <DirectoryPanel
          directories={$directories}
          selectedDirectory={$selectedDirectory}
          loading={$isLoading}
          on:directoryAdd={handleDirectoryAdd}
          on:directorySelect={handleDirectorySelect}
          on:directoryRemove={handleDirectoryRemove}
          on:error={handleComponentError}
        />
      </div>

      <!-- Right Panel: Playlist -->
      <div class="right-panel">
        <PlaylistPanel
          tracks={$currentPlaylist}
          selectedTrack={$selectedTrack}
          loading={$isLoading}
          on:trackSelect={handleTrackSelect}
          on:trackPlay={handleTrackPlay}
          on:error={handleComponentError}
        />
      </div>
    </div>

    <!-- Bottom Panel: Player Controls -->
    <div class="bottom-panel">
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
        on:showNotification={handleShowNotification}
      />
    </div>
  </div>

  <!-- Status Bar (Optional) -->
  <div class="status-bar">
    <div class="status-left">
      {#if $selectedDirectory}
        <span class="status-item">
          📁 {$selectedDirectory.name}
        </span>
      {/if}
      {#if $currentPlaylist.length > 0}
        <span class="status-item">
          🎵 {$currentPlaylist.length} {$_('playlist.title', { default: 'tracks' })}
        </span>
      {/if}
      <a href="/demo" class="status-item demo-link" target="_blank">
        🌐 I18n Demo
      </a>
    </div>
    <div class="status-right">
      <LanguageSwitcher />
      {#if $isShuffleMode}
        <span class="status-item shuffle-indicator">🔀 {$_('player.shuffle', { default: 'Shuffle' })}</span>
      {/if}
      {#if isInitialized}
        <span class="status-item ready-indicator">● {$_('app.ready', { default: 'Ready' })}</span>
      {/if}
    </div>
  </div>

  <!-- Toast Notifications -->
  <ToastNotifications />

  <!-- Global Confirmation Dialog -->
  {#if $confirmationDialog}
    <ConfirmationDialog
      isOpen={$confirmationDialog.isOpen}
      title={$confirmationDialog.title}
      message={$confirmationDialog.message}
      confirmText={$confirmationDialog.confirmText}
      cancelText={$confirmationDialog.cancelText}
      destructive={$confirmationDialog.destructive}
      on:confirm={async () => {
        try {
          await $confirmationDialog.onConfirm();
        } catch (error) {
          handleGlobalError(error, 'Confirmation action failed');
        } finally {
          uiActions.closeConfirmation();
        }
      }}
      on:cancel={async () => {
        try {
          if ($confirmationDialog.onCancel) {
            await $confirmationDialog.onCancel();
          }
        } catch (error) {
          console.warn('Cancel action failed:', error);
        } finally {
          uiActions.closeConfirmation();
        }
      }}
      on:close={() => uiActions.closeConfirmation()}
    />
  {/if}
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: var(--bg-primary, #ffffff);
    color: var(--text-primary, #333333);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    overflow: hidden;
  }

  /* Global Error Banner */
  .global-error-banner {
    background: linear-gradient(135deg, #fee, #fdd);
    border-bottom: 1px solid var(--error-border, #fcc);
    color: var(--error-text, #c33);
    z-index: 1000;
  }

  .error-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  .error-message {
    flex: 1;
    font-size: 0.9rem;
  }

  .error-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .error-toggle, .error-close {
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

  .error-toggle:hover, .error-close:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }

  .error-details {
    padding: 0.5rem 1rem;
    border-top: 1px solid var(--error-border, #fcc);
    background-color: rgba(255, 255, 255, 0.5);
  }

  .error-details pre {
    margin: 0;
    font-size: 0.8rem;
    overflow-x: auto;
    max-height: 200px;
    overflow-y: auto;
  }

  /* Loading Overlay */
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(2px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
  }

  .loading-content {
    text-align: center;
    padding: 2rem;
    background-color: var(--bg-primary, #ffffff);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .loading-spinner {
    width: 48px;
    height: 48px;
    border: 4px solid var(--border-light, #f0f0f0);
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
    font-size: 0.9rem;
  }

  /* Main Layout */
  .app-layout {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    transition: opacity 0.2s ease;
  }

  .app-layout.disabled {
    opacity: 0.7;
    pointer-events: none;
  }

  .main-content {
    display: flex;
    flex: 1;
    min-height: 0;
  }

  /* Left-Right Split Layout */
  .left-panel {
    flex: 0 0 320px;
    min-width: 280px;
    max-width: 400px;
    background-color: var(--bg-secondary, #f8f9fa);
    border-right: 1px solid var(--border-color, #e0e0e0);
    resize: horizontal;
    overflow: hidden;
  }

  .right-panel {
    flex: 1;
    min-width: 0;
    background-color: var(--bg-primary, #ffffff);
  }

  /* Bottom Panel */
  .bottom-panel {
    flex: 0 0 auto;
    background-color: var(--bg-primary, #ffffff);
    border-top: 1px solid var(--border-color, #e0e0e0);
  }

  /* Status Bar */
  .status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 1rem;
    background-color: var(--bg-secondary, #f8f9fa);
    border-top: 1px solid var(--border-color, #e0e0e0);
    font-size: 0.8rem;
    color: var(--text-secondary, #666666);
    min-height: 24px;
  }

  .status-left, .status-right {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .shuffle-indicator {
    color: var(--accent-color, #007bff);
  }

  .ready-indicator {
    color: var(--success-color, #28a745);
  }

  .demo-link {
    color: var(--accent-color, #007bff);
    text-decoration: none;
    cursor: pointer;
  }

  .demo-link:hover {
    text-decoration: underline;
  }

  /* CSS Custom Properties for Theming */
  :root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-hover: #f0f0f0;
    --text-primary: #333333;
    --text-secondary: #666666;
    --border-color: #e0e0e0;
    --border-light: #f0f0f0;
    --accent-color: #007bff;
    --accent-hover: #0056b3;
    --accent-light: #e3f2fd;
    --success-color: #28a745;
    --error-bg: #fee;
    --error-text: #c33;
    --error-border: #fcc;
  }

  /* Dark Mode Support */
  @media (prefers-color-scheme: dark) {
    :root {
      --bg-primary: #2d3748;
      --bg-secondary: #1a202c;
      --bg-hover: #4a5568;
      --text-primary: #f7fafc;
      --text-secondary: #a0aec0;
      --border-color: #4a5568;
      --border-light: #2d3748;
      --accent-color: #4299e1;
      --accent-hover: #3182ce;
      --accent-light: #2d3748;
      --success-color: #48bb78;
      --error-bg: #742a2a;
      --error-text: #feb2b2;
      --error-border: #9b2c2c;
    }

    .loading-overlay {
      background-color: rgba(45, 55, 72, 0.95);
    }

    .loading-content {
      background-color: var(--bg-primary);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
  }

  /* Responsive Design */
  @media (max-width: 1024px) {
    .left-panel {
      flex: 0 0 280px;
      min-width: 250px;
    }
  }

  @media (max-width: 768px) {
    .main-content {
      flex-direction: column;
    }
    
    .left-panel {
      flex: 0 0 200px;
      min-width: auto;
      max-width: none;
      border-right: none;
      border-bottom: 1px solid var(--border-color, #e0e0e0);
      resize: none;
    }
    
    .right-panel {
      flex: 1;
    }
    
    .status-bar {
      padding: 0.25rem 0.5rem;
    }
    
    .status-left, .status-right {
      gap: 0.5rem;
    }
  }

  @media (max-width: 480px) {
    .left-panel {
      flex: 0 0 150px;
    }
    
    .status-bar {
      font-size: 0.75rem;
    }
    
    .error-content {
      padding: 0.5rem;
      flex-direction: column;
      align-items: stretch;
      gap: 0.5rem;
    }
    
    .error-actions {
      justify-content: flex-end;
    }
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    :root {
      --border-color: #000000;
      --border-light: #666666;
    }
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .loading-spinner {
      animation: none;
    }
    
    .app-layout {
      transition: none;
    }
    
    .error-toggle, .error-close {
      transition: none;
    }
  }
</style>
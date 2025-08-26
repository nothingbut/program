/**
 * Playlist Manager - Advanced playlist control logic
 * Handles sequential and shuffle playback modes with boundary conditions
 */

import { writable, derived, get, type Readable } from 'svelte/store';
import type { Track } from '../types';
import { currentPlaylist, selectedTrack, playlistActions } from './playlist';
import { isShuffleMode, playbackActions } from './playback';

/**
 * Playlist manager state
 */
interface PlaylistManagerState {
  currentIndex: number;
  shuffleHistory: string[]; // Track IDs in shuffle order
  shuffleQueue: string[]; // Remaining tracks in shuffle mode
  isAutoPlayEnabled: boolean;
  repeatMode: 'none' | 'one' | 'all';
}

const initialState: PlaylistManagerState = {
  currentIndex: -1,
  shuffleHistory: [],
  shuffleQueue: [],
  isAutoPlayEnabled: true,
  repeatMode: 'none'
};

/**
 * Internal playlist manager state store
 */
const playlistManagerState = writable<PlaylistManagerState>(initialState);

/**
 * Derived store for current track index in playlist
 */
export const currentTrackIndex: Readable<number> = derived(
  [currentPlaylist, selectedTrack],
  ([$playlist, $selectedTrack]) => {
    if (!$selectedTrack || $playlist.length === 0) return -1;
    return $playlist.findIndex(track => track.id === $selectedTrack.id);
  }
);

/**
 * Derived store for navigation availability
 */
export const navigationState: Readable<{
  canGoNext: boolean;
  canGoPrevious: boolean;
  hasPlaylist: boolean;
  isAtStart: boolean;
  isAtEnd: boolean;
}> = derived(
  [currentPlaylist, currentTrackIndex, playlistManagerState, isShuffleMode],
  ([$playlist, $currentIndex, $managerState, $isShuffleMode]) => {
    const hasPlaylist = $playlist.length > 0;
    const isAtStart = $currentIndex <= 0;
    const isAtEnd = $currentIndex >= $playlist.length - 1;
    
    let canGoNext = false;
    let canGoPrevious = false;

    if (hasPlaylist) {
      if ($isShuffleMode) {
        // In shuffle mode, we can always go next (will generate new random if needed)
        canGoNext = true;
        // Can go previous if we have shuffle history
        canGoPrevious = $managerState.shuffleHistory.length > 0;
      } else {
        // In sequential mode
        canGoNext = !isAtEnd || $managerState.repeatMode === 'all';
        canGoPrevious = !isAtStart || $managerState.repeatMode === 'all';
      }
    }

    return {
      canGoNext,
      canGoPrevious,
      hasPlaylist,
      isAtStart,
      isAtEnd
    };
  }
);

/**
 * Playlist Manager Actions
 */
export const playlistManager = {
  /**
   * Initialize shuffle queue when shuffle mode is enabled
   */
  initializeShuffle(): void {
    const playlist = get(currentPlaylist);
    const currentTrack = get(selectedTrack);
    
    if (playlist.length === 0) return;

    // Create shuffle queue excluding current track
    const availableTracks = playlist
      .filter(track => track.id !== currentTrack?.id)
      .map(track => track.id);
    
    // Shuffle the available tracks
    const shuffledQueue = [...availableTracks];
    for (let i = shuffledQueue.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffledQueue[i], shuffledQueue[j]] = [shuffledQueue[j], shuffledQueue[i]];
    }

    playlistManagerState.update(state => ({
      ...state,
      shuffleQueue: shuffledQueue,
      shuffleHistory: currentTrack ? [currentTrack.id] : []
    }));
  },

  /**
   * Get the next track based on current playback mode
   */
  getNextTrack(): Track | null {
    const playlist = get(currentPlaylist);
    const currentIndex = get(currentTrackIndex);
    const managerState = get(playlistManagerState);
    const shuffleMode = get(isShuffleMode);

    if (playlist.length === 0) return null;

    if (shuffleMode) {
      return this._getNextShuffleTrack();
    } else {
      return this._getNextSequentialTrack();
    }
  },

  /**
   * Get the previous track based on current playback mode
   */
  getPreviousTrack(): Track | null {
    const playlist = get(currentPlaylist);
    const currentIndex = get(currentTrackIndex);
    const managerState = get(playlistManagerState);
    const shuffleMode = get(isShuffleMode);

    if (playlist.length === 0) return null;

    if (shuffleMode) {
      return this._getPreviousShuffleTrack();
    } else {
      return this._getPreviousSequentialTrack();
    }
  },

  /**
   * Play the next track and update state
   */
  playNext(): boolean {
    const nextTrack = this.getNextTrack();
    if (!nextTrack) return false;

    this._selectAndUpdateState(nextTrack);
    return true;
  },

  /**
   * Play the previous track and update state
   */
  playPrevious(): boolean {
    const previousTrack = this.getPreviousTrack();
    if (!previousTrack) return false;

    this._selectAndUpdateState(previousTrack);
    return true;
  },

  /**
   * Handle track end - auto-play next if enabled
   */
  onTrackEnd(): boolean {
    const managerState = get(playlistManagerState);
    
    if (!managerState.isAutoPlayEnabled) return false;

    // Handle repeat one mode
    if (managerState.repeatMode === 'one') {
      const currentTrack = get(selectedTrack);
      if (currentTrack) {
        // Restart the same track
        playbackActions.setCurrentTime(0);
        return true;
      }
    }

    // Try to play next track
    return this.playNext();
  },

  /**
   * Set auto-play mode
   */
  setAutoPlay(enabled: boolean): void {
    playlistManagerState.update(state => ({
      ...state,
      isAutoPlayEnabled: enabled
    }));
  },

  /**
   * Set repeat mode
   */
  setRepeatMode(mode: 'none' | 'one' | 'all'): void {
    playlistManagerState.update(state => ({
      ...state,
      repeatMode: mode
    }));
  },

  /**
   * Reset manager state when playlist changes
   */
  onPlaylistChange(): void {
    playlistManagerState.update(state => ({
      ...state,
      currentIndex: -1,
      shuffleHistory: [],
      shuffleQueue: []
    }));
  },

  /**
   * Handle shuffle mode toggle
   */
  onShuffleModeChange(shuffleEnabled: boolean): void {
    if (shuffleEnabled) {
      this.initializeShuffle();
    } else {
      // Clear shuffle state when disabled
      playlistManagerState.update(state => ({
        ...state,
        shuffleHistory: [],
        shuffleQueue: []
      }));
    }
  },

  /**
   * Get next track in shuffle mode
   */
  _getNextShuffleTrack(): Track | null {
    const playlist = get(currentPlaylist);
    const managerState = get(playlistManagerState);

    // If shuffle queue is empty, refill it (excluding current track)
    if (managerState.shuffleQueue.length === 0) {
      const currentTrack = get(selectedTrack);
      const availableTracks = playlist
        .filter(track => track.id !== currentTrack?.id)
        .map(track => track.id);

      if (availableTracks.length === 0) {
        // Only one track in playlist, handle repeat mode
        if (managerState.repeatMode === 'all' && currentTrack) {
          return currentTrack;
        }
        return null;
      }

      // Shuffle available tracks
      const shuffledQueue = [...availableTracks];
      for (let i = shuffledQueue.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffledQueue[i], shuffledQueue[j]] = [shuffledQueue[j], shuffledQueue[i]];
      }

      playlistManagerState.update(state => ({
        ...state,
        shuffleQueue: shuffledQueue
      }));
    }

    // Get next track from shuffle queue
    const nextTrackId = get(playlistManagerState).shuffleQueue[0];
    const nextTrack = playlist.find(track => track.id === nextTrackId);

    return nextTrack || null;
  },

  /**
   * Get previous track in shuffle mode
   */
  _getPreviousShuffleTrack(): Track | null {
    const playlist = get(currentPlaylist);
    const managerState = get(playlistManagerState);

    if (managerState.shuffleHistory.length < 2) {
      // No previous track in history
      return null;
    }

    // Get the track before current in history
    const previousTrackId = managerState.shuffleHistory[managerState.shuffleHistory.length - 2];
    const previousTrack = playlist.find(track => track.id === previousTrackId);

    return previousTrack || null;
  },

  /**
   * Get next track in sequential mode
   */
  _getNextSequentialTrack(): Track | null {
    const playlist = get(currentPlaylist);
    const currentIndex = get(currentTrackIndex);
    const managerState = get(playlistManagerState);

    if (currentIndex < playlist.length - 1) {
      // Next track in sequence
      return playlist[currentIndex + 1];
    } else if (playlist.length > 0 && managerState.repeatMode !== 'none') {
      // Loop back to first track (default behavior unless repeat is explicitly 'none')
      return playlist[0];
    }

    return null;
  },

  /**
   * Get previous track in sequential mode
   */
  _getPreviousSequentialTrack(): Track | null {
    const playlist = get(currentPlaylist);
    const currentIndex = get(currentTrackIndex);
    const managerState = get(playlistManagerState);

    if (currentIndex > 0) {
      // Previous track in sequence
      return playlist[currentIndex - 1];
    } else if (playlist.length > 0) {
      // Loop to last track (default behavior for boundary)
      return playlist[playlist.length - 1];
    }

    return null;
  },

  /**
   * Select track and update internal state
   */
  _selectAndUpdateState(track: Track): void {
    const playlist = get(currentPlaylist);
    const shuffleMode = get(isShuffleMode);
    
    // Update selected track
    playlistActions.selectTrack(track);
    
    if (shuffleMode) {
      playlistManagerState.update(state => {
        const newHistory = [...state.shuffleHistory];
        const newQueue = [...state.shuffleQueue];
        
        // Add to history if not already there
        if (!newHistory.includes(track.id)) {
          newHistory.push(track.id);
        }
        
        // Remove from queue if present
        const queueIndex = newQueue.indexOf(track.id);
        if (queueIndex !== -1) {
          newQueue.splice(queueIndex, 1);
        }
        
        return {
          ...state,
          shuffleHistory: newHistory,
          shuffleQueue: newQueue
        };
      });
    }
  },

  /**
   * Get current manager state (for debugging)
   */
  getState(): PlaylistManagerState {
    return get(playlistManagerState);
  }
};

// Subscribe to shuffle mode changes
isShuffleMode.subscribe(shuffleEnabled => {
  playlistManager.onShuffleModeChange(shuffleEnabled);
});

// Subscribe to playlist changes
currentPlaylist.subscribe(() => {
  playlistManager.onPlaylistChange();
});
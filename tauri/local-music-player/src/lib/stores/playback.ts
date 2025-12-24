/**
 * Playback state and control stores
 * Manages audio playback state and shuffle mode
 */

import { writable, derived, type Readable } from 'svelte/store';
import type { PlaybackState, Track } from '../types';
import { createDefaultPlaybackState } from '../types';

/**
 * Store for the current playback state
 */
export const playbackState = writable<PlaybackState>(createDefaultPlaybackState());

/**
 * Store for shuffle mode toggle
 */
export const isShuffleMode = writable<boolean>(false);

/**
 * Derived store for the currently playing track
 */
export const currentTrack: Readable<Track | null> = derived(
  playbackState,
  ($playbackState) => $playbackState.currentTrack
);

/**
 * Derived store for play/pause state
 */
export const isPlaying: Readable<boolean> = derived(
  playbackState,
  ($playbackState) => $playbackState.isPlaying
);

/**
 * Derived store for current playback time
 */
export const currentTime: Readable<number> = derived(
  playbackState,
  ($playbackState) => $playbackState.currentTime
);

/**
 * Derived store for track duration
 */
export const duration: Readable<number> = derived(
  playbackState,
  ($playbackState) => $playbackState.duration
);

/**
 * Derived store for volume level
 */
export const volume: Readable<number> = derived(
  playbackState,
  ($playbackState) => $playbackState.volume
);

/**
 * Derived store for playback progress (0-1)
 */
export const playbackProgress: Readable<number> = derived(
  playbackState,
  ($playbackState) => {
    if ($playbackState.duration === 0) return 0;
    return $playbackState.currentTime / $playbackState.duration;
  }
);

/**
 * Derived store for formatted time display
 */
export const formattedTime: Readable<{
  current: string;
  duration: string;
  remaining: string;
}> = derived(
  playbackState,
  ($playbackState) => {
    const formatTime = (seconds: number): string => {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = Math.floor(seconds % 60);
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    };

    const current = formatTime($playbackState.currentTime);
    const durationFormatted = formatTime($playbackState.duration);
    const remaining = formatTime($playbackState.duration - $playbackState.currentTime);

    return {
      current,
      duration: durationFormatted,
      remaining: `-${remaining}`
    };
  }
);

/**
 * Utility functions for playback control
 */
export const playbackActions = {
  /**
   * Update the current track
   */
  setCurrentTrack: (track: Track | null) => {
    playbackState.update(state => ({
      ...state,
      currentTrack: track,
      currentTime: 0,
      duration: track?.duration || 0
    }));
  },

  /**
   * Set playing state
   */
  setPlaying: (playing: boolean) => {
    playbackState.update(state => ({
      ...state,
      isPlaying: playing
    }));
  },

  /**
   * Update current playback time
   */
  setCurrentTime: (time: number) => {
    playbackState.update(state => ({
      ...state,
      currentTime: Math.max(0, Math.min(time, state.duration))
    }));
  },

  /**
   * Set track duration
   */
  setDuration: (duration: number) => {
    playbackState.update(state => ({
      ...state,
      duration: Math.max(0, duration)
    }));
  },

  /**
   * Set volume level
   */
  setVolume: (volume: number) => {
    playbackState.update(state => ({
      ...state,
      volume: Math.max(0, Math.min(1, volume))
    }));
  },

  /**
   * Toggle play/pause
   */
  togglePlayPause: () => {
    playbackState.update(state => ({
      ...state,
      isPlaying: !state.isPlaying
    }));
  },

  /**
   * Reset playback state
   */
  resetPlayback: () => {
    playbackState.set(createDefaultPlaybackState());
  },

  /**
   * Update entire playback state
   */
  updatePlaybackState: (newState: Partial<PlaybackState>) => {
    playbackState.update(state => ({
      ...state,
      ...newState
    }));
  }
};

/**
 * Shuffle mode utility functions
 */
export const shuffleActions = {
  /**
   * Toggle shuffle mode
   */
  toggleShuffle: () => {
    isShuffleMode.update(shuffle => !shuffle);
  },

  /**
   * Set shuffle mode
   */
  setShuffle: (shuffle: boolean) => {
    isShuffleMode.set(shuffle);
  }
};
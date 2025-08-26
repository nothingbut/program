/**
 * Playlist and track selection stores
 * Manages the current playlist and selected track
 */

import { writable, derived, type Readable } from 'svelte/store';
import type { Track } from '../types';

/**
 * Store for the current playlist (tracks from selected directory)
 */
export const currentPlaylist = writable<Track[]>([]);

/**
 * Store for the currently selected track in the playlist
 */
export const selectedTrack = writable<Track | null>(null);

/**
 * Derived store that provides the selected track's index in the playlist
 */
export const selectedTrackIndex: Readable<number> = derived(
  [currentPlaylist, selectedTrack],
  ([$playlist, $selectedTrack]) => {
    if (!$selectedTrack) return -1;
    return $playlist.findIndex(track => track.id === $selectedTrack.id);
  }
);

/**
 * Derived store that checks if there are tracks in the playlist
 */
export const hasPlaylist: Readable<boolean> = derived(
  currentPlaylist,
  ($playlist) => $playlist.length > 0
);

/**
 * Derived store that provides playlist statistics
 */
export const playlistStats: Readable<{
  trackCount: number;
  totalDuration: number;
  formattedDuration: string;
}> = derived(
  currentPlaylist,
  ($playlist) => {
    const trackCount = $playlist.length;
    const totalDuration = $playlist.reduce((sum, track) => sum + track.duration, 0);
    
    const hours = Math.floor(totalDuration / 3600);
    const minutes = Math.floor((totalDuration % 3600) / 60);
    const seconds = Math.floor(totalDuration % 60);
    
    let formattedDuration = '';
    if (hours > 0) {
      formattedDuration = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    } else {
      formattedDuration = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    return {
      trackCount,
      totalDuration,
      formattedDuration
    };
  }
);

/**
 * Utility functions for playlist management
 */
export const playlistActions = {
  /**
   * Set the current playlist
   */
  setPlaylist: (tracks: Track[]) => {
    currentPlaylist.set(tracks);
    // Clear selection when playlist changes
    selectedTrack.set(null);
  },

  /**
   * Add tracks to the current playlist
   */
  addTracks: (tracks: Track[]) => {
    currentPlaylist.update(playlist => [...playlist, ...tracks]);
  },

  /**
   * Select a track
   */
  selectTrack: (track: Track | null) => {
    selectedTrack.set(track);
  },

  /**
   * Get the next track in the playlist
   */
  getNextTrack: (isShuffleMode: boolean = false): Track | null => {
    let nextTrack: Track | null = null;
    let currentIndex = -1;
    let playlist: Track[] = [];

    // Get current values
    const unsubscribePlaylist = currentPlaylist.subscribe(p => playlist = p);
    const unsubscribeSelected = selectedTrackIndex.subscribe(i => currentIndex = i);
    
    unsubscribePlaylist();
    unsubscribeSelected();

    if (playlist.length === 0) return null;

    if (isShuffleMode) {
      // Random selection
      const randomIndex = Math.floor(Math.random() * playlist.length);
      nextTrack = playlist[randomIndex];
    } else {
      // Sequential selection
      if (currentIndex >= 0 && currentIndex < playlist.length - 1) {
        nextTrack = playlist[currentIndex + 1];
      } else if (playlist.length > 0) {
        // Loop back to first track
        nextTrack = playlist[0];
      }
    }

    return nextTrack;
  },

  /**
   * Get the previous track in the playlist
   */
  getPreviousTrack: (): Track | null => {
    let previousTrack: Track | null = null;
    let currentIndex = -1;
    let playlist: Track[] = [];

    // Get current values
    const unsubscribePlaylist = currentPlaylist.subscribe(p => playlist = p);
    const unsubscribeSelected = selectedTrackIndex.subscribe(i => currentIndex = i);
    
    unsubscribePlaylist();
    unsubscribeSelected();

    if (playlist.length === 0) return null;

    if (currentIndex > 0) {
      previousTrack = playlist[currentIndex - 1];
    } else if (playlist.length > 0) {
      // Loop to last track
      previousTrack = playlist[playlist.length - 1];
    }

    return previousTrack;
  },

  /**
   * Find a track by ID
   */
  findTrackById: (trackId: string): Track | null => {
    let foundTrack: Track | null = null;
    currentPlaylist.subscribe(playlist => {
      foundTrack = playlist.find(t => t.id === trackId) || null;
    })();
    return foundTrack;
  },

  /**
   * Clear the current playlist
   */
  clearPlaylist: () => {
    currentPlaylist.set([]);
    selectedTrack.set(null);
  }
};
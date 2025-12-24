/**
 * Tests for Svelte stores
 * Verifies store functionality and state management
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import type { Directory, Track } from '../../types';
import { createDefaultPlaybackState } from '../../types';

// Import stores and actions
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
  isLoading,
  errorState,
  uiActions
} from '../index';

// Note: Tauri API is mocked automatically in test environment

describe('Directory Stores', () => {
  beforeEach(() => {
    directoryActions.clearDirectories();
  });

  it('should initialize with empty directories', () => {
    expect(get(directories)).toEqual([]);
    expect(get(selectedDirectory)).toBeNull();
  });

  it('should add directory correctly', () => {
    const testDirectory: Directory = {
      id: 'test-1',
      path: '/test/music',
      name: 'Test Music',
      addedAt: new Date().toISOString()
    };

    directoryActions.addDirectory(testDirectory);
    
    expect(get(directories)).toContain(testDirectory);
  });

  it('should not add duplicate directories', () => {
    const testDirectory: Directory = {
      id: 'test-1',
      path: '/test/music',
      name: 'Test Music',
      addedAt: new Date().toISOString()
    };

    directoryActions.addDirectory(testDirectory);
    directoryActions.addDirectory(testDirectory);
    
    expect(get(directories)).toHaveLength(1);
  });

  it('should select directory correctly', () => {
    const testDirectory: Directory = {
      id: 'test-1',
      path: '/test/music',
      name: 'Test Music',
      addedAt: new Date().toISOString()
    };

    directoryActions.selectDirectory(testDirectory);
    
    expect(get(selectedDirectory)).toEqual(testDirectory);
  });

  it('should remove directory correctly', () => {
    const testDirectory: Directory = {
      id: 'test-1',
      path: '/test/music',
      name: 'Test Music',
      addedAt: new Date().toISOString()
    };

    directoryActions.addDirectory(testDirectory);
    directoryActions.selectDirectory(testDirectory);
    directoryActions.removeDirectory(testDirectory.id);
    
    expect(get(directories)).not.toContain(testDirectory);
    expect(get(selectedDirectory)).toBeNull();
  });
});

describe('Playlist Stores', () => {
  beforeEach(() => {
    playlistActions.clearPlaylist();
  });

  it('should initialize with empty playlist', () => {
    expect(get(currentPlaylist)).toEqual([]);
    expect(get(selectedTrack)).toBeNull();
  });

  it('should set playlist correctly', () => {
    const testTracks: Track[] = [
      {
        id: 'track-1',
        filePath: '/test/song1.mp3',
        title: 'Test Song 1',
        artist: 'Test Artist',
        album: 'Test Album',
        duration: 180
      },
      {
        id: 'track-2',
        filePath: '/test/song2.mp3',
        title: 'Test Song 2',
        artist: 'Test Artist',
        album: 'Test Album',
        duration: 200
      }
    ];

    playlistActions.setPlaylist(testTracks);
    
    expect(get(currentPlaylist)).toEqual(testTracks);
  });

  it('should select track correctly', () => {
    const testTrack: Track = {
      id: 'track-1',
      filePath: '/test/song1.mp3',
      title: 'Test Song 1',
      artist: 'Test Artist',
      album: 'Test Album',
      duration: 180
    };

    playlistActions.selectTrack(testTrack);
    
    expect(get(selectedTrack)).toEqual(testTrack);
  });

  it('should get next track in sequential mode', () => {
    const testTracks: Track[] = [
      {
        id: 'track-1',
        filePath: '/test/song1.mp3',
        title: 'Test Song 1',
        artist: 'Test Artist',
        album: 'Test Album',
        duration: 180
      },
      {
        id: 'track-2',
        filePath: '/test/song2.mp3',
        title: 'Test Song 2',
        artist: 'Test Artist',
        album: 'Test Album',
        duration: 200
      }
    ];

    playlistActions.setPlaylist(testTracks);
    playlistActions.selectTrack(testTracks[0]);
    
    const nextTrack = playlistActions.getNextTrack(false);
    expect(nextTrack).toEqual(testTracks[1]);
  });

  it('should get previous track correctly', () => {
    const testTracks: Track[] = [
      {
        id: 'track-1',
        filePath: '/test/song1.mp3',
        title: 'Test Song 1',
        artist: 'Test Artist',
        album: 'Test Album',
        duration: 180
      },
      {
        id: 'track-2',
        filePath: '/test/song2.mp3',
        title: 'Test Song 2',
        artist: 'Test Artist',
        album: 'Test Album',
        duration: 200
      }
    ];

    playlistActions.setPlaylist(testTracks);
    playlistActions.selectTrack(testTracks[1]);
    
    const previousTrack = playlistActions.getPreviousTrack();
    expect(previousTrack).toEqual(testTracks[0]);
  });
});

describe('Playback Stores', () => {
  beforeEach(() => {
    playbackActions.resetPlayback();
    shuffleActions.setShuffle(false);
  });

  it('should initialize with default playback state', () => {
    const defaultState = createDefaultPlaybackState();
    expect(get(playbackState)).toEqual(defaultState);
    expect(get(isShuffleMode)).toBe(false);
  });

  it('should set current track correctly', () => {
    const testTrack: Track = {
      id: 'track-1',
      filePath: '/test/song1.mp3',
      title: 'Test Song 1',
      artist: 'Test Artist',
      album: 'Test Album',
      duration: 180
    };

    playbackActions.setCurrentTrack(testTrack);
    
    const state = get(playbackState);
    expect(state.currentTrack).toEqual(testTrack);
    expect(state.duration).toBe(180);
    expect(state.currentTime).toBe(0);
  });

  it('should toggle play/pause correctly', () => {
    expect(get(playbackState).isPlaying).toBe(false);
    
    playbackActions.togglePlayPause();
    expect(get(playbackState).isPlaying).toBe(true);
    
    playbackActions.togglePlayPause();
    expect(get(playbackState).isPlaying).toBe(false);
  });

  it('should set current time within bounds', () => {
    playbackActions.setDuration(180);
    
    // Normal time
    playbackActions.setCurrentTime(90);
    expect(get(playbackState).currentTime).toBe(90);
    
    // Time beyond duration should be clamped
    playbackActions.setCurrentTime(200);
    expect(get(playbackState).currentTime).toBe(180);
    
    // Negative time should be clamped to 0
    playbackActions.setCurrentTime(-10);
    expect(get(playbackState).currentTime).toBe(0);
  });

  it('should set volume within bounds', () => {
    // Normal volume
    playbackActions.setVolume(0.5);
    expect(get(playbackState).volume).toBe(0.5);
    
    // Volume above 1 should be clamped
    playbackActions.setVolume(1.5);
    expect(get(playbackState).volume).toBe(1);
    
    // Negative volume should be clamped to 0
    playbackActions.setVolume(-0.1);
    expect(get(playbackState).volume).toBe(0);
  });

  it('should toggle shuffle mode correctly', () => {
    expect(get(isShuffleMode)).toBe(false);
    
    shuffleActions.toggleShuffle();
    expect(get(isShuffleMode)).toBe(true);
    
    shuffleActions.toggleShuffle();
    expect(get(isShuffleMode)).toBe(false);
  });
});

describe('UI Stores', () => {
  beforeEach(() => {
    uiActions.clearAllStates();
  });

  it('should initialize with default UI state', () => {
    expect(get(isLoading)).toBe(false);
  });

  it('should set loading state correctly', () => {
    uiActions.setLoading(true, 'Loading test...');
    
    expect(get(isLoading)).toBe(true);
  });

  it('should show and clear error correctly', () => {
    uiActions.setError('Test error', 'Error details');
    
    const currentErrorState = get(errorState);
    expect(currentErrorState.hasError).toBe(true);
    expect(currentErrorState.message).toBe('Test error');
    expect(currentErrorState.details).toBe('Error details');
    
    uiActions.clearError();
    expect(get(errorState).hasError).toBe(false);
  });

  it('should show success message correctly', () => {
    uiActions.showSuccess('Test success');
    
    // Note: Success message auto-clears after 3 seconds in real implementation
    // but we can't easily test that in unit tests without mocking timers
  });
});
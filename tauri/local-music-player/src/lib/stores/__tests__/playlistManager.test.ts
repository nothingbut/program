/**
 * Unit tests for playlist manager
 * Tests sequential and shuffle playback logic, boundary conditions, and auto-play
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';
import { playlistManager, currentTrackIndex, navigationState } from '../playlistManager';
import { currentPlaylist, selectedTrack, playlistActions } from '../playlist';
import { isShuffleMode, shuffleActions, playbackActions } from '../playback';
import type { Track } from '../../types';

// Mock tracks for testing
const createMockTrack = (id: string, title: string): Track => ({
  id,
  filePath: `/music/${title}.mp3`,
  title,
  artist: 'Test Artist',
  album: 'Test Album',
  trackNumber: parseInt(id),
  duration: 180, // 3 minutes
  coverArt: undefined
});

const mockTracks: Track[] = [
  createMockTrack('1', 'Track One'),
  createMockTrack('2', 'Track Two'),
  createMockTrack('3', 'Track Three'),
  createMockTrack('4', 'Track Four'),
  createMockTrack('5', 'Track Five')
];

describe('Playlist Manager', () => {
  beforeEach(() => {
    // Reset all stores
    playlistActions.clearPlaylist();
    shuffleActions.setShuffle(false);
    playbackActions.resetPlayback();
    
    // Set up a basic playlist
    playlistActions.setPlaylist(mockTracks);
  });

  describe('Sequential Playback', () => {
    beforeEach(() => {
      shuffleActions.setShuffle(false);
    });

    it('should get next track in sequence', () => {
      // Select first track
      playlistActions.selectTrack(mockTracks[0]);
      
      const nextTrack = playlistManager.getNextTrack();
      expect(nextTrack).toEqual(mockTracks[1]);
    });

    it('should get previous track in sequence', () => {
      // Select third track
      playlistActions.selectTrack(mockTracks[2]);
      
      const previousTrack = playlistManager.getPreviousTrack();
      expect(previousTrack).toEqual(mockTracks[1]);
    });

    it('should handle boundary conditions at start', () => {
      // Select first track
      playlistActions.selectTrack(mockTracks[0]);
      
      const previousTrack = playlistManager.getPreviousTrack();
      expect(previousTrack).toEqual(mockTracks[4]); // Should loop to last track
    });

    it('should handle boundary conditions at end', () => {
      // Select last track
      playlistActions.selectTrack(mockTracks[4]);
      
      // Set repeat mode to 'all' to enable looping
      playlistManager.setRepeatMode('all');
      
      const nextTrack = playlistManager.getNextTrack();
      expect(nextTrack).toEqual(mockTracks[0]); // Should loop to first track
    });

    it('should play next track and update state', () => {
      // Select first track
      playlistActions.selectTrack(mockTracks[0]);
      
      const success = playlistManager.playNext();
      expect(success).toBe(true);
      expect(get(selectedTrack)).toEqual(mockTracks[1]);
    });

    it('should play previous track and update state', () => {
      // Select third track
      playlistActions.selectTrack(mockTracks[2]);
      
      const success = playlistManager.playPrevious();
      expect(success).toBe(true);
      expect(get(selectedTrack)).toEqual(mockTracks[1]);
    });

    it('should handle empty playlist', () => {
      playlistActions.clearPlaylist();
      
      const nextTrack = playlistManager.getNextTrack();
      const previousTrack = playlistManager.getPreviousTrack();
      
      expect(nextTrack).toBeNull();
      expect(previousTrack).toBeNull();
    });

    it('should handle single track playlist', () => {
      const singleTrack = [mockTracks[0]];
      playlistActions.setPlaylist(singleTrack);
      playlistActions.selectTrack(singleTrack[0]);
      
      // Set repeat mode to 'all' to enable looping for single track
      playlistManager.setRepeatMode('all');
      
      const nextTrack = playlistManager.getNextTrack();
      const previousTrack = playlistManager.getPreviousTrack();
      
      // Should loop back to the same track
      expect(nextTrack).toEqual(singleTrack[0]);
      expect(previousTrack).toEqual(singleTrack[0]);
    });
  });

  describe('Shuffle Playback', () => {
    beforeEach(() => {
      shuffleActions.setShuffle(true);
      // Mock Math.random for predictable shuffle behavior
      vi.spyOn(Math, 'random').mockReturnValue(0.5);
    });

    it('should initialize shuffle queue when enabled', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.initializeShuffle();
      
      const state = playlistManager.getState();
      expect(state.shuffleQueue.length).toBe(4); // All tracks except current
      expect(state.shuffleHistory).toContain(mockTracks[0].id);
    });

    it('should get random track in shuffle mode', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.initializeShuffle();
      
      const nextTrack = playlistManager.getNextTrack();
      expect(nextTrack).toBeDefined();
      expect(nextTrack?.id).not.toBe(mockTracks[0].id); // Should not be current track
    });

    it('should maintain shuffle history', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.initializeShuffle();
      
      // Play next track
      playlistManager.playNext();
      const selectedAfterNext = get(selectedTrack);
      
      const state = playlistManager.getState();
      expect(state.shuffleHistory).toContain(mockTracks[0].id);
      if (selectedAfterNext) {
        expect(state.shuffleHistory).toContain(selectedAfterNext.id);
      }
    });

    it('should get previous track from shuffle history', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.initializeShuffle();
      
      // Manually add to history to test previous functionality
      const state = playlistManager.getState();
      state.shuffleHistory.push(mockTracks[1].id, mockTracks[2].id);
      
      playlistActions.selectTrack(mockTracks[2]);
      const previousTrack = playlistManager.getPreviousTrack();
      expect(previousTrack).toEqual(mockTracks[1]);
    });

    it('should handle empty shuffle history for previous', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.initializeShuffle();
      
      const previousTrack = playlistManager.getPreviousTrack();
      expect(previousTrack).toBeNull(); // No previous track in history
    });

    it('should refill shuffle queue when empty', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.initializeShuffle();
      
      // Manually empty the shuffle queue
      const state = playlistManager.getState();
      state.shuffleQueue.length = 0;
      
      const nextTrack = playlistManager.getNextTrack();
      expect(nextTrack).toBeDefined();
      
      const newState = playlistManager.getState();
      expect(newState.shuffleQueue.length).toBeGreaterThan(0);
    });

    it('should handle single track in shuffle mode', () => {
      const singleTrack = [mockTracks[0]];
      playlistActions.setPlaylist(singleTrack);
      playlistActions.selectTrack(singleTrack[0]);
      
      // Set repeat mode to all for single track handling
      playlistManager.setRepeatMode('all');
      
      const nextTrack = playlistManager.getNextTrack();
      expect(nextTrack).toEqual(singleTrack[0]);
    });
  });

  describe('Navigation State', () => {
    it('should correctly report navigation availability in sequential mode', () => {
      shuffleActions.setShuffle(false);
      playlistActions.selectTrack(mockTracks[2]); // Middle track
      
      const navState = get(navigationState);
      expect(navState.canGoNext).toBe(true);
      expect(navState.canGoPrevious).toBe(true);
      expect(navState.hasPlaylist).toBe(true);
      expect(navState.isAtStart).toBe(false);
      expect(navState.isAtEnd).toBe(false);
    });

    it('should correctly report navigation at playlist boundaries', () => {
      shuffleActions.setShuffle(false);
      
      // Test at start
      playlistActions.selectTrack(mockTracks[0]);
      let navState = get(navigationState);
      expect(navState.isAtStart).toBe(true);
      expect(navState.canGoPrevious).toBe(true); // Can loop to end
      
      // Test at end
      playlistActions.selectTrack(mockTracks[4]);
      navState = get(navigationState);
      expect(navState.isAtEnd).toBe(true);
      expect(navState.canGoNext).toBe(true); // Can loop to start
    });

    it('should correctly report navigation in shuffle mode', () => {
      shuffleActions.setShuffle(true);
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.initializeShuffle();
      
      const navState = get(navigationState);
      expect(navState.canGoNext).toBe(true); // Always true in shuffle
      expect(navState.canGoPrevious).toBe(true); // Has history
    });

    it('should handle empty playlist navigation', () => {
      playlistActions.clearPlaylist();
      
      const navState = get(navigationState);
      expect(navState.canGoNext).toBe(false);
      expect(navState.canGoPrevious).toBe(false);
      expect(navState.hasPlaylist).toBe(false);
    });
  });

  describe('Auto-play and Track End Handling', () => {
    it('should auto-play next track on track end', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.setAutoPlay(true);
      
      const success = playlistManager.onTrackEnd();
      expect(success).toBe(true);
      expect(get(selectedTrack)).toEqual(mockTracks[1]);
    });

    it('should not auto-play when disabled', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.setAutoPlay(false);
      
      const success = playlistManager.onTrackEnd();
      expect(success).toBe(false);
      expect(get(selectedTrack)).toEqual(mockTracks[0]); // Should remain same
    });

    it('should handle repeat one mode', () => {
      playlistActions.selectTrack(mockTracks[0]);
      playlistManager.setRepeatMode('one');
      playlistManager.setAutoPlay(true);
      
      // Mock playback actions
      const setCurrentTimeSpy = vi.spyOn(playbackActions, 'setCurrentTime');
      
      const success = playlistManager.onTrackEnd();
      expect(success).toBe(true);
      expect(setCurrentTimeSpy).toHaveBeenCalledWith(0);
      expect(get(selectedTrack)).toEqual(mockTracks[0]); // Should remain same track
    });

    it('should handle end of playlist without repeat', () => {
      playlistActions.selectTrack(mockTracks[4]); // Last track
      playlistManager.setRepeatMode('none');
      playlistManager.setAutoPlay(true);
      
      const success = playlistManager.onTrackEnd();
      expect(success).toBe(false); // Should not continue when repeat is 'none'
      expect(get(selectedTrack)).toEqual(mockTracks[4]); // Should remain on last track
    });
  });

  describe('Repeat Modes', () => {
    it('should set and get repeat mode', () => {
      playlistManager.setRepeatMode('all');
      expect(playlistManager.getState().repeatMode).toBe('all');
      
      playlistManager.setRepeatMode('one');
      expect(playlistManager.getState().repeatMode).toBe('one');
      
      playlistManager.setRepeatMode('none');
      expect(playlistManager.getState().repeatMode).toBe('none');
    });

    it('should handle repeat all mode at playlist end', () => {
      playlistManager.setRepeatMode('all');
      playlistActions.selectTrack(mockTracks[4]); // Last track
      
      const nextTrack = playlistManager.getNextTrack();
      expect(nextTrack).toEqual(mockTracks[0]); // Should loop to first
    });

    it('should handle repeat all mode at playlist start', () => {
      playlistManager.setRepeatMode('all');
      playlistActions.selectTrack(mockTracks[0]); // First track
      
      const previousTrack = playlistManager.getPreviousTrack();
      expect(previousTrack).toEqual(mockTracks[4]); // Should loop to last
    });
  });

  describe('Playlist Change Handling', () => {
    it('should reset state when playlist changes', () => {
      // Set up some state
      playlistActions.selectTrack(mockTracks[0]);
      shuffleActions.setShuffle(true);
      playlistManager.initializeShuffle();
      
      // Verify state exists
      let state = playlistManager.getState();
      expect(state.shuffleHistory.length).toBeGreaterThan(0);
      
      // Change playlist
      const newTracks = [createMockTrack('6', 'New Track')];
      playlistActions.setPlaylist(newTracks);
      
      // Verify state was reset
      state = playlistManager.getState();
      expect(state.currentIndex).toBe(-1);
      expect(state.shuffleHistory).toEqual([]);
      expect(state.shuffleQueue).toEqual([]);
    });

    it('should handle shuffle mode changes', () => {
      playlistActions.selectTrack(mockTracks[0]);
      
      // Enable shuffle
      shuffleActions.setShuffle(true);
      let state = playlistManager.getState();
      expect(state.shuffleQueue.length).toBeGreaterThan(0);
      
      // Disable shuffle
      shuffleActions.setShuffle(false);
      state = playlistManager.getState();
      expect(state.shuffleHistory).toEqual([]);
      expect(state.shuffleQueue).toEqual([]);
    });
  });

  describe('Current Track Index', () => {
    it('should correctly track current track index', () => {
      playlistActions.selectTrack(mockTracks[2]);
      expect(get(currentTrackIndex)).toBe(2);
      
      playlistActions.selectTrack(mockTracks[0]);
      expect(get(currentTrackIndex)).toBe(0);
      
      playlistActions.selectTrack(null);
      expect(get(currentTrackIndex)).toBe(-1);
    });

    it('should handle track not in playlist', () => {
      const outsideTrack = createMockTrack('999', 'Outside Track');
      playlistActions.selectTrack(outsideTrack);
      expect(get(currentTrackIndex)).toBe(-1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle corrupted state gracefully', () => {
      // Manually corrupt the state
      const state = playlistManager.getState();
      state.shuffleHistory = ['nonexistent-id'];
      state.shuffleQueue = ['another-nonexistent-id'];
      
      // Should not crash and should handle gracefully
      const nextTrack = playlistManager.getNextTrack();
      expect(nextTrack).toBeDefined(); // Should still work
    });

    it('should handle rapid mode switching', () => {
      playlistActions.selectTrack(mockTracks[0]);
      
      // Rapidly switch modes
      shuffleActions.setShuffle(true);
      shuffleActions.setShuffle(false);
      shuffleActions.setShuffle(true);
      
      // Should still work correctly
      const nextTrack = playlistManager.getNextTrack();
      expect(nextTrack).toBeDefined();
    });

    it('should handle concurrent operations', () => {
      playlistActions.selectTrack(mockTracks[0]);
      shuffleActions.setShuffle(true);
      
      // Simulate concurrent operations
      const promises = [
        Promise.resolve(playlistManager.playNext()),
        Promise.resolve(playlistManager.getNextTrack()),
        Promise.resolve(playlistManager.initializeShuffle())
      ];
      
      return Promise.all(promises).then(() => {
        // Should complete without errors
        expect(get(selectedTrack)).toBeDefined();
      });
    });
  });
});

describe('Integration with Stores', () => {
  beforeEach(() => {
    playlistActions.clearPlaylist();
    shuffleActions.setShuffle(false);
    playbackActions.resetPlayback();
  });

  it('should integrate correctly with playlist store', () => {
    playlistActions.setPlaylist(mockTracks);
    expect(get(currentPlaylist)).toEqual(mockTracks);
    
    playlistActions.selectTrack(mockTracks[1]);
    expect(get(selectedTrack)).toEqual(mockTracks[1]);
    expect(get(currentTrackIndex)).toBe(1);
  });

  it('should integrate correctly with shuffle store', () => {
    expect(get(isShuffleMode)).toBe(false);
    
    shuffleActions.setShuffle(true);
    expect(get(isShuffleMode)).toBe(true);
    
    shuffleActions.toggleShuffle();
    expect(get(isShuffleMode)).toBe(false);
  });

  it('should react to store changes', () => {
    playlistActions.setPlaylist(mockTracks);
    playlistActions.selectTrack(mockTracks[0]);
    
    // Change shuffle mode and verify manager reacts
    shuffleActions.setShuffle(true);
    const state = playlistManager.getState();
    expect(state.shuffleQueue.length).toBeGreaterThan(0);
  });
});
/**
 * Application state persistence stores
 * Handles saving and loading application state to/from backend
 */

import { writable, derived, get, type Readable } from 'svelte/store';
import { invoke } from '@tauri-apps/api/core';
import type { AppState, WindowGeometry } from '../types';
import { createDefaultAppState } from '../types';

// Import other stores for state composition
import { directories, selectedDirectory } from './directories';
import { currentPlaylist } from './playlist';
import { playbackState, isShuffleMode } from './playback';
import { uiActions } from './ui';

/**
 * Store for window geometry
 */
export const windowGeometry = writable<WindowGeometry>({
  x: 100,
  y: 100,
  width: 1200,
  height: 800
});

/**
 * Derived store that combines all application state
 */
export const appState: Readable<AppState> = derived(
  [directories, selectedDirectory, currentPlaylist, playbackState, isShuffleMode, windowGeometry],
  ([$directories, $selectedDirectory, $currentPlaylist, $playbackState, $isShuffleMode, $windowGeometry]) => ({
    directories: $directories,
    selectedDirectory: $selectedDirectory?.id || null,
    currentPlaylist: $currentPlaylist,
    playbackState: $playbackState,
    isShuffleMode: $isShuffleMode,
    windowGeometry: $windowGeometry
  })
);

/**
 * Store for persistence state
 */
export const persistenceState = writable<{
  isLoading: boolean;
  lastSaved: Date | null;
  lastLoaded: Date | null;
  autoSaveEnabled: boolean;
}>({
  isLoading: false,
  lastSaved: null,
  lastLoaded: null,
  autoSaveEnabled: true
});

/**
 * Auto-save interval ID
 */
let autoSaveInterval: number | null = null;

/**
 * Utility functions for state persistence
 */
export const persistenceActions = {
  /**
   * Save current application state to backend
   */
  saveAppState: async (): Promise<void> => {
    try {
      persistenceState.update(state => ({ ...state, isLoading: true }));
      
      const currentState = get(appState);
      await invoke('save_app_state', { state: currentState });
      
      persistenceState.update(state => ({
        ...state,
        isLoading: false,
        lastSaved: new Date()
      }));
      
      console.log('Application state saved successfully');
    } catch (error) {
      persistenceState.update(state => ({ ...state, isLoading: false }));
      console.error('Failed to save application state:', error);
      uiActions.showError('Failed to save application state', error as string);
      throw error;
    }
  },

  /**
   * Load application state from backend
   */
  loadAppState: async (): Promise<void> => {
    try {
      persistenceState.update(state => ({ ...state, isLoading: true }));
      
      const savedState = await invoke<AppState>('load_app_state');
      
      // Update individual stores with loaded state
      directories.set(savedState.directories || []);
      
      // Find and set selected directory
      if (savedState.selectedDirectory) {
        const selectedDir = savedState.directories?.find(d => d.id === savedState.selectedDirectory);
        selectedDirectory.set(selectedDir || null);
      } else {
        selectedDirectory.set(null);
      }
      
      currentPlaylist.set(savedState.currentPlaylist || []);
      playbackState.set(savedState.playbackState || createDefaultAppState().playbackState);
      isShuffleMode.set(savedState.isShuffleMode || false);
      windowGeometry.set(savedState.windowGeometry || createDefaultAppState().windowGeometry);
      
      persistenceState.update(state => ({
        ...state,
        isLoading: false,
        lastLoaded: new Date()
      }));
      
      console.log('Application state loaded successfully');
    } catch (error) {
      persistenceState.update(state => ({ ...state, isLoading: false }));
      console.error('Failed to load application state:', error);
      
      // Initialize with default state if loading fails
      const defaultState = createDefaultAppState();
      directories.set(defaultState.directories);
      selectedDirectory.set(null);
      currentPlaylist.set(defaultState.currentPlaylist);
      playbackState.set(defaultState.playbackState);
      isShuffleMode.set(defaultState.isShuffleMode);
      windowGeometry.set(defaultState.windowGeometry);
      
      uiActions.showError('Failed to load saved state, using defaults', error as string);
    }
  },

  /**
   * Enable auto-save functionality
   */
  enableAutoSave: (intervalMs: number = 30000) => {
    persistenceActions.disableAutoSave(); // Clear existing interval
    
    autoSaveInterval = setInterval(async () => {
      try {
        await persistenceActions.saveAppState();
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    }, intervalMs);
    
    persistenceState.update(state => ({ ...state, autoSaveEnabled: true }));
    console.log(`Auto-save enabled with ${intervalMs}ms interval`);
  },

  /**
   * Disable auto-save functionality
   */
  disableAutoSave: () => {
    if (autoSaveInterval) {
      clearInterval(autoSaveInterval);
      autoSaveInterval = null;
    }
    persistenceState.update(state => ({ ...state, autoSaveEnabled: false }));
    console.log('Auto-save disabled');
  },

  /**
   * Update window geometry
   */
  updateWindowGeometry: (geometry: Partial<WindowGeometry>) => {
    windowGeometry.update(current => ({ ...current, ...geometry }));
  },

  /**
   * Reset to default state
   */
  resetToDefaults: () => {
    const defaultState = createDefaultAppState();
    directories.set(defaultState.directories);
    selectedDirectory.set(null);
    currentPlaylist.set(defaultState.currentPlaylist);
    playbackState.set(defaultState.playbackState);
    isShuffleMode.set(defaultState.isShuffleMode);
    windowGeometry.set(defaultState.windowGeometry);
    
    persistenceState.update(state => ({
      ...state,
      lastSaved: null,
      lastLoaded: null
    }));
    
    console.log('Application state reset to defaults');
  }
};

/**
 * Initialize persistence system
 */
export const initializePersistence = async () => {
  try {
    // Load saved state on initialization
    await persistenceActions.loadAppState();
    
    // Enable auto-save by default
    persistenceActions.enableAutoSave();
    
    // Save state when the window is about to close
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        // Attempt to save state synchronously (best effort)
        try {
          persistenceActions.saveAppState();
        } catch (error) {
          console.error('Failed to save state on window close:', error);
        }
      });
    }
  } catch (error) {
    console.error('Failed to initialize persistence system:', error);
  }
};
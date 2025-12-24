/**
 * Directory management stores
 * Handles the list of music directories and current selection
 */

import { writable, derived, type Readable } from 'svelte/store';
import type { Directory } from '../types';

/**
 * Store for all added music directories
 */
export const directories = writable<Directory[]>([]);

/**
 * Store for the currently selected directory
 */
export const selectedDirectory = writable<Directory | null>(null);

/**
 * Derived store that provides the selected directory's ID
 */
export const selectedDirectoryId: Readable<string | null> = derived(
  selectedDirectory,
  ($selectedDirectory) => $selectedDirectory?.id || null
);

/**
 * Derived store that checks if any directories are available
 */
export const hasDirectories: Readable<boolean> = derived(
  directories,
  ($directories) => $directories.length > 0
);

/**
 * Utility functions for directory management
 */
export const directoryActions = {
  /**
   * Add a new directory to the list
   */
  addDirectory: (directory: Directory) => {
    directories.update(dirs => {
      // Check if directory already exists
      const exists = dirs.some(d => d.path === directory.path);
      if (exists) {
        return dirs;
      }
      return [...dirs, directory];
    });
  },

  /**
   * Remove a directory from the list
   */
  removeDirectory: (directoryId: string) => {
    directories.update(dirs => dirs.filter(d => d.id !== directoryId));
    
    // Clear selection if the removed directory was selected
    selectedDirectory.update(selected => {
      if (selected?.id === directoryId) {
        return null;
      }
      return selected;
    });
  },

  /**
   * Select a directory
   */
  selectDirectory: (directory: Directory | null) => {
    selectedDirectory.set(directory);
  },

  /**
   * Find a directory by ID
   */
  findDirectoryById: (directoryId: string): Directory | null => {
    let foundDirectory: Directory | null = null;
    directories.subscribe(dirs => {
      foundDirectory = dirs.find(d => d.id === directoryId) || null;
    })();
    return foundDirectory;
  },

  /**
   * Clear all directories
   */
  clearDirectories: () => {
    directories.set([]);
    selectedDirectory.set(null);
  }
};
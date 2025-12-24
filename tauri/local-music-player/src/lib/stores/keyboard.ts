/**
 * Keyboard shortcuts store and management
 */

import { writable, derived } from 'svelte/store';

// Keyboard shortcut definitions
export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  metaKey?: boolean;
  description: string;
  action: string;
}

// Default keyboard shortcuts
export const DEFAULT_SHORTCUTS: KeyboardShortcut[] = [
  {
    key: ' ',
    description: 'Play/Pause',
    action: 'playPause'
  },
  {
    key: 'ArrowLeft',
    description: 'Previous track',
    action: 'previous'
  },
  {
    key: 'ArrowRight',
    description: 'Next track',
    action: 'next'
  },
  {
    key: 'ArrowUp',
    description: 'Volume up',
    action: 'volumeUp'
  },
  {
    key: 'ArrowDown',
    description: 'Volume down',
    action: 'volumeDown'
  },
  {
    key: 's',
    description: 'Toggle shuffle',
    action: 'toggleShuffle'
  },
  {
    key: 'm',
    description: 'Mute/Unmute',
    action: 'toggleMute'
  },
  {
    key: 'o',
    ctrlKey: true,
    description: 'Open directory',
    action: 'openDirectory'
  },
  {
    key: 'f',
    ctrlKey: true,
    description: 'Search tracks',
    action: 'search'
  },
  {
    key: 'Escape',
    description: 'Clear selection/Close dialogs',
    action: 'escape'
  },
  {
    key: 'Delete',
    description: 'Remove selected directory',
    action: 'removeDirectory'
  },
  {
    key: 'Enter',
    description: 'Play selected track',
    action: 'playSelected'
  }
];

// Keyboard shortcuts store
export const keyboardShortcuts = writable<KeyboardShortcut[]>(DEFAULT_SHORTCUTS);

// Active shortcuts (enabled/disabled state)
export const shortcutsEnabled = writable<boolean>(true);

// Current pressed keys (for debugging)
export const pressedKeys = writable<Set<string>>(new Set());

// Keyboard event handlers registry
type KeyboardHandler = (event: KeyboardEvent) => void | boolean;
const keyboardHandlers = new Map<string, KeyboardHandler[]>();

/**
 * Register a keyboard shortcut handler
 */
export function registerKeyboardHandler(action: string, handler: KeyboardHandler) {
  if (!keyboardHandlers.has(action)) {
    keyboardHandlers.set(action, []);
  }
  keyboardHandlers.get(action)!.push(handler);
}

/**
 * Unregister a keyboard shortcut handler
 */
export function unregisterKeyboardHandler(action: string, handler: KeyboardHandler) {
  const handlers = keyboardHandlers.get(action);
  if (handlers) {
    const index = handlers.indexOf(handler);
    if (index >= 0) {
      handlers.splice(index, 1);
    }
  }
}

/**
 * Check if a keyboard event matches a shortcut
 */
export function matchesShortcut(event: KeyboardEvent, shortcut: KeyboardShortcut): boolean {
  return (
    event.key === shortcut.key &&
    !!event.ctrlKey === !!shortcut.ctrlKey &&
    !!event.altKey === !!shortcut.altKey &&
    !!event.shiftKey === !!shortcut.shiftKey &&
    !!event.metaKey === !!shortcut.metaKey
  );
}

/**
 * Handle global keyboard events
 */
export function handleGlobalKeyboard(event: KeyboardEvent): boolean {
  // Skip if shortcuts are disabled
  if (!shortcutsEnabled) return false;

  // Skip if focused on input elements
  const target = event.target as HTMLElement;
  if (target && (
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    target.contentEditable === 'true'
  )) {
    return false;
  }

  // Find matching shortcut
  let shortcuts: KeyboardShortcut[] = [];
  keyboardShortcuts.subscribe(value => shortcuts = value)();

  for (const shortcut of shortcuts) {
    if (matchesShortcut(event, shortcut)) {
      // Execute handlers for this action
      const handlers = keyboardHandlers.get(shortcut.action) || [];
      let handled = false;

      for (const handler of handlers) {
        const result = handler(event);
        if (result !== false) {
          handled = true;
          break;
        }
      }

      if (handled) {
        event.preventDefault();
        event.stopPropagation();
        return true;
      }
    }
  }

  return false;
}

/**
 * Format shortcut for display
 */
export function formatShortcut(shortcut: KeyboardShortcut): string {
  const parts: string[] = [];

  if (shortcut.ctrlKey) parts.push('Ctrl');
  if (shortcut.altKey) parts.push('Alt');
  if (shortcut.shiftKey) parts.push('Shift');
  if (shortcut.metaKey) parts.push('Cmd');

  // Format key name
  let keyName = shortcut.key;
  switch (keyName) {
    case ' ':
      keyName = 'SPACE';
      break;
    case 'ArrowLeft':
      keyName = '←';
      break;
    case 'ArrowRight':
      keyName = '→';
      break;
    case 'ArrowUp':
      keyName = '↑';
      break;
    case 'ArrowDown':
      keyName = '↓';
      break;
    case 'Escape':
      keyName = 'ESC';
      break;
    case 'Delete':
      keyName = 'DEL';
      break;
    case 'Enter':
      keyName = '↵';
      break;
    default:
      keyName = keyName.toUpperCase();
  }

  parts.push(keyName);

  return parts.join(' + ');
}

/**
 * Get shortcuts grouped by category
 */
export const shortcutsByCategory = derived(keyboardShortcuts, (shortcuts) => {
  const categories = {
    playback: [] as KeyboardShortcut[],
    navigation: [] as KeyboardShortcut[],
    volume: [] as KeyboardShortcut[],
    general: [] as KeyboardShortcut[]
  };

  for (const shortcut of shortcuts) {
    switch (shortcut.action) {
      case 'playPause':
      case 'previous':
      case 'next':
      case 'playSelected':
        categories.playback.push(shortcut);
        break;
      case 'volumeUp':
      case 'volumeDown':
      case 'toggleMute':
        categories.volume.push(shortcut);
        break;
      case 'toggleShuffle':
      case 'search':
      case 'escape':
        categories.navigation.push(shortcut);
        break;
      default:
        categories.general.push(shortcut);
    }
  }

  return categories;
});

// Keyboard actions
export const keyboardActions = {
  /**
   * Enable/disable keyboard shortcuts
   */
  setEnabled(enabled: boolean) {
    shortcutsEnabled.set(enabled);
  },

  /**
   * Update keyboard shortcuts
   */
  setShortcuts(shortcuts: KeyboardShortcut[]) {
    keyboardShortcuts.set(shortcuts);
  },

  /**
   * Add a new keyboard shortcut
   */
  addShortcut(shortcut: KeyboardShortcut) {
    keyboardShortcuts.update(shortcuts => [...shortcuts, shortcut]);
  },

  /**
   * Remove a keyboard shortcut
   */
  removeShortcut(action: string) {
    keyboardShortcuts.update(shortcuts => 
      shortcuts.filter(s => s.action !== action)
    );
  },

  /**
   * Reset to default shortcuts
   */
  resetToDefaults() {
    keyboardShortcuts.set([...DEFAULT_SHORTCUTS]);
  }
};
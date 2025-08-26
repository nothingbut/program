/**
 * Centralized export for all application stores
 * This provides a single import point for components
 */

// Directory stores
export { 
  directories, 
  selectedDirectory, 
  selectedDirectoryId, 
  hasDirectories, 
  directoryActions 
} from './directories';

// Playlist stores
export { 
  currentPlaylist, 
  selectedTrack, 
  selectedTrackIndex, 
  hasPlaylist, 
  playlistStats, 
  playlistActions 
} from './playlist';

// Playback stores
export { 
  playbackState, 
  isShuffleMode, 
  currentTrack, 
  isPlaying, 
  currentTime, 
  duration, 
  volume, 
  playbackProgress, 
  formattedTime, 
  playbackActions, 
  shuffleActions 
} from './playback';

// UI stores
export { 
  isLoading, 
  loadingMessage, 
  errorState, 
  successMessage, 
  confirmationDialog,
  toastNotifications,
  isScanningDirectory, 
  scanningProgress, 
  scanningProgressPercent, 
  isAnyLoading, 
  uiActions 
} from './ui';

// Keyboard stores
export {
  keyboardShortcuts,
  shortcutsEnabled,
  pressedKeys,
  shortcutsByCategory,
  keyboardActions,
  handleGlobalKeyboard,
  registerKeyboardHandler,
  unregisterKeyboardHandler,
  matchesShortcut,
  formatShortcut
} from './keyboard';

// Playlist Manager
export { 
  currentTrackIndex, 
  navigationState, 
  playlistManager 
} from './playlistManager';

// Persistence stores
export { 
  appState, 
  windowGeometry, 
  persistenceState, 
  persistenceActions, 
  initializePersistence 
} from './persistence';
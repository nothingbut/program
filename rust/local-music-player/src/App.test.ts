import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import App from './App.svelte';

// Mock Tauri API
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn()
}));

vi.mock('@tauri-apps/plugin-dialog', () => ({
  open: vi.fn()
}));

// Mock stores
vi.mock('./lib/stores', () => ({
  directories: { subscribe: vi.fn(() => vi.fn()) },
  selectedDirectory: { subscribe: vi.fn(() => vi.fn()) },
  directoryActions: {
    clearDirectories: vi.fn(),
    addDirectory: vi.fn(),
    selectDirectory: vi.fn(),
    removeDirectory: vi.fn()
  },
  currentPlaylist: { subscribe: vi.fn(() => vi.fn()) },
  selectedTrack: { subscribe: vi.fn(() => vi.fn()) },
  playlistActions: {
    setPlaylist: vi.fn(),
    selectTrack: vi.fn(),
    clearPlaylist: vi.fn()
  },
  playbackState: { subscribe: vi.fn(() => vi.fn()) },
  isShuffleMode: { subscribe: vi.fn(() => vi.fn()) },
  playbackActions: {
    setCurrentTrack: vi.fn(),
    setPlaying: vi.fn(),
    setCurrentTime: vi.fn(),
    setVolume: vi.fn()
  },
  shuffleActions: {
    toggleShuffle: vi.fn(),
    setShuffle: vi.fn()
  },
  playlistManager: {
    setAutoPlay: vi.fn(),
    playNext: vi.fn(),
    playPrevious: vi.fn(),
    onTrackEnd: vi.fn(),
    getState: vi.fn(() => ({}))
  },
  navigationState: { subscribe: vi.fn(() => vi.fn()) },
  uiActions: {
    setLoading: vi.fn(),
    showError: vi.fn(),
    clearError: vi.fn()
  },
  isLoading: { subscribe: vi.fn(() => vi.fn()) },
  errorState: { subscribe: vi.fn(() => vi.fn()) },
  persistenceActions: {},
  initializePersistence: vi.fn()
}));

// Mock API
vi.mock('./lib/api', () => ({
  directoryApi: {
    getAll: vi.fn(() => Promise.resolve([])),
    scan: vi.fn(() => Promise.resolve([])),
    remove: vi.fn(() => Promise.resolve())
  },
  playbackApi: {
    playTrack: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    resume: vi.fn(() => Promise.resolve()),
    seekTo: vi.fn(() => Promise.resolve()),
    setVolume: vi.fn(() => Promise.resolve()),
    getState: vi.fn(() => Promise.resolve({
      currentTrack: null,
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      volume: 1.0
    }))
  },
  stateApi: {
    save: vi.fn(() => Promise.resolve()),
    load: vi.fn(() => Promise.resolve({
      directories: [],
      selectedDirectory: null,
      currentPlaylist: [],
      playbackState: {
        currentTrack: null,
        isPlaying: false,
        currentTime: 0,
        duration: 0,
        volume: 1.0
      },
      isShuffleMode: false,
      windowGeometry: { x: 0, y: 0, width: 1200, height: 800 }
    }))
  },
  handleApiError: vi.fn((error) => String(error))
}));

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the main application layout', async () => {
    render(App);
    
    // Check that the main app container is rendered
    expect(screen.getByTestId('mp3-player-app')).toBeInTheDocument();
  });

  it('shows loading overlay when loading', async () => {
    // Mock loading state
    const mockSubscribe = vi.fn((callback) => {
      callback(true); // isLoading = true
      return vi.fn(); // unsubscribe function
    });
    
    vi.doMock('./lib/stores', () => ({
      ...vi.importActual('./lib/stores'),
      isLoading: { subscribe: mockSubscribe }
    }));

    render(App);
    
    // Should show loading overlay
    expect(screen.getByTestId('loading-overlay')).toBeInTheDocument();
  });

  it('has proper layout structure', async () => {
    render(App);
    
    const app = screen.getByTestId('mp3-player-app');
    expect(app).toBeInTheDocument();
    
    // Check for main layout sections
    const leftPanel = app.querySelector('.left-panel');
    const rightPanel = app.querySelector('.right-panel');
    const bottomPanel = app.querySelector('.bottom-panel');
    
    expect(leftPanel).toBeInTheDocument();
    expect(rightPanel).toBeInTheDocument();
    expect(bottomPanel).toBeInTheDocument();
  });

  it('includes status bar', async () => {
    render(App);
    
    const statusBar = screen.getByRole('generic', { name: /status/i }) || 
                     document.querySelector('.status-bar');
    expect(statusBar).toBeInTheDocument();
  });
});
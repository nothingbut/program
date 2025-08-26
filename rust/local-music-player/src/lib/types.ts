/**
 * Core data types for the MP3 player application
 * These interfaces mirror the Rust backend models
 */

export interface Directory {
  id: string;
  path: string;
  name: string;
  addedAt: string; // ISO date string from Rust DateTime<Utc>
}

export interface Track {
  id: string;
  filePath: string;
  title: string;
  artist: string;
  album: string;
  trackNumber?: number;
  duration: number; // seconds
  coverArt?: string; // base64 encoded image data
}

export interface PlaybackState {
  currentTrack: Track | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
}

export interface WindowGeometry {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface AppState {
  directories: Directory[];
  selectedDirectory: string | null;
  currentPlaylist: Track[];
  playbackState: PlaybackState;
  isShuffleMode: boolean;
  windowGeometry: WindowGeometry;
}

/**
 * API Response types for Tauri commands
 */
export type ApiResult<T> = Promise<T>;

/**
 * Component prop types
 */
export interface DirectoryPanelProps {
  directories: Directory[];
  selectedDirectory: Directory | null;
  loading?: boolean;
  onDirectoryAdd: () => void;
  onDirectorySelect: (directory: Directory) => void;
  onDirectoryRemove?: (directory: Directory) => void;
}

export interface PlaylistPanelProps {
  tracks: Track[];
  selectedTrack: Track | null;
  loading?: boolean;
  onTrackSelect: (track: Track) => void;
  onTrackPlay: (track: Track) => void;
}

export interface PlayerControlsProps {
  currentTrack: Track | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  isShuffleMode: boolean;
  volume: number;
  onPlayPause: () => void;
  onPrevious: () => void;
  onNext: () => void;
  onSeek: (time: number) => void;
  onVolumeChange: (volume: number) => void;
  onShuffleToggle: () => void;
}

/**
 * Utility types for UI state management
 */
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  details?: string;
}

/**
 * Event types for component communication
 */
export type DirectorySelectEvent = CustomEvent<{ directory: Directory }>;
export type TrackSelectEvent = CustomEvent<{ track: Track }>;
export type TrackPlayEvent = CustomEvent<{ track: Track }>;
export type PlaybackStateChangeEvent = CustomEvent<{ state: PlaybackState }>;

/**
 * Type guards for runtime type checking
 */
export function isDirectory(obj: any): obj is Directory {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.id === 'string' &&
    typeof obj.path === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.addedAt === 'string'
  );
}

export function isTrack(obj: any): obj is Track {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.id === 'string' &&
    typeof obj.filePath === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.artist === 'string' &&
    typeof obj.album === 'string' &&
    typeof obj.duration === 'number' &&
    (obj.trackNumber === undefined || typeof obj.trackNumber === 'number') &&
    (obj.coverArt === undefined || typeof obj.coverArt === 'string')
  );
}

export function isPlaybackState(obj: any): obj is PlaybackState {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    (obj.currentTrack === null || isTrack(obj.currentTrack)) &&
    typeof obj.isPlaying === 'boolean' &&
    typeof obj.currentTime === 'number' &&
    typeof obj.duration === 'number' &&
    typeof obj.volume === 'number'
  );
}

/**
 * Utility functions for data transformation
 */
export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export function formatTrackInfo(track: Track): string {
  const trackNum = track.trackNumber ? `(${track.trackNumber})` : '';
  return `${track.album}${trackNum}: ${track.title} - ${track.artist}`;
}

export function createDefaultPlaybackState(): PlaybackState {
  return {
    currentTrack: null,
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: 1.0,
  };
}

export function createDefaultAppState(): AppState {
  return {
    directories: [],
    selectedDirectory: null,
    currentPlaylist: [],
    playbackState: createDefaultPlaybackState(),
    isShuffleMode: false,
    windowGeometry: {
      x: 100,
      y: 100,
      width: 1200,
      height: 800,
    },
  };
}
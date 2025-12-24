import { invoke } from '@tauri-apps/api/core';
import type { Directory, Track, PlaybackState, AppState, ApiResult } from './types';

/**
 * Type-safe wrapper for Tauri commands
 * Provides a clean interface between frontend and backend
 */

// Directory Management Commands with enhanced error handling
export const directoryApi = {
  async add(path: string): ApiResult<Directory> {
    return withRetry(
      () => invoke('add_directory', { path }),
      { operation: 'add_directory', path }
    );
  },

  async getAll(): ApiResult<Directory[]> {
    return withRetry(
      () => invoke('get_directories'),
      { operation: 'get_directories' }
    );
  },

  async remove(id: string): ApiResult<void> {
    return withRetry(
      () => invoke('remove_directory', { id }),
      { operation: 'remove_directory', directoryId: id }
    );
  },

  async getById(id: string): ApiResult<Directory | null> {
    return withRetry(
      () => invoke('get_directory', { id }),
      { operation: 'get_directory', directoryId: id }
    );
  },

  async refresh(): ApiResult<string[]> {
    return withRetry(
      () => invoke('refresh_directories'),
      { operation: 'refresh_directories' }
    );
  },

  async scan(directoryId: string): ApiResult<Track[]> {
    return withRetry(
      () => invoke('scan_directory', { directoryId }),
      { operation: 'scan_directory', directoryId },
      1 // Only retry once for scanning as it's expensive
    );
  },
};

// Audio Playback Commands with enhanced error handling
export const playbackApi = {
  async playTrack(track: Track): ApiResult<void> {
    return withRetry(
      () => invoke('play_track', { track }),
      { operation: 'play_track', trackId: track.id, trackPath: track.filePath }
    );
  },

  async pause(): ApiResult<void> {
    return withRetry(
      () => invoke('pause_playback'),
      { operation: 'pause_playback' }
    );
  },

  async resume(): ApiResult<void> {
    return withRetry(
      () => invoke('resume_playback'),
      { operation: 'resume_playback' }
    );
  },

  async stop(): ApiResult<void> {
    return withRetry(
      () => invoke('stop_playback'),
      { operation: 'stop_playback' }
    );
  },

  async seekTo(position: number): ApiResult<void> {
    return withRetry(
      () => invoke('seek_to', { position }),
      { operation: 'seek_to', position }
    );
  },

  async getState(): ApiResult<PlaybackState> {
    return withRetry(
      () => invoke('get_playback_state'),
      { operation: 'get_playback_state' }
    );
  },

  async setVolume(volume: number): ApiResult<void> {
    return withRetry(
      () => invoke('set_volume', { volume }),
      { operation: 'set_volume', volume }
    );
  },

  async validateAudioFile(filePath: string): ApiResult<void> {
    return withRetry(
      () => invoke('validate_audio_file', { filePath }),
      { operation: 'validate_audio_file', filePath }
    );
  },

  async analyzeMp3File(filePath: string): ApiResult<string> {
    return withRetry(
      () => invoke('analyze_mp3_file', { filePath }),
      { operation: 'analyze_mp3_file', filePath }
    );
  },
};

// Application State Commands with enhanced error handling
export const stateApi = {
  async save(state: AppState): ApiResult<void> {
    return withRetry(
      () => invoke('save_app_state', { state }),
      { operation: 'save_app_state' }
    );
  },

  async load(): ApiResult<AppState> {
    return withRetry(
      () => invoke('load_app_state'),
      { operation: 'load_app_state' }
    );
  },
};

// Enhanced error handling with retry and recovery
import { parseError, retryWithBackoff, logError, type AppError } from './errors';

/**
 * Enhanced error handler that creates structured error objects
 */
export function handleApiError(error: unknown, context?: Record<string, unknown>): AppError {
  const appError = parseError(error, context);
  logError(appError);
  return appError;
}

/**
 * Legacy error handler for backward compatibility
 */
export function handleApiErrorLegacy(error: unknown): string {
  const appError = handleApiError(error);
  return appError.userMessage;
}

/**
 * Wrapper for API calls with automatic retry and error handling
 */
export async function withRetry<T>(
  operation: () => Promise<T>,
  context?: Record<string, unknown>,
  maxRetries: number = 2
): Promise<T> {
  try {
    return await retryWithBackoff(operation, maxRetries);
  } catch (error) {
    throw handleApiError(error, context);
  }
}

/**
 * Safe API call wrapper that doesn't throw but returns result or error
 */
export async function safeApiCall<T>(
  operation: () => Promise<T>,
  context?: Record<string, unknown>
): Promise<{ success: true; data: T } | { success: false; error: AppError }> {
  try {
    const data = await operation();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: handleApiError(error, context) };
  }
}

// Type-safe event listener helpers
export type TauriEventCallback<T> = (payload: T) => void;

export function createEventListener<T>(
  eventName: string,
  callback: TauriEventCallback<T>
) {
  // This will be implemented when we add event system
  // For now, it's a placeholder for future event handling
  return {
    eventName,
    callback,
    unsubscribe: () => {
      // Placeholder for cleanup
    },
  };
}
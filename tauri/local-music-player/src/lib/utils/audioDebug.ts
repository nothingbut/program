import { playbackApi } from '../api';

/**
 * Debug utilities for audio playback issues
 */

export interface AudioFileInfo {
  path: string;
  exists: boolean;
  size?: number;
  extension?: string;
  isValid: boolean;
  error?: string;
  mp3Analysis?: string;
}

/**
 * Validate an audio file and return diagnostic information
 */
export async function validateAudioFile(filePath: string): Promise<AudioFileInfo> {
  const info: AudioFileInfo = {
    path: filePath,
    exists: false,
    isValid: false,
  };

  try {
    // Extract file extension
    const pathParts = filePath.split('.');
    if (pathParts.length > 1) {
      info.extension = pathParts[pathParts.length - 1].toLowerCase();
    }

    // Try to validate the file using the backend
    await playbackApi.validateAudioFile(filePath);
    
    info.exists = true;
    info.isValid = true;

    // If it's an MP3 file, get detailed analysis
    if (info.extension === 'mp3') {
      try {
        info.mp3Analysis = await playbackApi.analyzeMp3File(filePath);
      } catch (analysisError) {
        // Analysis failed, but validation passed - not critical
        console.warn('MP3 analysis failed:', analysisError);
      }
    }
    
  } catch (error) {
    info.exists = true; // File exists but has issues
    info.isValid = false;
    info.error = error instanceof Error ? error.message : String(error);
  }

  return info;
}

/**
 * Get supported audio formats
 */
export function getSupportedFormats(): string[] {
  return ['mp3', 'flac', 'wav', 'ogg', 'm4a'];
}

/**
 * Check if a file extension is supported
 */
export function isSupportedFormat(extension: string): boolean {
  return getSupportedFormats().includes(extension.toLowerCase());
}

/**
 * Format audio file diagnostic information for display
 */
export function formatAudioDiagnostics(info: AudioFileInfo): string {
  const lines: string[] = [];
  
  lines.push(`File: ${info.path}`);
  lines.push(`Extension: ${info.extension || 'unknown'}`);
  lines.push(`Supported format: ${info.extension ? isSupportedFormat(info.extension) : 'unknown'}`);
  lines.push(`Valid: ${info.isValid ? 'Yes' : 'No'}`);
  
  if (info.error) {
    lines.push(`Error: ${info.error}`);
  }

  if (info.mp3Analysis) {
    lines.push('');
    lines.push('MP3 Analysis:');
    lines.push(info.mp3Analysis);
  }
  
  return lines.join('\n');
}
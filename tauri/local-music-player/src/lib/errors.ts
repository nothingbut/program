/**
 * Comprehensive error handling system for the MP3 Player
 * Provides typed errors, error recovery, and user-friendly messaging
 */

/**
 * Error severity levels
 */
export enum ErrorSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

/**
 * Error categories for better handling
 */
export enum ErrorCategory {
  NETWORK = 'network',
  FILE_SYSTEM = 'file_system',
  AUDIO_PLAYBACK = 'audio_playback',
  METADATA = 'metadata',
  PERSISTENCE = 'persistence',
  USER_INPUT = 'user_input',
  SYSTEM = 'system',
  UNKNOWN = 'unknown'
}

/**
 * Base error interface
 */
export interface AppError {
  id: string;
  message: string;
  userMessage: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  timestamp: Date;
  context?: Record<string, unknown>;
  originalError?: unknown;
  recoverable: boolean;
  retryable: boolean;
  stack?: string;
}

/**
 * Error recovery action
 */
export interface ErrorRecoveryAction {
  label: string;
  action: () => Promise<void> | void;
  primary?: boolean;
}

/**
 * Error with recovery options
 */
export interface RecoverableError extends AppError {
  recoveryActions: ErrorRecoveryAction[];
}

/**
 * Create a standardized error object
 */
export function createAppError(
  message: string,
  userMessage: string,
  category: ErrorCategory = ErrorCategory.UNKNOWN,
  severity: ErrorSeverity = ErrorSeverity.ERROR,
  options: {
    context?: Record<string, unknown>;
    originalError?: unknown;
    recoverable?: boolean;
    retryable?: boolean;
  } = {}
): AppError {
  const error: AppError = {
    id: generateErrorId(),
    message,
    userMessage,
    category,
    severity,
    timestamp: new Date(),
    context: options.context,
    originalError: options.originalError,
    recoverable: options.recoverable ?? false,
    retryable: options.retryable ?? false,
    stack: new Error().stack
  };

  return error;
}

/**
 * Create a recoverable error with actions
 */
export function createRecoverableError(
  message: string,
  userMessage: string,
  recoveryActions: ErrorRecoveryAction[],
  category: ErrorCategory = ErrorCategory.UNKNOWN,
  severity: ErrorSeverity = ErrorSeverity.ERROR,
  options: {
    context?: Record<string, unknown>;
    originalError?: unknown;
  } = {}
): RecoverableError {
  const baseError = createAppError(message, userMessage, category, severity, {
    ...options,
    recoverable: true,
    retryable: recoveryActions.some(action => action.label.toLowerCase().includes('retry'))
  });

  return {
    ...baseError,
    recoveryActions
  };
}

/**
 * Generate unique error ID
 */
function generateErrorId(): string {
  return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Parse and categorize unknown errors
 */
export function parseError(error: unknown, context?: Record<string, unknown>): AppError {
  if (typeof error === 'string') {
    return createAppError(
      error,
      getUserFriendlyMessage(error),
      categorizeError(error),
      ErrorSeverity.ERROR,
      { context, originalError: error }
    );
  }

  if (error instanceof Error) {
    return createAppError(
      error.message,
      getUserFriendlyMessage(error.message),
      categorizeError(error.message),
      ErrorSeverity.ERROR,
      { context, originalError: error }
    );
  }

  if (typeof error === 'object' && error !== null) {
    const errorObj = error as Record<string, unknown>;
    const message = String(errorObj.message || errorObj.error || 'Unknown error');
    
    return createAppError(
      message,
      getUserFriendlyMessage(message),
      categorizeError(message),
      ErrorSeverity.ERROR,
      { context, originalError: error }
    );
  }

  return createAppError(
    'Unknown error occurred',
    'An unexpected error occurred. Please try again.',
    ErrorCategory.UNKNOWN,
    ErrorSeverity.ERROR,
    { context, originalError: error }
  );
}

/**
 * Categorize error based on message content
 */
function categorizeError(message: string): ErrorCategory {
  const lowerMessage = message.toLowerCase();

  if (lowerMessage.includes('network') || lowerMessage.includes('connection') || lowerMessage.includes('timeout')) {
    return ErrorCategory.NETWORK;
  }
  
  if (lowerMessage.includes('file') || lowerMessage.includes('directory') || lowerMessage.includes('path') || lowerMessage.includes('permission')) {
    return ErrorCategory.FILE_SYSTEM;
  }
  
  if (lowerMessage.includes('audio') || lowerMessage.includes('playback') || lowerMessage.includes('sound') || lowerMessage.includes('volume')) {
    return ErrorCategory.AUDIO_PLAYBACK;
  }
  
  if (lowerMessage.includes('metadata') || lowerMessage.includes('tag') || lowerMessage.includes('mp3') || lowerMessage.includes('id3')) {
    return ErrorCategory.METADATA;
  }
  
  if (lowerMessage.includes('save') || lowerMessage.includes('load') || lowerMessage.includes('persist') || lowerMessage.includes('storage')) {
    return ErrorCategory.PERSISTENCE;
  }
  
  if (lowerMessage.includes('invalid') || lowerMessage.includes('format') || lowerMessage.includes('input')) {
    return ErrorCategory.USER_INPUT;
  }
  
  if (lowerMessage.includes('system') || lowerMessage.includes('memory') || lowerMessage.includes('resource')) {
    return ErrorCategory.SYSTEM;
  }

  return ErrorCategory.UNKNOWN;
}

/**
 * Convert technical error messages to user-friendly ones
 */
function getUserFriendlyMessage(message: string): string {
  const lowerMessage = message.toLowerCase();

  // File system errors
  if (lowerMessage.includes('permission denied') || lowerMessage.includes('access denied')) {
    return 'Permission denied. Please check file permissions and try again.';
  }
  
  if (lowerMessage.includes('file not found') || lowerMessage.includes('no such file')) {
    return 'The requested file could not be found. It may have been moved or deleted.';
  }
  
  if (lowerMessage.includes('directory not found') || lowerMessage.includes('no such directory')) {
    return 'The selected directory could not be found. It may have been moved or deleted.';
  }

  // Audio errors
  if (lowerMessage.includes('unsupported format') || lowerMessage.includes('invalid format')) {
    return 'This audio format is not supported. Please use MP3 files.';
  }
  
  if (lowerMessage.includes('corrupted') || lowerMessage.includes('damaged')) {
    return 'The audio file appears to be corrupted and cannot be played.';
  }
  
  if (lowerMessage.includes('audio device') || lowerMessage.includes('sound device')) {
    return 'Audio device not available. Please check your sound settings.';
  }

  // Network errors
  if (lowerMessage.includes('timeout') || lowerMessage.includes('timed out')) {
    return 'The operation timed out. Please check your connection and try again.';
  }
  
  if (lowerMessage.includes('connection') || lowerMessage.includes('network')) {
    return 'Network connection error. Please check your internet connection.';
  }

  // Metadata errors
  if (lowerMessage.includes('metadata') || lowerMessage.includes('tag')) {
    return 'Could not read music file information. The file may be corrupted.';
  }

  // Generic fallbacks
  if (lowerMessage.includes('failed to') || lowerMessage.includes('cannot') || lowerMessage.includes('unable to')) {
    return `Operation failed: ${message}`;
  }

  // If no specific pattern matches, return a generic user-friendly message
  if (message.length > 100) {
    return 'An error occurred while processing your request. Please try again.';
  }

  return message;
}

/**
 * Common error recovery actions
 */
export const commonRecoveryActions = {
  retry: (action: () => Promise<void> | void): ErrorRecoveryAction => ({
    label: 'Retry',
    action,
    primary: true
  }),

  refresh: (action: () => Promise<void> | void): ErrorRecoveryAction => ({
    label: 'Refresh',
    action
  }),

  dismiss: (): ErrorRecoveryAction => ({
    label: 'Dismiss',
    action: () => {}
  }),

  reload: (): ErrorRecoveryAction => ({
    label: 'Reload Application',
    action: () => window.location.reload()
  }),

  reportBug: (): ErrorRecoveryAction => ({
    label: 'Report Bug',
    action: () => {
      // In a real app, this would open a bug report form
      console.log('Bug report functionality would be implemented here');
    }
  })
};

/**
 * Error logging utility
 */
export function logError(error: AppError): void {
  const logLevel = error.severity === ErrorSeverity.CRITICAL ? 'error' : 
                   error.severity === ErrorSeverity.ERROR ? 'error' :
                   error.severity === ErrorSeverity.WARNING ? 'warn' : 'info';

  console[logLevel](`[${error.category}] ${error.message}`, {
    id: error.id,
    timestamp: error.timestamp,
    context: error.context,
    originalError: error.originalError,
    stack: error.stack
  });
}

/**
 * Retry utility with exponential backoff
 */
export async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxRetries) {
        throw error;
      }

      // Exponential backoff with jitter
      const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}
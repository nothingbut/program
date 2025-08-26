use thiserror::Error;

/// Application-specific error types
#[derive(Debug, Error)]
pub enum AppError {
    #[error("File system error: {0}")]
    FileSystem(#[from] std::io::Error),
    
    #[error("Audio metadata error: {0}")]
    Metadata(String),
    
    #[error("Audio playback error: {0}")]
    Playback(String),
    
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    
    #[error("Database error: {0}")]
    Database(String),
    
    #[error("Invalid directory path: {0}")]
    InvalidPath(String),
    
    #[error("Track not found: {0}")]
    TrackNotFound(String),
    
    #[error("Directory not found: {0}")]
    DirectoryNotFound(String),
    
    #[error("Unsupported audio format: {0}")]
    UnsupportedFormat(String),
    
    #[error("Permission denied: {0}")]
    PermissionDenied(String),
}

/// Result type alias for convenience
pub type AppResult<T> = Result<T, AppError>;

/// Convert AppError to String for Tauri command returns
impl From<AppError> for String {
    fn from(error: AppError) -> Self {
        error.to_string()
    }
}

/// Helper trait for converting Results to Tauri-compatible format
pub trait IntoTauriResult<T> {
    fn into_tauri_result(self) -> Result<T, String>;
}

impl<T> IntoTauriResult<T> for AppResult<T> {
    fn into_tauri_result(self) -> Result<T, String> {
        self.map_err(|e| e.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io;

    #[test]
    fn test_error_conversion() {
        let io_error = io::Error::new(io::ErrorKind::NotFound, "File not found");
        let app_error = AppError::FileSystem(io_error);
        let error_string: String = app_error.into();
        
        assert!(error_string.contains("File system error"));
        assert!(error_string.contains("File not found"));
    }

    #[test]
    fn test_metadata_error() {
        let error = AppError::Metadata("Invalid MP3 format".to_string());
        assert_eq!(error.to_string(), "Audio metadata error: Invalid MP3 format");
    }

    #[test]
    fn test_into_tauri_result() {
        let success: AppResult<i32> = Ok(42);
        let tauri_result = success.into_tauri_result();
        assert_eq!(tauri_result, Ok(42));

        let error: AppResult<i32> = Err(AppError::TrackNotFound("test".to_string()));
        let tauri_result = error.into_tauri_result();
        assert!(tauri_result.is_err());
        assert!(tauri_result.unwrap_err().contains("Track not found"));
    }
}
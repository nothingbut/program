use crate::{AppState, AppError};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tauri::{AppHandle, Manager};
use tokio::fs;

/// Version information for state file compatibility
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct StateVersion {
    pub major: u32,
    pub minor: u32,
    pub patch: u32,
}

impl StateVersion {
    pub const CURRENT: StateVersion = StateVersion {
        major: 1,
        minor: 0,
        patch: 0,
    };

    /// Check if this version is compatible with the current version
    pub fn is_compatible(&self) -> bool {
        // For now, only exact version match is supported
        // In the future, we can implement backward compatibility logic
        self.major == Self::CURRENT.major
    }
}

/// Wrapper for persisted state with version information
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PersistedState {
    pub version: StateVersion,
    pub app_state: AppState,
}

impl PersistedState {
    pub fn new(app_state: AppState) -> Self {
        Self {
            version: StateVersion::CURRENT,
            app_state,
        }
    }
}

/// Handles application state persistence
#[derive(Debug, Clone)]
pub struct PersistenceManager {
    app_handle: AppHandle,
}

impl PersistenceManager {
    pub fn new(app_handle: AppHandle) -> Self {
        Self { app_handle }
    }

    /// Get the path to the state file
    fn get_state_file_path(&self) -> Result<PathBuf, AppError> {
        let app_data_dir = self
            .app_handle
            .path()
            .app_data_dir()
            .map_err(|e| AppError::FileSystem(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                format!("Failed to get app data directory: {}", e),
            )))?;

        Ok(app_data_dir.join("app_state.json"))
    }

    /// Get the path to the backup state file
    fn get_backup_state_file_path(&self) -> Result<PathBuf, AppError> {
        let app_data_dir = self
            .app_handle
            .path()
            .app_data_dir()
            .map_err(|e| AppError::FileSystem(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                format!("Failed to get app data directory: {}", e),
            )))?;

        Ok(app_data_dir.join("app_state_backup.json"))
    }

    /// Save application state to disk
    pub async fn save_app_state(&self, app_state: AppState) -> Result<(), AppError> {
        let state_file_path = self.get_state_file_path()?;
        let backup_file_path = self.get_backup_state_file_path()?;

        // Ensure the app data directory exists
        if let Some(parent) = state_file_path.parent() {
            fs::create_dir_all(parent).await?;
        }

        // Create backup of existing state file if it exists
        if state_file_path.exists() {
            if let Err(e) = fs::copy(&state_file_path, &backup_file_path).await {
                eprintln!("Warning: Failed to create backup of state file: {}", e);
            }
        }

        // Create persisted state with version information
        let persisted_state = PersistedState::new(app_state);

        // Serialize state to JSON
        let json_data = serde_json::to_string_pretty(&persisted_state)
            .map_err(|e| AppError::Serialization(e))?;

        // Write to temporary file first, then rename to ensure atomicity
        let temp_file_path = state_file_path.with_extension("tmp");
        fs::write(&temp_file_path, json_data).await?;
        fs::rename(&temp_file_path, &state_file_path).await?;

        println!("Application state saved to: {:?}", state_file_path);
        Ok(())
    }

    /// Load application state from disk
    pub async fn load_app_state(&self) -> Result<AppState, AppError> {
        let state_file_path = self.get_state_file_path()?;
        let backup_file_path = self.get_backup_state_file_path()?;

        // Try to load from main state file first
        match self.try_load_from_file(&state_file_path).await {
            Ok(app_state) => {
                println!("Application state loaded from: {:?}", state_file_path);
                return Ok(app_state);
            }
            Err(e) => {
                // Check if this is just a missing file (normal on first run)
                if let AppError::FileSystem(io_err) = &e {
                    if io_err.kind() == std::io::ErrorKind::NotFound {
                        // This is normal on first run, don't print an error
                        println!("No existing state file found, using default application state");
                        return Ok(AppState::default());
                    }
                }
                
                // For other errors, try backup and show error messages
                eprintln!("Failed to load state from main file: {}", e);
                
                // Try to load from backup file
                if backup_file_path.exists() {
                    eprintln!("Attempting to load from backup file...");
                    match self.try_load_from_file(&backup_file_path).await {
                        Ok(app_state) => {
                            println!("Application state loaded from backup: {:?}", backup_file_path);
                            
                            // Try to restore the main file from backup
                            if let Err(restore_err) = fs::copy(&backup_file_path, &state_file_path).await {
                                eprintln!("Warning: Failed to restore main state file from backup: {}", restore_err);
                            }
                            
                            return Ok(app_state);
                        }
                        Err(backup_err) => {
                            eprintln!("Failed to load state from backup file: {}", backup_err);
                        }
                    }
                }
            }
        }

        // If both main and backup files failed, return default state
        println!("Using default application state");
        Ok(AppState::default())
    }

    /// Try to load state from a specific file
    async fn try_load_from_file(&self, file_path: &PathBuf) -> Result<AppState, AppError> {
        if !file_path.exists() {
            return Err(AppError::FileSystem(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "State file does not exist",
            )));
        }

        // Read file contents
        let json_data = fs::read_to_string(file_path).await?;

        // Try to deserialize as versioned state first
        match serde_json::from_str::<PersistedState>(&json_data) {
            Ok(persisted_state) => {
                // Check version compatibility
                if !persisted_state.version.is_compatible() {
                    return Err(AppError::Database(format!(
                        "Incompatible state file version: {:?}, current: {:?}",
                        persisted_state.version,
                        StateVersion::CURRENT
                    )));
                }
                Ok(persisted_state.app_state)
            }
            Err(_) => {
                // Try to deserialize as legacy AppState (without version)
                match serde_json::from_str::<AppState>(&json_data) {
                    Ok(app_state) => {
                        println!("Loaded legacy state file, will upgrade on next save");
                        Ok(app_state)
                    }
                    Err(e) => Err(AppError::Serialization(e)),
                }
            }
        }
    }

    /// Clear saved state (useful for testing or reset functionality)
    pub async fn clear_saved_state(&self) -> Result<(), AppError> {
        let state_file_path = self.get_state_file_path()?;
        let backup_file_path = self.get_backup_state_file_path()?;

        // Remove main state file
        if state_file_path.exists() {
            fs::remove_file(&state_file_path).await?;
        }

        // Remove backup file
        if backup_file_path.exists() {
            fs::remove_file(&backup_file_path).await?;
        }

        println!("Saved state cleared");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Directory, WindowGeometry};
    use std::path::PathBuf;

    fn create_test_app_state() -> AppState {
        let mut app_state = AppState::default();
        app_state.directories.push(Directory::new(PathBuf::from("/test/music")));
        app_state.is_shuffle_mode = true;
        app_state.window_geometry = WindowGeometry {
            x: 200,
            y: 150,
            width: 1400,
            height: 900,
        };
        app_state
    }

    #[test]
    fn test_state_version_compatibility() {
        let current = StateVersion::CURRENT;
        assert!(current.is_compatible());

        let incompatible = StateVersion {
            major: 2,
            minor: 0,
            patch: 0,
        };
        assert!(!incompatible.is_compatible());
    }

    #[test]
    fn test_persisted_state_serialization() {
        let app_state = create_test_app_state();
        let persisted_state = PersistedState::new(app_state.clone());

        let serialized = serde_json::to_string(&persisted_state).unwrap();
        let deserialized: PersistedState = serde_json::from_str(&serialized).unwrap();

        assert_eq!(persisted_state, deserialized);
        assert_eq!(persisted_state.app_state, app_state);
    }

    #[test]
    fn test_legacy_state_deserialization() {
        let app_state = create_test_app_state();
        
        // Serialize as legacy format (without version)
        let legacy_json = serde_json::to_string(&app_state).unwrap();
        
        // Should be able to deserialize as AppState
        let deserialized: AppState = serde_json::from_str(&legacy_json).unwrap();
        assert_eq!(app_state, deserialized);
    }
}
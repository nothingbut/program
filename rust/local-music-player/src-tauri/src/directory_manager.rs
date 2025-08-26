use crate::{AppError, Directory};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::Mutex;
use tauri::{AppHandle, Manager};
use tokio::sync::RwLock;

/// Directory manager state that handles directory persistence and validation
#[derive(Debug, Default, Clone)]
pub struct DirectoryManager {
    directories: std::sync::Arc<RwLock<HashMap<String, Directory>>>,
    storage_path: std::sync::Arc<Mutex<Option<PathBuf>>>,
}

/// Serializable directory storage format
#[derive(Debug, Serialize, Deserialize)]
struct DirectoryStorage {
    directories: Vec<Directory>,
}

impl DirectoryManager {
    pub fn new() -> Self {
        Self {
            directories: std::sync::Arc::new(RwLock::new(HashMap::new())),
            storage_path: std::sync::Arc::new(Mutex::new(None)),
        }
    }

    /// Initialize the directory manager with app data directory
    pub async fn initialize(&self, app_handle: &AppHandle) -> Result<(), AppError> {
        let app_data_dir = app_handle
            .path()
            .app_data_dir()
            .map_err(|e| AppError::FileSystem(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                format!("Failed to get app data directory: {}", e)
            )))?;

        // Create app data directory if it doesn't exist
        if !app_data_dir.exists() {
            fs::create_dir_all(&app_data_dir)?;
        }

        let storage_path = app_data_dir.join("directories.json");
        *self.storage_path.lock().unwrap() = Some(storage_path.clone());

        // Load existing directories
        self.load_directories().await?;

        Ok(())
    }

    /// Validate directory path for security and accessibility
    fn validate_directory_path(path: &Path) -> Result<(), AppError> {
        // Check if path exists
        if !path.exists() {
            return Err(AppError::FileSystem(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                format!("Directory does not exist: {}", path.display())
            )));
        }

        // Check if it's actually a directory
        if !path.is_dir() {
            return Err(AppError::FileSystem(std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                format!("Path is not a directory: {}", path.display())
            )));
        }

        // Check if we can read the directory
        match fs::read_dir(path) {
            Ok(_) => Ok(()),
            Err(e) => Err(AppError::FileSystem(std::io::Error::new(
                e.kind(),
                format!("Cannot read directory {}: {}", path.display(), e)
            ))),
        }
    }

    /// Add a new directory to the manager
    pub async fn add_directory(&self, path: PathBuf) -> Result<Directory, AppError> {
        // Validate the directory path
        Self::validate_directory_path(&path)?;

        // Check if directory already exists
        let directories = self.directories.read().await;
        for directory in directories.values() {
            if directory.path == path {
                return Err(AppError::Database(format!(
                    "Directory already exists: {}",
                    path.display()
                )));
            }
        }
        drop(directories);

        // Create new directory entry
        let directory = Directory::new(path);

        // Add to storage
        let mut directories = self.directories.write().await;
        directories.insert(directory.id.clone(), directory.clone());
        drop(directories);

        // Persist to disk
        self.save_directories().await?;

        Ok(directory)
    }

    /// Get all directories
    pub async fn get_directories(&self) -> Result<Vec<Directory>, AppError> {
        let directories = self.directories.read().await;
        let mut result: Vec<Directory> = directories.values().cloned().collect();
        
        // Sort by added_at timestamp for consistent ordering
        result.sort_by(|a, b| a.added_at.cmp(&b.added_at));
        
        Ok(result)
    }

    /// Remove a directory by ID
    pub async fn remove_directory(&self, id: &str) -> Result<(), AppError> {
        let mut directories = self.directories.write().await;
        
        if directories.remove(id).is_none() {
            return Err(AppError::Database(format!(
                "Directory with ID {} not found",
                id
            )));
        }
        
        drop(directories);

        // Persist changes to disk
        self.save_directories().await?;

        Ok(())
    }

    /// Get a specific directory by ID
    pub async fn get_directory(&self, id: &str) -> Result<Option<Directory>, AppError> {
        let directories = self.directories.read().await;
        Ok(directories.get(id).cloned())
    }

    /// Load directories from persistent storage
    async fn load_directories(&self) -> Result<(), AppError> {
        let storage_path = self.storage_path.lock().unwrap().clone();
        let storage_path = match storage_path {
            Some(path) => path,
            None => return Err(AppError::Database("Storage path not initialized".to_string())),
        };

        if !storage_path.exists() {
            // No existing storage file, start with empty directories
            return Ok(());
        }

        let content = fs::read_to_string(&storage_path)?;
        let storage: DirectoryStorage = serde_json::from_str(&content)
            .map_err(|e| AppError::Serialization(e))?;

        let mut directories = self.directories.write().await;
        directories.clear();
        
        for directory in storage.directories {
            // Validate that the directory still exists and is accessible
            if Self::validate_directory_path(&directory.path).is_ok() {
                directories.insert(directory.id.clone(), directory);
            }
            // Skip directories that are no longer accessible
        }

        Ok(())
    }

    /// Save directories to persistent storage
    async fn save_directories(&self) -> Result<(), AppError> {
        let storage_path = self.storage_path.lock().unwrap().clone();
        let storage_path = match storage_path {
            Some(path) => path,
            None => return Err(AppError::Database("Storage path not initialized".to_string())),
        };

        let directories = self.directories.read().await;
        let storage = DirectoryStorage {
            directories: directories.values().cloned().collect(),
        };

        let content = serde_json::to_string_pretty(&storage)
            .map_err(|e| AppError::Serialization(e))?;

        fs::write(&storage_path, content)?;

        Ok(())
    }

    /// Refresh directory accessibility - remove directories that are no longer accessible
    pub async fn refresh_directories(&self) -> Result<Vec<String>, AppError> {
        let mut directories = self.directories.write().await;
        let mut removed_ids = Vec::new();

        directories.retain(|id, directory| {
            if Self::validate_directory_path(&directory.path).is_err() {
                removed_ids.push(id.clone());
                false
            } else {
                true
            }
        });

        drop(directories);

        if !removed_ids.is_empty() {
            self.save_directories().await?;
        }

        Ok(removed_ids)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[tokio::test]
    async fn test_directory_validation() {
        let temp_dir = TempDir::new().unwrap();
        let valid_path = temp_dir.path();
        let invalid_path = temp_dir.path().join("nonexistent");

        // Valid directory should pass
        assert!(DirectoryManager::validate_directory_path(valid_path).is_ok());

        // Non-existent directory should fail
        assert!(DirectoryManager::validate_directory_path(&invalid_path).is_err());

        // File instead of directory should fail
        let file_path = temp_dir.path().join("test.txt");
        fs::write(&file_path, "test").unwrap();
        assert!(DirectoryManager::validate_directory_path(&file_path).is_err());
    }

    async fn setup_test_manager() -> (DirectoryManager, TempDir) {
        let manager = DirectoryManager::new();
        let temp_storage = TempDir::new().unwrap();
        let storage_path = temp_storage.path().join("directories.json");
        *manager.storage_path.lock().unwrap() = Some(storage_path);
        (manager, temp_storage)
    }

    #[tokio::test]
    async fn test_add_and_get_directories() {
        let (manager, _temp_storage) = setup_test_manager().await;
        let temp_dir = TempDir::new().unwrap();

        // Add directory
        let directory = manager.add_directory(temp_dir.path().to_path_buf()).await.unwrap();
        assert_eq!(directory.path, temp_dir.path());
        assert_eq!(directory.name, temp_dir.path().file_name().unwrap().to_str().unwrap());

        // Get directories
        let directories = manager.get_directories().await.unwrap();
        assert_eq!(directories.len(), 1);
        assert_eq!(directories[0].id, directory.id);

        // Try to add same directory again - should fail
        let result = manager.add_directory(temp_dir.path().to_path_buf()).await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_remove_directory() {
        let (manager, _temp_storage) = setup_test_manager().await;
        let temp_dir = TempDir::new().unwrap();

        // Add directory
        let directory = manager.add_directory(temp_dir.path().to_path_buf()).await.unwrap();

        // Remove directory
        assert!(manager.remove_directory(&directory.id).await.is_ok());

        // Verify it's removed
        let directories = manager.get_directories().await.unwrap();
        assert_eq!(directories.len(), 0);

        // Try to remove non-existent directory
        assert!(manager.remove_directory("nonexistent").await.is_err());
    }

    #[tokio::test]
    async fn test_get_directory_by_id() {
        let (manager, _temp_storage) = setup_test_manager().await;
        let temp_dir = TempDir::new().unwrap();

        // Add directory
        let directory = manager.add_directory(temp_dir.path().to_path_buf()).await.unwrap();

        // Get by ID
        let found = manager.get_directory(&directory.id).await.unwrap();
        assert!(found.is_some());
        assert_eq!(found.unwrap().id, directory.id);

        // Get non-existent ID
        let not_found = manager.get_directory("nonexistent").await.unwrap();
        assert!(not_found.is_none());
    }

    #[tokio::test]
    async fn test_refresh_directories() {
        let (manager, _temp_storage) = setup_test_manager().await;
        let temp_dir = TempDir::new().unwrap();

        // Add directory
        let directory = manager.add_directory(temp_dir.path().to_path_buf()).await.unwrap();

        // Verify it exists
        let directories = manager.get_directories().await.unwrap();
        assert_eq!(directories.len(), 1);

        // Manually remove the directory from filesystem
        drop(temp_dir); // This removes the temp directory

        // Refresh should remove the inaccessible directory
        let removed = manager.refresh_directories().await.unwrap();
        assert_eq!(removed.len(), 1);
        assert_eq!(removed[0], directory.id);

        // Verify it's removed from manager
        let directories = manager.get_directories().await.unwrap();
        assert_eq!(directories.len(), 0);
    }
}
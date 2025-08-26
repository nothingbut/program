use local_mp3_player_lib::{AppState, Directory, PlaybackState, WindowGeometry, Track};
use local_mp3_player_lib::persistence::{PersistenceManager, PersistedState, StateVersion};
use std::path::PathBuf;
use tempfile::TempDir;
use tokio::fs;

// Mock AppHandle for testing
struct MockAppHandle {
    app_data_dir: PathBuf,
}

impl MockAppHandle {
    fn new(app_data_dir: PathBuf) -> Self {
        Self { app_data_dir }
    }
}

// Helper function to create a test app state
fn create_test_app_state() -> AppState {
    let mut app_state = AppState::default();
    
    // Add some directories
    app_state.directories.push(Directory::new(PathBuf::from("/test/music1")));
    app_state.directories.push(Directory::new(PathBuf::from("/test/music2")));
    
    // Set selected directory
    app_state.selected_directory = Some(app_state.directories[0].id.clone());
    
    // Add some tracks to playlist
    let mut track1 = Track::new(PathBuf::from("/test/music1/song1.mp3"));
    track1.title = "Test Song 1".to_string();
    track1.artist = "Test Artist 1".to_string();
    track1.album = "Test Album".to_string();
    track1.duration = 180.0;
    
    let mut track2 = Track::new(PathBuf::from("/test/music1/song2.mp3"));
    track2.title = "Test Song 2".to_string();
    track2.artist = "Test Artist 2".to_string();
    track2.album = "Test Album".to_string();
    track2.duration = 210.0;
    
    app_state.current_playlist = vec![track1.clone(), track2];
    
    // Set playback state
    app_state.playback_state = PlaybackState {
        current_track: Some(track1),
        is_playing: true,
        current_time: 45.0,
        duration: 180.0,
        volume: 0.8,
    };
    
    // Set shuffle mode
    app_state.is_shuffle_mode = true;
    
    // Set window geometry
    app_state.window_geometry = WindowGeometry {
        x: 200,
        y: 150,
        width: 1400,
        height: 900,
    };
    
    app_state
}

// Note: These tests would need to be adapted to work with the actual Tauri AppHandle
// For now, they test the core persistence logic

#[tokio::test]
async fn test_state_version_compatibility() {
    let current = StateVersion::CURRENT;
    assert!(current.is_compatible());

    let incompatible = StateVersion {
        major: 2,
        minor: 0,
        patch: 0,
    };
    assert!(!incompatible.is_compatible());
}

#[tokio::test]
async fn test_persisted_state_serialization() {
    let app_state = create_test_app_state();
    let persisted_state = PersistedState::new(app_state.clone());

    // Test serialization and deserialization
    let serialized = serde_json::to_string_pretty(&persisted_state).unwrap();
    let deserialized: PersistedState = serde_json::from_str(&serialized).unwrap();

    assert_eq!(persisted_state.version, deserialized.version);
    assert_eq!(persisted_state.app_state, deserialized.app_state);
}

#[tokio::test]
async fn test_legacy_state_compatibility() {
    let app_state = create_test_app_state();
    
    // Serialize as legacy format (without version wrapper)
    let legacy_json = serde_json::to_string_pretty(&app_state).unwrap();
    
    // Should be able to deserialize as AppState
    let deserialized: AppState = serde_json::from_str(&legacy_json).unwrap();
    assert_eq!(app_state, deserialized);
}

#[tokio::test]
async fn test_state_file_operations() {
    let temp_dir = TempDir::new().unwrap();
    let app_data_dir = temp_dir.path().to_path_buf();
    
    // Create test state
    let original_state = create_test_app_state();
    let persisted_state = PersistedState::new(original_state.clone());
    
    // Test file paths
    let state_file_path = app_data_dir.join("app_state.json");
    let backup_file_path = app_data_dir.join("app_state_backup.json");
    
    // Ensure directory exists
    fs::create_dir_all(&app_data_dir).await.unwrap();
    
    // Write state to file
    let json_data = serde_json::to_string_pretty(&persisted_state).unwrap();
    fs::write(&state_file_path, &json_data).await.unwrap();
    
    // Verify file exists and can be read
    assert!(state_file_path.exists());
    let read_data = fs::read_to_string(&state_file_path).await.unwrap();
    let loaded_state: PersistedState = serde_json::from_str(&read_data).unwrap();
    
    assert_eq!(persisted_state.app_state, loaded_state.app_state);
}

#[tokio::test]
async fn test_backup_file_creation() {
    let temp_dir = TempDir::new().unwrap();
    let app_data_dir = temp_dir.path().to_path_buf();
    
    let state_file_path = app_data_dir.join("app_state.json");
    let backup_file_path = app_data_dir.join("app_state_backup.json");
    
    // Ensure directory exists
    fs::create_dir_all(&app_data_dir).await.unwrap();
    
    // Create initial state file
    let initial_state = AppState::default();
    let initial_persisted = PersistedState::new(initial_state);
    let initial_json = serde_json::to_string_pretty(&initial_persisted).unwrap();
    fs::write(&state_file_path, &initial_json).await.unwrap();
    
    // Create backup (simulate what PersistenceManager does)
    fs::copy(&state_file_path, &backup_file_path).await.unwrap();
    
    // Verify backup exists and contains same data
    assert!(backup_file_path.exists());
    let backup_data = fs::read_to_string(&backup_file_path).await.unwrap();
    let backup_state: PersistedState = serde_json::from_str(&backup_data).unwrap();
    
    assert_eq!(initial_persisted.app_state, backup_state.app_state);
}

#[tokio::test]
async fn test_corrupted_state_file_handling() {
    let temp_dir = TempDir::new().unwrap();
    let app_data_dir = temp_dir.path().to_path_buf();
    
    let state_file_path = app_data_dir.join("app_state.json");
    
    // Ensure directory exists
    fs::create_dir_all(&app_data_dir).await.unwrap();
    
    // Write corrupted JSON to state file
    fs::write(&state_file_path, "{ invalid json }").await.unwrap();
    
    // Try to read the corrupted file
    let read_result = fs::read_to_string(&state_file_path).await.unwrap();
    let parse_result = serde_json::from_str::<PersistedState>(&read_result);
    
    // Should fail to parse
    assert!(parse_result.is_err());
    
    // Should also fail to parse as legacy AppState
    let legacy_parse_result = serde_json::from_str::<AppState>(&read_result);
    assert!(legacy_parse_result.is_err());
}

#[tokio::test]
async fn test_incompatible_version_handling() {
    let temp_dir = TempDir::new().unwrap();
    let app_data_dir = temp_dir.path().to_path_buf();
    
    let state_file_path = app_data_dir.join("app_state.json");
    
    // Ensure directory exists
    fs::create_dir_all(&app_data_dir).await.unwrap();
    
    // Create state with incompatible version
    let incompatible_state = PersistedState {
        version: StateVersion {
            major: 99,
            minor: 0,
            patch: 0,
        },
        app_state: AppState::default(),
    };
    
    let json_data = serde_json::to_string_pretty(&incompatible_state).unwrap();
    fs::write(&state_file_path, &json_data).await.unwrap();
    
    // Try to read the incompatible state
    let read_data = fs::read_to_string(&state_file_path).await.unwrap();
    let loaded_state: PersistedState = serde_json::from_str(&read_data).unwrap();
    
    // Version should be incompatible
    assert!(!loaded_state.version.is_compatible());
}

#[tokio::test]
async fn test_atomic_write_operation() {
    let temp_dir = TempDir::new().unwrap();
    let app_data_dir = temp_dir.path().to_path_buf();
    
    let state_file_path = app_data_dir.join("app_state.json");
    let temp_file_path = state_file_path.with_extension("tmp");
    
    // Ensure directory exists
    fs::create_dir_all(&app_data_dir).await.unwrap();
    
    // Simulate atomic write operation
    let test_state = create_test_app_state();
    let persisted_state = PersistedState::new(test_state.clone());
    let json_data = serde_json::to_string_pretty(&persisted_state).unwrap();
    
    // Write to temp file first
    fs::write(&temp_file_path, &json_data).await.unwrap();
    assert!(temp_file_path.exists());
    assert!(!state_file_path.exists());
    
    // Then rename to final location
    fs::rename(&temp_file_path, &state_file_path).await.unwrap();
    assert!(!temp_file_path.exists());
    assert!(state_file_path.exists());
    
    // Verify content is correct
    let read_data = fs::read_to_string(&state_file_path).await.unwrap();
    let loaded_state: PersistedState = serde_json::from_str(&read_data).unwrap();
    assert_eq!(test_state, loaded_state.app_state);
}

#[tokio::test]
async fn test_app_state_completeness() {
    let test_state = create_test_app_state();
    
    // Verify all fields are properly set
    assert!(!test_state.directories.is_empty());
    assert!(test_state.selected_directory.is_some());
    assert!(!test_state.current_playlist.is_empty());
    assert!(test_state.playback_state.current_track.is_some());
    assert!(test_state.playback_state.is_playing);
    assert!(test_state.is_shuffle_mode);
    assert_ne!(test_state.window_geometry, WindowGeometry::default());
    
    // Test serialization roundtrip
    let serialized = serde_json::to_string(&test_state).unwrap();
    let deserialized: AppState = serde_json::from_str(&serialized).unwrap();
    assert_eq!(test_state, deserialized);
}
use local_mp3_player_lib::{AppState, Directory, Track, PlaybackState, WindowGeometry};
use std::path::PathBuf;

/// Integration test to verify the complete persistence workflow
/// This test simulates the full save/load cycle that would happen in the application

fn create_comprehensive_test_state() -> AppState {
    let mut app_state = AppState::default();
    
    // Add multiple directories
    let dir1 = Directory::new(PathBuf::from("/Users/test/Music/Rock"));
    let dir2 = Directory::new(PathBuf::from("/Users/test/Music/Jazz"));
    let dir3 = Directory::new(PathBuf::from("/Users/test/Music/Classical"));
    
    app_state.directories = vec![dir1.clone(), dir2.clone(), dir3];
    app_state.selected_directory = Some(dir1.id.clone());
    
    // Create a realistic playlist
    let mut track1 = Track::new(PathBuf::from("/Users/test/Music/Rock/song1.mp3"));
    track1.title = "Bohemian Rhapsody".to_string();
    track1.artist = "Queen".to_string();
    track1.album = "A Night at the Opera".to_string();
    track1.track_number = Some(11);
    track1.duration = 355.0; // 5:55
    track1.cover_art = Some(vec![0xFF, 0xD8, 0xFF, 0xE0]); // JPEG header bytes
    
    let mut track2 = Track::new(PathBuf::from("/Users/test/Music/Rock/song2.mp3"));
    track2.title = "Stairway to Heaven".to_string();
    track2.artist = "Led Zeppelin".to_string();
    track2.album = "Led Zeppelin IV".to_string();
    track2.track_number = Some(4);
    track2.duration = 482.0; // 8:02
    
    let mut track3 = Track::new(PathBuf::from("/Users/test/Music/Rock/song3.mp3"));
    track3.title = "Hotel California".to_string();
    track3.artist = "Eagles".to_string();
    track3.album = "Hotel California".to_string();
    track3.track_number = Some(1);
    track3.duration = 391.0; // 6:31
    
    app_state.current_playlist = vec![track1.clone(), track2, track3];
    
    // Set realistic playback state
    app_state.playback_state = PlaybackState {
        current_track: Some(track1),
        is_playing: true,
        current_time: 127.5, // 2:07.5 into the song
        duration: 355.0,
        volume: 0.75,
    };
    
    // Set shuffle mode and window geometry
    app_state.is_shuffle_mode = true;
    app_state.window_geometry = WindowGeometry {
        x: 150,
        y: 100,
        width: 1600,
        height: 1000,
    };
    
    app_state
}

#[tokio::test]
async fn test_complete_persistence_workflow() {
    // Create a comprehensive test state
    let original_state = create_comprehensive_test_state();
    
    // Test serialization to JSON (what would be saved to disk)
    let json_data = serde_json::to_string_pretty(&original_state).unwrap();
    
    // Verify the JSON contains expected data
    assert!(json_data.contains("Bohemian Rhapsody"));
    assert!(json_data.contains("Queen"));
    assert!(json_data.contains("/Users/test/Music/Rock"));
    assert!(json_data.contains("\"is_shuffle_mode\": true"));
    assert!(json_data.contains("\"width\": 1600"));
    
    // Test deserialization (what would be loaded from disk)
    let loaded_state: AppState = serde_json::from_str(&json_data).unwrap();
    
    // Verify all data is preserved correctly
    assert_eq!(original_state, loaded_state);
    
    // Verify specific fields
    assert_eq!(loaded_state.directories.len(), 3);
    assert_eq!(loaded_state.current_playlist.len(), 3);
    assert!(loaded_state.selected_directory.is_some());
    assert!(loaded_state.playback_state.current_track.is_some());
    assert!(loaded_state.is_shuffle_mode);
    
    // Verify track details
    let first_track = &loaded_state.current_playlist[0];
    assert_eq!(first_track.title, "Bohemian Rhapsody");
    assert_eq!(first_track.artist, "Queen");
    assert_eq!(first_track.duration, 355.0);
    assert!(first_track.cover_art.is_some());
    
    // Verify playback state details
    let playback = &loaded_state.playback_state;
    assert!(playback.is_playing);
    assert_eq!(playback.current_time, 127.5);
    assert_eq!(playback.volume, 0.75);
    
    // Verify window geometry
    let geometry = &loaded_state.window_geometry;
    assert_eq!(geometry.width, 1600);
    assert_eq!(geometry.height, 1000);
}

#[tokio::test]
async fn test_state_with_empty_collections() {
    let mut empty_state = AppState::default();
    
    // Set some non-default values but keep collections empty
    empty_state.is_shuffle_mode = true;
    empty_state.window_geometry.width = 800;
    empty_state.playback_state.volume = 0.5;
    
    // Test serialization/deserialization
    let json_data = serde_json::to_string_pretty(&empty_state).unwrap();
    let loaded_state: AppState = serde_json::from_str(&json_data).unwrap();
    
    assert_eq!(empty_state, loaded_state);
    assert!(loaded_state.directories.is_empty());
    assert!(loaded_state.current_playlist.is_empty());
    assert!(loaded_state.selected_directory.is_none());
    assert!(loaded_state.playback_state.current_track.is_none());
    assert!(loaded_state.is_shuffle_mode);
}

#[tokio::test]
async fn test_state_with_unicode_content() {
    let mut unicode_state = AppState::default();
    
    // Add directory with unicode path
    let unicode_dir = Directory::new(PathBuf::from("/Users/test/音乐/中文歌曲"));
    unicode_state.directories.push(unicode_dir);
    
    // Add track with unicode metadata
    let mut unicode_track = Track::new(PathBuf::from("/Users/test/音乐/中文歌曲/歌曲.mp3"));
    unicode_track.title = "月亮代表我的心".to_string();
    unicode_track.artist = "邓丽君".to_string();
    unicode_track.album = "经典歌曲集".to_string();
    
    unicode_state.current_playlist.push(unicode_track);
    
    // Test serialization/deserialization with unicode content
    let json_data = serde_json::to_string_pretty(&unicode_state).unwrap();
    let loaded_state: AppState = serde_json::from_str(&json_data).unwrap();
    
    assert_eq!(unicode_state, loaded_state);
    
    // Verify unicode content is preserved
    assert!(json_data.contains("月亮代表我的心"));
    assert!(json_data.contains("邓丽君"));
    assert_eq!(loaded_state.current_playlist[0].title, "月亮代表我的心");
    assert_eq!(loaded_state.current_playlist[0].artist, "邓丽君");
}

#[tokio::test]
async fn test_state_with_large_cover_art() {
    let mut state_with_art = AppState::default();
    
    // Create track with large cover art data
    let mut track = Track::new(PathBuf::from("/test/song.mp3"));
    track.title = "Test Song".to_string();
    
    // Create a large cover art (simulate a 100KB image)
    let large_cover_art: Vec<u8> = (0..100_000).map(|i| (i % 256) as u8).collect();
    track.cover_art = Some(large_cover_art.clone());
    
    state_with_art.current_playlist.push(track);
    
    // Test serialization/deserialization with large binary data
    let json_data = serde_json::to_string(&state_with_art).unwrap();
    let loaded_state: AppState = serde_json::from_str(&json_data).unwrap();
    
    assert_eq!(state_with_art, loaded_state);
    
    // Verify large cover art is preserved
    let loaded_cover_art = &loaded_state.current_playlist[0].cover_art;
    assert!(loaded_cover_art.is_some());
    assert_eq!(loaded_cover_art.as_ref().unwrap().len(), 100_000);
    assert_eq!(loaded_cover_art.as_ref().unwrap(), &large_cover_art);
}

#[tokio::test]
async fn test_state_size_and_performance() {
    // Create a state with many items to test performance
    let mut large_state = AppState::default();
    
    // Add many directories
    for i in 0..10 {
        let dir = Directory::new(PathBuf::from(format!("/test/music/dir_{}", i)));
        large_state.directories.push(dir);
    }
    
    // Add many tracks
    for i in 0..100 {
        let mut track = Track::new(PathBuf::from(format!("/test/music/track_{}.mp3", i)));
        track.title = format!("Track {}", i);
        track.artist = format!("Artist {}", i % 50); // 50 different artists
        track.album = format!("Album {}", i % 20); // 20 different albums
        track.duration = 180.0 + (i as f64 * 0.1); // Varying durations
        large_state.current_playlist.push(track);
    }
    
    // Measure serialization time and size
    let start_time = std::time::Instant::now();
    let json_data = serde_json::to_string(&large_state).unwrap();
    let serialization_time = start_time.elapsed();
    
    println!("Serialization time for large state: {:?}", serialization_time);
    println!("Serialized size: {} bytes", json_data.len());
    
    // Measure deserialization time
    let start_time = std::time::Instant::now();
    let loaded_state: AppState = serde_json::from_str(&json_data).unwrap();
    let deserialization_time = start_time.elapsed();
    
    println!("Deserialization time for large state: {:?}", deserialization_time);
    
    // Verify data integrity
    assert_eq!(large_state, loaded_state);
    assert_eq!(loaded_state.directories.len(), 10);
    assert_eq!(loaded_state.current_playlist.len(), 100);
    
    // Performance assertions (these are reasonable for the data size)
    assert!(serialization_time.as_millis() < 1000, "Serialization should be fast");
    assert!(deserialization_time.as_millis() < 1000, "Deserialization should be fast");
    assert!(json_data.len() < 1_000_000, "Serialized size should be reasonable"); // < 1MB
}

#[test]
fn test_app_state_default_values() {
    let default_state = AppState::default();
    
    // Verify default values are sensible
    assert!(default_state.directories.is_empty());
    assert!(default_state.selected_directory.is_none());
    assert!(default_state.current_playlist.is_empty());
    assert!(default_state.playback_state.current_track.is_none());
    assert!(!default_state.playback_state.is_playing);
    assert_eq!(default_state.playback_state.current_time, 0.0);
    assert_eq!(default_state.playback_state.volume, 1.0);
    assert!(!default_state.is_shuffle_mode);
    
    // Verify window geometry defaults
    let geometry = &default_state.window_geometry;
    assert_eq!(geometry.x, 100);
    assert_eq!(geometry.y, 100);
    assert_eq!(geometry.width, 1200);
    assert_eq!(geometry.height, 800);
}

#[test]
fn test_state_field_independence() {
    let mut state = AppState::default();
    
    // Modify each field independently and verify others remain unchanged
    let original_state = state.clone();
    
    // Test directory modification
    state.directories.push(Directory::new(PathBuf::from("/test")));
    assert_ne!(state.directories, original_state.directories);
    assert_eq!(state.selected_directory, original_state.selected_directory);
    assert_eq!(state.current_playlist, original_state.current_playlist);
    
    // Reset and test selected directory
    state = original_state.clone();
    state.selected_directory = Some("test-id".to_string());
    assert_eq!(state.directories, original_state.directories);
    assert_ne!(state.selected_directory, original_state.selected_directory);
    
    // Reset and test playlist
    state = original_state.clone();
    state.current_playlist.push(Track::new(PathBuf::from("/test.mp3")));
    assert_ne!(state.current_playlist, original_state.current_playlist);
    assert_eq!(state.playback_state, original_state.playback_state);
    
    // Reset and test shuffle mode
    state = original_state.clone();
    state.is_shuffle_mode = true;
    assert_ne!(state.is_shuffle_mode, original_state.is_shuffle_mode);
    assert_eq!(state.window_geometry, original_state.window_geometry);
}
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Represents a music directory that contains MP3 files
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct Directory {
    pub id: String,
    pub path: PathBuf,
    pub name: String,
    pub added_at: DateTime<Utc>,
}

impl Directory {
    pub fn new(path: PathBuf) -> Self {
        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("Unknown")
            .to_string();
        
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            path,
            name,
            added_at: Utc::now(),
        }
    }
}

/// Represents an MP3 track with metadata
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct Track {
    pub id: String,
    pub file_path: PathBuf,
    pub title: String,
    pub artist: String,
    pub album: String,
    pub track_number: Option<u32>,
    pub year: Option<u32>,
    pub genre: Option<String>,
    pub duration: f64, // seconds
    pub cover_art: Option<Vec<u8>>, // raw image data
}

impl Track {
    pub fn new(file_path: PathBuf) -> Self {
        let title = file_path
            .file_stem()
            .and_then(|n| n.to_str())
            .unwrap_or("Unknown")
            .to_string();
        
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            file_path,
            title,
            artist: "Unknown".to_string(),
            album: "Unknown".to_string(),
            track_number: None,
            year: None,
            genre: None,
            duration: 0.0,
            cover_art: None,
        }
    }
    
    /// Get cover art as base64 encoded string for frontend
    pub fn cover_art_base64(&self) -> Option<String> {
        self.cover_art.as_ref().map(|data| {
            use base64::Engine;
            base64::engine::general_purpose::STANDARD.encode(data)
        })
    }
}

/// Current playback state of the audio player
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct PlaybackState {
    pub current_track: Option<Track>,
    pub is_playing: bool,
    pub current_time: f64,
    pub duration: f64,
    pub volume: f32,
}

impl Default for PlaybackState {
    fn default() -> Self {
        Self {
            current_track: None,
            is_playing: false,
            current_time: 0.0,
            duration: 0.0,
            volume: 1.0,
        }
    }
}

/// Window geometry for state persistence
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct WindowGeometry {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}

impl Default for WindowGeometry {
    fn default() -> Self {
        Self {
            x: 100,
            y: 100,
            width: 1200,
            height: 800,
        }
    }
}

/// Complete application state for persistence
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct AppState {
    pub directories: Vec<Directory>,
    pub selected_directory: Option<String>,
    pub current_playlist: Vec<Track>,
    pub playback_state: PlaybackState,
    pub is_shuffle_mode: bool,
    pub window_geometry: WindowGeometry,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            directories: Vec::new(),
            selected_directory: None,
            current_playlist: Vec::new(),
            playback_state: PlaybackState::default(),
            is_shuffle_mode: false,
            window_geometry: WindowGeometry::default(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_directory_creation() {
        let path = PathBuf::from("/test/music");
        let directory = Directory::new(path.clone());
        
        assert_eq!(directory.path, path);
        assert_eq!(directory.name, "music");
        assert!(!directory.id.is_empty());
    }

    #[test]
    fn test_track_creation() {
        let path = PathBuf::from("/test/song.mp3");
        let track = Track::new(path.clone());
        
        assert_eq!(track.file_path, path);
        assert_eq!(track.title, "song");
        assert_eq!(track.artist, "Unknown");
        assert!(!track.id.is_empty());
    }

    #[test]
    fn test_track_cover_art_base64() {
        let mut track = Track::new(PathBuf::from("/test/song.mp3"));
        track.cover_art = Some(vec![1, 2, 3, 4]);
        
        let base64_result = track.cover_art_base64();
        assert!(base64_result.is_some());
        use base64::Engine;
        assert_eq!(base64_result.unwrap(), base64::engine::general_purpose::STANDARD.encode(&[1, 2, 3, 4]));
    }

    #[test]
    fn test_playback_state_default() {
        let state = PlaybackState::default();
        
        assert!(state.current_track.is_none());
        assert!(!state.is_playing);
        assert_eq!(state.current_time, 0.0);
        assert_eq!(state.volume, 1.0);
    }

    #[test]
    fn test_app_state_serialization() {
        let app_state = AppState::default();
        let serialized = serde_json::to_string(&app_state).unwrap();
        let deserialized: AppState = serde_json::from_str(&serialized).unwrap();
        
        assert_eq!(app_state, deserialized);
    }
}
pub mod audio_player;
pub mod directory_manager;
pub mod errors;
pub mod models;
pub mod persistence;
pub mod mp3_analyzer;

pub use audio_player::{AudioPlayer, PlaybackEvent};
pub use directory_manager::DirectoryManager;
pub use errors::*;
pub use models::*;
pub use persistence::PersistenceManager;

// Inline MetadataParser for now
use id3::TagLike;
use std::path::Path;
use tokio::fs;

/// Metadata parser for audio files using id3 library
pub struct MetadataParser;

impl MetadataParser {
    /// Create a new metadata parser instance
    pub fn new() -> Self {
        Self
    }

    /// Scan a directory for audio files and extract their metadata
    pub async fn scan_directory<P: AsRef<Path>>(&self, directory_path: P) -> AppResult<Vec<Track>> {
        let path = directory_path.as_ref();

        if !path.exists() {
            return Err(AppError::DirectoryNotFound(path.display().to_string()));
        }

        if !path.is_dir() {
            return Err(AppError::InvalidPath(format!(
                "Path is not a directory: {}",
                path.display()
            )));
        }

        let mut tracks = Vec::new();
        let mut entries = fs::read_dir(path).await?;

        while let Some(entry) = entries.next_entry().await? {
            let entry_path = entry.path();

            // Check if it's a supported audio file
            if self.is_supported_audio_file(&entry_path) {
                match self.parse_track_metadata(&entry_path).await {
                    Ok(track) => tracks.push(track),
                    Err(_e) => {
                        // Create a basic track with minimal information from filename
                        let mut basic_track = Track::new(entry_path.clone());

                        // Try to extract title from filename
                        if let Some(file_stem) = entry_path.file_stem().and_then(|s| s.to_str()) {
                            basic_track.title = file_stem.to_string();

                            // Try to parse artist-title pattern from filename
                            if let Some((artist, title)) = self.parse_filename_pattern(file_stem) {
                                basic_track.artist = artist;
                                basic_track.title = title;
                            }
                        }

                        tracks.push(basic_track);
                    }
                }
            }
        }

        // Sort tracks by track number, then by title
        tracks.sort_by(|a, b| match (a.track_number, b.track_number) {
            (Some(a_num), Some(b_num)) => a_num.cmp(&b_num),
            (Some(_), None) => std::cmp::Ordering::Less,
            (None, Some(_)) => std::cmp::Ordering::Greater,
            (None, None) => a.title.cmp(&b.title),
        });

        Ok(tracks)
    }

    /// Parse metadata from a single audio file with robust error handling
    pub async fn parse_track_metadata<P: AsRef<Path>>(&self, file_path: P) -> AppResult<Track> {
        let path = file_path.as_ref();

        if !path.exists() {
            return Err(AppError::FileSystem(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                format!("File not found: {}", path.display()),
            )));
        }

        let mut track = Track::new(path.to_path_buf());

        // Try to parse metadata with id3 for MP3 files
        if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
            if ext.to_lowercase() == "mp3" {
                if let Ok(()) = self.try_parse_with_id3(path, &mut track) {
                    return Ok(track);
                }
            }
        }

        // Fallback to filename parsing
        self.fallback_metadata_extraction(path, &mut track).await?;

        Ok(track)
    }

    /// Try to parse MP3 metadata using id3 library
    fn try_parse_with_id3(
        &self,
        path: &Path,
        track: &mut Track,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let tag = id3::Tag::read_from_path(path)?;

        // Extract metadata
        if let Some(title) = tag.title() {
            track.title = self.clean_metadata_string(title.to_string());
        }

        if let Some(artist) = tag.artist() {
            track.artist = self.clean_metadata_string(artist.to_string());
        }

        if let Some(album) = tag.album() {
            track.album = self.clean_metadata_string(album.to_string());
        }

        if let Some(track_num) = tag.track() {
            track.track_number = Some(track_num);
        }

        if let Some(year) = tag.year() {
            track.year = Some(year as u32);
        }

        if let Some(genre) = tag.genre() {
            track.genre = Some(self.clean_metadata_string(genre.to_string()));
        }

        // Try to get duration (id3 doesn't provide this directly)
        if track.duration == 0.0 {
            if let Ok(metadata) = std::fs::metadata(path) {
                let file_size = metadata.len();
                // Very rough estimation: assume 128 kbps bitrate
                track.duration = (file_size as f64 * 8.0) / 128_000.0;
                track.duration = track.duration.max(1.0).min(7200.0); // Cap between 1s and 2h
            }
        }

        Ok(())
    }

    /// Clean and validate metadata strings
    fn clean_metadata_string(&self, input: String) -> String {
        // Remove null bytes and other control characters that might cause issues
        let cleaned: String = input
            .chars()
            .filter(|c| !c.is_control() || *c == '\n' || *c == '\r' || *c == '\t')
            .collect();

        // Trim whitespace
        let trimmed = cleaned.trim();

        // Return cleaned string or "Unknown" if empty
        if trimmed.is_empty() {
            "Unknown".to_string()
        } else {
            trimmed.to_string()
        }
    }

    /// Fallback metadata extraction when libraries fail
    async fn fallback_metadata_extraction(&self, path: &Path, track: &mut Track) -> AppResult<()> {
        // Try to extract basic information from filename
        if let Some(file_stem) = path.file_stem().and_then(|s| s.to_str()) {
            // Try to parse common filename patterns like "Artist - Title.mp3"
            if let Some((artist, title)) = self.parse_filename_pattern(file_stem) {
                if track.artist == "Unknown" {
                    track.artist = artist;
                }
                if track.title == "Unknown" {
                    track.title = title;
                }
            } else {
                // Use the full filename as title if no pattern matches
                track.title = file_stem.to_string();
            }
        }

        // Try to get basic file duration using a more robust method
        if track.duration == 0.0 {
            track.duration = self
                .estimate_duration_from_file_size(path)
                .await
                .unwrap_or(0.0);
        }

        Ok(())
    }

    /// Parse common filename patterns to extract artist and title
    fn parse_filename_pattern(&self, filename: &str) -> Option<(String, String)> {
        // Common patterns:
        // "Artist - Title"
        // "Artist-Title"
        // But avoid treating track numbers like "01 - Song" as "Artist - Title"

        // Try "Artist - Title" pattern first
        if let Some(pos) = filename.find(" - ") {
            let potential_artist = filename[..pos].trim();
            let title = filename[pos + 3..].trim().to_string();
            
            // Don't treat pure numbers or short numeric prefixes as artist names
            if !potential_artist.is_empty() && !title.is_empty() {
                // Check if the potential artist is just a number (likely a track number)
                if potential_artist.parse::<u32>().is_ok() || 
                   (potential_artist.len() <= 3 && potential_artist.chars().all(|c| c.is_ascii_digit())) {
                    // This looks like a track number, don't parse as artist-title
                    return None;
                }
                return Some((potential_artist.to_string(), title));
            }
        }

        // Try "Artist-Title" pattern (without spaces) - be more careful here too
        if let Some(pos) = filename.find('-') {
            let potential_artist = filename[..pos].trim();
            let title = filename[pos + 1..].trim().to_string();
            
            if !potential_artist.is_empty() && !title.is_empty() {
                // Same check for numeric prefixes
                if potential_artist.parse::<u32>().is_ok() || 
                   (potential_artist.len() <= 3 && potential_artist.chars().all(|c| c.is_ascii_digit())) {
                    return None;
                }
                return Some((potential_artist.to_string(), title));
            }
        }

        None
    }

    /// Estimate duration from file size (very rough approximation)
    async fn estimate_duration_from_file_size(&self, path: &Path) -> AppResult<f64> {
        let metadata = fs::metadata(path).await?;
        let file_size = metadata.len();

        // Very rough estimation: assume 128 kbps bitrate
        let estimated_duration = (file_size as f64 * 8.0) / 128_000.0;

        // Cap the estimation to reasonable bounds (1 second to 2 hours)
        Ok(estimated_duration.max(1.0).min(7200.0))
    }

    /// Check if a file is a supported audio file based on its extension
    fn is_supported_audio_file<P: AsRef<Path>>(&self, path: P) -> bool {
        path.as_ref()
            .extension()
            .and_then(|ext| ext.to_str())
            .map(|ext| {
                let ext_lower = ext.to_lowercase();
                matches!(ext_lower.as_str(), "mp3" | "flac" | "ogg" | "m4a" | "wav")
            })
            .unwrap_or(false)
    }

    /// Validate that a file is a valid audio file by attempting to read its metadata
    pub async fn validate_audio_file<P: AsRef<Path>>(&self, file_path: P) -> bool {
        match self.parse_track_metadata(file_path).await {
            Ok(_) => true,
            Err(_) => false,
        }
    }

    /// Get supported audio file extensions
    pub fn supported_extensions() -> Vec<&'static str> {
        vec!["mp3", "flac", "ogg", "m4a", "wav"]
    }
}

impl Default for MetadataParser {
    fn default() -> Self {
        Self::new()
    }
}

use std::path::PathBuf;
use tauri::{Emitter, Manager, State};

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

/// Add a new directory to the music library
#[tauri::command]
async fn add_directory(
    path: String,
    directory_manager: State<'_, DirectoryManager>,
) -> Result<Directory, String> {
    let path_buf = PathBuf::from(path);
    directory_manager
        .add_directory(path_buf)
        .await
        .map_err(|e| e.to_string())
}

/// Get all directories in the music library
#[tauri::command]
async fn get_directories(
    directory_manager: State<'_, DirectoryManager>,
) -> Result<Vec<Directory>, String> {
    directory_manager
        .get_directories()
        .await
        .map_err(|e| e.to_string())
}

/// Remove a directory from the music library
#[tauri::command]
async fn remove_directory(
    id: String,
    directory_manager: State<'_, DirectoryManager>,
) -> Result<(), String> {
    directory_manager
        .remove_directory(&id)
        .await
        .map_err(|e| e.to_string())
}

/// Get a specific directory by ID
#[tauri::command]
async fn get_directory(
    id: String,
    directory_manager: State<'_, DirectoryManager>,
) -> Result<Option<Directory>, String> {
    directory_manager
        .get_directory(&id)
        .await
        .map_err(|e| e.to_string())
}

/// Refresh directories and remove inaccessible ones
#[tauri::command]
async fn refresh_directories(
    directory_manager: State<'_, DirectoryManager>,
) -> Result<Vec<String>, String> {
    directory_manager
        .refresh_directories()
        .await
        .map_err(|e| e.to_string())
}

/// Scan a directory for MP3 files and extract metadata
#[tauri::command]
async fn scan_directory(
    directory_id: String,
    directory_manager: State<'_, DirectoryManager>,
) -> Result<Vec<Track>, String> {
    // Get the directory by ID
    let directory = directory_manager
        .get_directory(&directory_id)
        .await
        .map_err(|e| e.to_string())?;

    match directory {
        Some(dir) => {
            let parser = MetadataParser::new();
            parser
                .scan_directory(&dir.path)
                .await
                .map_err(|e| e.to_string())
        }
        None => Err(format!("Directory with ID '{}' not found", directory_id)),
    }
}

/// Play a track by its file path
#[tauri::command]
async fn play_track(track: Track, audio_player: State<'_, AudioPlayer>) -> Result<(), String> {
    // Validate the audio file before attempting to play
    if let Err(e) = crate::audio_player::validate_audio_file(&track.file_path) {
        return Err(format!("Audio validation failed: {}", e));
    }

    audio_player
        .play_track(track)
        .await
        .map_err(|e| e.to_string())
}

/// Pause current playback
#[tauri::command]
async fn pause_playback(audio_player: State<'_, AudioPlayer>) -> Result<(), String> {
    audio_player.pause_playback().map_err(|e| e.to_string())
}

/// Resume current playback
#[tauri::command]
async fn resume_playback(audio_player: State<'_, AudioPlayer>) -> Result<(), String> {
    audio_player.resume_playback().map_err(|e| e.to_string())
}

/// Stop current playback
#[tauri::command]
async fn stop_playback(audio_player: State<'_, AudioPlayer>) -> Result<(), String> {
    audio_player.stop_playback().map_err(|e| e.to_string())
}

/// Seek to a specific position in the current track
#[tauri::command]
async fn seek_to(position: f64, audio_player: State<'_, AudioPlayer>) -> Result<(), String> {
    audio_player.seek_to(position).map_err(|e| e.to_string())
}

/// Set playback volume (0.0 to 1.0)
#[tauri::command]
async fn set_volume(volume: f32, audio_player: State<'_, AudioPlayer>) -> Result<(), String> {
    audio_player.set_volume(volume).map_err(|e| e.to_string())
}

/// Get current playback state
#[tauri::command]
async fn get_playback_state(audio_player: State<'_, AudioPlayer>) -> Result<PlaybackState, String> {
    Ok(audio_player.get_playback_state())
}

/// Save application state to disk
#[tauri::command]
async fn save_app_state(
    state: AppState,
    persistence_manager: State<'_, PersistenceManager>,
) -> Result<(), String> {
    persistence_manager
        .save_app_state(state)
        .await
        .map_err(|e| e.to_string())
}

/// Load application state from disk
#[tauri::command]
async fn load_app_state(
    persistence_manager: State<'_, PersistenceManager>,
) -> Result<AppState, String> {
    persistence_manager
        .load_app_state()
        .await
        .map_err(|e| e.to_string())
}

/// Clear saved application state (useful for reset functionality)
#[tauri::command]
async fn clear_saved_state(
    persistence_manager: State<'_, PersistenceManager>,
) -> Result<(), String> {
    persistence_manager
        .clear_saved_state()
        .await
        .map_err(|e| e.to_string())
}

/// Validate an audio file to check if it can be played
#[tauri::command]
async fn validate_audio_file(file_path: String) -> Result<(), String> {
    crate::audio_player::validate_audio_file(&file_path)
        .map_err(|e| e.to_string())
}

/// Analyze an MP3 file and return detailed diagnostic information
#[tauri::command]
async fn analyze_mp3_file(file_path: String) -> Result<String, String> {
    match crate::mp3_analyzer::analyze_mp3_file(&file_path) {
        Ok(info) => Ok(info.format_analysis()),
        Err(e) => Err(format!("Failed to analyze MP3 file: {}", e)),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            // Initialize directory manager
            let directory_manager = DirectoryManager::new();

            // Initialize with app handle
            let app_handle = app.handle().clone();
            let manager_clone = directory_manager.clone();

            tauri::async_runtime::spawn(async move {
                if let Err(e) = manager_clone.initialize(&app_handle).await {
                    eprintln!("Failed to initialize directory manager: {}", e);
                }
            });

            // Initialize audio player
            let (audio_player, mut event_receiver) = AudioPlayer::new()
                .map_err(|e| format!("Failed to initialize audio player: {}", e))?;

            // Handle audio player events
            let app_handle_clone = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                while let Some(event) = event_receiver.recv().await {
                    // Emit events to frontend
                    match event {
                        PlaybackEvent::TrackStarted(track) => {
                            let _ = app_handle_clone.emit("track-started", &track);
                        }
                        PlaybackEvent::TrackPaused => {
                            let _ = app_handle_clone.emit("track-paused", ());
                        }
                        PlaybackEvent::TrackResumed => {
                            let _ = app_handle_clone.emit("track-resumed", ());
                        }
                        PlaybackEvent::TrackStopped => {
                            let _ = app_handle_clone.emit("track-stopped", ());
                        }
                        PlaybackEvent::TrackFinished => {
                            let _ = app_handle_clone.emit("track-finished", ());
                        }
                        PlaybackEvent::PositionChanged(position) => {
                            let _ = app_handle_clone.emit("position-changed", position);
                        }
                        PlaybackEvent::VolumeChanged(volume) => {
                            let _ = app_handle_clone.emit("volume-changed", volume);
                        }
                        PlaybackEvent::Error(error) => {
                            let _ = app_handle_clone.emit("playback-error", error);
                        }
                    }
                }
            });

            // Initialize persistence manager
            let persistence_manager = PersistenceManager::new(app.handle().clone());

            app.manage(directory_manager);
            app.manage(audio_player);
            app.manage(persistence_manager);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            add_directory,
            get_directories,
            remove_directory,
            get_directory,
            refresh_directories,
            scan_directory,
            play_track,
            pause_playback,
            resume_playback,
            stop_playback,
            seek_to,
            set_volume,
            get_playback_state,
            save_app_state,
            load_app_state,
            clear_saved_state,
            validate_audio_file,
            analyze_mp3_file
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

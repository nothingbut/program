use crate::{AppError, PlaybackState, Track};
use rodio::{Decoder, OutputStream, OutputStreamHandle, Sink};
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use std::sync::{Arc, Mutex};
use tokio::sync::{mpsc, oneshot};

/// Audio player engine using rodio in a separate thread
#[derive(Clone)]
pub struct AudioPlayer {
    command_sender: mpsc::UnboundedSender<AudioCommand>,
    state: Arc<Mutex<AudioPlayerState>>,
    #[allow(dead_code)] // Used for future event emission functionality
    event_sender: mpsc::UnboundedSender<PlaybackEvent>,
}

/// Internal state that can be safely shared across threads
struct AudioPlayerState {
    current_track: Option<Track>,
    is_playing: bool,
    volume: f32,
    current_time: f64,
    duration: f64,
    playback_start_time: Option<std::time::Instant>,
}

/// Commands sent to the audio thread
enum AudioCommand {
    PlayTrack {
        track: Track,
        response: oneshot::Sender<Result<(), AppError>>,
    },
    Pause {
        response: oneshot::Sender<Result<(), AppError>>,
    },
    Resume {
        response: oneshot::Sender<Result<(), AppError>>,
    },
    Stop {
        response: oneshot::Sender<Result<(), AppError>>,
    },
    SetVolume {
        volume: f32,
        response: oneshot::Sender<Result<(), AppError>>,
    },
    Seek {
        position: f64,
        response: oneshot::Sender<Result<(), AppError>>,
    },
}

/// Events emitted by the audio player
#[derive(Debug, Clone)]
pub enum PlaybackEvent {
    TrackStarted(Track),
    TrackPaused,
    TrackResumed,
    TrackStopped,
    TrackFinished,
    PositionChanged(f64),
    VolumeChanged(f32),
    Error(String),
}

impl AudioPlayer {
    /// Create a new audio player instance
    pub fn new() -> Result<(Self, mpsc::UnboundedReceiver<PlaybackEvent>), AppError> {
        let (command_sender, command_receiver) = mpsc::unbounded_channel();
        let (event_sender, event_receiver) = mpsc::unbounded_channel();

        let state = Arc::new(Mutex::new(AudioPlayerState {
            current_track: None,
            is_playing: false,
            volume: 1.0,
            current_time: 0.0,
            duration: 0.0,
            playback_start_time: None,
        }));

        let player = AudioPlayer {
            command_sender,
            state: state.clone(),
            event_sender: event_sender.clone(),
        };

        // Spawn the audio thread using std::thread to avoid Send issues
        let state_clone = state.clone();
        let event_sender_clone = event_sender.clone();
        std::thread::spawn(move || {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(audio_thread(command_receiver, state_clone, event_sender_clone));
        });

        Ok((player, event_receiver))
    }

    /// Play a track from file path
    pub async fn play_track(&self, track: Track) -> Result<(), AppError> {
        let (response_tx, response_rx) = oneshot::channel();
        
        self.command_sender
            .send(AudioCommand::PlayTrack {
                track,
                response: response_tx,
            })
            .map_err(|_| AppError::Playback("Audio thread is not running".to_string()))?;

        response_rx
            .await
            .map_err(|_| AppError::Playback("Failed to receive response from audio thread".to_string()))?
    }

    /// Pause current playback
    pub fn pause_playback(&self) -> Result<(), AppError> {
        let (response_tx, response_rx) = oneshot::channel();
        
        self.command_sender
            .send(AudioCommand::Pause {
                response: response_tx,
            })
            .map_err(|_| AppError::Playback("Audio thread is not running".to_string()))?;

        // Use blocking wait since this is a sync function
        tokio::task::block_in_place(|| {
            tokio::runtime::Handle::current().block_on(response_rx)
        })
        .map_err(|_| AppError::Playback("Failed to receive response from audio thread".to_string()))?
    }

    /// Resume current playback
    pub fn resume_playback(&self) -> Result<(), AppError> {
        let (response_tx, response_rx) = oneshot::channel();
        
        self.command_sender
            .send(AudioCommand::Resume {
                response: response_tx,
            })
            .map_err(|_| AppError::Playback("Audio thread is not running".to_string()))?;

        // Use blocking wait since this is a sync function
        tokio::task::block_in_place(|| {
            tokio::runtime::Handle::current().block_on(response_rx)
        })
        .map_err(|_| AppError::Playback("Failed to receive response from audio thread".to_string()))?
    }

    /// Stop current playback
    pub fn stop_playback(&self) -> Result<(), AppError> {
        let (response_tx, response_rx) = oneshot::channel();
        
        self.command_sender
            .send(AudioCommand::Stop {
                response: response_tx,
            })
            .map_err(|_| AppError::Playback("Audio thread is not running".to_string()))?;

        // Use blocking wait since this is a sync function
        tokio::task::block_in_place(|| {
            tokio::runtime::Handle::current().block_on(response_rx)
        })
        .map_err(|_| AppError::Playback("Failed to receive response from audio thread".to_string()))?
    }

    /// Seek to a specific position in seconds
    pub fn seek_to(&self, position: f64) -> Result<(), AppError> {
        let (response_tx, response_rx) = oneshot::channel();
        
        self.command_sender
            .send(AudioCommand::Seek {
                position,
                response: response_tx,
            })
            .map_err(|_| AppError::Playback("Audio thread is not running".to_string()))?;

        // Use blocking wait since this is a sync function
        tokio::task::block_in_place(|| {
            tokio::runtime::Handle::current().block_on(response_rx)
        })
        .map_err(|_| AppError::Playback("Failed to receive response from audio thread".to_string()))?
    }

    /// Set playback volume (0.0 to 1.0)
    pub fn set_volume(&self, volume: f32) -> Result<(), AppError> {
        let (response_tx, response_rx) = oneshot::channel();
        
        self.command_sender
            .send(AudioCommand::SetVolume {
                volume,
                response: response_tx,
            })
            .map_err(|_| AppError::Playback("Audio thread is not running".to_string()))?;

        // Use blocking wait since this is a sync function
        tokio::task::block_in_place(|| {
            tokio::runtime::Handle::current().block_on(response_rx)
        })
        .map_err(|_| AppError::Playback("Failed to receive response from audio thread".to_string()))?
    }

    /// Get current playback state
    pub fn get_playback_state(&self) -> PlaybackState {
        let state = self.state.lock().unwrap();
        
        PlaybackState {
            current_track: state.current_track.clone(),
            is_playing: state.is_playing,
            current_time: state.current_time,
            duration: state.duration,
            volume: state.volume,
        }
    }

    /// Check if a track is currently playing
    pub fn is_playing(&self) -> bool {
        let state = self.state.lock().unwrap();
        state.is_playing
    }

    /// Check if playback is finished
    pub fn is_finished(&self) -> bool {
        let state = self.state.lock().unwrap();
        !state.is_playing && state.current_track.is_none()
    }

    /// Get current track
    pub fn current_track(&self) -> Option<Track> {
        let state = self.state.lock().unwrap();
        state.current_track.clone()
    }
}

/// Audio thread that handles all rodio operations
async fn audio_thread(
    mut command_receiver: mpsc::UnboundedReceiver<AudioCommand>,
    state: Arc<Mutex<AudioPlayerState>>,
    event_sender: mpsc::UnboundedSender<PlaybackEvent>,
) {
    // Initialize audio output in this thread
    let (_stream, stream_handle) = match OutputStream::try_default() {
        Ok(output) => output,
        Err(e) => {
            let _ = event_sender.send(PlaybackEvent::Error(format!(
                "Failed to create audio output: {}", e
            )));
            return;
        }
    };

    let mut current_sink: Option<Sink> = None;
    
    // Create a timer for position updates
    let mut position_update_interval = tokio::time::interval(tokio::time::Duration::from_millis(100));
    let mut last_position = 0.0;

    loop {
        tokio::select! {
            // Handle commands
            command = command_receiver.recv() => {
                match command {
                    Some(command) => {
                        match command {
                            AudioCommand::PlayTrack { track, response } => {
                                let result = handle_play_track(
                                    &track,
                                    &stream_handle,
                                    &mut current_sink,
                                    &state,
                                    &event_sender,
                                ).await;
                                let _ = response.send(result);
                            }
                            AudioCommand::Pause { response } => {
                                let result = handle_pause(&mut current_sink, &state, &event_sender);
                                let _ = response.send(result);
                            }
                            AudioCommand::Resume { response } => {
                                let result = handle_resume(&mut current_sink, &state, &event_sender);
                                let _ = response.send(result);
                            }
                            AudioCommand::Stop { response } => {
                                let result = handle_stop(&mut current_sink, &state, &event_sender);
                                let _ = response.send(result);
                            }
                            AudioCommand::SetVolume { volume, response } => {
                                let result = handle_set_volume(volume, &mut current_sink, &state, &event_sender);
                                let _ = response.send(result);
                            }
                            AudioCommand::Seek { position, response } => {
                                let result = handle_seek(position);
                                let _ = response.send(result);
                            }
                        }
                    }
                    None => break, // Channel closed
                }
            }
            
            // Handle position updates
            _ = position_update_interval.tick() => {
                update_position(&mut current_sink, &state, &event_sender, &mut last_position);
            }
        }
    }
}

async fn handle_play_track(
    track: &Track,
    stream_handle: &OutputStreamHandle,
    current_sink: &mut Option<Sink>,
    state: &Arc<Mutex<AudioPlayerState>>,
    event_sender: &mpsc::UnboundedSender<PlaybackEvent>,
) -> Result<(), AppError> {
    // Stop current playback if any
    if let Some(ref sink) = current_sink {
        sink.stop();
    }

    // Create new sink
    let sink = Sink::try_new(stream_handle)
        .map_err(|e| AppError::Playback(format!("Failed to create sink: {}", e)))?;

    // Validate file exists and is readable
    if !track.file_path.exists() {
        return Err(AppError::Playback(format!(
            "Audio file not found: {}", 
            track.file_path.display()
        )));
    }

    // Check file size to avoid empty files
    let metadata = std::fs::metadata(&track.file_path)
        .map_err(|e| AppError::FileSystem(e))?;
    
    if metadata.len() == 0 {
        return Err(AppError::Playback(format!(
            "Audio file is empty: {}", 
            track.file_path.display()
        )));
    }

    // Load and decode the audio file with better error context
    
    let decoder = create_robust_decoder(&track.file_path)
        .map_err(|e| {
            let file_ext = track.file_path.extension()
                .and_then(|ext| ext.to_str())
                .unwrap_or("unknown");
            
            AppError::Playback(format!(
                "Failed to decode audio file '{}' (format: {}): {}. The audio file appears to be corrupted and cannot be played.", 
                track.file_path.display(),
                file_ext,
                e
            ))
        })?;

    // Get current volume from state
    let volume = {
        let state_guard = state.lock().unwrap();
        state_guard.volume
    };

    // Set volume and play
    sink.set_volume(volume);
    sink.append(decoder);
    sink.play();

    // Update state
    {
        let mut state_guard = state.lock().unwrap();
        state_guard.current_track = Some(track.clone());
        state_guard.is_playing = true;
        state_guard.current_time = 0.0;
        state_guard.duration = track.duration;
        state_guard.playback_start_time = Some(std::time::Instant::now());
    }

    *current_sink = Some(sink);

    // Send event
    let _ = event_sender.send(PlaybackEvent::TrackStarted(track.clone()));

    Ok(())
}

fn handle_pause(
    current_sink: &mut Option<Sink>,
    state: &Arc<Mutex<AudioPlayerState>>,
    event_sender: &mpsc::UnboundedSender<PlaybackEvent>,
) -> Result<(), AppError> {
    if let Some(ref sink) = current_sink {
        let mut state_guard = state.lock().unwrap();
        if state_guard.is_playing {
            sink.pause();
            state_guard.is_playing = false;
            state_guard.playback_start_time = None; // Clear start time when paused
            let _ = event_sender.send(PlaybackEvent::TrackPaused);
        }
    }
    Ok(())
}

fn handle_resume(
    current_sink: &mut Option<Sink>,
    state: &Arc<Mutex<AudioPlayerState>>,
    event_sender: &mpsc::UnboundedSender<PlaybackEvent>,
) -> Result<(), AppError> {
    if let Some(ref sink) = current_sink {
        let mut state_guard = state.lock().unwrap();
        if !state_guard.is_playing {
            sink.play();
            state_guard.is_playing = true;
            state_guard.playback_start_time = Some(std::time::Instant::now()); // Reset start time when resumed
            let _ = event_sender.send(PlaybackEvent::TrackResumed);
        }
    }
    Ok(())
}

fn handle_stop(
    current_sink: &mut Option<Sink>,
    state: &Arc<Mutex<AudioPlayerState>>,
    event_sender: &mpsc::UnboundedSender<PlaybackEvent>,
) -> Result<(), AppError> {
    if let Some(ref sink) = current_sink {
        sink.stop();
        let mut state_guard = state.lock().unwrap();
        state_guard.is_playing = false;
        state_guard.current_track = None;
        state_guard.current_time = 0.0;
        state_guard.duration = 0.0;
        state_guard.playback_start_time = None;
        let _ = event_sender.send(PlaybackEvent::TrackStopped);
    }
    *current_sink = None;
    Ok(())
}

fn handle_set_volume(
    volume: f32,
    current_sink: &mut Option<Sink>,
    state: &Arc<Mutex<AudioPlayerState>>,
    event_sender: &mpsc::UnboundedSender<PlaybackEvent>,
) -> Result<(), AppError> {
    let clamped_volume = volume.clamp(0.0, 1.0);
    
    {
        let mut state_guard = state.lock().unwrap();
        state_guard.volume = clamped_volume;
    }

    if let Some(ref sink) = current_sink {
        sink.set_volume(clamped_volume);
    }

    let _ = event_sender.send(PlaybackEvent::VolumeChanged(clamped_volume));
    Ok(())
}

fn handle_seek(_position: f64) -> Result<(), AppError> {
    // Note: rodio doesn't support seeking directly
    // This is a limitation we'll need to work around
    // For now, we'll return an error indicating this limitation
    Err(AppError::Playback(
        "Seeking is not supported in the current rodio version".to_string()
    ))
}

/// Create a robust decoder that tries multiple strategies
fn create_robust_decoder<P: AsRef<std::path::Path>>(path: P) -> Result<Decoder<BufReader<File>>, Box<dyn std::error::Error + Send + Sync>> {
    let path = path.as_ref();
    
    // Strategy 1: Try standard decoder first
    if let Ok(decoder) = try_standard_decoder(path) {
        return Ok(decoder);
    }
    
    // Strategy 2: Try with a larger buffer size (helps with some MP3 files)
    if let Ok(decoder) = try_buffered_decoder(path) {
        return Ok(decoder);
    }
    
    // Strategy 3: Try reading a portion of the file first to validate
    if let Ok(decoder) = try_validated_decoder(path) {
        return Ok(decoder);
    }
    
    // Strategy 4: Try skipping potential problematic headers
    if let Ok(decoder) = try_skip_header_decoder(path) {
        return Ok(decoder);
    }
    
    Err("All decoding strategies failed. The file may be corrupted or use an unsupported MP3 encoding.".into())
}

/// Try with a larger buffer size (helps with some MP3 files)
fn try_buffered_decoder<P: AsRef<std::path::Path>>(path: P) -> Result<Decoder<BufReader<File>>, Box<dyn std::error::Error + Send + Sync>> {
    let file = File::open(path)?;
    let buf_reader = BufReader::with_capacity(128 * 1024, file); // 128KB buffer
    let decoder = Decoder::new(buf_reader)?;
    Ok(decoder)
}

/// Try the standard rodio decoder
fn try_standard_decoder<P: AsRef<std::path::Path>>(path: P) -> Result<Decoder<BufReader<File>>, Box<dyn std::error::Error + Send + Sync>> {
    let file = File::open(path)?;
    let buf_reader = BufReader::new(file);
    let decoder = Decoder::new(buf_reader)?;
    Ok(decoder)
}

/// Try validating the file first by reading a small portion
fn try_validated_decoder<P: AsRef<std::path::Path>>(path: P) -> Result<Decoder<BufReader<File>>, Box<dyn std::error::Error + Send + Sync>> {
    let path = path.as_ref();
    
    // First, try to read the first few bytes to check for MP3 header
    let mut file = File::open(path)?;
    let mut header = [0u8; 10];
    file.read_exact(&mut header)?;
    
    // Check for MP3 sync word (0xFF 0xFB, 0xFF 0xFA, etc.)
    if header[0] == 0xFF && (header[1] & 0xE0) == 0xE0 {
        // Looks like a valid MP3 header, try decoding
        drop(file);
        let file = File::open(path)?;
        let buf_reader = BufReader::with_capacity(256 * 1024, file); // Even larger buffer
        let decoder = Decoder::new(buf_reader)?;
        Ok(decoder)
    } else {
        Err("File does not appear to have a valid MP3 header".into())
    }
}

/// Try skipping potential problematic headers (like large ID3 tags)
fn try_skip_header_decoder<P: AsRef<std::path::Path>>(path: P) -> Result<Decoder<BufReader<File>>, Box<dyn std::error::Error + Send + Sync>> {
    let path = path.as_ref();
    let mut file = File::open(path)?;
    
    // Read first chunk to look for ID3 tags or other headers
    let mut buffer = [0u8; 1024];
    file.read_exact(&mut buffer)?;
    drop(file);
    
    // Look for MP3 sync word in the first 1KB
    for i in 0..buffer.len() - 4 {
        if buffer[i] == 0xFF && (buffer[i + 1] & 0xE0) == 0xE0 {
            // Found potential MP3 frame, try decoding from this position
            let file = File::open(path)?;
            let mut buf_reader = BufReader::new(file);
            
            // Skip to the found position
            if i > 0 {
                let mut skip_buffer = vec![0u8; i];
                buf_reader.read_exact(&mut skip_buffer)?;
            }
            
            // Try to decode from here
            if let Ok(decoder) = Decoder::new(buf_reader) {
                return Ok(decoder);
            }
        }
    }
    
    Err("Could not find valid MP3 frame in first 1KB".into())
}

/// Update playback position and emit events
fn update_position(
    current_sink: &mut Option<Sink>,
    state: &Arc<Mutex<AudioPlayerState>>,
    event_sender: &mpsc::UnboundedSender<PlaybackEvent>,
    last_position: &mut f64,
) {
    if let Some(ref sink) = current_sink {
        let mut state_guard = state.lock().unwrap();
        
        // Only update if we're playing and not paused
        if state_guard.is_playing && !sink.is_paused() {
            if let Some(start_time) = state_guard.playback_start_time {
                // Calculate elapsed time since playback started
                let elapsed = start_time.elapsed().as_secs_f64();
                let new_position = state_guard.current_time + elapsed;
                
                // Don't exceed duration
                if new_position <= state_guard.duration {
                    state_guard.current_time = new_position;
                    
                    // Update start time for next calculation
                    state_guard.playback_start_time = Some(std::time::Instant::now());
                    
                    // Only send event if position changed significantly (to avoid spam)
                    if (new_position - *last_position).abs() >= 0.5 {
                        let _ = event_sender.send(PlaybackEvent::PositionChanged(new_position));
                        *last_position = new_position;
                    }
                } else {
                    // Track finished
                    state_guard.current_time = state_guard.duration;
                    state_guard.is_playing = false;
                    state_guard.playback_start_time = None;
                    let _ = event_sender.send(PlaybackEvent::TrackFinished);
                }
            }
        }
    }
}

/// Helper function to validate audio file
pub fn validate_audio_file<P: AsRef<Path>>(path: P) -> Result<(), AppError> {
    let path = path.as_ref();
    
    // Check if file exists
    if !path.exists() {
        return Err(AppError::Playback(format!(
            "Audio file not found: {}", 
            path.display()
        )));
    }

    // Check file size
    let metadata = std::fs::metadata(path)
        .map_err(|e| AppError::FileSystem(e))?;
    
    if metadata.len() == 0 {
        return Err(AppError::Playback(format!(
            "Audio file is empty: {}", 
            path.display()
        )));
    }

    // Check if it's a supported format by extension
    let supported_extensions = ["mp3", "flac", "wav", "ogg", "m4a"];
    let file_ext = path.extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| ext.to_lowercase());
    
    if let Some(ext) = &file_ext {
        if !supported_extensions.contains(&ext.as_str()) {
            return Err(AppError::Playback(format!(
                "Unsupported audio format: .{} (supported: {})", 
                ext,
                supported_extensions.join(", ")
            )));
        }
    }

    // Try to decode the file using robust decoder
    create_robust_decoder(path)
        .map_err(|e| {
            AppError::Playback(format!(
                "Cannot decode audio file '{}' (format: {}): {}. The file may be corrupted or use an unsupported codec.", 
                path.display(),
                file_ext.unwrap_or_else(|| "unknown".to_string()),
                e
            ))
        })?;
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;
    use tempfile::NamedTempFile;

    fn create_test_track() -> Track {
        Track {
            id: "test-track".to_string(),
            file_path: PathBuf::from("test_assets/sample.mp3"),
            title: "Test Song".to_string(),
            artist: "Test Artist".to_string(),
            album: "Test Album".to_string(),
            track_number: Some(1),
            year: Some(2023),
            genre: Some("Rock".to_string()),
            duration: 180.0,
            cover_art: None,
        }
    }

    #[tokio::test]
    async fn test_audio_player_creation() {
        let result = AudioPlayer::new();
        assert!(result.is_ok());
        
        let (player, _receiver) = result.unwrap();
        assert!(!player.is_playing());
        assert!(player.current_track().is_none());
    }

    #[test]
    fn test_playback_state_default() {
        let (player, _receiver) = AudioPlayer::new().unwrap();
        let state = player.get_playback_state();
        
        assert!(state.current_track.is_none());
        assert!(!state.is_playing);
        assert_eq!(state.current_time, 0.0);
        assert_eq!(state.volume, 1.0);
    }

    #[tokio::test(flavor = "multi_thread")]
    async fn test_volume_control() {
        let (player, _receiver) = AudioPlayer::new().unwrap();
        
        // Give the audio thread time to start
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        
        // Test setting volume
        assert!(player.set_volume(0.5).is_ok());
        let state = player.get_playback_state();
        assert_eq!(state.volume, 0.5);
        
        // Test volume clamping
        assert!(player.set_volume(1.5).is_ok());
        let state = player.get_playback_state();
        assert_eq!(state.volume, 1.0);
        
        assert!(player.set_volume(-0.5).is_ok());
        let state = player.get_playback_state();
        assert_eq!(state.volume, 0.0);
    }

    #[tokio::test(flavor = "multi_thread")]
    async fn test_pause_resume_without_track() {
        let (player, _receiver) = AudioPlayer::new().unwrap();
        
        // Give the audio thread time to start
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        
        // Should not error when pausing/resuming without a track
        assert!(player.pause_playback().is_ok());
        assert!(player.resume_playback().is_ok());
        assert!(player.stop_playback().is_ok());
    }

    #[tokio::test(flavor = "multi_thread")]
    async fn test_seek_limitation() {
        let (player, _receiver) = AudioPlayer::new().unwrap();
        
        // Give the audio thread time to start
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        
        // Seeking should return an error indicating the limitation
        let result = player.seek_to(30.0);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Seeking is not supported"));
    }

    #[test]
    fn test_validate_audio_file_with_invalid_file() {
        // Create a temporary file with invalid content
        let temp_file = NamedTempFile::new().unwrap();
        std::fs::write(temp_file.path(), b"not an audio file").unwrap();
        
        let result = validate_audio_file(temp_file.path());
        assert!(result.is_err());
    }
}
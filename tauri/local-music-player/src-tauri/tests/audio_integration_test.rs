use local_mp3_player_lib::{AudioPlayer, Track};
use std::path::PathBuf;
use tokio::time::{sleep, Duration};

/// Integration test for the audio player functionality
/// Tests the complete workflow from creation to playback control
#[tokio::test(flavor = "multi_thread")]
async fn test_audio_player_integration() {
    // Create audio player
    let (player, mut event_receiver) = AudioPlayer::new().unwrap();
    
    // Give the audio thread time to initialize
    sleep(Duration::from_millis(100)).await;
    
    // Test initial state
    let initial_state = player.get_playback_state();
    assert!(initial_state.current_track.is_none());
    assert!(!initial_state.is_playing);
    assert_eq!(initial_state.volume, 1.0);
    assert_eq!(initial_state.current_time, 0.0);
    
    // Test volume control
    assert!(player.set_volume(0.7).is_ok());
    let state_after_volume = player.get_playback_state();
    assert_eq!(state_after_volume.volume, 0.7);
    
    // Test volume clamping
    assert!(player.set_volume(1.5).is_ok());
    let state_clamped = player.get_playback_state();
    assert_eq!(state_clamped.volume, 1.0);
    
    // Test pause/resume without track (should not error)
    assert!(player.pause_playback().is_ok());
    assert!(player.resume_playback().is_ok());
    assert!(player.stop_playback().is_ok());
    
    // Test seeking limitation
    let seek_result = player.seek_to(30.0);
    assert!(seek_result.is_err());
    assert!(seek_result.unwrap_err().to_string().contains("Seeking is not supported"));
    
    // Test helper functions
    assert!(!player.is_playing());
    assert!(player.is_finished());
    assert!(player.current_track().is_none());
    
    // Test with a mock track (won't actually play since file doesn't exist)
    let mock_track = Track {
        id: "test-track".to_string(),
        file_path: PathBuf::from("nonexistent.mp3"),
        title: "Test Song".to_string(),
        artist: "Test Artist".to_string(),
        album: "Test Album".to_string(),
        track_number: Some(1),
        year: Some(2023),
        genre: Some("Rock".to_string()),
        duration: 180.0,
        cover_art: None,
    };
    
    // This should fail because the file doesn't exist
    let play_result = player.play_track(mock_track).await;
    assert!(play_result.is_err());
    
    // Verify events can be received (though we won't get any successful playback events)
    // Just check that the receiver is working
    tokio::select! {
        _ = sleep(Duration::from_millis(50)) => {
            // Timeout is expected since we don't have valid audio files
        }
        event = event_receiver.recv() => {
            // If we get an event, it should be an error event
            if let Some(event) = event {
                println!("Received event: {:?}", event);
            }
        }
    }
}

/// Test the audio player state management
#[tokio::test(flavor = "multi_thread")]
async fn test_audio_player_state_management() {
    let (player, _receiver) = AudioPlayer::new().unwrap();
    
    // Give the audio thread time to initialize
    sleep(Duration::from_millis(100)).await;
    
    // Test multiple volume changes
    let volumes = [0.0, 0.25, 0.5, 0.75, 1.0];
    for volume in volumes {
        assert!(player.set_volume(volume).is_ok());
        let state = player.get_playback_state();
        assert_eq!(state.volume, volume);
    }
    
    // Test that state is consistent across multiple calls
    for _ in 0..5 {
        let state1 = player.get_playback_state();
        let state2 = player.get_playback_state();
        assert_eq!(state1.volume, state2.volume);
        assert_eq!(state1.is_playing, state2.is_playing);
        assert_eq!(state1.current_time, state2.current_time);
    }
}

/// Test concurrent access to the audio player
#[tokio::test(flavor = "multi_thread")]
async fn test_audio_player_concurrent_access() {
    let (player, _receiver) = AudioPlayer::new().unwrap();
    
    // Give the audio thread time to initialize
    sleep(Duration::from_millis(100)).await;
    
    // Clone the player for concurrent access
    let player1 = player.clone();
    let player2 = player.clone();
    let player3 = player.clone();
    
    // Spawn multiple tasks that interact with the player concurrently
    let task1 = tokio::spawn(async move {
        for i in 0..10 {
            let volume = (i as f32) / 10.0;
            assert!(player1.set_volume(volume).is_ok());
            sleep(Duration::from_millis(10)).await;
        }
    });
    
    let task2 = tokio::spawn(async move {
        for _ in 0..10 {
            let _state = player2.get_playback_state();
            sleep(Duration::from_millis(10)).await;
        }
    });
    
    let task3 = tokio::spawn(async move {
        for _ in 0..10 {
            let _ = player3.pause_playback();
            let _ = player3.resume_playback();
            sleep(Duration::from_millis(10)).await;
        }
    });
    
    // Wait for all tasks to complete
    let (result1, result2, result3) = tokio::join!(task1, task2, task3);
    assert!(result1.is_ok());
    assert!(result2.is_ok());
    assert!(result3.is_ok());
    
    // Verify final state is still valid
    let final_state = player.get_playback_state();
    assert!(final_state.volume >= 0.0 && final_state.volume <= 1.0);
}
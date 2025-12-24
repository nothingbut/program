use local_mp3_player_lib::MetadataParser;
use std::fs::File;
use std::io::Write;
use tempfile::TempDir;

#[tokio::test]
async fn test_complete_directory_scan_workflow() {
    // Create a temporary directory with some fake MP3 files
    let temp_dir = TempDir::new().unwrap();
    
    // Create some fake MP3 files
    let mp3_files = [
        "01 - First Song.mp3",
        "02 - Second Song.mp3", 
        "03 - Third Song.mp3",
        "Album Cover.jpg", // This should be ignored
        "README.txt",      // This should be ignored
    ];
    
    for file in &mp3_files {
        let file_path = temp_dir.path().join(file);
        File::create(&file_path).unwrap();
        
        // Add some fake content to make it look more realistic
        if file.ends_with(".mp3") {
            let mut f = File::create(&file_path).unwrap();
            f.write_all(b"fake mp3 content").unwrap();
        }
    }
    
    // Test the metadata parser directly (since DirectoryManager needs app handle for initialization)
    let parser = MetadataParser::new();
    let tracks = parser.scan_directory(temp_dir.path()).await.unwrap();
    

    
    // Should find exactly 3 MP3 files
    assert_eq!(tracks.len(), 3);
    
    // Check that all tracks have basic information
    for track in &tracks {
        assert!(!track.id.is_empty());
        assert!(!track.title.is_empty());
        assert_eq!(track.artist, "Unknown"); // Since these are fake files
        assert_eq!(track.album, "Unknown");  // Since these are fake files
        assert!(track.file_path.exists());
        assert!(track.file_path.extension().unwrap() == "mp3");
    }
    
    // Check that tracks are sorted properly (by title since no track numbers)
    let titles: Vec<&str> = tracks.iter().map(|t| t.title.as_str()).collect();
    let mut expected_titles = vec!["01 - First Song", "02 - Second Song", "03 - Third Song"];
    expected_titles.sort();
    assert_eq!(titles, expected_titles);
}

#[tokio::test]
async fn test_error_handling_with_invalid_directory() {
    let parser = MetadataParser::new();
    
    // Try to scan a non-existent directory
    let result = parser.scan_directory("/this/path/does/not/exist").await;
    assert!(result.is_err());
}

#[tokio::test]
async fn test_metadata_extraction_robustness() {
    let temp_dir = TempDir::new().unwrap();
    let parser = MetadataParser::new();
    
    // Create files with various naming patterns
    let test_files = [
        "normal_song.mp3",
        "song with spaces.mp3",
        "song-with-dashes.mp3",
        "UPPERCASE.MP3",
        "file.with.dots.mp3",
        "unicode_测试.mp3",
        "empty.mp3", // Empty file
    ];
    
    for file in &test_files {
        let file_path = temp_dir.path().join(file);
        File::create(&file_path).unwrap();
        
        // Add minimal content to some files
        if !file.contains("empty") {
            let mut f = File::create(&file_path).unwrap();
            f.write_all(b"minimal content").unwrap();
        }
    }
    
    let tracks = parser.scan_directory(temp_dir.path()).await.unwrap();
    
    // Should find all MP3 files
    assert_eq!(tracks.len(), test_files.len());
    
    // Each track should have a valid title derived from filename
    for track in &tracks {
        assert!(!track.title.is_empty());
        assert!(!track.id.is_empty());
        assert!(track.file_path.exists());
        
        // Duration might be 0 for fake files, but should be a valid number
        assert!(track.duration >= 0.0);
        
        // Cover art should be None for fake files
        assert!(track.cover_art.is_none());
    }
}
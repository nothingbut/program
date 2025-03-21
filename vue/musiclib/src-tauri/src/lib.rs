
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::State;

// 数据结构定义
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Song {
    pub id: String,
    pub title: String,
    pub artist: String,
    pub album_id: String,
    pub album_title: String,
    pub track_number: i32,
    pub duration: i32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Album {
    pub id: String,
    pub title: String,
    pub artist: String,
    pub cover_url: String,
    pub year: i32,
    pub songs: Vec<Song>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MusicLibrary {
    pub id: String,
    pub name: String,
    pub albums: Vec<Album>,
}

// 应用状态管理
pub struct AppState {
    libraries: Mutex<Vec<MusicLibrary>>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            libraries: Mutex::new(Vec::new()),
        }
    }
}

// API 实现
#[tauri::command]
async fn get_music_libraries(state: State<'_, AppState>) -> Result<Vec<MusicLibrary>, String> {
    let libraries = state.libraries.lock().map_err(|e| e.to_string())?;
    Ok(libraries.clone())
}

#[tauri::command]
async fn get_music_library(
    state: State<'_, AppState>,
    id: String,
) -> Result<Option<MusicLibrary>, String> {
    let libraries = state.libraries.lock().map_err(|e| e.to_string())?;
    Ok(libraries.iter().find(|lib| lib.id == id).cloned())
}

#[tauri::command]
async fn get_albums(
    state: State<'_, AppState>,
    library_id: String,
) -> Result<Vec<Album>, String> {
    let libraries = state.libraries.lock().map_err(|e| e.to_string())?;
    if let Some(library) = libraries.iter().find(|lib| lib.id == library_id) {
        Ok(library.albums.clone())
    } else {
        Ok(Vec::new())
    }
}

#[tauri::command]
async fn get_album(
    state: State<'_, AppState>,
    library_id: String,
    album_id: String,
) -> Result<Option<Album>, String> {
    let libraries = state.libraries.lock().map_err(|e| e.to_string())?;
    if let Some(library) = libraries.iter().find(|lib| lib.id == library_id) {
        Ok(library.albums.iter().find(|album| album.id == album_id).cloned())
    } else {
        Ok(None)
    }
}

#[tauri::command]
async fn add_music_library(
    state: State<'_, AppState>,
    name: String,
) -> Result<MusicLibrary, String> {
    let mut libraries = state.libraries.lock().map_err(|e| e.to_string())?;
    let new_library = MusicLibrary {
        id: uuid::Uuid::new_v4().to_string(),
        name,
        albums: Vec::new(),
    };
    libraries.push(new_library.clone());
    Ok(new_library)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(AppState::new())
        .invoke_handler(tauri::generate_handler![
            get_music_libraries,
            get_music_library,
            get_albums,
            get_album,
            add_music_library
        ])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

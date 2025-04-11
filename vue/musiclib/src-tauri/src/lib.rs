use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::State;
mod database;
use database::Database;
use id3::{Tag, TagLike};
use log::{error, info};
use std::collections::HashMap;
use std::path::PathBuf;
use tauri::Manager;
use walkdir::WalkDir;

// 为音频文件创建URL的命令
#[tauri::command]
async fn get_audio_file_url(
    app_handle: tauri::AppHandle,
    file_path: String,
) -> Result<String, String> {
    info!("【API】获取音频文件URL，文件路径：{}", file_path);
    
    // 验证文件是否存在
    let path = std::path::Path::new(&file_path);
    if !path.exists() {
        error!("【错误】文件不存在：{}", file_path);
        return Err("文件不存在".to_string());
    }

    // 使用 Tauri 的 asset 协议
    let file_path = std::path::PathBuf::from(&file_path);
    
    // 验证文件是否存在
    if !file_path.exists() {
        error!("【错误】文件不存在：{}", file_path.display());
        return Err("文件不存在".to_string());
    }

    // 使用 asset:// 协议构建 URL
    let file_url = format!("assets://{}", file_path.to_string_lossy());
    info!("【API】生成音频文件URL：{}", file_url);
    Ok(file_url)
}

// 数据结构定义
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Song {
    pub id: String,
    pub title: String,
    pub artist: String,
    pub album_id: String,
    pub track_number: Option<i32>,
    pub duration: Option<i32>,
    pub file_path: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Album {
    pub id: String,
    pub title: String,
    pub artist: String,
    pub cover_data: Option<String>,
    pub year: Option<i32>,
    pub songs: Vec<Song>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CreateLibraryParams {
    pub name: String,
    pub directories: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LibraryDirectory {
    pub id: String,
    pub directory_path: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MusicLibrary {
    pub id: String,
    pub name: String,
    pub albums: Vec<Album>,
    pub directories: Vec<LibraryDirectory>,
}

// 用于存储MP3元数据的临时结构
#[derive(Debug)]
struct Mp3Metadata {
    title: String,
    artist: String,
    album: String,
    album_artist: String,
    track_number: Option<i32>,
    year: Option<i32>,
    duration: i32,
    file_path: String,
    cover_data: Option<String>,  // base64 编码的封面图片数据
}

// 应用状态管理
pub struct AppState {
    db: Mutex<Database>,
}

impl AppState {
    pub fn new(app_dir: PathBuf) -> anyhow::Result<Self> {
        let db_path = app_dir.join("musiclib.db");
        info!("【初始化】数据库路径：{:?}", db_path);
        let db = Database::new(db_path)?;
        Ok(Self { db: Mutex::new(db) })
    }

    // 扫描目录中的MP3文件
    fn scan_directories(&self, directories: &[String]) -> Vec<Mp3Metadata> {
        let mut metadata_list = Vec::new();

        for dir in directories {
            info!("【扫描】开始扫描目录：{}", dir);
            for entry in WalkDir::new(dir)
                .follow_links(true)
                .into_iter()
                .filter_map(|e| e.ok())
            {
                let path = entry.path();
                if path
                    .extension()
                    .map_or(false, |ext| ext.eq_ignore_ascii_case("mp3"))
                {
                    if let Some(metadata) = self.read_mp3_metadata(path) {
                        metadata_list.push(metadata);
                    }
                }
            }
        }

        info!("【扫描】共找到 {} 个MP3文件", metadata_list.len());
        metadata_list
    }

    // 读取MP3文件的元数据
    fn read_mp3_metadata(&self, path: &std::path::Path) -> Option<Mp3Metadata> {
        info!("【解析】开始解析MP3文件：{:?}", path);
        
        // 读取ID3标签
        let tag = match Tag::read_from_path(path) {
            Ok(tag) => {
                info!("【解析】成功读取ID3标签");
                tag
            },
            Err(e) => {
                error!("【错误】读取ID3标签失败 {:?}: {}", path, e);
                return None;
            }
        };

        // 安全地提取文本字段
        let safe_extract_text = |key: &str, value: Option<&str>, fallback: &str| -> String {
            match value {
                Some(text) => {
                    info!("【解析】成功读取{}: {}", key, text);
                    if text.chars().all(|c| !c.is_control() || c.is_whitespace()) {
                        text.to_string()
                    } else {
                        let cleaned = text.chars()
                            .filter(|c| !c.is_control() || c.is_whitespace())
                            .collect::<String>();
                        info!("【解析】{}包含控制字符，已清理: {}", key, cleaned);
                        if cleaned.is_empty() {
                            fallback.to_string()
                        } else {
                            cleaned
                        }
                    }
                },
                None => {
                    info!("【解析】未找到{}，使用默认值: {}", key, fallback);
                    fallback.to_string()
                }
            }
        };

        // 提取标签信息
        let title = safe_extract_text("标题", tag.title(), "Unknown Title");
        let artist = safe_extract_text("艺术家", tag.artist(), "Unknown Artist");
        let album = safe_extract_text("专辑", tag.album(), "Unknown Album");
        let album_artist = safe_extract_text("专辑艺术家", tag.album_artist(), &artist);

        // 提取封面图片
        let cover_data = if let Some(picture) = tag.pictures().next() {
            info!("【解析】成功读取封面图片，格式：{}", picture.mime_type);
            Some(base64::encode(&picture.data))
        } else {
            info!("【解析】未找到封面图片");
            None
        };

        // 记录字段的详细诊断信息
        for (field, value) in [
            ("标题", &title),
            ("艺术家", &artist),
            ("专辑", &album),
            ("专辑艺术家", &album_artist)
        ] {
            info!("【诊断】{}", field);
            info!("  - 值: {}", value);
            info!("  - 长度: {} 字符", value.chars().count());
            info!("  - 字节: {:?}", value.as_bytes());
            if let Some(first_invalid) = value.chars().find(|c| c.is_control() && !c.is_whitespace()) {
                info!("  - 警告: 包含控制字符 U+{:04X}", first_invalid as u32);
            }
        }

        // 提取音轨号
        let track_number = tag.track().map(|t| {
            info!("【解析】成功读取音轨号: {}", t);
            t as i32
        });

        // 提取年份
        let year = tag.year().map(|y| {
            info!("【解析】成功读取年份: {}", y);
            y as i32
        });

        // 提取时长（id3库不直接提供时长信息，需要其他方式获取）
        let duration = 0; // TODO: 使用其他库获取时长
        info!("【解析】时长信息暂不可用");

        let file_path = path.to_string_lossy().into_owned();
        
        // 执行健全性检查
        let is_valid = {
            let has_valid_title = !title.trim().is_empty() && title != "Unknown Title";
            let has_valid_artist = !artist.trim().is_empty() && artist != "Unknown Artist";
            let has_valid_album = !album.trim().is_empty() && album != "Unknown Album";
            
            if !has_valid_title {
                error!("【验证】标题无效或为默认值");
            }
            if !has_valid_artist {
                error!("【验证】艺术家无效或为默认值");
            }
            if !has_valid_album {
                error!("【验证】专辑名无效或为默认值");
            }
            
            has_valid_title || has_valid_artist || has_valid_album
        };

        if !is_valid {
            error!("【错误】元数据验证失败，所有主要字段都是默认值或无效");
            error!("【错误】文件路径：{}", path.display());
            return None;
        }

        // 构造元数据对象
        let metadata = Mp3Metadata {
            title,
            artist,
            album,
            album_artist,
            track_number,
            year,
            duration,
            file_path,
            cover_data,
        };

        info!("【完成】成功创建元数据对象");
        info!("【完成】摘要：");
        info!("  - 标题: {}", metadata.title);
        info!("  - 艺术家: {}", metadata.artist);
        info!("  - 专辑: {}", metadata.album);
        info!("  - 专辑艺术家: {}", metadata.album_artist);
        info!("  - 音轨号: {:?}", metadata.track_number);
        info!("  - 年份: {:?}", metadata.year);
        info!("  - 时长: {}秒", metadata.duration);
        
        Some(metadata)
    }

    // 将歌曲按专辑分组并保存到数据库
    fn process_music_files_with_db(
        db: &Database,
        library_id: &str,
        metadata_list: Vec<Mp3Metadata>,
    ) -> Result<(), String> {
        info!("【处理】开始处理音乐文件");
        info!("step 1");
        // 按专辑分组
        let mut albums: HashMap<String, Vec<Mp3Metadata>> = HashMap::new();
        for metadata in metadata_list {
            albums
                .entry(format!("{} - {}", metadata.album_artist, metadata.album))
                .or_insert_with(Vec::new)
                .push(metadata);
        }
        info!("step 2");

        // 保存到数据库
        for (album_key, songs) in albums {
            if songs.is_empty() {
                info!("【警告】专辑 {} 为空，跳过", album_key);
                continue;
            }

            let first_song = &songs[0];
            let album_id = uuid::Uuid::new_v4().to_string();

            // 添加专辑
            db.add_album(
                &album_id,
                library_id,
                &first_song.album,
                &first_song.album_artist,
                first_song.cover_data.as_deref(),
                first_song.year,
            )
            .map_err(|e| e.to_string())?;

            // 添加歌曲
            for song in songs {
                let song_id = uuid::Uuid::new_v4().to_string();
                db.add_song(
                    &song_id,
                    &album_id,
                    &song.title,
                    &song.artist,
                    song.track_number,
                    Some(song.duration),
                    Some(&song.file_path),
                )
                .map_err(|e| e.to_string())?;
            }
        }

        info!("【处理】音乐文件处理完成");
        Ok(())
    }
}

// API 实现
#[tauri::command]
async fn get_music_libraries(state: State<'_, AppState>) -> Result<Vec<MusicLibrary>, String> {
    info!("【API】开始获取所有音乐库");
    let db = state.db.lock().map_err(|e| {
        let err = e.to_string();
        error!("【错误】获取数据库锁失败：{}", err);
        err
    })?;

    match db.get_music_libraries() {
        Ok(libraries) => {
            let mut result = Vec::new();
            
            for (library_id, name) in libraries {
                // 获取目录信息
                let directories = db.get_library_directories(&library_id)
                    .map_err(|e| e.to_string())?
                    .into_iter()
                    .map(|(id, directory_path)| LibraryDirectory { id, directory_path })
                    .collect();

                // 获取专辑信息
                let albums = db.get_albums(&library_id).map_err(|e| e.to_string())?;
                let mut library_albums = Vec::new();

                for (album_id, title, artist, cover_data, year) in albums {
                    let songs = db.get_songs(&album_id).map_err(|e| e.to_string())?;
                    let album_songs = songs
                        .into_iter()
                        .map(
                            |(id, title, artist, track_number, duration, file_path)| Song {
                                id,
                                title,
                                artist,
                                album_id: album_id.clone(),
                                track_number,
                                duration,
                                file_path,
                            },
                        )
                        .collect();

                    library_albums.push(Album {
                        id: album_id,
                        title,
                        artist,
                        cover_data,
                        year,
                        songs: album_songs,
                    });
                }

                result.push(MusicLibrary {
                    id: library_id,
                    name,
                    albums: library_albums,
                    directories,
                });
            }
            
            info!("【API】成功获取音乐库列表，共 {} 个", result.len());
            Ok(result)
        }
        Err(e) => {
            let err = e.to_string();
            error!("【错误】获取音乐库列表失败：{}", err);
            Err(err)
        }
    }
}

#[tauri::command]
async fn get_music_library(
    state: State<'_, AppState>,
    id: String,
) -> Result<Option<MusicLibrary>, String> {
    info!("【API】开始获取音乐库详情，ID：{}", id);
    let db = state.db.lock().map_err(|e| {
        let err = e.to_string();
        error!("【错误】获取数据库锁失败：{}", err);
        err
    })?;

    match db.get_music_library(&id) {
        Ok(library) => {
            match &library {
                Some((library_id, name)) => {
                    info!("【API】找到音乐库：{} ({})", name, library_id);
                    
                    // 获取目录信息
                    let directories = db.get_library_directories(library_id)
                        .map_err(|e| e.to_string())?
                        .into_iter()
                        .map(|(id, directory_path)| LibraryDirectory { id, directory_path })
                        .collect();

                    // 获取专辑信息
                    let albums = db.get_albums(library_id).map_err(|e| e.to_string())?;
                    let mut library_albums = Vec::new();

                    for (album_id, title, artist, cover_data, year) in albums {
                        let songs = db.get_songs(&album_id).map_err(|e| e.to_string())?;
                        let album_songs = songs
                            .into_iter()
                            .map(
                                |(id, title, artist, track_number, duration, file_path)| Song {
                                    id,
                                    title,
                                    artist,
                                    album_id: album_id.clone(),
                                    track_number,
                                    duration,
                                    file_path,
                                },
                            )
                            .collect();

                        library_albums.push(Album {
                            id: album_id,
                            title,
                            artist,
                            cover_data,
                            year,
                            songs: album_songs,
                        });
                    }

                    Ok(Some(MusicLibrary {
                        id: library_id.clone(),
                        name: name.clone(),
                        albums: library_albums,
                        directories,
                    }))
                }
                None => {
                    info!("【API】未找到指定音乐库：{}", id);
                    Ok(None)
                }
            }
        }
        Err(e) => {
            let err = e.to_string();
            error!("【错误】获取音乐库详情失败：{}", err);
            Err(err)
        }
    }
}

#[tauri::command]
async fn add_library_directory(
    state: State<'_, AppState>,
    library_id: String,
    directory_path: String,
) -> Result<(), String> {
    info!("【API】添加音乐库目录，库ID：{}，目录：{}", library_id, directory_path);
    
    let db = state.db.lock().map_err(|e| {
        let err = e.to_string();
        error!("【错误】获取数据库锁失败：{}", err);
        err
    })?;

    let id = uuid::Uuid::new_v4().to_string();
    db.add_library_directory(&id, &library_id, &directory_path).map_err(|e| {
        let err = e.to_string();
        error!("【错误】添加目录失败：{}", err);
        err
    })?;

    // 扫描新添加的目录
    let metadata_list = state.scan_directories(&[directory_path]);
    AppState::process_music_files_with_db(&db, &library_id, metadata_list)?;

    info!("【API】目录添加成功");
    Ok(())
}

#[tauri::command]
async fn get_library_directories(
    state: State<'_, AppState>,
    library_id: String,
) -> Result<Vec<LibraryDirectory>, String> {
    info!("【API】获取音乐库目录列表，库ID：{}", library_id);
    
    let db = state.db.lock().map_err(|e| {
        let err = e.to_string();
        error!("【错误】获取数据库锁失败：{}", err);
        err
    })?;

    match db.get_library_directories(&library_id) {
        Ok(directories) => {
            let result = directories
                .into_iter()
                .map(|(id, directory_path)| LibraryDirectory { id, directory_path })
                .collect();
            info!("【API】成功获取目录列表");
            Ok(result)
        }
        Err(e) => {
            let err = e.to_string();
            error!("【错误】获取目录列表失败：{}", err);
            Err(err)
        }
    }
}

#[tauri::command]
async fn remove_library_directory(
    state: State<'_, AppState>,
    directory_id: String,
) -> Result<(), String> {
    info!("【API】移除音乐库目录，目录ID：{}", directory_id);
    
    let db = state.db.lock().map_err(|e| {
        let err = e.to_string();
        error!("【错误】获取数据库锁失败：{}", err);
        err
    })?;

    db.remove_library_directory(&directory_id).map_err(|e| {
        let err = e.to_string();
        error!("【错误】移除目录失败：{}", err);
        err
    })?;

    info!("【API】目录移除成功");
    Ok(())
}

#[tauri::command]
async fn create_music_library(
    state: State<'_, AppState>,
    params: CreateLibraryParams,
) -> Result<MusicLibrary, String> {
    info!("【API】开始创建新音乐库：{}", params.name);

    // 创建音乐库
    let id = uuid::Uuid::new_v4().to_string();
    let db = state.db.lock().map_err(|e| {
        let err = e.to_string();
        error!("【错误】获取数据库锁失败：{}", err);
        err
    })?;

    db.add_music_library(&id, &params.name).map_err(|e| {
        let err = e.to_string();
        error!("【错误】添加音乐库失败：{}", err);
        err
    })?;

    // 扫描目录
    info!("【API】开始扫描目录");
    let metadata_list = state.scan_directories(&params.directories);

    // 处理音乐文件
    AppState::process_music_files_with_db(&db, &id, metadata_list)?;

    // 添加目录到数据库
    let mut library_directories = Vec::new();
    for directory_path in params.directories {
        let directory_id = uuid::Uuid::new_v4().to_string();
        db.add_library_directory(&directory_id, &id, &directory_path).map_err(|e| {
            let err = e.to_string();
            error!("【错误】添加目录失败：{}", err);
            err
        })?;
        library_directories.push(LibraryDirectory {
            id: directory_id,
            directory_path,
        });
    }

    // 获取创建的音乐库信息
    let albums = db.get_albums(&id).map_err(|e| e.to_string())?;
    let mut library_albums = Vec::new();

    for (album_id, title, artist, cover_data, year) in albums {
        let songs = db.get_songs(&album_id).map_err(|e| e.to_string())?;
        let album_songs = songs
            .into_iter()
            .map(
                |(id, title, artist, track_number, duration, file_path)| Song {
                    id,
                    title,
                    artist,
                    album_id: album_id.clone(),
                    track_number,
                    duration,
                    file_path,
                },
            )
            .collect();

        library_albums.push(Album {
            id: album_id,
            title,
            artist,
            cover_data,
            year,
            songs: album_songs,
        });
    }

    info!("【API】音乐库创建成功：{} ({})", params.name, id);
    Ok(MusicLibrary {
        id,
        name: params.name,
        albums: library_albums,
        directories: library_directories
    })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let app_dir = app.path().app_data_dir().expect("获取应用数据目录失败");

            info!("【初始化】应用数据目录：{:?}", app_dir);
            // 确保目录存在
            std::fs::create_dir_all(&app_dir)?;

            let state = AppState::new(app_dir)?;
            app.manage(state);

            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            info!("【初始化】应用启动完成");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_music_libraries,
            get_music_library,
            create_music_library,
            add_library_directory,
            get_library_directories,
            remove_library_directory,
            get_audio_file_url
        ])
        .run(tauri::generate_context!())
        .expect("运行应用程序时出错");
}
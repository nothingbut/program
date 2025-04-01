use log::info;
use rusqlite::{params, Connection, Result};
use std::path::Path;

pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn new<P: AsRef<Path>>(path: P) -> Result<Self> {
        info!("【数据库】开始创建/连接数据库：{:?}", path.as_ref());
        let conn = Connection::open(path)?;

        // 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON", [])?;
        info!("【数据库】已启用外键约束");

        // 创建音乐库表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS music_libraries (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;
        info!("【数据库】已创建音乐库表");

        // 创建专辑表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS albums (
                id TEXT PRIMARY KEY,
                library_id TEXT NOT NULL,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                cover_url TEXT,
                year INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(library_id) REFERENCES music_libraries(id) ON DELETE CASCADE
            )",
            [],
        )?;
        info!("【数据库】已创建专辑表");

        // 创建歌曲表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS songs (
                id TEXT PRIMARY KEY,
                album_id TEXT NOT NULL,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                track_number INTEGER,
                duration INTEGER,
                file_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(album_id) REFERENCES albums(id) ON DELETE CASCADE
            )",
            [],
        )?;
        info!("【数据库】已创建歌曲表");

        // 创建音乐库目录表
        conn.execute(
            "CREATE TABLE IF NOT EXISTS library_directories (
                id TEXT PRIMARY KEY,
                library_id TEXT NOT NULL,
                directory_path TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(library_id) REFERENCES music_libraries(id) ON DELETE CASCADE
            )",
            [],
        )?;
        info!("【数据库】已创建音乐库目录表");

        info!("【数据库】数据库初始化完成");
        Ok(Self { conn })
    }

    // 音乐库操作
    pub fn add_music_library(&self, id: &str, name: &str) -> Result<()> {
        info!("【数据库】添加音乐库：{} ({})", name, id);
        self.conn.execute(
            "INSERT INTO music_libraries (id, name) VALUES (?1, ?2)",
            params![id, name],
        )?;
        info!("【数据库】音乐库添加成功");
        Ok(())
    }

    pub fn get_music_libraries(&self) -> Result<Vec<(String, String)>> {
        info!("【数据库】获取所有音乐库");
        let mut stmt = self.conn.prepare("SELECT id, name FROM music_libraries")?;
        let rows = stmt.query_map([], |row| Ok((row.get(0)?, row.get(1)?)))?;

        let mut libraries = Vec::new();
        for row in rows {
            libraries.push(row?);
        }
        info!("【数据库】成功获取 {} 个音乐库", libraries.len());
        Ok(libraries)
    }

    pub fn get_music_library(&self, id: &str) -> Result<Option<(String, String)>> {
        info!("【数据库】查询音乐库：{}", id);
        let mut stmt = self
            .conn
            .prepare("SELECT id, name FROM music_libraries WHERE id = ?1")?;
        let mut rows = stmt.query_map(params![id], |row| Ok((row.get(0)?, row.get(1)?)))?;

        if let Some(row) = rows.next() {
            let result = row?;
            info!("【数据库】找到音乐库：{}", result.1);
            Ok(Some(result))
        } else {
            info!("【数据库】未找到音乐库：{}", id);
            Ok(None)
        }
    }

    // 专辑操作
    pub fn add_album(
        &self,
        id: &str,
        library_id: &str,
        title: &str,
        artist: &str,
        cover_url: Option<&str>,
        year: Option<i32>,
    ) -> Result<()> {
        info!("【数据库】添加专辑：{} - {}", artist, title);
        self.conn.execute(
            "INSERT INTO albums (id, library_id, title, artist, cover_url, year)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params![id, library_id, title, artist, cover_url, year],
        )?;
        info!("【数据库】专辑添加成功");
        Ok(())
    }

    pub fn get_albums(
        &self,
        library_id: &str,
    ) -> Result<Vec<(String, String, String, Option<String>, Option<i32>)>> {
        info!("【数据库】获取音乐库的专辑列表：{}", library_id);
        let mut stmt = self.conn.prepare(
            "SELECT id, title, artist, cover_url, year 
             FROM albums 
             WHERE library_id = ?1",
        )?;

        let rows = stmt.query_map(params![library_id], |row| {
            Ok((
                row.get(0)?,
                row.get(1)?,
                row.get(2)?,
                row.get(3)?,
                row.get(4)?,
            ))
        })?;

        let mut albums = Vec::new();
        for row in rows {
            albums.push(row?);
        }
        info!("【数据库】成功获取 {} 张专辑", albums.len());
        Ok(albums)
    }

    // 歌曲操作
    pub fn add_song(
        &self,
        id: &str,
        album_id: &str,
        title: &str,
        artist: &str,
        track_number: Option<i32>,
        duration: Option<i32>,
        file_path: Option<&str>,
    ) -> Result<()> {
        info!("【数据库】添加歌曲：{} - {}", artist, title);
        self.conn.execute(
            "INSERT INTO songs (id, album_id, title, artist, track_number, duration, file_path)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![
                id,
                album_id,
                title,
                artist,
                track_number,
                duration,
                file_path
            ],
        )?;
        info!("【数据库】歌曲添加成功");
        Ok(())
    }

    pub fn get_songs(
        &self,
        album_id: &str,
    ) -> Result<
        Vec<(
            String,
            String,
            String,
            Option<i32>,
            Option<i32>,
            Option<String>,
        )>,
    > {
        info!("【数据库】获取专辑的歌曲列表：{}", album_id);
        let mut stmt = self.conn.prepare(
            "SELECT id, title, artist, track_number, duration, file_path 
             FROM songs 
             WHERE album_id = ?1
             ORDER BY track_number",
        )?;

        let rows = stmt.query_map(params![album_id], |row| {
            Ok((
                row.get(0)?,
                row.get(1)?,
                row.get(2)?,
                row.get(3)?,
                row.get(4)?,
                row.get(5)?,
            ))
        })?;

        let mut songs = Vec::new();
        for row in rows {
            songs.push(row?);
        }
        info!("【数据库】成功获取 {} 首歌曲", songs.len());
        Ok(songs)
    }

    // 音乐库目录操作
    pub fn add_library_directory(&self, id: &str, library_id: &str, directory_path: &str) -> Result<()> {
        info!("【数据库】添加音乐库目录：{} -> {}", library_id, directory_path);
        self.conn.execute(
            "INSERT INTO library_directories (id, library_id, directory_path) 
             VALUES (?1, ?2, ?3)",
            params![id, library_id, directory_path],
        )?;
        info!("【数据库】音乐库目录添加成功");
        Ok(())
    }

    pub fn get_library_directories(&self, library_id: &str) -> Result<Vec<(String, String)>> {
        info!("【数据库】获取音乐库的目录列表：{}", library_id);
        let mut stmt = self.conn.prepare(
            "SELECT id, directory_path 
             FROM library_directories 
             WHERE library_id = ?1"
        )?;

        let rows = stmt.query_map(params![library_id], |row| {
            Ok((row.get(0)?, row.get(1)?))
        })?;

        let mut directories = Vec::new();
        for row in rows {
            directories.push(row?);
        }
        info!("【数据库】成功获取 {} 个目录", directories.len());
        Ok(directories)
    }

    pub fn remove_library_directory(&self, id: &str) -> Result<()> {
        info!("【数据库】移除音乐库目录：{}", id);
        self.conn.execute(
            "DELETE FROM library_directories WHERE id = ?1",
            params![id],
        )?;
        info!("【数据库】音乐库目录移除成功");
        Ok(())
    }
}
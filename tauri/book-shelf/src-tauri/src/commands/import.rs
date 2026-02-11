use crate::models::Chapter;
use regex::Regex;
use sqlx::Row;
use tauri::{command, State};

// Result type for atomic import operation
#[derive(serde::Serialize)]
pub struct ImportResult {
    pub book_id: i64,
    pub chapter_count: i64,
    pub word_count: i64,
}

// Validates TXT file before import
fn validate_txt_file(path: &str) -> Result<(), String> {
    let file_path = std::path::Path::new(path);

    // Check if file exists
    if !file_path.exists() {
        return Err("文件不存在".to_string());
    }

    // Check file extension
    if !path.to_lowercase().ends_with(".txt") {
        return Err("仅支持 TXT 文件格式".to_string());
    }

    // Check file size (limit to 50MB)
    match std::fs::metadata(path) {
        Ok(metadata) => {
            let size_mb = metadata.len() / (1024 * 1024);
            if metadata.len() > 50 * 1024 * 1024 {
                return Err(format!("文件过大（{}MB），最大支持 50MB", size_mb));
            }
        }
        Err(e) => {
            return Err(format!("无法读取文件信息: {}", e));
        }
    }

    Ok(())
}

// Reads file with encoding detection (UTF-8 or GBK)
fn read_with_encoding(path: &str) -> Result<String, String> {
    let bytes = std::fs::read(path)
        .map_err(|e| format!("读取文件失败: {}", e))?;

    // Try UTF-8 first
    if let Ok(text) = std::str::from_utf8(&bytes) {
        return Ok(text.to_string());
    }

    // Try GBK (common for Chinese text files)
    let (decoded, _, had_errors) = encoding_rs::GBK.decode(&bytes);
    if had_errors {
        return Err("文件编码无法识别，请确保是 UTF-8 或 GBK 格式".to_string());
    }

    Ok(decoded.to_string())
}

fn parse_chapters(content: &str) -> Vec<Chapter> {
    let mut chapters = Vec::new();

    // 常见的章节标题正则表达式
    let patterns = vec![
        Regex::new(r"(?m)^\s*第[一二三四五六七八九十百千万0-9]+[章节回集部卷之]\s*(.+?)\s*$").unwrap(),
        Regex::new(r"(?m)^\s*Chapter\s*[0-9]+\s*(.+?)\s*$").unwrap(),
        Regex::new(r"(?m)^\s*[0-9]+\.\s*(.+?)\s*$").unwrap(),
        Regex::new(r"(?m)^\s*【(.+?)】\s*$").unwrap(),
        Regex::new(r"(?m)^\s*（(.+?)）\s*$").unwrap(),
    ];

    // 尝试不同的匹配模式
    let mut chapter_matches = Vec::new();

    for pattern in &patterns {
        let captures: Vec<_> = pattern.find_iter(content).collect();
        if captures.len() > 3 { // 至少找到3个章节才认为是有效模式
            chapter_matches = captures;
            break;
        }
    }

    if chapter_matches.is_empty() {
        // 如果没有找到章节标题，将整个文件作为一章
        chapters.push(Chapter {
            id: None,
            book_id: 0,
            title: "全文".to_string(),
            content: Some(content.trim().to_string()),
            sort_order: 1,
            word_count: content.chars().count() as i64,
            created_at: chrono::Utc::now().to_rfc3339(),
        });
    } else {
        // 根据章节标题分割内容
        let mut last_pos = 0;

        for (index, mat) in chapter_matches.iter().enumerate() {
            let start_pos = mat.start();

            if index > 0 {
                // 提取上一章节的内容
                let chapter_content = &content[last_pos..start_pos].trim();
                let chapter_title = chapter_matches[index - 1].as_str().trim();

                if !chapter_content.is_empty() {
                    chapters.push(Chapter {
                        id: None,
                        book_id: 0,
                        title: clean_chapter_title(chapter_title),
                        content: Some(chapter_content.to_string()),
                        sort_order: index as i64,
                        word_count: chapter_content.chars().count() as i64,
                        created_at: chrono::Utc::now().to_rfc3339(),
                    });
                }
            }

            last_pos = start_pos;
        }

        // 处理最后一章
        if last_pos < content.len() {
            let chapter_content = &content[last_pos..].trim();
            let chapter_title = chapter_matches.last().unwrap().as_str().trim();

            if !chapter_content.is_empty() {
                chapters.push(Chapter {
                    id: None,
                    book_id: 0,
                    title: clean_chapter_title(chapter_title),
                    content: Some(chapter_content.to_string()),
                    sort_order: chapters.len() as i64 + 1,
                    word_count: chapter_content.chars().count() as i64,
                    created_at: chrono::Utc::now().to_rfc3339(),
                });
            }
        }
    }

    chapters
}

fn clean_chapter_title(title: &str) -> String {
    title
        .trim()
        .replace("第", "")
        .replace("章", "")
        .replace("节", "")
        .replace("回", "")
        .replace("集", "")
        .replace("部", "")
        .replace("卷", "")
        .replace("之", "")
        .trim()
        .to_string()
}

// Atomic import operation: creates book and imports chapters in a single transaction
#[command]
pub async fn import_book_atomic(
    db_instances: State<'_, tauri_plugin_sql::DbInstances>,
    file_path: String,
    title: String,
    author: Option<String>,
    description: Option<String>,
    category_id: Option<i64>,
) -> Result<ImportResult, String> {
    // Step 1: Validate file
    validate_txt_file(&file_path)?;

    // Step 2: Read file with encoding detection
    let content = read_with_encoding(&file_path)?;

    // Step 3: Parse chapters
    let chapters = parse_chapters(&content);

    if chapters.is_empty() {
        return Err("未能解析出任何章节，请检查文件格式".to_string());
    }

    if chapters.len() > 10000 {
        return Err(format!("章节数量过多（{}），最大支持 10000 章", chapters.len()));
    }

    // Step 4: Get database connection
    let instances = db_instances.0.read().await;
    let db_pool = instances
        .get("sqlite:bookshelf.db")
        .ok_or("Database not loaded")?;

    // Extract the internal SQLite pool
    let pool = match db_pool {
        tauri_plugin_sql::DbPool::Sqlite(pool) => pool,
        #[allow(unreachable_patterns)]
        _ => return Err("Wrong database type".to_string()),
    };

    let now = chrono::Utc::now().to_rfc3339();

    // Step 5: Begin transaction
    let mut tx = pool
        .begin()
        .await
        .map_err(|e| format!("无法开始事务: {}", e))?;

    // Execute all database operations, rolling back on any error
    let result: Result<ImportResult, String> = async {
        // Step 6: Create book record
        sqlx::query(
            "INSERT INTO books (title, author, description, category_id, word_count, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, 0, ?5, ?6)",
        )
        .bind(&title)
        .bind(&author)
        .bind(&description)
        .bind(category_id)
        .bind(&now)
        .bind(&now)
        .execute(&mut *tx)
        .await
        .map_err(|e| format!("创建书籍失败: {}", e))?;

        // Get the newly created book ID
        let book_id: i64 = sqlx::query("SELECT last_insert_rowid() as id")
            .fetch_one(&mut *tx)
            .await
            .map_err(|e| format!("获取书籍ID失败: {}", e))?
            .try_get("id")
            .map_err(|e| format!("解析书籍ID失败: {}", e))?;

        // Step 7: Insert all chapters
        let mut total_word_count = 0i64;
        for (index, chapter) in chapters.iter().enumerate() {
            let sort_order = (index + 1) as i64;
            let word_count = chapter
                .content
                .as_ref()
                .map(|c| c.chars().count() as i64)
                .unwrap_or(0);
            total_word_count += word_count;

            sqlx::query(
                "INSERT INTO chapters (book_id, title, content, sort_order, word_count, created_at)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            )
            .bind(book_id)
            .bind(&chapter.title)
            .bind(&chapter.content)
            .bind(sort_order)
            .bind(word_count)
            .bind(&now)
            .execute(&mut *tx)
            .await
            .map_err(|e| format!("保存章节失败: {}", e))?;
        }

        // Step 8: Update book with final word count and file path
        sqlx::query("UPDATE books SET word_count = ?1, file_path = ?2 WHERE id = ?3")
            .bind(total_word_count)
            .bind(&file_path)
            .bind(book_id)
            .execute(&mut *tx)
            .await
            .map_err(|e| format!("更新书籍信息失败: {}", e))?;

        Ok(ImportResult {
            book_id,
            chapter_count: chapters.len() as i64,
            word_count: total_word_count,
        })
    }
    .await;

    // Step 9: Commit or rollback based on result
    match result {
        Ok(import_result) => {
            tx.commit()
                .await
                .map_err(|e| format!("提交事务失败: {}", e))?;
            Ok(import_result)
        }
        Err(e) => {
            // Rollback happens automatically when tx is dropped
            Err(e)
        }
    }
}

use crate::models::Chapter;
use tauri::{command, AppHandle, Manager};

#[command]
pub async fn get_chapters_by_book(
    app: AppHandle,
    book_id: i64,
) -> Result<Vec<Chapter>, String> {
    let db = app.state::<tauri_plugin_sql::DbInstances>();
    let instances = db.0.read().await;
    let db_pool = instances
        .get("sqlite:bookshelf.db")
        .ok_or("Database not loaded")?;

    let pool = match db_pool {
        tauri_plugin_sql::DbPool::Sqlite(pool) => pool,
        #[allow(unreachable_patterns)]
        _ => return Err("Wrong database type".to_string()),
    };

    let rows = sqlx::query_as::<_, (i64, i64, String, Option<String>, i64, i64, String)>(
        "SELECT id, book_id, title, content, sort_order, word_count, created_at
         FROM chapters WHERE book_id = ?1 ORDER BY sort_order"
    )
    .bind(book_id)
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Failed to fetch chapters: {}", e))?;

    let chapters = rows
        .into_iter()
        .map(|(id, book_id, title, content, sort_order, word_count, created_at)| Chapter {
            id: Some(id),
            book_id,
            title,
            content,
            sort_order,
            word_count,
            created_at,
        })
        .collect();

    Ok(chapters)
}

#[command]
pub async fn get_chapter_by_id(
    app: AppHandle,
    id: i64,
) -> Result<Option<Chapter>, String> {
    let db = app.state::<tauri_plugin_sql::DbInstances>();
    let instances = db.0.read().await;
    let db_pool = instances
        .get("sqlite:bookshelf.db")
        .ok_or("Database not loaded")?;

    let pool = match db_pool {
        tauri_plugin_sql::DbPool::Sqlite(pool) => pool,
        #[allow(unreachable_patterns)]
        _ => return Err("Wrong database type".to_string()),
    };

    let row = sqlx::query_as::<_, (i64, i64, String, Option<String>, i64, i64, String)>(
        "SELECT id, book_id, title, content, sort_order, word_count, created_at
         FROM chapters WHERE id = ?1"
    )
    .bind(id)
    .fetch_optional(pool)
    .await
    .map_err(|e| format!("Failed to fetch chapter: {}", e))?;

    Ok(row.map(|(id, book_id, title, content, sort_order, word_count, created_at)| {
        Chapter {
            id: Some(id),
            book_id,
            title,
            content,
            sort_order,
            word_count,
            created_at,
        }
    }))
}

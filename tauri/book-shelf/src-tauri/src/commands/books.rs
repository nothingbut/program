use crate::models::Book;
use tauri::{command, AppHandle, Manager};

#[command]
pub async fn get_all_books(app: AppHandle) -> Result<Vec<Book>, String> {
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

    let rows = sqlx::query_as::<_, (
        i64,
        String,
        Option<String>,
        Option<String>,
        Option<String>,
        Option<i64>,
        Option<String>,
        Option<i64>,
        i64,
        String,
        String,
    )>(
        "SELECT id, title, author, description, cover_image, category_id, file_path, file_size, word_count, created_at, updated_at
         FROM books ORDER BY created_at DESC"
    )
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Failed to fetch books: {}", e))?;

    let books = rows
        .into_iter()
        .map(
            |(
                id,
                title,
                author,
                description,
                cover_image,
                category_id,
                file_path,
                file_size,
                word_count,
                created_at,
                updated_at,
            )| Book {
                id: Some(id),
                title,
                author,
                description,
                cover_image,
                category_id,
                file_path,
                file_size,
                word_count,
                created_at,
                updated_at,
                category_name: None,
            },
        )
        .collect();

    Ok(books)
}

#[command]
pub async fn get_book_by_id(app: AppHandle, id: i64) -> Result<Option<Book>, String> {
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

    let row = sqlx::query_as::<_, (
        i64,
        String,
        Option<String>,
        Option<String>,
        Option<String>,
        Option<i64>,
        Option<String>,
        Option<i64>,
        i64,
        String,
        String,
    )>(
        "SELECT id, title, author, description, cover_image, category_id, file_path, file_size, word_count, created_at, updated_at
         FROM books WHERE id = ?1"
    )
    .bind(id)
    .fetch_optional(pool)
    .await
    .map_err(|e| format!("Failed to fetch book: {}", e))?;

    Ok(row.map(
        |(
            id,
            title,
            author,
            description,
            cover_image,
            category_id,
            file_path,
            file_size,
            word_count,
            created_at,
            updated_at,
        )| Book {
            id: Some(id),
            title,
            author,
            description,
            cover_image,
            category_id,
            file_path,
            file_size,
            word_count,
            created_at,
            updated_at,
            category_name: None,
        },
    ))
}

#[command]
pub async fn get_books_by_category(
    app: AppHandle,
    category_id: i64,
) -> Result<Vec<Book>, String> {
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

    let rows = sqlx::query_as::<_, (
        i64,
        String,
        Option<String>,
        Option<String>,
        Option<String>,
        Option<i64>,
        Option<String>,
        Option<i64>,
        i64,
        String,
        String,
    )>(
        "SELECT id, title, author, description, cover_image, category_id, file_path, file_size, word_count, created_at, updated_at
         FROM books WHERE category_id = ?1 ORDER BY created_at DESC"
    )
    .bind(category_id)
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Failed to fetch books by category: {}", e))?;

    let books = rows
        .into_iter()
        .map(
            |(
                id,
                title,
                author,
                description,
                cover_image,
                category_id,
                file_path,
                file_size,
                word_count,
                created_at,
                updated_at,
            )| Book {
                id: Some(id),
                title,
                author,
                description,
                cover_image,
                category_id,
                file_path,
                file_size,
                word_count,
                created_at,
                updated_at,
                category_name: None,
            },
        )
        .collect();

    Ok(books)
}

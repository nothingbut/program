use crate::models::Category;
use tauri::{command, AppHandle, Manager};

#[command]
pub async fn get_all_categories(
    app: AppHandle,
) -> Result<Vec<Category>, String> {
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

    let rows = sqlx::query_as::<_, (i64, String, Option<i64>, i64, String)>(
        "SELECT id, name, parent_id, sort_order, created_at FROM categories ORDER BY sort_order"
    )
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Failed to fetch categories: {}", e))?;

    let categories = rows
        .into_iter()
        .map(|(id, name, parent_id, sort_order, created_at)| Category {
            id: Some(id),
            name,
            parent_id,
            sort_order,
            created_at,
            children: None,
            books: None,
        })
        .collect();

    Ok(categories)
}

#[command]
pub async fn get_category_by_id(
    app: AppHandle,
    id: i64,
) -> Result<Option<Category>, String> {
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

    let row = sqlx::query_as::<_, (i64, String, Option<i64>, i64, String)>(
        "SELECT id, name, parent_id, sort_order, created_at FROM categories WHERE id = ?1"
    )
    .bind(id)
    .fetch_optional(pool)
    .await
    .map_err(|e| format!("Failed to fetch category: {}", e))?;

    Ok(row.map(|(id, name, parent_id, sort_order, created_at)| Category {
        id: Some(id),
        name,
        parent_id,
        sort_order,
        created_at,
        children: None,
        books: None,
    }))
}

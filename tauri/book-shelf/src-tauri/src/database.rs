use tauri::State;
use tauri_plugin_sql::SqlitePool;

pub struct DatabaseState(pub SqlitePool);

pub async fn get_database(db: State<'_, DatabaseState>) -> Result<&SqlitePool, String> {
    Ok(&db.0)
}

pub async fn execute_query(
    db: &SqlitePool,
    query: &str,
    params: &[&dyn tauri_plugin_sql::rusqlite::ToSql],
) -> Result<Vec<tauri_plugin_sql::rusqlite::Row>, String> {
    let conn = db.get().map_err(|e| format!("Database connection error: {}", e))?;
    
    let mut stmt = conn
        .prepare(query)
        .map_err(|e| format!("Query preparation error: {}", e))?;
    
    let rows = stmt
        .query_map(params, |row| Ok(row.clone()))
        .map_err(|e| format!("Query execution error: {}", e))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| format!("Row collection error: {}", e))?;
    
    Ok(rows)
}

pub async fn execute_update(
    db: &SqlitePool,
    query: &str,
    params: &[&dyn tauri_plugin_sql::rusqlite::ToSql],
) -> Result<i64, String> {
    let conn = db.get().map_err(|e| format!("Database connection error: {}", e))?;
    
    let result = conn
        .execute(query, params)
        .map_err(|e| format!("Update execution error: {}", e))?;
    
    Ok(result as i64)
}
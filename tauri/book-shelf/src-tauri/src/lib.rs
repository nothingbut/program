use tauri_plugin_sql::{Migration, MigrationKind};

pub mod commands;
mod models;
use commands::categories::*;
use commands::books::*;
use commands::chapters::*;
use commands::import::*;

// 获取数据库迁移
fn get_migrations() -> Vec<Migration> {
    vec![
        Migration {
            version: 1,
            description: "initial schema",
            kind: MigrationKind::Up,
            sql: include_str!("../migrations/0001_initial.sql"),
        },
        Migration {
            version: 2,
            description: "test data",
            kind: MigrationKind::Up,
            sql: include_str!("../migrations/0002_test_data.sql"),
        },
    ]
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(
            tauri_plugin_sql::Builder::default()
                .add_migrations("sqlite:bookshelf.db", get_migrations())
                .build(),
        )
        .invoke_handler(tauri::generate_handler![
            // Category commands
            get_all_categories,
            get_category_by_id,
            // Book commands
            get_all_books,
            get_book_by_id,
            get_books_by_category,
            // Chapter commands
            get_chapters_by_book,
            get_chapter_by_id,
            // Import commands
            import_book_atomic,
        ])
        
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

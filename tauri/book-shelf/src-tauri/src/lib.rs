use tauri_plugin_sql::{Migration, MigrationKind};

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
        .plugin(
            tauri_plugin_sql::Builder::default()
                .add_migrations("sqlite:bookshelf.db", get_migrations())
                .build(),
        )
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

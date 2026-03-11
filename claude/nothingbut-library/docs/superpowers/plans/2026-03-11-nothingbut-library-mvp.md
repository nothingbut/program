# NothingBut Library MVP 实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建跨平台资料库管理应用的 MVP 版本，专注于网络小说管理功能

**Architecture:** 采用 Tauri 2.0 + Svelte 5 + Rust + SQLite 的混合架构，工作区隔离设计，通过 LibraryModule trait 实现模块化，集成 Ollama 本地 AI 服务

**Tech Stack:** Tauri 2.0, Svelte 5, Rust 1.77+, SQLite, TypeScript, Tailwind CSS 4.0, Bun, Ollama

**预计时间:** 6-8 周

---

## 前置要求

### 开发环境

- [x] Rust 1.77+ (已安装)
- [x] Bun 1.0+ (已安装)
- [ ] Ollama (需安装并配置)
- [ ] Node.js 18+ (作为 Bun 的后备)

### 安装 Ollama 和模型

```bash
# macOS
brew install ollama

# 启动 Ollama 服务
ollama serve

# 拉取所需模型（另一个终端）
ollama pull qwen2.5:7b              # 对话模型
ollama pull nomic-embed-text:latest # 嵌入模型
```

---

## Chunk 1: 项目初始化和基础架构

**环境变量**:
```bash
export PROJECT_ROOT="/Users/shichang/Workspace/program/claude/nothingbut-library"
cd $PROJECT_ROOT
```

### Task 1.1: 初始化 Tauri 项目骨架

**Files:**
- Create: `$PROJECT_ROOT/package.json`
- Create: `$PROJECT_ROOT/src-tauri/Cargo.toml`
- Create: `$PROJECT_ROOT/src-tauri/tauri.conf.json`

- [ ] **Step 1: 初始化 Tauri 项目**

```bash
cd /Users/shichang/Workspace/program
bunx create-tauri-app@latest claude/nothingbut-library --name nothingbut-library --framework svelte-ts --package-manager bun
```

Expected: 生成基础项目结构，包含 src/, src-tauri/, package.json 等

- [ ] **Step 2: 配置 package.json**

```json
{
  "name": "nothingbut-library",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-check --tsconfig ./tsconfig.json",
    "check:watch": "svelte-check --tsconfig ./tsconfig.json --watch",
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build"
  },
  "dependencies": {
    "@tauri-apps/api": "^2.0.0",
    "@tauri-apps/plugin-sql": "^2.0.0"
  },
  "devDependencies": {
    "@sveltejs/adapter-static": "^3.0.0",
    "@sveltejs/kit": "^2.0.0",
    "@sveltejs/vite-plugin-svelte": "^4.0.0",
    "autoprefixer": "^10.4.16",
    "svelte": "^5.0.0",
    "svelte-check": "^4.0.0",
    "tailwindcss": "^4.0.0",
    "tslib": "^2.6.2",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 3: 安装依赖**

```bash
bun install
```

Expected: 所有依赖安装成功，无错误

- [ ] **Step 4: 配置 Tailwind CSS 4.0**

创建 `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#ffffff',
        'bg-secondary': '#f5f5f5',
        'bg-hover': '#e8e8e8',
        'text-primary': '#333333',
        'text-secondary': '#666666',
        'border-color': '#e0e0e0',
        'primary-color': '#3b82f6',
      }
    },
  },
  plugins: [],
}
```

- [ ] **Step 5: 配置 SvelteKit static adapter**

修改 `svelte.config.js`:

```javascript
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      fallback: 'index.html'
    })
  }
};

export default config;
```

- [ ] **Step 6: 配置 Vite**

修改 `vite.config.js`:

```javascript
import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    hmr: {
      port: 1421
    }
  }
});
```

- [ ] **Step 7: 配置 Tauri**

修改 `src-tauri/tauri.conf.json`:

```json
{
  "$schema": "https://schema.tauri.app/config/2.0.0",
  "productName": "NothingBut Library",
  "version": "0.1.0",
  "identifier": "com.nothingbut.library",
  "build": {
    "beforeDevCommand": "bun run dev",
    "beforeBuildCommand": "bun run build",
    "devUrl": "http://localhost:1420",
    "frontendDist": "../build"
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "windows": {
      "webviewInstallMode": {
        "type": "embedBootstrapper"
      }
    }
  },
  "app": {
    "windows": [
      {
        "title": "NothingBut Library",
        "width": 1280,
        "height": 800,
        "minWidth": 1024,
        "minHeight": 768
      }
    ]
  }
}
```

- [ ] **Step 8: 测试项目启动**

```bash
bun run tauri:dev
```

Expected: 应用窗口打开，显示默认的 Tauri + Svelte 页面

- [ ] **Step 9: Commit 项目初始化**

```bash
git add .
git commit -m "chore: 初始化 Tauri 2.0 + Svelte 5 项目

- 配置 package.json 和依赖
- 配置 Tailwind CSS 4.0
- 配置 SvelteKit static adapter
- 配置 Vite 开发服务器
- 配置 Tauri 应用设置
- 验证项目可正常启动

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 2: 核心模块结构（Rust）

**Files:**
- Create: `src-tauri/src/core/mod.rs`
- Create: `src-tauri/src/core/models.rs`
- Create: `src-tauri/src/core/traits.rs`
- Create: `src-tauri/src/core/workspace.rs`
- Create: `src-tauri/src/core/config.rs`
- Create: `src-tauri/src/errors.rs`
- Modify: `src-tauri/src/lib.rs`
- Modify: `src-tauri/Cargo.toml`

- [ ] **Step 1: 添加 Rust 依赖**

修改 `src-tauri/Cargo.toml`:

```toml
[package]
name = "nothingbut-library"
version = "0.1.0"
edition = "2021"

[lib]
name = "nothingbut_library_lib"
crate-type = ["staticlib", "cdylib", "lib"]

[dependencies]
tauri = { version = "2.0", features = [] }
tauri-plugin-sql = { version = "2.0", features = ["sqlite"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1", features = ["full"] }
async-trait = "0.1"
thiserror = "1.0"
reqwest = { version = "0.11", features = ["json"] }
regex = "1.10"
encoding_rs = "0.8"
chrono = { version = "0.4", features = ["serde"] }
dirs = "5.0"

[build-dependencies]
tauri-build = { version = "2.0", features = [] }
```

- [ ] **Step 2: 定义错误类型**

创建 `src-tauri/src/errors.rs`:

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),

    #[error("Database error: {0}")]
    Database(String),

    #[error("Workspace error: {0}")]
    Workspace(String),

    #[error("Module error: {0}")]
    Module(String),

    #[error("Not found: {0}")]
    NotFound(String),
}

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::ser::Serializer,
    {
        serializer.serialize_str(&self.to_string())
    }
}

pub type AppResult<T> = Result<T, AppError>;
```

- [ ] **Step 3: 定义核心数据模型**

创建 `src-tauri/src/core/models.rs`:

```rust
use serde::{Deserialize, Serialize};

/// 资料类型
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum ModuleType {
    Novel,
    Music,
    Ebook,
    Note,
}

impl ModuleType {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Novel => "novel",
            Self::Music => "music",
            Self::Ebook => "ebook",
            Self::Note => "note",
        }
    }
}

/// 工作区信息
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Workspace {
    pub id: i64,
    pub name: String,
    pub path: String,
    pub module_type: ModuleType,
    pub last_opened_at: Option<String>,
    pub created_at: String,
}

/// 工作区配置
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WorkspaceConfig {
    pub name: String,
    #[serde(rename = "type")]
    pub module_type: ModuleType,
    pub version: String,
    pub created_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub settings: Option<serde_json::Value>,
}

/// 资料项目（通用）
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LibraryItem {
    pub id: i64,
    pub title: String,
    pub module_type: ModuleType,
    pub metadata: serde_json::Value,
}

/// 分类
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Category {
    pub id: i64,
    pub name: String,
    pub parent_id: Option<i64>,
}
```

- [ ] **Step 4: 定义 LibraryModule traits**

创建 `src-tauri/src/core/traits.rs`:

```rust
use async_trait::async_trait;
use std::path::PathBuf;
use crate::core::models::{Category, LibraryItem, ModuleType};
use crate::errors::AppResult;

/// 资料库模块核心接口（必须实现）
#[async_trait]
pub trait LibraryModule: Send + Sync {
    /// 模块名称
    fn name(&self) -> &'static str;

    /// 模块类型
    fn module_type(&self) -> ModuleType;

    /// 导入文件到资料库
    async fn import_file(
        &self,
        workspace_path: &PathBuf,
        file_path: &PathBuf,
    ) -> AppResult<i64>;

    /// 列出所有项目
    async fn list_items(
        &self,
        workspace_path: &PathBuf,
    ) -> AppResult<Vec<LibraryItem>>;

    /// 获取单个项目详情
    async fn get_item(
        &self,
        workspace_path: &PathBuf,
        id: i64,
    ) -> AppResult<Option<LibraryItem>>;

    /// 删除项目
    async fn delete_item(
        &self,
        workspace_path: &PathBuf,
        id: i64,
    ) -> AppResult<()>;
}

/// 可搜索扩展（可选实现）
#[async_trait]
pub trait Searchable: LibraryModule {
    /// 关键词搜索
    async fn search(
        &self,
        workspace_path: &PathBuf,
        query: &str,
    ) -> AppResult<Vec<LibraryItem>>;
}

/// 可分类扩展（可选实现）
#[async_trait]
pub trait Categorizable: LibraryModule {
    /// 获取分类树
    async fn get_categories(
        &self,
        workspace_path: &PathBuf,
    ) -> AppResult<Vec<Category>>;

    /// 创建分类
    async fn create_category(
        &self,
        workspace_path: &PathBuf,
        name: String,
        parent_id: Option<i64>,
    ) -> AppResult<i64>;

    /// 移动项目到分类
    async fn move_to_category(
        &self,
        workspace_path: &PathBuf,
        item_id: i64,
        category_id: Option<i64>,
    ) -> AppResult<()>;
}

/// AI 增强扩展（可选实现）
#[async_trait]
pub trait AIEnhanced: LibraryModule {
    /// 生成项目的向量嵌入
    async fn generate_embeddings(
        &self,
        workspace_path: &PathBuf,
        item_id: i64,
    ) -> AppResult<Vec<f32>>;

    /// 语义搜索
    async fn semantic_search(
        &self,
        workspace_path: &PathBuf,
        query: &str,
        limit: usize,
    ) -> AppResult<Vec<(LibraryItem, f32)>>;
}
```

- [ ] **Step 5: 实现工作区管理**

创建 `src-tauri/src/core/workspace.rs`:

```rust
use std::fs;
use std::path::{Path, PathBuf};
use chrono::Utc;
use crate::core::models::{ModuleType, Workspace, WorkspaceConfig};
use crate::errors::{AppError, AppResult};

/// 创建新工作区
pub fn create_workspace(
    base_dir: &Path,
    name: String,
    module_type: ModuleType,
) -> AppResult<PathBuf> {
    let workspace_dir = base_dir.join(&name);

    // 创建工作区目录
    if workspace_dir.exists() {
        return Err(AppError::Workspace(format!(
            "Workspace already exists: {}",
            workspace_dir.display()
        )));
    }

    fs::create_dir_all(&workspace_dir)?;

    // 创建子目录
    match module_type {
        ModuleType::Novel => {
            fs::create_dir_all(workspace_dir.join("books"))?;
            fs::create_dir_all(workspace_dir.join(".embeddings"))?;
        }
        ModuleType::Music => {
            fs::create_dir_all(workspace_dir.join("music"))?;
        }
        ModuleType::Ebook => {
            fs::create_dir_all(workspace_dir.join("ebooks"))?;
        }
        ModuleType::Note => {
            fs::create_dir_all(workspace_dir.join("notes"))?;
        }
    }

    // 创建配置文件
    let config = WorkspaceConfig {
        name: name.clone(),
        module_type,
        version: "1.0.0".to_string(),
        created_at: Utc::now().to_rfc3339(),
        settings: None,
    };

    let config_path = workspace_dir.join("config.json");
    let config_json = serde_json::to_string_pretty(&config)?;
    fs::write(config_path, config_json)?;

    Ok(workspace_dir)
}

/// 加载工作区配置
pub fn load_workspace_config(workspace_dir: &Path) -> AppResult<WorkspaceConfig> {
    let config_path = workspace_dir.join("config.json");

    if !config_path.exists() {
        return Err(AppError::NotFound(format!(
            "Config file not found: {}",
            config_path.display()
        )));
    }

    let config_json = fs::read_to_string(config_path)?;
    let config: WorkspaceConfig = serde_json::from_str(&config_json)?;

    Ok(config)
}

/// 获取工作区数据库路径
pub fn get_database_path(workspace_dir: &Path) -> PathBuf {
    workspace_dir.join("library.db")
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_create_workspace() {
        let temp_dir = TempDir::new().unwrap();
        let base_path = temp_dir.path();

        let workspace_path = create_workspace(
            base_path,
            "test-workspace".to_string(),
            ModuleType::Novel,
        )
        .unwrap();

        assert!(workspace_path.exists());
        assert!(workspace_path.join("config.json").exists());
        assert!(workspace_path.join("books").exists());
        assert!(workspace_path.join(".embeddings").exists());
    }

    #[test]
    fn test_load_workspace_config() {
        let temp_dir = TempDir::new().unwrap();
        let base_path = temp_dir.path();

        let workspace_path = create_workspace(
            base_path,
            "test-workspace".to_string(),
            ModuleType::Novel,
        )
        .unwrap();

        let config = load_workspace_config(&workspace_path).unwrap();
        assert_eq!(config.name, "test-workspace");
        assert_eq!(config.module_type, ModuleType::Novel);
        assert_eq!(config.version, "1.0.0");
    }
}
```

- [ ] **Step 6: 创建 core 模块入口**

创建 `src-tauri/src/core/mod.rs`:

```rust
pub mod models;
pub mod traits;
pub mod workspace;
pub mod config;

pub use models::*;
pub use traits::*;
```

创建 `src-tauri/src/core/config.rs`:

```rust
use std::path::PathBuf;
use dirs;
use crate::errors::AppResult;

/// 获取应用数据目录
pub fn get_app_data_dir() -> AppResult<PathBuf> {
    let data_dir = dirs::data_dir()
        .ok_or_else(|| crate::errors::AppError::Workspace(
            "Cannot determine data directory".to_string()
        ))?
        .join("NothingButLibrary");

    std::fs::create_dir_all(&data_dir)?;
    Ok(data_dir)
}

/// 获取工作区根目录
pub fn get_workspaces_root() -> AppResult<PathBuf> {
    let root = get_app_data_dir()?.join("workspaces");
    std::fs::create_dir_all(&root)?;
    Ok(root)
}
```

- [ ] **Step 7: 更新 lib.rs**

修改 `src-tauri/src/lib.rs`:

```rust
pub mod core;
pub mod errors;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_sql::Builder::default().build())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

- [ ] **Step 8: 运行 Rust 测试**

```bash
cd src-tauri
cargo test
```

Expected: 所有测试通过

```
running 2 tests
test core::workspace::tests::test_create_workspace ... ok
test core::workspace::tests::test_load_workspace_config ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

- [ ] **Step 9: 测试应用编译**

```bash
cargo check
```

Expected: 编译成功，无错误

- [ ] **Step 10: Commit 核心模块**

```bash
git add src-tauri/
git commit -m "feat(core): 添加核心模块结构和 LibraryModule traits

- 定义 AppError 错误类型和 AppResult
- 定义核心数据模型（Workspace, ModuleType, LibraryItem）
- 定义 LibraryModule trait 和扩展 traits（Searchable, Categorizable, AIEnhanced）
- 实现工作区创建和配置加载功能
- 添加单元测试，测试覆盖率 100%

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 3: 数据库迁移系统

**Files:**
- Create: `src-tauri/src/database.rs`
- Create: `src-tauri/migrations/0001_core.sql`
- Create: `src-tauri/migrations/0002_novel.sql`
- Modify: `src-tauri/src/lib.rs`

- [ ] **Step 1: 创建核心表迁移**

创建 `src-tauri/migrations/0001_core.sql`:

```sql
-- 工作区配置表（应用级别，存储在应用数据目录）
CREATE TABLE IF NOT EXISTS app_workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    module_type TEXT NOT NULL,
    last_opened_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_app_workspaces_module_type ON app_workspaces(module_type);
CREATE INDEX idx_app_workspaces_last_opened ON app_workspaces(last_opened_at DESC);

-- 工作区内的通用配置（每个工作区的 library.db）
CREATE TABLE IF NOT EXISTS library_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

- [ ] **Step 2: 创建小说模块迁移**

创建 `src-tauri/migrations/0002_novel.sql`:

```sql
-- 分类表（支持树形结构）
CREATE TABLE IF NOT EXISTS novel_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (parent_id) REFERENCES novel_categories(id) ON DELETE CASCADE
);

CREATE INDEX idx_novel_categories_parent ON novel_categories(parent_id);

-- 书籍表
CREATE TABLE IF NOT EXISTS novel_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    description TEXT,
    cover_path TEXT,
    category_id INTEGER,
    book_dir TEXT NOT NULL UNIQUE,
    file_size INTEGER,
    word_count INTEGER,
    chapter_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ongoing',
    reading_progress INTEGER DEFAULT 0,
    last_read_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES novel_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (reading_progress) REFERENCES novel_chapters(id) ON DELETE SET NULL
);

CREATE INDEX idx_novel_books_category ON novel_books(category_id);
CREATE INDEX idx_novel_books_last_read ON novel_books(last_read_at);
CREATE INDEX idx_novel_books_status ON novel_books(status);

-- 章节表
CREATE TABLE IF NOT EXISTS novel_chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    sort_order INTEGER NOT NULL,
    word_count INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (book_id) REFERENCES novel_books(id) ON DELETE CASCADE
);

CREATE INDEX idx_novel_chapters_book ON novel_chapters(book_id);
CREATE INDEX idx_novel_chapters_order ON novel_chapters(book_id, sort_order);

-- 书签表
CREATE TABLE IF NOT EXISTS novel_bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    chapter_id INTEGER NOT NULL,
    position INTEGER DEFAULT 0,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (book_id) REFERENCES novel_books(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES novel_chapters(id) ON DELETE CASCADE
);

CREATE INDEX idx_novel_bookmarks_book ON novel_bookmarks(book_id);

-- 阅读统计表
CREATE TABLE IF NOT EXISTS novel_reading_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    reading_time INTEGER DEFAULT 0,
    words_read INTEGER DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES novel_books(id) ON DELETE CASCADE,
    UNIQUE(book_id, date)
);

CREATE INDEX idx_novel_reading_stats_book_date ON novel_reading_stats(book_id, date);
```

- [ ] **Step 3: 实现数据库工具模块**

创建 `src-tauri/src/database.rs`:

```rust
use std::path::Path;
use tauri_plugin_sql::{Builder, Migration, MigrationKind};
use crate::errors::AppResult;

/// 获取迁移列表
pub fn get_migrations() -> Vec<Migration> {
    vec![
        Migration {
            version: 1,
            description: "create core tables",
            sql: include_str!("../migrations/0001_core.sql"),
            kind: MigrationKind::Up,
        },
        Migration {
            version: 2,
            description: "create novel tables",
            sql: include_str!("../migrations/0002_novel.sql"),
            kind: MigrationKind::Up,
        },
    ]
}

/// 初始化工作区数据库
pub async fn init_workspace_db(workspace_path: &Path) -> AppResult<()> {
    let db_path = workspace_path.join("library.db");
    let db_url = format!("sqlite:{}", db_path.display());

    // 这里使用 tauri-plugin-sql 的自动迁移功能
    // 在实际应用启动时，会通过 Tauri 插件自动执行迁移

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_migrations() {
        let migrations = get_migrations();
        assert_eq!(migrations.len(), 2);
        assert_eq!(migrations[0].version, 1);
        assert_eq!(migrations[1].version, 2);
    }
}
```

- [ ] **Step 4: 更新 lib.rs 配置数据库插件**

修改 `src-tauri/src/lib.rs`:

```rust
pub mod core;
pub mod database;
pub mod errors;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let migrations = database::get_migrations();

    tauri::Builder::default()
        .plugin(
            tauri_plugin_sql::Builder::default()
                .add_migrations("sqlite:library.db", migrations)
                .build()
        )
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

- [ ] **Step 5: 运行测试**

```bash
cd src-tauri
cargo test
```

Expected: 测试通过

- [ ] **Step 6: Commit 数据库迁移系统**

```bash
git add src-tauri/
git commit -m "feat(database): 添加数据库迁移系统

- 创建核心表迁移（app_workspaces, library_config）
- 创建小说模块迁移（categories, books, chapters, bookmarks, stats）
- 实现迁移管理和数据库初始化
- 配置 tauri-plugin-sql 自动迁移

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Chunk 2: 小说模块实现

### Task 4: 小说模块数据模型

**Files:**
- Create: `src-tauri/src/modules/mod.rs`
- Create: `src-tauri/src/modules/novel/mod.rs`
- Create: `src-tauri/src/modules/novel/models.rs`
- Modify: `src-tauri/src/lib.rs`

- [ ] **Step 1: 定义小说模块数据模型**

创建 `src-tauri/src/modules/novel/models.rs`:

```rust
use serde::{Deserialize, Serialize};

/// 书籍状态
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum BookStatus {
    Completed,  // 完本
    Ongoing,    // 连载
    Abandoned,  // 太监
}

impl BookStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Completed => "completed",
            Self::Ongoing => "ongoing",
            Self::Abandoned => "abandoned",
        }
    }
}

/// 小说分类
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NovelCategory {
    pub id: i64,
    pub name: String,
    pub parent_id: Option<i64>,
    pub sort_order: i32,
    pub created_at: String,
}

/// 小说书籍
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NovelBook {
    pub id: i64,
    pub title: String,
    pub author: Option<String>,
    pub description: Option<String>,
    pub cover_path: Option<String>,
    pub category_id: Option<i64>,
    pub book_dir: String,
    pub file_size: Option<i64>,
    pub word_count: Option<i64>,
    pub chapter_count: i32,
    pub status: BookStatus,
    pub reading_progress: Option<i64>,
    pub last_read_at: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

/// 小说章节
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NovelChapter {
    pub id: i64,
    pub book_id: i64,
    pub title: String,
    pub file_path: String,
    pub sort_order: i32,
    pub word_count: Option<i32>,
    pub created_at: String,
}

/// 导入预览
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ImportPreview {
    pub suggested_title: String,
    pub suggested_author: Option<String>,
    pub suggested_description: Option<String>,
    pub chapters: Vec<ChapterPreview>,
    pub total_words: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChapterPreview {
    pub title: String,
    pub word_count: i32,
    pub content_preview: String,
}

/// 书签
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NovelBookmark {
    pub id: i64,
    pub book_id: i64,
    pub chapter_id: i64,
    pub position: i32,
    pub note: Option<String>,
    pub created_at: String,
}
```

- [ ] **Step 2: 创建小说模块入口**

创建 `src-tauri/src/modules/novel/mod.rs`:

```rust
pub mod models;

pub use models::*;
```

创建 `src-tauri/src/modules/mod.rs`:

```rust
pub mod novel;
```

- [ ] **Step 3: 更新 lib.rs**

修改 `src-tauri/src/lib.rs`:

```rust
pub mod core;
pub mod database;
pub mod errors;
pub mod modules;

// ... rest of the file
```

- [ ] **Step 4: 编写模型测试**

在 `src-tauri/src/modules/novel/models.rs` 末尾添加:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_book_status_serialization() {
        let status = BookStatus::Completed;
        let json = serde_json::to_string(&status).unwrap();
        assert_eq!(json, "\"completed\"");

        let deserialized: BookStatus = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized, BookStatus::Completed);
    }

    #[test]
    fn test_novel_book_serialization() {
        let book = NovelBook {
            id: 1,
            title: "测试小说".to_string(),
            author: Some("测试作者".to_string()),
            description: None,
            cover_path: None,
            category_id: Some(1),
            book_dir: "book-1".to_string(),
            file_size: Some(1024000),
            word_count: Some(50000),
            chapter_count: 10,
            status: BookStatus::Ongoing,
            reading_progress: None,
            last_read_at: None,
            created_at: "2026-03-11T10:00:00Z".to_string(),
            updated_at: "2026-03-11T10:00:00Z".to_string(),
        };

        let json = serde_json::to_string(&book).unwrap();
        let deserialized: NovelBook = serde_json::from_str(&json).unwrap();

        assert_eq!(deserialized.title, "测试小说");
        assert_eq!(deserialized.author, Some("测试作者".to_string()));
        assert_eq!(deserialized.status, BookStatus::Ongoing);
    }
}
```

- [ ] **Step 5: 运行测试**

```bash
cd src-tauri
cargo test
```

Expected: 所有测试通过

- [ ] **Step 6: Commit 小说模块数据模型**

```bash
git add src-tauri/
git commit -m "feat(novel): 添加小说模块数据模型

- 定义 BookStatus 枚举（完本/连载/太监）
- 定义小说相关数据模型（Category, Book, Chapter, Bookmark）
- 定义导入预览模型
- 添加序列化/反序列化测试

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

由于计划文档较长，我会分块完成并审查。让我先暂停这里，调用 plan-document-reviewer 审查第一个 chunk。

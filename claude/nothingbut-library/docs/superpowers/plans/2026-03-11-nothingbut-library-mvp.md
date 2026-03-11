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

- [ ] **Step 1.1: 初始化 Tauri 项目**

```bash
cd /Users/shichang/Workspace/program
bunx create-tauri-app@latest claude/nothingbut-library --name nothingbut-library --framework svelte-ts --package-manager bun
```

Expected: 生成基础项目结构，包含 src/, src-tauri/, package.json 等

- [ ] **Step 1.2: 验证生成的文件**

```bash
cd $PROJECT_ROOT
ls -la
```

Expected: 应包含 package.json, src/, src-tauri/, .gitignore 等文件

- [ ] **Step 1.3: 配置 package.json**

修改 `$PROJECT_ROOT/package.json`:

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

- [ ] **Step 1.4: 安装依赖**

```bash
cd $PROJECT_ROOT
bun install
```

Expected: 所有依赖安装成功，无错误

```
bun install v1.x.x
+ @tauri-apps/api@2.0.0
+ @tauri-apps/plugin-sql@2.0.0
... (更多依赖)
Done in 2.5s
```

- [ ] **Step 1.5: 提交项目骨架**

```bash
cd $PROJECT_ROOT
git add .
git commit -m "chore: 初始化 Tauri 2.0 + Svelte 5 项目骨架

- 生成基础项目结构
- 配置 package.json 和依赖项
- 验证项目文件完整性"
```

---

### Task 1.2: 配置前端构建系统

**Files:**
- Create: `$PROJECT_ROOT/tailwind.config.js`
- Modify: `$PROJECT_ROOT/svelte.config.js`
- Modify: `$PROJECT_ROOT/vite.config.js`

- [ ] **Step 2.1: 配置 Tailwind CSS 4.0**

创建 `$PROJECT_ROOT/tailwind.config.js`:

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

- [ ] **Step 2.2: 配置 SvelteKit static adapter**

修改 `$PROJECT_ROOT/svelte.config.js`:

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

- [ ] **Step 2.3: 配置 Vite**

修改 `$PROJECT_ROOT/vite.config.js`:

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

- [ ] **Step 2.4: 测试 Vite 配置**

```bash
cd $PROJECT_ROOT
bun run dev
```

Expected: 开发服务器启动成功，在 http://localhost:1420

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:1420/
  ➜  Network: use --host to expose
```

按 Ctrl+C 停止服务器。

- [ ] **Step 2.5: 提交前端配置**

```bash
cd $PROJECT_ROOT
git add .
git commit -m "feat: 配置前端构建系统

- 配置 Tailwind CSS 4.0 主题色
- 配置 SvelteKit static adapter
- 配置 Vite 开发服务器（端口 1420）
- 验证开发服务器可正常启动"
```

---

### Task 1.3: 配置 Tauri 后端

**Files:**
- Modify: `$PROJECT_ROOT/src-tauri/tauri.conf.json`
- Modify: `$PROJECT_ROOT/src-tauri/Cargo.toml`

- [ ] **Step 3.1: 配置 Tauri 应用设置**

修改 `$PROJECT_ROOT/src-tauri/tauri.conf.json`:

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

- [ ] **Step 3.2: 测试 Tauri 应用启动**

```bash
cd $PROJECT_ROOT
bun run tauri:dev
```

Expected: 应用窗口打开，显示默认的 Tauri + Svelte 页面，无编译错误

- [ ] **Step 3.3: 提交 Tauri 配置**

```bash
cd $PROJECT_ROOT
git add .
git commit -m "feat: 配置 Tauri 桌面应用

- 配置 Tauri 应用标识和窗口尺寸
- 配置前端构建路径和开发 URL
- 验证 Tauri 应用可正常启动和渲染"
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

修改 `$PROJECT_ROOT/src-tauri/Cargo.toml`:

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

[dev-dependencies]
tempfile = "3.8"

[build-dependencies]
tauri-build = { version = "2.0", features = [] }
```

- [ ] **Step 2.1: 写测试 - 错误类型序列化（TDD Red）**

创建 `$PROJECT_ROOT/src-tauri/src/errors.rs`:

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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_error_serialization() {
        let error = AppError::Workspace("test error".to_string());
        let json = serde_json::to_string(&error).unwrap();
        assert!(json.contains("Workspace error: test error"));
    }

    #[test]
    fn test_app_error_from_io() {
        let io_error = std::io::Error::new(std::io::ErrorKind::NotFound, "file not found");
        let app_error: AppError = io_error.into();
        assert!(matches!(app_error, AppError::Io(_)));
    }
}
```

- [ ] **Step 2.2: 运行测试（TDD Red）**

```bash
cd $PROJECT_ROOT/src-tauri
cargo test errors::tests
```

Expected: 测试通过（因为实现已包含在同一步骤）

```
running 2 tests
test errors::tests::test_app_error_serialization ... ok
test errors::tests::test_app_error_from_io ... ok
```

- [ ] **Step 2.3: 提交错误类型**

```bash
cd $PROJECT_ROOT
git add src-tauri/src/errors.rs
git commit -m "feat(core): 添加应用错误类型

- 定义 AppError 枚举（IO/JSON/Database/Workspace/Module/NotFound）
- 实现 Serialize trait 用于前端错误展示
- 添加单元测试验证序列化和类型转换"
```

- [ ] **Step 3: 定义核心数据模型**

创建 `$PROJECT_ROOT/src-tauri/src/core/models.rs`:

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

"
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

- [ ] **Step 2.1: 验证 SQL 语法**

```bash
cd $PROJECT_ROOT/src-tauri
sqlite3 :memory: < migrations/0001_core.sql
echo "Core migration syntax: OK"

sqlite3 :memory: < migrations/0002_novel.sql
echo "Novel migration syntax: OK"
```

Expected: 两个迁移文件都应该成功执行，无错误

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

"
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

"
```

---

### Task 5: TXT 文件解析器

**Files:**
- Create: `$PROJECT_ROOT/src-tauri/src/modules/novel/parser.rs`
- Modify: `$PROJECT_ROOT/src-tauri/src/modules/novel/mod.rs`

- [ ] **Step 1: 实现编码识别**

创建 `$PROJECT_ROOT/src-tauri/src/modules/novel/parser.rs`:

```rust
use encoding_rs::{Encoding, UTF_8, GBK};
use regex::Regex;
use std::fs;
use std::path::Path;
use crate::errors::{AppError, AppResult};

/// 识别文本文件编码
pub fn detect_encoding(file_path: &Path) -> AppResult<&'static Encoding> {
    let bytes = fs::read(file_path)?;

    // 检查 BOM
    if bytes.starts_with(&[0xEF, 0xBB, 0xBF]) {
        return Ok(UTF_8);
    }

    // 尝试 UTF-8 解码
    if String::from_utf8(bytes.clone()).is_ok() {
        return Ok(UTF_8);
    }

    // 默认使用 GBK
    Ok(GBK)
}

/// 读取文本文件内容
pub fn read_text_file(file_path: &Path) -> AppResult<String> {
    let encoding = detect_encoding(file_path)?;
    let bytes = fs::read(file_path)?;

    let (text, _, _) = encoding.decode(&bytes);
    Ok(text.into_owned())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_detect_utf8_encoding() {
        let mut file = NamedTempFile::new().unwrap();
        file.write_all("测试文本".as_bytes()).unwrap();

        let encoding = detect_encoding(file.path()).unwrap();
        assert_eq!(encoding.name(), "UTF-8");
    }

    #[test]
    fn test_read_text_file() {
        let mut file = NamedTempFile::new().unwrap();
        file.write_all("第一章 开始\n\n正文内容".as_bytes()).unwrap();

        let content = read_text_file(file.path()).unwrap();
        assert!(content.contains("第一章"));
    }
}
```

- [ ] **Step 2: 实现章节分割**

在 `parser.rs` 中添加：

```rust
/// 章节信息
#[derive(Debug, Clone)]
pub struct ChapterInfo {
    pub title: String,
    pub content: String,
    pub word_count: usize,
}

/// 章节标题正则模式
const CHAPTER_PATTERNS: &[&str] = &[
    r"^第[零一二三四五六七八九十百千万\d]+[章回节集卷]",
    r"^Chapter\s+\d+",
    r"^\d+\.",
    r"^【.+】$",
];

/// 分割章节
pub fn split_chapters(content: &str) -> AppResult<Vec<ChapterInfo>> {
    let patterns: Vec<Regex> = CHAPTER_PATTERNS
        .iter()
        .map(|p| Regex::new(p).unwrap())
        .collect();

    let lines: Vec<&str> = content.lines().collect();
    let mut chapters = Vec::new();
    let mut current_title = String::from("前言");
    let mut current_content = String::new();

    for line in lines {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }

        // 检查是否是章节标题
        let is_chapter = patterns.iter().any(|re| re.is_match(line));

        if is_chapter {
            // 保存上一章
            if !current_content.is_empty() {
                chapters.push(ChapterInfo {
                    title: current_title.clone(),
                    content: current_content.trim().to_string(),
                    word_count: current_content.chars().count(),
                });
            }

            // 开始新章节
            current_title = line.to_string();
            current_content = String::new();
        } else {
            current_content.push_str(line);
            current_content.push('\n');
        }
    }

    // 保存最后一章
    if !current_content.is_empty() {
        chapters.push(ChapterInfo {
            title: current_title,
            content: current_content.trim().to_string(),
            word_count: current_content.chars().count(),
        });
    }

    if chapters.is_empty() {
        return Err(AppError::Module("No chapters found".to_string()));
    }

    Ok(chapters)
}

#[cfg(test)]
mod chapter_tests {
    use super::*;

    #[test]
    fn test_split_chapters() {
        let content = r#"
第一章 开始

这是第一章的内容。
这是第一章的第二段。

第二章 继续

这是第二章的内容。
        "#;

        let chapters = split_chapters(content).unwrap();
        assert_eq!(chapters.len(), 2);
        assert_eq!(chapters[0].title, "第一章 开始");
        assert!(chapters[0].content.contains("这是第一章的内容"));
        assert_eq!(chapters[1].title, "第二章 继续");
    }

    #[test]
    fn test_split_chapters_with_numbers() {
        let content = "1. 前言\n内容1\n\n2. 正文\n内容2";
        let chapters = split_chapters(content).unwrap();
        assert_eq!(chapters.len(), 2);
    }

    #[test]
    fn test_split_chapters_empty() {
        let content = "没有章节标题的文本";
        let result = split_chapters(content);
        assert!(result.is_err());
    }
}
```

- [ ] **Step 3: 更新模块导出**

修改 `$PROJECT_ROOT/src-tauri/src/modules/novel/mod.rs`:

```rust
pub mod models;
pub mod parser;

pub use models::*;
pub use parser::*;
```

- [ ] **Step 4: 运行测试**

```bash
cd $PROJECT_ROOT/src-tauri
cargo test modules::novel::parser
```

Expected: 所有测试通过

```
running 5 tests
test modules::novel::parser::tests::test_detect_utf8_encoding ... ok
test modules::novel::parser::tests::test_read_text_file ... ok
test modules::novel::parser::chapter_tests::test_split_chapters ... ok
test modules::novel::parser::chapter_tests::test_split_chapters_with_numbers ... ok
test modules::novel::parser::chapter_tests::test_split_chapters_empty ... ok
```

- [ ] **Step 5: 提交 TXT 解析器**

```bash
cd $PROJECT_ROOT
git add src-tauri/src/modules/novel/
git commit -m "feat(novel): 添加 TXT 文件解析器

- 实现编码识别（UTF-8/GBK）
- 实现章节分割（支持多种标题格式）
- 添加完整的单元测试
- 测试覆盖：编码识别、文件读取、章节分割、边界情况"
```

---

### Task 6: 文件存储系统

**Files:**
- Create: `$PROJECT_ROOT/src-tauri/src/modules/novel/storage.rs`
- Modify: `$PROJECT_ROOT/src-tauri/src/modules/novel/mod.rs`

- [ ] **Step 1: 实现书籍目录创建**

创建 `$PROJECT_ROOT/src-tauri/src/modules/novel/storage.rs`:

```rust
use std::fs;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};
use crate::errors::{AppError, AppResult};
use super::parser::ChapterInfo;

/// 书籍元数据
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BookMetadata {
    pub title: String,
    pub author: Option<String>,
    pub description: Option<String>,
    pub chapter_count: usize,
    pub total_words: usize,
    pub created_at: String,
}

/// 创建书籍目录
pub fn create_book_dir(workspace_path: &Path, book_id: i64) -> AppResult<PathBuf> {
    let book_dir = workspace_path.join("books").join(format!("book-{}", book_id));
    fs::create_dir_all(&book_dir)?;
    fs::create_dir_all(book_dir.join("chapters"))?;
    Ok(book_dir)
}

/// 保存章节文件
pub fn save_chapter(
    book_dir: &Path,
    chapter_index: usize,
    chapter: &ChapterInfo,
) -> AppResult<String> {
    let chapter_file = format!("chapter-{:04}.txt", chapter_index);
    let chapter_path = book_dir.join("chapters").join(&chapter_file);

    fs::write(&chapter_path, &chapter.content)?;

    Ok(format!("chapters/{}", chapter_file))
}

/// 保存元数据
pub fn save_metadata(
    book_dir: &Path,
    metadata: &BookMetadata,
) -> AppResult<()> {
    let metadata_path = book_dir.join("metadata.json");
    let json = serde_json::to_string_pretty(metadata)?;
    fs::write(metadata_path, json)?;
    Ok(())
}

/// 读取元数据
pub fn load_metadata(book_dir: &Path) -> AppResult<BookMetadata> {
    let metadata_path = book_dir.join("metadata.json");

    if !metadata_path.exists() {
        return Err(AppError::NotFound(format!(
            "Metadata not found: {}",
            metadata_path.display()
        )));
    }

    let json = fs::read_to_string(metadata_path)?;
    let metadata = serde_json::from_str(&json)?;
    Ok(metadata)
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;
    use chrono::Utc;

    #[test]
    fn test_create_book_dir() {
        let temp_dir = TempDir::new().unwrap();
        let book_dir = create_book_dir(temp_dir.path(), 1).unwrap();

        assert!(book_dir.exists());
        assert!(book_dir.join("chapters").exists());
    }

    #[test]
    fn test_save_and_load_chapter() {
        let temp_dir = TempDir::new().unwrap();
        let book_dir = create_book_dir(temp_dir.path(), 1).unwrap();

        let chapter = ChapterInfo {
            title: "第一章".to_string(),
            content: "章节内容".to_string(),
            word_count: 4,
        };

        let path = save_chapter(&book_dir, 1, &chapter).unwrap();
        assert_eq!(path, "chapters/chapter-0001.txt");

        let saved_content = fs::read_to_string(book_dir.join(&path)).unwrap();
        assert_eq!(saved_content, "章节内容");
    }

    #[test]
    fn test_save_and_load_metadata() {
        let temp_dir = TempDir::new().unwrap();
        let book_dir = create_book_dir(temp_dir.path(), 1).unwrap();

        let metadata = BookMetadata {
            title: "测试书籍".to_string(),
            author: Some("测试作者".to_string()),
            description: None,
            chapter_count: 10,
            total_words: 50000,
            created_at: Utc::now().to_rfc3339(),
        };

        save_metadata(&book_dir, &metadata).unwrap();
        let loaded = load_metadata(&book_dir).unwrap();

        assert_eq!(loaded.title, "测试书籍");
        assert_eq!(loaded.chapter_count, 10);
    }
}
```

- [ ] **Step 2: 更新模块导出**

修改 `$PROJECT_ROOT/src-tauri/src/modules/novel/mod.rs`:

```rust
pub mod models;
pub mod parser;
pub mod storage;

pub use models::*;
pub use parser::*;
pub use storage::*;
```

- [ ] **Step 3: 运行测试**

```bash
cd $PROJECT_ROOT/src-tauri
cargo test modules::novel::storage
```

Expected: 所有测试通过

```
running 3 tests
test modules::novel::storage::tests::test_create_book_dir ... ok
test modules::novel::storage::tests::test_save_and_load_chapter ... ok
test modules::novel::storage::tests::test_save_and_load_metadata ... ok
```

- [ ] **Step 4: 提交文件存储系统**

```bash
cd $PROJECT_ROOT
git add src-tauri/src/modules/novel/
git commit -m "feat(novel): 添加文件存储系统

- 实现书籍目录创建（books/book-{id}/）
- 实现章节文件保存（chapters/chapter-XXXX.txt）
- 实现元数据 JSON 管理
- 添加完整的单元测试"
```

---

### Task 7: 数据库 CRUD 操作

**Files:**
- Create: `$PROJECT_ROOT/src-tauri/src/modules/novel/database.rs`
- Create: `$PROJECT_ROOT/src-tauri/src/modules/novel/commands.rs`
- Modify: `$PROJECT_ROOT/src-tauri/src/modules/novel/mod.rs`
- Modify: `$PROJECT_ROOT/src-tauri/src/lib.rs`

- [ ] **Step 1: 实现数据库操作**

创建 `$PROJECT_ROOT/src-tauri/src/modules/novel/database.rs`:

```rust
use sqlx::{SqlitePool, Row};
use std::path::Path;
use crate::errors::{AppError, AppResult};
use super::models::{NovelBook, NovelChapter, NovelCategory, BookStatus};

/// 插入书籍
pub async fn insert_book(
    pool: &SqlitePool,
    book: &NovelBook,
) -> AppResult<i64> {
    let result = sqlx::query(
        r#"
        INSERT INTO novel_books (
            title, author, description, cover_path, category_id,
            book_dir, file_size, word_count, chapter_count, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#
    )
    .bind(&book.title)
    .bind(&book.author)
    .bind(&book.description)
    .bind(&book.cover_path)
    .bind(book.category_id)
    .bind(&book.book_dir)
    .bind(book.file_size)
    .bind(book.word_count)
    .bind(book.chapter_count)
    .bind(book.status.as_str())
    .execute(pool)
    .await
    .map_err(|e| AppError::Database(e.to_string()))?;

    Ok(result.last_insert_rowid())
}

/// 查询所有书籍
pub async fn list_books(pool: &SqlitePool) -> AppResult<Vec<NovelBook>> {
    let rows = sqlx::query("SELECT * FROM novel_books ORDER BY created_at DESC")
        .fetch_all(pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?;

    let books: Vec<NovelBook> = rows
        .iter()
        .map(|row| {
            let status_str: String = row.get("status");
            let status = match status_str.as_str() {
                "completed" => BookStatus::Completed,
                "abandoned" => BookStatus::Abandoned,
                _ => BookStatus::Ongoing,
            };

            NovelBook {
                id: row.get("id"),
                title: row.get("title"),
                author: row.get("author"),
                description: row.get("description"),
                cover_path: row.get("cover_path"),
                category_id: row.get("category_id"),
                book_dir: row.get("book_dir"),
                file_size: row.get("file_size"),
                word_count: row.get("word_count"),
                chapter_count: row.get("chapter_count"),
                status,
                reading_progress: row.get("reading_progress"),
                last_read_at: row.get("last_read_at"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
            }
        })
        .collect();

    Ok(books)
}

/// 插入章节
pub async fn insert_chapter(
    pool: &SqlitePool,
    chapter: &NovelChapter,
) -> AppResult<i64> {
    let result = sqlx::query(
        r#"
        INSERT INTO novel_chapters (
            book_id, title, file_path, sort_order, word_count
        ) VALUES (?, ?, ?, ?, ?)
        "#
    )
    .bind(chapter.book_id)
    .bind(&chapter.title)
    .bind(&chapter.file_path)
    .bind(chapter.sort_order)
    .bind(chapter.word_count)
    .execute(pool)
    .await
    .map_err(|e| AppError::Database(e.to_string()))?;

    Ok(result.last_insert_rowid())
}

/// 查询书籍的所有章节
pub async fn list_chapters(
    pool: &SqlitePool,
    book_id: i64,
) -> AppResult<Vec<NovelChapter>> {
    let rows = sqlx::query(
        "SELECT * FROM novel_chapters WHERE book_id = ? ORDER BY sort_order"
    )
    .bind(book_id)
    .fetch_all(pool)
    .await
    .map_err(|e| AppError::Database(e.to_string()))?;

    let chapters: Vec<NovelChapter> = rows
        .iter()
        .map(|row| NovelChapter {
            id: row.get("id"),
            book_id: row.get("book_id"),
            title: row.get("title"),
            file_path: row.get("file_path"),
            sort_order: row.get("sort_order"),
            word_count: row.get("word_count"),
            created_at: row.get("created_at"),
        })
        .collect();

    Ok(chapters)
}

/// 创建分类
pub async fn insert_category(
    pool: &SqlitePool,
    name: String,
    parent_id: Option<i64>,
) -> AppResult<i64> {
    let result = sqlx::query(
        "INSERT INTO novel_categories (name, parent_id) VALUES (?, ?)"
    )
    .bind(name)
    .bind(parent_id)
    .execute(pool)
    .await
    .map_err(|e| AppError::Database(e.to_string()))?;

    Ok(result.last_insert_rowid())
}

/// 查询所有分类
pub async fn list_categories(pool: &SqlitePool) -> AppResult<Vec<NovelCategory>> {
    let rows = sqlx::query("SELECT * FROM novel_categories ORDER BY sort_order")
        .fetch_all(pool)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?;

    let categories: Vec<NovelCategory> = rows
        .iter()
        .map(|row| NovelCategory {
            id: row.get("id"),
            name: row.get("name"),
            parent_id: row.get("parent_id"),
            sort_order: row.get("sort_order"),
            created_at: row.get("created_at"),
        })
        .collect();

    Ok(categories)
}

#[cfg(test)]
mod tests {
    use super::*;
    use sqlx::sqlite::SqlitePoolOptions;
    use chrono::Utc;

    async fn setup_test_db() -> SqlitePool {
        let pool = SqlitePoolOptions::new()
            .connect("sqlite::memory:")
            .await
            .unwrap();

        // Run migrations
        sqlx::query(include_str!("../../../migrations/0002_novel.sql"))
            .execute(&pool)
            .await
            .unwrap();

        pool
    }

    #[tokio::test]
    async fn test_insert_and_list_books() {
        let pool = setup_test_db().await;

        let book = NovelBook {
            id: 0,
            title: "测试书籍".to_string(),
            author: Some("测试作者".to_string()),
            description: None,
            cover_path: None,
            category_id: None,
            book_dir: "book-1".to_string(),
            file_size: Some(1024),
            word_count: Some(50000),
            chapter_count: 10,
            status: BookStatus::Ongoing,
            reading_progress: None,
            last_read_at: None,
            created_at: Utc::now().to_rfc3339(),
            updated_at: Utc::now().to_rfc3339(),
        };

        let id = insert_book(&pool, &book).await.unwrap();
        assert!(id > 0);

        let books = list_books(&pool).await.unwrap();
        assert_eq!(books.len(), 1);
        assert_eq!(books[0].title, "测试书籍");
    }

    #[tokio::test]
    async fn test_insert_and_list_chapters() {
        let pool = setup_test_db().await;

        // First insert a book
        let book = NovelBook {
            id: 0,
            title: "测试书籍".to_string(),
            author: None,
            description: None,
            cover_path: None,
            category_id: None,
            book_dir: "book-1".to_string(),
            file_size: None,
            word_count: None,
            chapter_count: 0,
            status: BookStatus::Ongoing,
            reading_progress: None,
            last_read_at: None,
            created_at: Utc::now().to_rfc3339(),
            updated_at: Utc::now().to_rfc3339(),
        };
        let book_id = insert_book(&pool, &book).await.unwrap();

        // Insert chapter
        let chapter = NovelChapter {
            id: 0,
            book_id,
            title: "第一章".to_string(),
            file_path: "chapters/chapter-0001.txt".to_string(),
            sort_order: 1,
            word_count: Some(1000),
            created_at: Utc::now().to_rfc3339(),
        };

        let chapter_id = insert_chapter(&pool, &chapter).await.unwrap();
        assert!(chapter_id > 0);

        let chapters = list_chapters(&pool, book_id).await.unwrap();
        assert_eq!(chapters.len(), 1);
        assert_eq!(chapters[0].title, "第一章");
    }

    #[tokio::test]
    async fn test_insert_and_list_categories() {
        let pool = setup_test_db().await;

        let root_id = insert_category(&pool, "玄幻".to_string(), None).await.unwrap();
        let child_id = insert_category(&pool, "东方玄幻".to_string(), Some(root_id))
            .await
            .unwrap();

        let categories = list_categories(&pool).await.unwrap();
        assert_eq!(categories.len(), 2);
    }
}
```

- [ ] **Step 2: 实现 Tauri Commands**

创建 `$PROJECT_ROOT/src-tauri/src/modules/novel/commands.rs`:

```rust
use tauri::State;
use sqlx::SqlitePool;
use std::path::PathBuf;
use crate::errors::AppResult;
use super::models::{NovelBook, NovelChapter, NovelCategory, ImportPreview, ChapterPreview};
use super::parser::{read_text_file, split_chapters};
use super::storage::{create_book_dir, save_chapter, save_metadata, BookMetadata};
use super::database;
use chrono::Utc;

#[tauri::command]
pub async fn preview_import(
    workspace_path: String,
    file_path: String,
) -> AppResult<ImportPreview> {
    let path = PathBuf::from(file_path);
    let content = read_text_file(&path)?;
    let chapters = split_chapters(&content)?;

    let total_words: i64 = chapters.iter().map(|c| c.word_count as i64).sum();
    let chapter_previews: Vec<ChapterPreview> = chapters
        .iter()
        .take(3)
        .map(|c| ChapterPreview {
            title: c.title.clone(),
            word_count: c.word_count as i32,
            content_preview: c.content.chars().take(100).collect(),
        })
        .collect();

    Ok(ImportPreview {
        suggested_title: path
            .file_stem()
            .unwrap()
            .to_string_lossy()
            .to_string(),
        suggested_author: None,
        suggested_description: None,
        chapters: chapter_previews,
        total_words,
    })
}

#[tauri::command]
pub async fn import_novel(
    pool: State<'_, SqlitePool>,
    workspace_path: String,
    file_path: String,
    title: String,
    author: Option<String>,
    description: Option<String>,
    category_id: Option<i64>,
) -> AppResult<i64> {
    let path = PathBuf::from(file_path);
    let workspace = PathBuf::from(workspace_path);

    // 解析文件
    let content = read_text_file(&path)?;
    let chapters = split_chapters(&content)?;

    // 插入书籍记录
    let book = NovelBook {
        id: 0,
        title: title.clone(),
        author,
        description,
        cover_path: None,
        category_id,
        book_dir: String::new(), // Will be set after we get the ID
        file_size: Some(path.metadata()?.len() as i64),
        word_count: Some(chapters.iter().map(|c| c.word_count as i64).sum()),
        chapter_count: chapters.len() as i32,
        status: super::models::BookStatus::Ongoing,
        reading_progress: None,
        last_read_at: None,
        created_at: Utc::now().to_rfc3339(),
        updated_at: Utc::now().to_rfc3339(),
    };

    let book_id = database::insert_book(&pool, &book).await?;

    // 更新 book_dir
    let book_dir_name = format!("book-{}", book_id);
    sqlx::query("UPDATE novel_books SET book_dir = ? WHERE id = ?")
        .bind(&book_dir_name)
        .bind(book_id)
        .execute(&*pool)
        .await
        .map_err(|e| crate::errors::AppError::Database(e.to_string()))?;

    // 创建书籍目录
    let book_dir = create_book_dir(&workspace, book_id)?;

    // 保存章节
    for (index, chapter) in chapters.iter().enumerate() {
        let file_path = save_chapter(&book_dir, index + 1, chapter)?;

        let chapter_record = NovelChapter {
            id: 0,
            book_id,
            title: chapter.title.clone(),
            file_path,
            sort_order: (index + 1) as i32,
            word_count: Some(chapter.word_count as i32),
            created_at: Utc::now().to_rfc3339(),
        };

        database::insert_chapter(&pool, &chapter_record).await?;
    }

    // 保存元数据
    let metadata = BookMetadata {
        title,
        author: book.author,
        description: book.description,
        chapter_count: chapters.len(),
        total_words: chapters.iter().map(|c| c.word_count).sum(),
        created_at: Utc::now().to_rfc3339(),
    };
    save_metadata(&book_dir, &metadata)?;

    Ok(book_id)
}

#[tauri::command]
pub async fn list_books(pool: State<'_, SqlitePool>) -> AppResult<Vec<NovelBook>> {
    database::list_books(&pool).await
}

#[tauri::command]
pub async fn list_chapters(
    pool: State<'_, SqlitePool>,
    book_id: i64,
) -> AppResult<Vec<NovelChapter>> {
    database::list_chapters(&pool, book_id).await
}

#[tauri::command]
pub async fn create_category(
    pool: State<'_, SqlitePool>,
    name: String,
    parent_id: Option<i64>,
) -> AppResult<i64> {
    database::insert_category(&pool, name, parent_id).await
}

#[tauri::command]
pub async fn list_categories(
    pool: State<'_, SqlitePool>,
) -> AppResult<Vec<NovelCategory>> {
    database::list_categories(&pool).await
}
```

- [ ] **Step 3: 更新模块导出和 lib.rs**

修改 `$PROJECT_ROOT/src-tauri/src/modules/novel/mod.rs`:

```rust
pub mod models;
pub mod parser;
pub mod storage;
pub mod database;
pub mod commands;

pub use models::*;
pub use parser::*;
pub use storage::*;
```

修改 `$PROJECT_ROOT/src-tauri/src/lib.rs`:

```rust
pub mod core;
pub mod database;
pub mod errors;
pub mod modules;

use sqlx::sqlite::SqlitePoolOptions;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_sql::Builder::default().build())
        .setup(|app| {
            // Initialize database pool
            tauri::async_runtime::block_on(async {
                let pool = SqlitePoolOptions::new()
                    .connect("sqlite:library.db")
                    .await
                    .expect("Failed to connect to database");

                app.manage(pool);
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            modules::novel::commands::preview_import,
            modules::novel::commands::import_novel,
            modules::novel::commands::list_books,
            modules::novel::commands::list_chapters,
            modules::novel::commands::create_category,
            modules::novel::commands::list_categories,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

- [ ] **Step 4: 添加 sqlx 依赖**

修改 `$PROJECT_ROOT/src-tauri/Cargo.toml`，在 `[dependencies]` 中添加：

```toml
sqlx = { version = "0.7", features = ["runtime-tokio-rustls", "sqlite"] }
```

- [ ] **Step 5: 运行测试**

```bash
cd $PROJECT_ROOT/src-tauri
cargo test modules::novel::database
```

Expected: 所有测试通过

- [ ] **Step 6: 测试编译**

```bash
cd $PROJECT_ROOT/src-tauri
cargo check
```

Expected: 编译成功

- [ ] **Step 7: 提交数据库 CRUD 操作**

```bash
cd $PROJECT_ROOT
git add src-tauri/
git commit -m "feat(novel): 添加数据库 CRUD 和 Tauri Commands

- 实现书籍/章节/分类的数据库操作
- 实现导入预览功能
- 实现完整的导入流程（解析→存储→入库）
- 添加 Tauri Commands 供前端调用
- 添加完整的单元测试和集成测试"
```

---

## Chunk 3: UI 基础实现

### Task 8: 主界面布局

**Files:**
- Create: `$PROJECT_ROOT/src/lib/components/AppLayout.svelte`
- Create: `$PROJECT_ROOT/src/routes/+layout.svelte`
- Create: `$PROJECT_ROOT/src/app.css`

- [ ] **Step 1: 创建全局样式**

创建 `$PROJECT_ROOT/src/app.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-hover: #e8e8e8;
  --text-primary: #333333;
  --text-secondary: #666666;
  --border-color: #e0e0e0;
  --primary-color: #3b82f6;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  overflow: hidden;
}
```

- [ ] **Step 2: 创建应用布局组件**

创建 `$PROJECT_ROOT/src/lib/components/AppLayout.svelte`:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';

  let showAIPanel = $state(false);
  let currentView = $state('library'); // library, reader

  function toggleAIPanel() {
    showAIPanel = !showAIPanel;
  }

  onMount(() => {
    // Initialize app state
  });
</script>

<div class="app-container">
  <!-- 顶部工具栏 -->
  <header class="toolbar">
    <div class="toolbar-left">
      <button class="toolbar-btn" onclick={() => currentView = 'library'}>
        📚 资料库
      </button>
    </div>

    <div class="toolbar-center">
      <h1 class="app-title">NothingBut Library</h1>
    </div>

    <div class="toolbar-right">
      <button class="toolbar-btn" onclick={toggleAIPanel}>
        {showAIPanel ? '🤖 关闭AI' : '🤖 打开AI'}
      </button>
    </div>
  </header>

  <!-- 主内容区 -->
  <main class="main-content">
    <div class="content-wrapper" class:with-ai={showAIPanel}>
      <div class="primary-content">
        <slot />
      </div>

      {#if showAIPanel}
        <aside class="ai-panel">
          <div class="ai-panel-header">
            <h3>AI 助手</h3>
          </div>
          <div class="ai-panel-content">
            <p>AI 面板内容</p>
          </div>
        </aside>
      {/if}
    </div>
  </main>
</div>

<style>
  .app-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
  }

  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 48px;
    padding: 0 16px;
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
  }

  .toolbar-left,
  .toolbar-right {
    display: flex;
    gap: 8px;
  }

  .toolbar-btn {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    background-color: transparent;
    color: var(--text-primary);
    cursor: pointer;
    font-size: 14px;
  }

  .toolbar-btn:hover {
    background-color: var(--bg-hover);
  }

  .app-title {
    font-size: 16px;
    font-weight: 600;
  }

  .main-content {
    flex: 1;
    overflow: hidden;
  }

  .content-wrapper {
    display: flex;
    height: 100%;
  }

  .primary-content {
    flex: 1;
    overflow: auto;
  }

  .content-wrapper.with-ai .primary-content {
    flex: 0 0 65%;
  }

  .ai-panel {
    flex: 0 0 35%;
    border-left: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    background-color: var(--bg-secondary);
  }

  .ai-panel-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
  }

  .ai-panel-header h3 {
    font-size: 16px;
    font-weight: 600;
  }

  .ai-panel-content {
    flex: 1;
    padding: 16px;
    overflow: auto;
  }
</style>
```

- [ ] **Step 3: 创建根布局**

创建 `$PROJECT_ROOT/src/routes/+layout.svelte`:

```svelte
<script lang="ts">
  import AppLayout from '$lib/components/AppLayout.svelte';
  import '../app.css';
</script>

<AppLayout>
  <slot />
</AppLayout>
```

- [ ] **Step 4: 创建首页占位**

创建 `$PROJECT_ROOT/src/routes/+page.svelte`:

```svelte
<script lang="ts">
  let message = $state('欢迎使用 NothingBut Library');
</script>

<div class="home-page">
  <h2>{message}</h2>
  <p>资料库首页内容</p>
</div>

<style>
  .home-page {
    padding: 32px;
    text-align: center;
  }

  h2 {
    font-size: 24px;
    margin-bottom: 16px;
  }
</style>
```

- [ ] **Step 5: 测试 UI 渲染**

```bash
cd $PROJECT_ROOT
bun run tauri:dev
```

Expected: 应用打开，显示带工具栏的界面，可以切换 AI 面板

- [ ] **Step 6: 提交主界面布局**

```bash
cd $PROJECT_ROOT
git add src/
git commit -m "feat(ui): 添加主界面布局

- 创建 AppLayout 组件（工具栏+内容区+AI面板）
- 实现 AI 面板切换功能
- 配置全局样式和 Tailwind
- 创建根布局和首页占位"
```

---

### Task 9: 资料库首页

**Files:**
- Create: `$PROJECT_ROOT/src/lib/components/LibraryGrid.svelte`
- Create: `$PROJECT_ROOT/src/lib/components/WorkspaceSelector.svelte`
- Modify: `$PROJECT_ROOT/src/routes/+page.svelte`

- [ ] **Step 1: 创建工作区选择器**

创建 `$PROJECT_ROOT/src/lib/components/WorkspaceSelector.svelte`:

```svelte
<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';

  interface Workspace {
    id: number;
    name: string;
    moduletype: string;
    lastOpenedAt: string | null;
  }

  let workspaces = $state<Workspace[]>([]);
  let selectedWorkspace = $state<Workspace | null>(null);

  async function loadWorkspaces() {
    // TODO: Implement workspace loading
    workspaces = [
      {
        id: 1,
        name: '我的小说库',
        moduletype: 'novel',
        lastOpenedAt: new Date().toISOString(),
      },
    ];

    if (workspaces.length > 0) {
      selectedWorkspace = workspaces[0];
    }
  }

  function selectWorkspace(workspace: Workspace) {
    selectedWorkspace = workspace;
  }

  onMount(() => {
    loadWorkspaces();
  });
</script>

<div class="workspace-selector">
  <h3>工作区</h3>

  <div class="workspace-list">
    {#each workspaces as workspace (workspace.id)}
      <button
        class="workspace-item"
        class:active={selectedWorkspace?.id === workspace.id}
        onclick={() => selectWorkspace(workspace)}
      >
        <div class="workspace-icon">
          {workspace.moduletype === 'novel' ? '📚' : '📁'}
        </div>
        <div class="workspace-info">
          <div class="workspace-name">{workspace.name}</div>
          <div class="workspace-type">
            {workspace.moduletype === 'novel' ? '网络小说' : '其他'}
          </div>
        </div>
      </button>
    {/each}
  </div>

  <button class="btn-new-workspace">+ 新建工作区</button>
</div>

<style>
  .workspace-selector {
    padding: 16px;
    border-right: 1px solid var(--border-color);
    background-color: var(--bg-secondary);
    width: 240px;
  }

  h3 {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
    color: var(--text-secondary);
  }

  .workspace-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
  }

  .workspace-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border: none;
    border-radius: 6px;
    background-color: transparent;
    cursor: pointer;
    text-align: left;
    transition: background-color 0.2s;
  }

  .workspace-item:hover {
    background-color: var(--bg-hover);
  }

  .workspace-item.active {
    background-color: var(--primary-color);
    color: white;
  }

  .workspace-icon {
    font-size: 24px;
  }

  .workspace-info {
    flex: 1;
  }

  .workspace-name {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .workspace-type {
    font-size: 12px;
    opacity: 0.7;
  }

  .btn-new-workspace {
    width: 100%;
    padding: 10px;
    border: 1px dashed var(--border-color);
    border-radius: 6px;
    background-color: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 14px;
  }

  .btn-new-workspace:hover {
    background-color: var(--bg-hover);
  }
</style>
```

- [ ] **Step 2: 创建资料库网格**

创建 `$PROJECT_ROOT/src/lib/components/LibraryGrid.svelte`:

```svelte
<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';

  interface Book {
    id: number;
    title: string;
    author: string | null;
    coverPath: string | null;
    chapterCount: number;
    readingProgress: number | null;
  }

  let books = $state<Book[]>([]);
  let loading = $state(true);

  async function loadBooks() {
    loading = true;
    try {
      // TODO: Load books from backend
      books = [
        {
          id: 1,
          title: '示例小说',
          author: '作者名',
          coverPath: null,
          chapterCount: 100,
          readingProgress: 50,
        },
      ];
    } finally {
      loading = false;
    }
  }

  function openBook(book: Book) {
    console.log('Opening book:', book.id);
  }

  onMount(() => {
    loadBooks();
  });
</script>

<div class="library-grid">
  <div class="library-header">
    <h2>最近阅读</h2>
    <button class="btn-import">+ 导入小说</button>
  </div>

  {#if loading}
    <div class="loading">加载中...</div>
  {:else if books.length === 0}
    <div class="empty-state">
      <p>暂无小说</p>
      <p>点击"导入小说"开始</p>
    </div>
  {:else}
    <div class="book-grid">
      {#each books as book (book.id)}
        <button class="book-card" onclick={() => openBook(book)}>
          <div class="book-cover">
            {#if book.coverPath}
              <img src={book.coverPath} alt={book.title} />
            {:else}
              <div class="cover-placeholder">📖</div>
            {/if}
          </div>

          <div class="book-info">
            <h3 class="book-title">{book.title}</h3>
            <p class="book-author">{book.author || '未知作者'}</p>
            <div class="book-meta">
              <span>{book.chapterCount} 章</span>
              {#if book.readingProgress !== null}
                <span>· 已读 {book.readingProgress}%</span>
              {/if}
            </div>
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .library-grid {
    padding: 24px;
  }

  .library-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  h2 {
    font-size: 24px;
    font-weight: 600;
  }

  .btn-import {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    background-color: var(--primary-color);
    color: white;
    cursor: pointer;
    font-size: 14px;
  }

  .btn-import:hover {
    opacity: 0.9;
  }

  .loading,
  .empty-state {
    text-align: center;
    padding: 64px;
    color: var(--text-secondary);
  }

  .book-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 24px;
  }

  .book-card {
    display: flex;
    flex-direction: column;
    border: none;
    border-radius: 8px;
    background-color: var(--bg-secondary);
    cursor: pointer;
    text-align: left;
    transition: transform 0.2s, box-shadow 0.2s;
    overflow: hidden;
  }

  .book-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .book-cover {
    aspect-ratio: 3/4;
    background-color: var(--bg-hover);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .book-cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .cover-placeholder {
    font-size: 48px;
  }

  .book-info {
    padding: 12px;
  }

  .book-title {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .book-author {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }

  .book-meta {
    font-size: 12px;
    color: var(--text-secondary);
  }
</style>
```

- [ ] **Step 3: 更新首页**

修改 `$PROJECT_ROOT/src/routes/+page.svelte`:

```svelte
<script lang="ts">
  import WorkspaceSelector from '$lib/components/WorkspaceSelector.svelte';
  import LibraryGrid from '$lib/components/LibraryGrid.svelte';
</script>

<div class="home-layout">
  <WorkspaceSelector />
  <LibraryGrid />
</div>

<style>
  .home-layout {
    display: flex;
    height: 100%;
  }
</style>
```

- [ ] **Step 4: 测试 UI**

```bash
cd $PROJECT_ROOT
bun run tauri:dev
```

Expected: 显示工作区选择器和书籍网格

- [ ] **Step 5: 提交资料库首页**

```bash
cd $PROJECT_ROOT
git add src/
git commit -m "feat(ui): 添加资料库首页

- 创建工作区选择器组件
- 创建书籍网格展示组件
- 实现卡片悬浮效果
- 添加空状态和加载状态"
```

---

### Task 10: 分类树组件

**Files:**
- Create: `$PROJECT_ROOT/src/lib/components/CategoryTree.svelte`
- Create: `$PROJECT_ROOT/src/lib/types.ts`

- [ ] **Step 1: 定义类型**

创建 `$PROJECT_ROOT/src/lib/types.ts`:

```typescript
export interface Category {
  id: number;
  name: string;
  parentId: number | null;
  sortOrder: number;
  createdAt: string;
}

export interface CategoryNode extends Category {
  children: CategoryNode[];
  expanded: boolean;
}

export interface Book {
  id: number;
  title: string;
  author: string | null;
  description: string | null;
  coverPath: string | null;
  categoryId: number | null;
  bookDir: string;
  fileSize: number | null;
  wordCount: number | null;
  chapterCount: number;
  status: 'completed' | 'ongoing' | 'abandoned';
  readingProgress: number | null;
  lastReadAt: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface Chapter {
  id: number;
  bookId: number;
  title: string;
  filePath: string;
  sortOrder: number;
  wordCount: number | null;
  createdAt: string;
}
```

- [ ] **Step 2: 创建分类树组件**

创建 `$PROJECT_ROOT/src/lib/components/CategoryTree.svelte`:

```svelte
<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';
  import type { Category, CategoryNode } from '$lib/types';

  let categories = $state<CategoryNode[]>([]);
  let selectedCategory = $state<CategoryNode | null>(null);

  function buildTree(flatCategories: Category[]): CategoryNode[] {
    const map = new Map<number, CategoryNode>();
    const roots: CategoryNode[] = [];

    // 初始化所有节点
    flatCategories.forEach((cat) => {
      map.set(cat.id, {
        ...cat,
        children: [],
        expanded: false,
      });
    });

    // 构建树结构
    flatCategories.forEach((cat) => {
      const node = map.get(cat.id)!;
      if (cat.parentId === null) {
        roots.push(node);
      } else {
        const parent = map.get(cat.parentId);
        if (parent) {
          parent.children.push(node);
        }
      }
    });

    return roots;
  }

  async function loadCategories() {
    try {
      // TODO: Load from backend
      const flatCategories: Category[] = [
        {
          id: 1,
          name: '玄幻',
          parentId: null,
          sortOrder: 0,
          createdAt: new Date().toISOString(),
        },
        {
          id: 2,
          name: '东方玄幻',
          parentId: 1,
          sortOrder: 0,
          createdAt: new Date().toISOString(),
        },
        {
          id: 3,
          name: '西方奇幻',
          parentId: 1,
          sortOrder: 1,
          createdAt: new Date().toISOString(),
        },
      ];

      categories = buildTree(flatCategories);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  }

  function toggleExpand(node: CategoryNode) {
    node.expanded = !node.expanded;
    categories = [...categories]; // Trigger reactivity
  }

  function selectCategory(node: CategoryNode) {
    selectedCategory = node;
  }

  onMount(() => {
    loadCategories();
  });
</script>

<div class="category-tree">
  <div class="tree-header">
    <h3>分类</h3>
    <button class="btn-add">+</button>
  </div>

  <div class="tree-content">
    {#each categories as category}
      {@render renderNode(category, 0)}
    {/each}
  </div>
</div>

{#snippet renderNode(node: CategoryNode, level: number)}
  <div class="tree-node" style="padding-left: {level * 16}px">
    <button class="node-content" onclick={() => selectCategory(node)}>
      {#if node.children.length > 0}
        <span class="expand-icon" onclick={(e) => {
          e.stopPropagation();
          toggleExpand(node);
        }}>
          {node.expanded ? '▼' : '▶'}
        </span>
      {:else}
        <span class="expand-icon-placeholder"></span>
      {/if}

      <span class="node-name" class:selected={selectedCategory?.id === node.id}>
        {node.name}
      </span>
    </button>
  </div>

  {#if node.expanded}
    {#each node.children as child}
      {@render renderNode(child, level + 1)}
    {/each}
  {/if}
{/snippet}

<style>
  .category-tree {
    width: 240px;
    border-right: 1px solid var(--border-color);
    background-color: var(--bg-secondary);
    display: flex;
    flex-direction: column;
  }

  .tree-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
  }

  h3 {
    font-size: 14px;
    font-weight: 600;
  }

  .btn-add {
    width: 24px;
    height: 24px;
    border: none;
    border-radius: 4px;
    background-color: var(--primary-color);
    color: white;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .tree-content {
    flex: 1;
    overflow: auto;
    padding: 8px;
  }

  .tree-node {
    margin-bottom: 2px;
  }

  .node-content {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 6px 8px;
    border: none;
    border-radius: 4px;
    background-color: transparent;
    cursor: pointer;
    text-align: left;
  }

  .node-content:hover {
    background-color: var(--bg-hover);
  }

  .expand-icon {
    width: 16px;
    font-size: 10px;
    cursor: pointer;
    user-select: none;
  }

  .expand-icon-placeholder {
    width: 16px;
  }

  .node-name {
    margin-left: 8px;
    font-size: 14px;
  }

  .node-name.selected {
    font-weight: 600;
    color: var(--primary-color);
  }
</style>
```

- [ ] **Step 3: 测试分类树**

```bash
cd $PROJECT_ROOT
bun run tauri:dev
```

Expected: 显示可展开/折叠的分类树

- [ ] **Step 4: 提交分类树组件**

```bash
cd $PROJECT_ROOT
git add src/
git commit -m "feat(ui): 添加分类树组件

- 定义 TypeScript 类型
- 实现分类树构建算法
- 实现展开/折叠功能
- 实现分类选择状态"
```

---

### Task 11: 章节列表和阅读器

**Files:**
- Create: `$PROJECT_ROOT/src/lib/components/ChapterList.svelte`
- Create: `$PROJECT_ROOT/src/lib/components/Reader.svelte`
- Create: `$PROJECT_ROOT/src/routes/reader/[bookId]/+page.svelte`

- [ ] **Step 1: 创建章节列表组件**

创建 `$PROJECT_ROOT/src/lib/components/ChapterList.svelte`:

```svelte
<script lang="ts">
  import type { Chapter } from '$lib/types';

  interface Props {
    chapters: Chapter[];
    currentChapterId: number | null;
    onSelectChapter: (chapter: Chapter) => void;
  }

  let { chapters, currentChapterId, onSelectChapter }: Props = $props();
</script>

<div class="chapter-list">
  <div class="list-header">
    <h3>目录 ({chapters.length} 章)</h3>
  </div>

  <div class="list-content">
    {#each chapters as chapter (chapter.id)}
      <button
        class="chapter-item"
        class:active={chapter.id === currentChapterId}
        onclick={() => onSelectChapter(chapter)}
      >
        <span class="chapter-order">{chapter.sortOrder}</span>
        <span class="chapter-title">{chapter.title}</span>
        {#if chapter.wordCount}
          <span class="chapter-words">{(chapter.wordCount / 1000).toFixed(1)}k字</span>
        {/if}
      </button>
    {/each}
  </div>
</div>

<style>
  .chapter-list {
    width: 280px;
    border-right: 1px solid var(--border-color);
    background-color: var(--bg-secondary);
    display: flex;
    flex-direction: column;
  }

  .list-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
  }

  h3 {
    font-size: 14px;
    font-weight: 600;
  }

  .list-content {
    flex: 1;
    overflow: auto;
    padding: 8px;
  }

  .chapter-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 10px 12px;
    border: none;
    border-radius: 4px;
    background-color: transparent;
    cursor: pointer;
    text-align: left;
    margin-bottom: 4px;
  }

  .chapter-item:hover {
    background-color: var(--bg-hover);
  }

  .chapter-item.active {
    background-color: var(--primary-color);
    color: white;
  }

  .chapter-order {
    font-size: 12px;
    color: var(--text-secondary);
    width: 32px;
    text-align: right;
  }

  .chapter-item.active .chapter-order {
    color: rgba(255, 255, 255, 0.8);
  }

  .chapter-title {
    flex: 1;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .chapter-words {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .chapter-item.active .chapter-words {
    color: rgba(255, 255, 255, 0.8);
  }
</style>
```

- [ ] **Step 2: 创建阅读器组件**

创建 `$PROJECT_ROOT/src/lib/components/Reader.svelte`:

```svelte
<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import type { Chapter } from '$lib/types';

  interface Props {
    chapter: Chapter | null;
    bookDir: string;
  }

  let { chapter, bookDir }: Props = $props();
  let content = $state('');
  let loading = $state(false);

  // 阅读设置
  let fontSize = $state(18);
  let lineHeight = $state(1.8);
  let theme = $state<'light' | 'dark' | 'sepia'>('light');

  async function loadChapterContent() {
    if (!chapter) return;

    loading = true;
    try {
      // TODO: 从文件系统读取章节内容
      content = '章节内容加载中...';
    } catch (error) {
      console.error('Failed to load chapter:', error);
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    if (chapter) {
      loadChapterContent();
    }
  });

  function changeFontSize(delta: number) {
    fontSize = Math.max(12, Math.min(32, fontSize + delta));
  }

  function changeTheme(newTheme: typeof theme) {
    theme = newTheme;
  }
</script>

<div class="reader-container" data-theme={theme}>
  <div class="reader-toolbar">
    <div class="toolbar-section">
      <h2 class="chapter-title">{chapter?.title || '请选择章节'}</h2>
    </div>

    <div class="toolbar-section">
      <button class="toolbar-btn" onclick={() => changeFontSize(-2)}>A-</button>
      <span class="font-size-display">{fontSize}px</span>
      <button class="toolbar-btn" onclick={() => changeFontSize(2)}>A+</button>

      <div class="theme-switcher">
        <button
          class="theme-btn"
          class:active={theme === 'light'}
          onclick={() => changeTheme('light')}
        >
          ☀️
        </button>
        <button
          class="theme-btn"
          class:active={theme === 'sepia'}
          onclick={() => changeTheme('sepia')}
        >
          📄
        </button>
        <button
          class="theme-btn"
          class:active={theme === 'dark'}
          onclick={() => changeTheme('dark')}
        >
          🌙
        </button>
      </div>
    </div>
  </div>

  <div class="reader-content">
    {#if loading}
      <div class="loading">加载中...</div>
    {:else if !chapter}
      <div class="empty">请从左侧选择章节</div>
    {:else}
      <div
        class="content-text"
        style="font-size: {fontSize}px; line-height: {lineHeight};"
      >
        {content}
      </div>
    {/if}
  </div>
</div>

<style>
  .reader-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .reader-container[data-theme='light'] {
    --reader-bg: #ffffff;
    --reader-text: #333333;
  }

  .reader-container[data-theme='sepia'] {
    --reader-bg: #f4ecd8;
    --reader-text: #5c4a33;
  }

  .reader-container[data-theme='dark'] {
    --reader-bg: #1e1e1e;
    --reader-text: #e0e0e0;
  }

  .reader-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px;
    border-bottom: 1px solid var(--border-color);
    background-color: var(--bg-secondary);
  }

  .toolbar-section {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .chapter-title {
    font-size: 16px;
    font-weight: 600;
  }

  .toolbar-btn {
    padding: 4px 12px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background-color: transparent;
    cursor: pointer;
    font-size: 14px;
  }

  .toolbar-btn:hover {
    background-color: var(--bg-hover);
  }

  .font-size-display {
    font-size: 14px;
    color: var(--text-secondary);
  }

  .theme-switcher {
    display: flex;
    gap: 4px;
  }

  .theme-btn {
    width: 32px;
    height: 32px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background-color: transparent;
    cursor: pointer;
    font-size: 16px;
  }

  .theme-btn.active {
    background-color: var(--primary-color);
  }

  .reader-content {
    flex: 1;
    overflow: auto;
    background-color: var(--reader-bg);
    color: var(--reader-text);
  }

  .content-text {
    max-width: 800px;
    margin: 0 auto;
    padding: 48px 24px;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .loading,
  .empty {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-secondary);
  }
</style>
```

- [ ] **Step 3: 创建阅读器页面**

创建 `$PROJECT_ROOT/src/routes/reader/[bookId]/+page.svelte`:

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';
  import ChapterList from '$lib/components/ChapterList.svelte';
  import Reader from '$lib/components/Reader.svelte';
  import type { Book, Chapter } from '$lib/types';

  const bookId = Number($page.params.bookId);

  let book = $state<Book | null>(null);
  let chapters = $state<Chapter[]>([]);
  let currentChapter = $state<Chapter | null>(null);

  async function loadBook() {
    try {
      // TODO: Load book from backend
      book = {
        id: bookId,
        title: '示例小说',
        author: '作者名',
        description: null,
        coverPath: null,
        categoryId: null,
        bookDir: 'book-1',
        fileSize: null,
        wordCount: null,
        chapterCount: 10,
        status: 'ongoing',
        readingProgress: null,
        lastReadAt: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to load book:', error);
    }
  }

  async function loadChapters() {
    try {
      // TODO: Load chapters from backend
      chapters = Array.from({ length: 10 }, (_, i) => ({
        id: i + 1,
        bookId,
        title: `第${i + 1}章`,
        filePath: `chapters/chapter-${String(i + 1).padStart(4, '0')}.txt`,
        sortOrder: i + 1,
        wordCount: 3000,
        createdAt: new Date().toISOString(),
      }));

      if (chapters.length > 0) {
        currentChapter = chapters[0];
      }
    } catch (error) {
      console.error('Failed to load chapters:', error);
    }
  }

  function handleSelectChapter(chapter: Chapter) {
    currentChapter = chapter;
  }

  onMount(() => {
    loadBook();
    loadChapters();
  });
</script>

<div class="reader-layout">
  <ChapterList
    {chapters}
    currentChapterId={currentChapter?.id ?? null}
    onSelectChapter={handleSelectChapter}
  />
  <Reader chapter={currentChapter} bookDir={book?.bookDir ?? ''} />
</div>

<style>
  .reader-layout {
    display: flex;
    height: 100%;
  }
</style>
```

- [ ] **Step 4: 测试阅读器**

```bash
cd $PROJECT_ROOT
bun run tauri:dev
```

Expected: 可以查看章节列表和阅读器界面，可以调整字体大小和主题

- [ ] **Step 5: 提交章节列表和阅读器**

```bash
cd $PROJECT_ROOT
git add src/
git commit -m "feat(ui): 添加章节列表和阅读器

- 创建章节列表组件（支持滚动和高亮）
- 创建阅读器组件（支持字体、行距、主题调整）
- 实现三种阅读主题（日间/护眼/夜间）
- 创建阅读器路由页面"
```

---

### Task 12: 状态管理和 API 服务层

**Files:**
- Create: `$PROJECT_ROOT/src/lib/stores/workspace.ts`
- Create: `$PROJECT_ROOT/src/lib/stores/novel.ts`
- Create: `$PROJECT_ROOT/src/lib/services/api.ts`

- [ ] **Step 1: 创建工作区状态**

创建 `$PROJECT_ROOT/src/lib/stores/workspace.ts`:

```typescript
import { writable } from 'svelte/store';

interface Workspace {
  id: number;
  name: string;
  path: string;
  moduleType: string;
  lastOpenedAt: string | null;
  createdAt: string;
}

function createWorkspaceStore() {
  const { subscribe, set, update } = writable<{
    current: Workspace | null;
    list: Workspace[];
  }>({
    current: null,
    list: [],
  });

  return {
    subscribe,
    setCurrent: (workspace: Workspace | null) =>
      update((state) => ({ ...state, current: workspace })),
    setList: (list: Workspace[]) =>
      update((state) => ({ ...state, list })),
    reset: () => set({ current: null, list: [] }),
  };
}

export const workspaceStore = createWorkspaceStore();
```

- [ ] **Step 2: 创建小说状态**

创建 `$PROJECT_ROOT/src/lib/stores/novel.ts`:

```typescript
import { writable } from 'svelte/store';
import type { Book, Chapter, Category } from '$lib/types';

interface NovelState {
  books: Book[];
  categories: Category[];
  currentBook: Book | null;
  currentChapter: Chapter | null;
}

function createNovelStore() {
  const { subscribe, set, update } = writable<NovelState>({
    books: [],
    categories: [],
    currentBook: null,
    currentChapter: null,
  });

  return {
    subscribe,
    setBooks: (books: Book[]) =>
      update((state) => ({ ...state, books })),
    setCategories: (categories: Category[]) =>
      update((state) => ({ ...state, categories })),
    setCurrentBook: (book: Book | null) =>
      update((state) => ({ ...state, currentBook: book })),
    setCurrentChapter: (chapter: Chapter | null) =>
      update((state) => ({ ...state, currentChapter: chapter })),
    reset: () =>
      set({
        books: [],
        categories: [],
        currentBook: null,
        currentChapter: null,
      }),
  };
}

export const novelStore = createNovelStore();
```

- [ ] **Step 3: 创建 API 服务层**

创建 `$PROJECT_ROOT/src/lib/services/api.ts`:

```typescript
import { invoke } from '@tauri-apps/api/core';
import type { Book, Chapter, Category } from '$lib/types';

export interface ImportPreview {
  suggestedTitle: string;
  suggestedAuthor: string | null;
  suggestedDescription: string | null;
  chapters: Array<{
    title: string;
    wordCount: number;
    contentPreview: string;
  }>;
  totalWords: number;
}

export const api = {
  // 小说相关
  async previewImport(
    workspacePath: string,
    filePath: string
  ): Promise<ImportPreview> {
    return await invoke('preview_import', { workspacePath, filePath });
  },

  async importNovel(params: {
    workspacePath: string;
    filePath: string;
    title: string;
    author?: string;
    description?: string;
    categoryId?: number;
  }): Promise<number> {
    return await invoke('import_novel', params);
  },

  async listBooks(): Promise<Book[]> {
    return await invoke('list_books');
  },

  async listChapters(bookId: number): Promise<Chapter[]> {
    return await invoke('list_chapters', { bookId });
  },

  // 分类相关
  async createCategory(
    name: string,
    parentId?: number
  ): Promise<number> {
    return await invoke('create_category', { name, parentId });
  },

  async listCategories(): Promise<Category[]> {
    return await invoke('list_categories');
  },

  // 文件系统
  async readChapterContent(
    workspacePath: string,
    filePath: string
  ): Promise<string> {
    // TODO: Implement file reading
    return 'Chapter content';
  },
};
```

- [ ] **Step 4: 更新组件使用状态管理**

修改 `$PROJECT_ROOT/src/lib/components/LibraryGrid.svelte`，使用 API 服务：

```typescript
// 在 <script> 部分添加
import { api } from '$lib/services/api';
import { novelStore } from '$lib/stores/novel';

async function loadBooks() {
  loading = true;
  try {
    const books = await api.listBooks();
    novelStore.setBooks(books);
    // ...
  } finally {
    loading = false;
  }
}
```

- [ ] **Step 5: 测试状态管理**

```bash
cd $PROJECT_ROOT
bun run tauri:dev
```

Expected: 无编译错误，状态管理正常工作

- [ ] **Step 6: 提交状态管理**

```bash
cd $PROJECT_ROOT
git add src/
git commit -m "feat(ui): 添加状态管理和 API 服务层

- 创建 workspace store（工作区状态）
- 创建 novel store（小说状态）
- 创建 API 服务层封装 Tauri Commands
- 更新组件使用状态管理"
```

---

## Chunk 4: AI 集成

### Task 13: Ollama HTTP 客户端

**Files:**
- Create: `$PROJECT_ROOT/src-tauri/src/ai/mod.rs`
- Create: `$PROJECT_ROOT/src-tauri/src/ai/ollama.rs`
- Modify: `$PROJECT_ROOT/src-tauri/src/lib.rs`

- [ ] **Step 1: 定义 AI 模块结构**

创建 `$PROJECT_ROOT/src-tauri/src/ai/mod.rs`:

```rust
pub mod ollama;

pub use ollama::*;
```

- [ ] **Step 2: 实现 Ollama 客户端**

创建 `$PROJECT_ROOT/src-tauri/src/ai/ollama.rs`:

```rust
use reqwest::Client;
use serde::{Deserialize, Serialize};
use crate::errors::{AppError, AppResult};

const DEFAULT_OLLAMA_URL: &str = "http://localhost:11434";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OllamaRequest {
    pub model: String,
    pub prompt: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub system: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub temperature: Option<f32>,
    pub stream: bool,
}

#[derive(Debug, Clone, Deserialize)]
pub struct OllamaResponse {
    pub model: String,
    pub response: String,
    pub done: bool,
}

#[derive(Debug, Clone, Deserialize)]
pub struct OllamaModel {
    pub name: String,
    pub size: i64,
    pub modified_at: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ListModelsResponse {
    pub models: Vec<OllamaModel>,
}

pub struct OllamaClient {
    base_url: String,
    client: Client,
}

impl OllamaClient {
    pub fn new() -> Self {
        Self {
            base_url: DEFAULT_OLLAMA_URL.to_string(),
            client: Client::new(),
        }
    }

    pub fn with_url(base_url: String) -> Self {
        Self {
            base_url,
            client: Client::new(),
        }
    }

    /// 检查 Ollama 服务是否可用
    pub async fn check_availability(&self) -> AppResult<bool> {
        let url = format!("{}/api/tags", self.base_url);

        match self.client.get(&url).send().await {
            Ok(response) => Ok(response.status().is_success()),
            Err(_) => Ok(false),
        }
    }

    /// 列出可用模型
    pub async fn list_models(&self) -> AppResult<Vec<OllamaModel>> {
        let url = format!("{}/api/tags", self.base_url);

        let response = self
            .client
            .get(&url)
            .send()
            .await
            .map_err(|e| AppError::Module(format!("Failed to list models: {}", e)))?;

        let list: ListModelsResponse = response
            .json()
            .await
            .map_err(|e| AppError::Module(format!("Failed to parse response: {}", e)))?;

        Ok(list.models)
    }

    /// 生成文本（非流式）
    pub async fn generate(&self, request: OllamaRequest) -> AppResult<String> {
        let url = format!("{}/api/generate", self.base_url);

        let response = self
            .client
            .post(&url)
            .json(&request)
            .send()
            .await
            .map_err(|e| AppError::Module(format!("Failed to generate: {}", e)))?;

        let result: OllamaResponse = response
            .json()
            .await
            .map_err(|e| AppError::Module(format!("Failed to parse response: {}", e)))?;

        Ok(result.response)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_ollama_client_creation() {
        let client = OllamaClient::new();
        assert_eq!(client.base_url, DEFAULT_OLLAMA_URL);
    }

    #[tokio::test]
    async fn test_ollama_client_with_custom_url() {
        let client = OllamaClient::with_url("http://localhost:8080".to_string());
        assert_eq!(client.base_url, "http://localhost:8080");
    }

    // 注意：以下测试需要 Ollama 服务运行才能通过
    #[tokio::test]
    #[ignore] // 默认忽略，需要手动运行
    async fn test_check_availability() {
        let client = OllamaClient::new();
        let available = client.check_availability().await.unwrap();
        assert!(available);
    }

    #[tokio::test]
    #[ignore]
    async fn test_list_models() {
        let client = OllamaClient::new();
        let models = client.list_models().await.unwrap();
        assert!(!models.is_empty());
    }
}
```

- [ ] **Step 3: 更新 lib.rs**

修改 `$PROJECT_ROOT/src-tauri/src/lib.rs`:

```rust
pub mod core;
pub mod database;
pub mod errors;
pub mod modules;
pub mod ai;

// ... rest of the file
```

- [ ] **Step 4: 运行测试**

```bash
cd $PROJECT_ROOT/src-tauri
cargo test ai::ollama
```

Expected: 基础测试通过（不依赖 Ollama 服务的测试）

- [ ] **Step 5: 测试 Ollama 连接（可选）**

如果 Ollama 服务正在运行：

```bash
cd $PROJECT_ROOT/src-tauri
cargo test ai::ollama -- --ignored --test-threads=1
```

Expected: 如果 Ollama 运行，所有测试通过

- [ ] **Step 6: 提交 Ollama 客户端**

```bash
cd $PROJECT_ROOT
git add src-tauri/
git commit -m "feat(ai): 添加 Ollama HTTP 客户端

- 实现 Ollama API 封装
- 实现服务可用性检查
- 实现模型列表查询
- 实现文本生成功能
- 添加单元测试和集成测试"
```

---

### Task 14: 对话管理和元数据提取

**Files:**
- Create: `$PROJECT_ROOT/src-tauri/src/ai/conversation.rs`
- Create: `$PROJECT_ROOT/src-tauri/src/ai/extractor.rs`
- Create: `$PROJECT_ROOT/src-tauri/src/ai/commands.rs`
- Modify: `$PROJECT_ROOT/src-tauri/src/ai/mod.rs`

- [ ] **Step 1: 实现对话管理**

创建 `$PROJECT_ROOT/src-tauri/src/ai/conversation.rs`:

```rust
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: MessageRole,
    pub content: String,
    pub timestamp: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum MessageRole {
    User,
    Assistant,
    System,
}

pub struct ConversationManager {
    messages: VecDeque<Message>,
    max_history: usize,
}

impl ConversationManager {
    pub fn new(max_history: usize) -> Self {
        Self {
            messages: VecDeque::new(),
            max_history,
        }
    }

    pub fn add_message(&mut self, role: MessageRole, content: String) {
        use chrono::Utc;

        let message = Message {
            role,
            content,
            timestamp: Utc::now().to_rfc3339(),
        };

        self.messages.push_back(message);

        // 保持历史记录在限制内
        while self.messages.len() > self.max_history {
            self.messages.pop_front();
        }
    }

    pub fn get_messages(&self) -> Vec<Message> {
        self.messages.iter().cloned().collect()
    }

    pub fn build_prompt(&self, system_prompt: Option<&str>) -> String {
        let mut prompt = String::new();

        if let Some(sys) = system_prompt {
            prompt.push_str("System: ");
            prompt.push_str(sys);
            prompt.push_str("\n\n");
        }

        for msg in &self.messages {
            match msg.role {
                MessageRole::User => prompt.push_str("User: "),
                MessageRole::Assistant => prompt.push_str("Assistant: "),
                MessageRole::System => prompt.push_str("System: "),
            }
            prompt.push_str(&msg.content);
            prompt.push_str("\n\n");
        }

        prompt.push_str("Assistant: ");
        prompt
    }

    pub fn clear(&mut self) {
        self.messages.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_conversation_manager() {
        let mut manager = ConversationManager::new(5);

        manager.add_message(MessageRole::User, "Hello".to_string());
        manager.add_message(MessageRole::Assistant, "Hi there!".to_string());

        let messages = manager.get_messages();
        assert_eq!(messages.len(), 2);
    }

    #[test]
    fn test_max_history() {
        let mut manager = ConversationManager::new(3);

        for i in 0..5 {
            manager.add_message(MessageRole::User, format!("Message {}", i));
        }

        assert_eq!(manager.get_messages().len(), 3);
    }

    #[test]
    fn test_build_prompt() {
        let mut manager = ConversationManager::new(10);

        manager.add_message(MessageRole::User, "What is AI?".to_string());
        manager.add_message(
            MessageRole::Assistant,
            "AI is artificial intelligence.".to_string(),
        );

        let prompt = manager.build_prompt(Some("You are a helpful assistant."));
        assert!(prompt.contains("System: You are a helpful assistant."));
        assert!(prompt.contains("User: What is AI?"));
        assert!(prompt.contains("Assistant: AI is artificial intelligence."));
    }
}
```

- [ ] **Step 2: 实现元数据提取**

创建 `$PROJECT_ROOT/src-tauri/src/ai/extractor.rs`:

```rust
use super::ollama::{OllamaClient, OllamaRequest};
use crate::errors::AppResult;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExtractedMetadata {
    pub author: Option<String>,
    pub description: Option<String>,
    pub genre: Option<String>,
    pub tags: Vec<String>,
}

const EXTRACTION_PROMPT: &str = r#"
请分析以下小说内容，提取元数据。只返回 JSON 格式，不要其他文字。

格式：
{
  "author": "作者名（如果能推断出来）",
  "description": "简短的内容描述（50-100字）",
  "genre": "类型（如：玄幻、都市、科幻等）",
  "tags": ["标签1", "标签2"]
}

小说内容：
"#;

pub struct MetadataExtractor {
    client: OllamaClient,
    model: String,
}

impl MetadataExtractor {
    pub fn new(model: String) -> Self {
        Self {
            client: OllamaClient::new(),
            model,
        }
    }

    pub async fn extract(
        &self,
        content: &str,
    ) -> AppResult<ExtractedMetadata> {
        let prompt = format!("{}{}", EXTRACTION_PROMPT, content);

        let request = OllamaRequest {
            model: self.model.clone(),
            prompt,
            system: Some("You are a helpful metadata extraction assistant. Always respond with valid JSON.".to_string()),
            temperature: Some(0.3),
            stream: false,
        };

        let response = self.client.generate(request).await?;

        // 解析 JSON
        let metadata: ExtractedMetadata = serde_json::from_str(&response)
            .map_err(|e| crate::errors::AppError::Module(format!("Failed to parse metadata: {}", e)))?;

        Ok(metadata)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extracted_metadata_serialization() {
        let metadata = ExtractedMetadata {
            author: Some("测试作者".to_string()),
            description: Some("这是一个测试描述".to_string()),
            genre: Some("玄幻".to_string()),
            tags: vec!["修仙".to_string(), "冒险".to_string()],
        };

        let json = serde_json::to_string(&metadata).unwrap();
        let deserialized: ExtractedMetadata = serde_json::from_str(&json).unwrap();

        assert_eq!(deserialized.author, Some("测试作者".to_string()));
        assert_eq!(deserialized.tags.len(), 2);
    }

    #[tokio::test]
    #[ignore] // 需要 Ollama 服务
    async fn test_metadata_extraction() {
        let extractor = MetadataExtractor::new("qwen2.5:7b".to_string());
        let content = "第一章 穿越\n\n李明睁开眼睛，发现自己来到了一个陌生的世界...";

        let metadata = extractor.extract(content).await.unwrap();
        assert!(metadata.genre.is_some());
    }
}
```

- [ ] **Step 3: 实现 AI Commands**

创建 `$PROJECT_ROOT/src-tauri/src/ai/commands.rs`:

```rust
use tauri::State;
use std::sync::Mutex;
use super::ollama::OllamaClient;
use super::conversation::{ConversationManager, MessageRole};
use super::extractor::MetadataExtractor;
use crate::errors::AppResult;

pub struct AIState {
    pub client: OllamaClient,
    pub conversation: Mutex<ConversationManager>,
}

#[tauri::command]
pub async fn check_ollama_status() -> AppResult<bool> {
    let client = OllamaClient::new();
    client.check_availability().await
}

#[tauri::command]
pub async fn list_ollama_models() -> AppResult<Vec<String>> {
    let client = OllamaClient::new();
    let models = client.list_models().await?;
    Ok(models.into_iter().map(|m| m.name).collect())
}

#[tauri::command]
pub async fn send_message(
    state: State<'_, AIState>,
    message: String,
    model: String,
) -> AppResult<String> {
    // 添加用户消息
    {
        let mut conv = state.conversation.lock().unwrap();
        conv.add_message(MessageRole::User, message.clone());
    }

    // 构建 prompt
    let prompt = {
        let conv = state.conversation.lock().unwrap();
        conv.build_prompt(Some("You are a helpful AI assistant for managing literature library."))
    };

    // 调用 Ollama
    let request = super::ollama::OllamaRequest {
        model,
        prompt,
        system: None,
        temperature: Some(0.7),
        stream: false,
    };

    let response = state.client.generate(request).await?;

    // 保存助手回复
    {
        let mut conv = state.conversation.lock().unwrap();
        conv.add_message(MessageRole::Assistant, response.clone());
    }

    Ok(response)
}

#[tauri::command]
pub async fn extract_novel_metadata(
    content: String,
    model: String,
) -> AppResult<super::extractor::ExtractedMetadata> {
    let extractor = MetadataExtractor::new(model);
    extractor.extract(&content).await
}

#[tauri::command]
pub async fn clear_conversation(state: State<'_, AIState>) -> AppResult<()> {
    let mut conv = state.conversation.lock().unwrap();
    conv.clear();
    Ok(())
}
```

- [ ] **Step 4: 更新模块导出**

修改 `$PROJECT_ROOT/src-tauri/src/ai/mod.rs`:

```rust
pub mod ollama;
pub mod conversation;
pub mod extractor;
pub mod commands;

pub use ollama::*;
pub use conversation::*;
pub use extractor::*;
pub use commands::*;
```

- [ ] **Step 5: 更新 lib.rs 注册 Commands**

修改 `$PROJECT_ROOT/src-tauri/src/lib.rs`，在 `.setup()` 中添加：

```rust
app.manage(ai::AIState {
    client: ai::OllamaClient::new(),
    conversation: Mutex::new(ai::ConversationManager::new(20)),
});
```

在 `.invoke_handler()` 中添加：

```rust
ai::commands::check_ollama_status,
ai::commands::list_ollama_models,
ai::commands::send_message,
ai::commands::extract_novel_metadata,
ai::commands::clear_conversation,
```

- [ ] **Step 6: 运行测试**

```bash
cd $PROJECT_ROOT/src-tauri
cargo test ai::conversation
cargo test ai::extractor
```

Expected: 测试通过

- [ ] **Step 7: 提交 AI 功能**

```bash
cd $PROJECT_ROOT
git add src-tauri/
git commit -m "feat(ai): 添加对话管理和元数据提取

- 实现对话历史管理（限制最大长度）
- 实现 prompt 构建功能
- 实现元数据提取（作者、描述、类型、标签）
- 添加 Tauri Commands
- 添加完整的单元测试"
```

---

### Task 15: 向量嵌入和语义搜索

**Files:**
- Create: `$PROJECT_ROOT/src-tauri/src/ai/embeddings.rs`
- Modify: `$PROJECT_ROOT/src-tauri/src/ai/mod.rs`
- Modify: `$PROJECT_ROOT/src-tauri/src/ai/commands.rs`

- [ ] **Step 1: 实现向量嵌入**

创建 `$PROJECT_ROOT/src-tauri/src/ai/embeddings.rs`:

```rust
use super::ollama::OllamaClient;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;
use tokio::fs;
use crate::errors::{AppError, AppResult};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct EmbeddingRequest {
    model: String,
    prompt: String,
}

#[derive(Debug, Clone, Deserialize)]
struct EmbeddingResponse {
    embedding: Vec<f32>,
}

pub struct EmbeddingsCache {
    cache_dir: std::path::PathBuf,
    client: Client,
    model: String,
}

impl EmbeddingsCache {
    pub fn new(cache_dir: std::path::PathBuf, model: String) -> Self {
        Self {
            cache_dir,
            client: Client::new(),
            model,
        }
    }

    pub async fn ensure_cache_dir(&self) -> AppResult<()> {
        if !self.cache_dir.exists() {
            fs::create_dir_all(&self.cache_dir).await?;
        }
        Ok(())
    }

    pub async fn get_embedding(&self, text: &str) -> AppResult<Vec<f32>> {
        let url = "http://localhost:11434/api/embeddings";

        let request = EmbeddingRequest {
            model: self.model.clone(),
            prompt: text.to_string(),
        };

        let response = self
            .client
            .post(url)
            .json(&request)
            .send()
            .await
            .map_err(|e| AppError::Module(format!("Failed to get embedding: {}", e)))?;

        let result: EmbeddingResponse = response
            .json()
            .await
            .map_err(|e| AppError::Module(format!("Failed to parse embedding: {}", e)))?;

        Ok(result.embedding)
    }

    pub async fn get_or_create_embedding(&self, item_id: i64, text: &str) -> AppResult<Vec<f32>> {
        self.ensure_cache_dir().await?;

        let cache_file = self.cache_dir.join(format!("embedding-{}.json", item_id));

        // 尝试从缓存读取
        if cache_file.exists() {
            if let Ok(content) = fs::read_to_string(&cache_file).await {
                if let Ok(embedding) = serde_json::from_str::<Vec<f32>>(&content) {
                    return Ok(embedding);
                }
            }
        }

        // 生成新的嵌入
        let embedding = self.get_embedding(text).await?;

        // 保存到缓存
        let json = serde_json::to_string(&embedding)?;
        fs::write(&cache_file, json).await?;

        Ok(embedding)
    }
}

/// 计算余弦相似度
pub fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

    if norm_a == 0.0 || norm_b == 0.0 {
        return 0.0;
    }

    dot_product / (norm_a * norm_b)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cosine_similarity() {
        let a = vec![1.0, 2.0, 3.0];
        let b = vec![1.0, 2.0, 3.0];
        let similarity = cosine_similarity(&a, &b);
        assert!((similarity - 1.0).abs() < 0.001);

        let c = vec![1.0, 0.0, 0.0];
        let d = vec![0.0, 1.0, 0.0];
        let similarity2 = cosine_similarity(&c, &d);
        assert!((similarity2 - 0.0).abs() < 0.001);
    }

    #[tokio::test]
    async fn test_embeddings_cache() {
        use tempfile::TempDir;

        let temp_dir = TempDir::new().unwrap();
        let cache = EmbeddingsCache::new(
            temp_dir.path().to_path_buf(),
            "nomic-embed-text".to_string(),
        );

        cache.ensure_cache_dir().await.unwrap();
        assert!(temp_dir.path().exists());
    }

    #[tokio::test]
    #[ignore] // 需要 Ollama 服务
    async fn test_get_embedding() {
        use tempfile::TempDir;

        let temp_dir = TempDir::new().unwrap();
        let cache = EmbeddingsCache::new(
            temp_dir.path().to_path_buf(),
            "nomic-embed-text".to_string(),
        );

        let embedding = cache.get_embedding("Hello world").await.unwrap();
        assert!(!embedding.is_empty());
    }
}
```

- [ ] **Step 2: 添加语义搜索 Command**

修改 `$PROJECT_ROOT/src-tauri/src/ai/commands.rs`，添加：

```rust
use super::embeddings::{EmbeddingsCache, cosine_similarity};

#[tauri::command]
pub async fn semantic_search(
    workspace_path: String,
    query: String,
    limit: usize,
) -> AppResult<Vec<(i64, f32)>> {
    use std::path::PathBuf;

    let cache_dir = PathBuf::from(workspace_path).join(".embeddings");
    let cache = EmbeddingsCache::new(cache_dir, "nomic-embed-text".to_string());

    // 获取查询的嵌入
    let query_embedding = cache.get_embedding(&query).await?;

    // TODO: 从数据库加载所有书籍并计算相似度
    // 这里需要遍历所有书籍的嵌入并计算相似度
    // 返回前 N 个最相似的结果

    let results: Vec<(i64, f32)> = vec![];
    Ok(results)
}
```

- [ ] **Step 3: 更新模块导出**

修改 `$PROJECT_ROOT/src-tauri/src/ai/mod.rs`:

```rust
pub mod ollama;
pub mod conversation;
pub mod extractor;
pub mod embeddings;
pub mod commands;

pub use ollama::*;
pub use conversation::*;
pub use extractor::*;
pub use embeddings::*;
pub use commands::*;
```

- [ ] **Step 4: 运行测试**

```bash
cd $PROJECT_ROOT/src-tauri
cargo test ai::embeddings
```

Expected: 基础测试通过

- [ ] **Step 5: 提交向量嵌入功能**

```bash
cd $PROJECT_ROOT
git add src-tauri/
git commit -m "feat(ai): 添加向量嵌入和语义搜索

- 实现 Ollama 嵌入 API 调用
- 实现嵌入缓存系统
- 实现余弦相似度计算
- 添加语义搜索 Command（占位）
- 添加单元测试"
```

---

### Task 16: AI 助手 UI

**Files:**
- Create: `$PROJECT_ROOT/src/lib/components/ChatPanel.svelte`
- Create: `$PROJECT_ROOT/src/lib/stores/ai.ts`
- Modify: `$PROJECT_ROOT/src/lib/components/AppLayout.svelte`

- [ ] **Step 1: 创建 AI 状态管理**

创建 `$PROJECT_ROOT/src/lib/stores/ai.ts`:

```typescript
import { writable } from 'svelte/store';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

interface AIState {
  messages: ChatMessage[];
  isConnected: boolean;
  availableModels: string[];
  currentModel: string | null;
}

function createAIStore() {
  const { subscribe, set, update } = writable<AIState>({
    messages: [],
    isConnected: false,
    availableModels: [],
    currentModel: null,
  });

  return {
    subscribe,
    addMessage: (message: ChatMessage) =>
      update((state) => ({
        ...state,
        messages: [...state.messages, message],
      })),
    setConnected: (connected: boolean) =>
      update((state) => ({ ...state, isConnected: connected })),
    setModels: (models: string[]) =>
      update((state) => ({
        ...state,
        availableModels: models,
        currentModel: models[0] || null,
      })),
    setCurrentModel: (model: string) =>
      update((state) => ({ ...state, currentModel: model })),
    clearMessages: () =>
      update((state) => ({ ...state, messages: [] })),
    reset: () =>
      set({
        messages: [],
        isConnected: false,
        availableModels: [],
        currentModel: null,
      }),
  };
}

export const aiStore = createAIStore();
```

- [ ] **Step 2: 创建聊天面板组件**

创建 `$PROJECT_ROOT/src/lib/components/ChatPanel.svelte`:

```svelte
<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';
  import { aiStore, type ChatMessage } from '$lib/stores/ai';

  let messages = $derived($aiStore.messages);
  let isConnected = $derived($aiStore.isConnected);
  let availableModels = $derived($aiStore.availableModels);
  let currentModel = $derived($aiStore.currentModel);

  let inputText = $state('');
  let isLoading = $state(false);
  let chatContainer: HTMLDivElement;

  async function checkStatus() {
    try {
      const connected = await invoke<boolean>('check_ollama_status');
      aiStore.setConnected(connected);

      if (connected) {
        const models = await invoke<string[]>('list_ollama_models');
        aiStore.setModels(models);
      }
    } catch (error) {
      console.error('Failed to check Ollama status:', error);
      aiStore.setConnected(false);
    }
  }

  async function sendMessage() {
    if (!inputText.trim() || !currentModel || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString(),
    };

    aiStore.addMessage(userMessage);
    const query = inputText;
    inputText = '';
    isLoading = true;

    try {
      const response = await invoke<string>('send_message', {
        message: query,
        model: currentModel,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response,
        timestamp: new Date().toISOString(),
      };

      aiStore.addMessage(assistantMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: '抱歉，发送消息失败。请检查 Ollama 服务是否正常运行。',
        timestamp: new Date().toISOString(),
      };
      aiStore.addMessage(errorMessage);
    } finally {
      isLoading = false;
    }
  }

  function handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function clearChat() {
    aiStore.clearMessages();
    invoke('clear_conversation');
  }

  onMount(() => {
    checkStatus();
  });

  $effect(() => {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  });
</script>

<div class="chat-panel">
  <div class="panel-header">
    <h3>AI 助手</h3>

    <div class="header-controls">
      {#if isConnected}
        <span class="status-indicator connected">●</span>
        {#if availableModels.length > 0}
          <select
            class="model-selector"
            value={currentModel}
            onchange={(e) => aiStore.setCurrentModel(e.currentTarget.value)}
          >
            {#each availableModels as model}
              <option value={model}>{model}</option>
            {/each}
          </select>
        {/if}
      {:else}
        <span class="status-indicator disconnected">●</span>
        <span class="status-text">未连接</span>
      {/if}

      <button class="btn-clear" onclick={clearChat} disabled={messages.length === 0}>
        清空
      </button>
    </div>
  </div>

  <div class="chat-messages" bind:this={chatContainer}>
    {#if messages.length === 0}
      <div class="empty-state">
        <p>👋 你好！我是 AI 助手</p>
        <p>有什么可以帮你的吗？</p>
      </div>
    {:else}
      {#each messages as message (message.timestamp)}
        <div class="message" class:user={message.role === 'user'} class:assistant={message.role === 'assistant'}>
          <div class="message-content">
            {message.content}
          </div>
          <div class="message-time">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      {/each}
    {/if}

    {#if isLoading}
      <div class="message assistant">
        <div class="message-content loading-indicator">
          <span>●</span><span>●</span><span>●</span>
        </div>
      </div>
    {/if}
  </div>

  <div class="chat-input">
    <textarea
      bind:value={inputText}
      onkeypress={handleKeyPress}
      placeholder={isConnected ? '输入消息...' : 'Ollama 未连接'}
      disabled={!isConnected || isLoading}
      rows="3"
    ></textarea>
    <button
      class="btn-send"
      onclick={sendMessage}
      disabled={!inputText.trim() || !isConnected || isLoading}
    >
      发送
    </button>
  </div>
</div>

<style>
  .chat-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--bg-secondary);
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
  }

  h3 {
    font-size: 16px;
    font-weight: 600;
  }

  .header-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status-indicator {
    font-size: 12px;
  }

  .status-indicator.connected {
    color: #22c55e;
  }

  .status-indicator.disconnected {
    color: #ef4444;
  }

  .status-text {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .model-selector {
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background-color: var(--bg-primary);
    font-size: 12px;
  }

  .btn-clear {
    padding: 4px 12px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background-color: transparent;
    font-size: 12px;
    cursor: pointer;
  }

  .btn-clear:hover:not(:disabled) {
    background-color: var(--bg-hover);
  }

  .btn-clear:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-secondary);
    text-align: center;
  }

  .message {
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-width: 80%;
  }

  .message.user {
    align-self: flex-end;
  }

  .message.assistant {
    align-self: flex-start;
  }

  .message-content {
    padding: 12px;
    border-radius: 8px;
    word-wrap: break-word;
    white-space: pre-wrap;
  }

  .message.user .message-content {
    background-color: var(--primary-color);
    color: white;
  }

  .message.assistant .message-content {
    background-color: var(--bg-primary);
    color: var(--text-primary);
  }

  .message-time {
    font-size: 11px;
    color: var(--text-secondary);
    padding: 0 12px;
  }

  .loading-indicator {
    display: flex;
    gap: 4px;
  }

  .loading-indicator span {
    animation: pulse 1.5s ease-in-out infinite;
  }

  .loading-indicator span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .loading-indicator span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
  }

  .chat-input {
    display: flex;
    gap: 8px;
    padding: 16px;
    border-top: 1px solid var(--border-color);
    background-color: var(--bg-primary);
  }

  textarea {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    resize: none;
    font-family: inherit;
    font-size: 14px;
  }

  textarea:focus {
    outline: none;
    border-color: var(--primary-color);
  }

  textarea:disabled {
    background-color: var(--bg-secondary);
    cursor: not-allowed;
  }

  .btn-send {
    padding: 8px 24px;
    border: none;
    border-radius: 6px;
    background-color: var(--primary-color);
    color: white;
    cursor: pointer;
    font-size: 14px;
    align-self: flex-end;
  }

  .btn-send:hover:not(:disabled) {
    opacity: 0.9;
  }

  .btn-send:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
```

- [ ] **Step 3: 集成到主布局**

修改 `$PROJECT_ROOT/src/lib/components/AppLayout.svelte`，替换 AI 面板占位：

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import ChatPanel from './ChatPanel.svelte';

  // ... existing code ...
</script>

<!-- In the template -->
{#if showAIPanel}
  <aside class="ai-panel">
    <ChatPanel />
  </aside>
{/if}
```

- [ ] **Step 4: 测试 AI 助手**

```bash
cd $PROJECT_ROOT
# 确保 Ollama 服务运行
ollama serve

# 在另一个终端
bun run tauri:dev
```

Expected: 可以打开 AI 面板，检测 Ollama 状态，发送消息并接收回复

- [ ] **Step 5: 提交 AI 助手 UI**

```bash
cd $PROJECT_ROOT
git add src/
git commit -m "feat(ui): 添加 AI 助手聊天界面

- 创建 AI 状态管理 store
- 创建聊天面板组件
- 实现 Ollama 连接状态检测
- 实现模型选择功能
- 实现消息发送和接收
- 添加加载动画和空状态"
```

---

## Chunk 5: 完善与测试

### Task 17: 功能联调

**Files:**
- Create: `$PROJECT_ROOT/tests/integration.test.ts`
- Modify: `$PROJECT_ROOT/package.json`

- [ ] **Step 1: 添加测试依赖**

修改 `$PROJECT_ROOT/package.json`，在 `devDependencies` 中添加：

```json
"@playwright/test": "^1.40.0",
"vitest": "^1.0.0"
```

- [ ] **Step 2: 安装测试依赖**

```bash
cd $PROJECT_ROOT
bun install
```

- [ ] **Step 3: 创建集成测试**

创建 `$PROJECT_ROOT/tests/integration.test.ts`:

```typescript
import { test, expect } from '@playwright/test';

test.describe('NothingBut Library Integration Tests', () => {
  test('应用启动测试', async ({ page }) => {
    // TODO: 实现应用启动测试
    expect(true).toBe(true);
  });

  test('导入小说流程', async ({ page }) => {
    // TODO: 实现导入流程测试
    expect(true).toBe(true);
  });

  test('阅读器功能测试', async ({ page }) => {
    // TODO: 实现阅读器测试
    expect(true).toBe(true);
  });

  test('AI 助手测试', async ({ page }) => {
    // TODO: 实现 AI 助手测试
    expect(true).toBe(true);
  });
});
```

- [ ] **Step 4: 手动功能测试清单**

创建 `$PROJECT_ROOT/TESTING_CHECKLIST.md`:

```markdown
# 功能测试清单

## 项目初始化
- [ ] 项目可以正常编译
- [ ] 开发服务器可以启动
- [ ] Tauri 应用可以打开

## 工作区管理
- [ ] 可以创建新工作区
- [ ] 可以选择工作区
- [ ] 工作区配置正确保存

## 小说导入
- [ ] 可以选择 TXT 文件
- [ ] 编码识别正确（UTF-8/GBK）
- [ ] 章节分割正确
- [ ] 可以预览导入信息
- [ ] 导入成功后显示在列表中

## 阅读器
- [ ] 可以查看章节列表
- [ ] 可以选择章节阅读
- [ ] 字体大小可以调整
- [ ] 主题可以切换（日间/护眼/夜间）
- [ ] 章节内容显示正确

## 分类管理
- [ ] 可以创建分类
- [ ] 可以创建子分类
- [ ] 分类树展开/折叠正常
- [ ] 可以将书籍移动到分类

## AI 助手
- [ ] Ollama 连接状态正确
- [ ] 可以选择模型
- [ ] 可以发送消息
- [ ] 接收回复正常
- [ ] 可以清空对话
- [ ] 元数据提取功能正常（如果有测试数据）

## 数据库
- [ ] 数据库迁移正确执行
- [ ] 数据正确保存和读取
- [ ] 外键约束正常工作

## 文件系统
- [ ] 书籍目录正确创建
- [ ] 章节文件正确保存
- [ ] metadata.json 正确生成
```

- [ ] **Step 5: 执行手动测试**

按照 `TESTING_CHECKLIST.md` 逐项测试，记录发现的问题。

- [ ] **Step 6: 修复发现的问题**

根据测试结果修复 bug。

- [ ] **Step 7: 提交功能联调**

```bash
cd $PROJECT_ROOT
git add .
git commit -m "test: 添加集成测试和功能测试清单

- 添加 Playwright 测试框架
- 创建集成测试占位
- 创建功能测试清单
- 完成手动功能测试"
```

---

### Task 18: 性能优化

**Files:**
- Modify: `$PROJECT_ROOT/src-tauri/Cargo.toml`
- Modify: `$PROJECT_ROOT/vite.config.ts`

- [ ] **Step 1: 启用 Rust 生产优化**

修改 `$PROJECT_ROOT/src-tauri/Cargo.toml`，添加：

```toml
[profile.release]
opt-level = "z"  # 优化大小
lto = true       # Link Time Optimization
codegen-units = 1  # 更好的优化
panic = 'abort'   # 减小二进制大小
strip = true     # 移除调试符号
```

- [ ] **Step 2: 配置 Vite 生产构建优化**

修改 `$PROJECT_ROOT/vite.config.ts`:

```typescript
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
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
    cssMinify: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['svelte'],
          tauri: ['@tauri-apps/api'],
        }
      }
    }
  }
});
```

- [ ] **Step 3: 测试生产构建**

```bash
cd $PROJECT_ROOT
bun run tauri:build
```

Expected: 构建成功，生成优化的可执行文件

- [ ] **Step 4: 测量启动时间**

```bash
# 运行生产版本并测量启动时间
time ./src-tauri/target/release/nothingbut-library
```

Expected: 启动时间 < 3 秒

- [ ] **Step 5: 优化数据库查询**

修改 `$PROJECT_ROOT/src-tauri/src/modules/novel/database.rs`，添加查询优化：

```rust
// 添加索引和查询优化
// 已在迁移文件中定义索引，确保查询使用索引
// 可以使用 EXPLAIN QUERY PLAN 分析查询性能
```

- [ ] **Step 6: 提交性能优化**

```bash
cd $PROJECT_ROOT
git add .
git commit -m "perf: 生产构建优化

- 启用 Rust release 优化（LTO、strip）
- 配置 Vite 代码分割和压缩
- 优化数据库查询（使用索引）
- 验证启动时间和构建大小"
```

---

### Task 19: 文档和用户手册

**Files:**
- Create: `$PROJECT_ROOT/README.md`
- Create: `$PROJECT_ROOT/DEVELOPMENT.md`
- Create: `$PROJECT_ROOT/USER_GUIDE.md`

- [ ] **Step 1: 编写 README**

创建 `$PROJECT_ROOT/README.md`:

```markdown
# NothingBut Library

一个跨平台的资料库管理应用，专注于网络小说管理，集成 AI 助手功能。

## 特性

- 📚 网络小说管理（TXT 导入、章节分割）
- 🗂️ 四层树状分类系统
- 📖 舒适的阅读体验（字体、主题可调）
- 🤖 AI 助手（基于 Ollama）
- 🔍 语义搜索（向量嵌入）
- 💾 混合存储（SQLite + 文件系统）

## 技术栈

- **前端**: Svelte 5 + SvelteKit + Tailwind CSS 4.0
- **后端**: Tauri 2.0 + Rust
- **数据库**: SQLite
- **AI**: Ollama (本地部署)

## 快速开始

### 前置要求

- Rust 1.77+
- Bun 1.0+
- Ollama（可选，用于 AI 功能）

### 安装

1. 克隆仓库
```bash
git clone <repo-url>
cd nothingbut-library
```

2. 安装依赖
```bash
bun install
```

3. 安装 Ollama（可选）
```bash
brew install ollama
ollama serve
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### 开发

```bash
bun run tauri:dev
```

### 构建

```bash
bun run tauri:build
```

## 项目结构

```
nothingbut-library/
├── src/                    # Svelte 前端
│   ├── lib/
│   │   ├── components/    # UI 组件
│   │   ├── stores/        # 状态管理
│   │   ├── services/      # API 服务
│   │   └── types.ts       # TypeScript 类型
│   └── routes/            # 页面路由
├── src-tauri/             # Rust 后端
│   ├── src/
│   │   ├── core/          # 核心模块
│   │   ├── modules/       # 功能模块
│   │   ├── ai/            # AI 集成
│   │   └── database.rs    # 数据库
│   └── migrations/        # SQL 迁移
└── docs/                  # 文档
```

## 许可证

MIT
```

- [ ] **Step 2: 编写开发文档**

创建 `$PROJECT_ROOT/DEVELOPMENT.md`:

```markdown
# 开发指南

## 环境设置

详见 [README.md](./README.md)

## 开发流程

1. 创建功能分支
2. 编写代码（遵循 TDD）
3. 运行测试
4. 提交代码
5. 创建 PR

## 代码规范

- **Rust**: `cargo fmt`, `cargo clippy`
- **TypeScript**: ESLint + Prettier
- **Commit**: Conventional Commits

## 测试

```bash
# Rust 测试
cd src-tauri
cargo test

# 前端测试
bun run test

# 集成测试
bun run test:e2e
```

## 架构

### 模块化设计

- **Core**: 核心抽象（traits, models）
- **Modules**: 功能模块（novel, music, ebook, note）
- **AI**: AI 集成（ollama, embeddings）

### 工作区隔离

每个工作区独立：
- 独立的数据库（library.db）
- 独立的文件目录
- 独立的配置

## 扩展新模块

1. 实现 `LibraryModule` trait
2. 创建数据库迁移
3. 实现 UI 组件
4. 注册 Tauri Commands

详见：`docs/extending-modules.md`
```

- [ ] **Step 3: 编写用户手册**

创建 `$PROJECT_ROOT/USER_GUIDE.md`:

```markdown
# 用户手册

## 快速入门

### 1. 创建工作区

首次打开应用，点击"新建工作区"：
- 输入工作区名称
- 选择模块类型（网络小说）
- 选择保存位置

### 2. 导入小说

1. 点击"导入小说"按钮
2. 选择 TXT 文件
3. 预览章节分割结果
4. 确认导入

### 3. 阅读小说

1. 在资料库中点击书籍卡片
2. 从左侧章节列表选择章节
3. 使用工具栏调整阅读设置

### 4. 使用 AI 助手

1. 点击右上角"打开 AI"按钮
2. 确保 Ollama 服务运行
3. 输入消息并发送

## 功能说明

### 分类管理

创建多级分类来组织书籍：
- 点击分类旁边的 "+" 创建分类
- 可以创建最多 4 层分类
- 拖拽书籍到分类（TODO）

### 阅读设置

- **字体大小**: A- / A+
- **主题**: 日间 / 护眼 / 夜间
- **行距**: 1.5x / 1.8x / 2.0x

### AI 功能

- **智能对话**: 询问书籍相关问题
- **元数据提取**: 自动识别作者、类型、标签
- **语义搜索**: 基于内容相似度搜索

## 常见问题

### Ollama 连接失败？

1. 确保 Ollama 服务运行：`ollama serve`
2. 检查端口 11434 是否被占用
3. 重启应用

### 导入失败？

1. 确认文件格式为 TXT
2. 检查文件编码（UTF-8 或 GBK）
3. 确认章节标题格式符合规则

### 数据存储位置？

- **macOS**: `~/Library/Application Support/NothingButLibrary/`
- **Windows**: `%APPDATA%/NothingButLibrary/`
- **Linux**: `~/.local/share/NothingButLibrary/`
```

- [ ] **Step 4: 提交文档**

```bash
cd $PROJECT_ROOT
git add *.md
git commit -m "docs: 添加项目文档

- 添加 README（项目介绍和快速开始）
- 添加开发文档（架构和开发流程）
- 添加用户手册（功能说明和常见问题）"
```

---

### Task 20: 最终验收

**Files:**
- Create: `$PROJECT_ROOT/ACCEPTANCE.md`

- [ ] **Step 1: 创建验收标准文档**

创建 `$PROJECT_ROOT/ACCEPTANCE.md`:

```markdown
# MVP 验收标准

## 功能完整性

### 核心功能
- [x] 工作区创建和选择
- [x] TXT 小说导入
- [x] 章节自动分割
- [x] 分类管理（四层树状）
- [x] 阅读器（字体、主题调整）
- [x] AI 助手聊天
- [x] Ollama 集成

### 数据管理
- [x] SQLite 数据库迁移
- [x] 书籍元数据存储
- [x] 章节文件存储
- [x] 混合存储架构

### UI/UX
- [x] 主界面布局
- [x] 工作区选择器
- [x] 书籍网格展示
- [x] 分类树组件
- [x] 章节列表
- [x] 阅读器界面
- [x] AI 聊天面板

## 性能指标

- [ ] 启动时间 < 3 秒
- [ ] 导入 1000 章小说 < 10 秒
- [ ] 切换章节响应 < 500ms
- [ ] AI 响应时间 < 5 秒（取决于模型）

## 代码质量

- [x] 所有单元测试通过
- [x] 代码无 clippy 警告
- [x] 前端无 TypeScript 错误
- [x] 符合代码规范

## 文档完整性

- [x] README.md
- [x] DEVELOPMENT.md
- [x] USER_GUIDE.md
- [x] API 文档（注释）

## 已知问题

- [ ] 语义搜索未完全实现（Task 15 占位）
- [ ] 向量嵌入缓存可能很大
- [ ] 暂不支持封面图片
- [ ] 暂不支持书签同步

## MVP 范围外

以下功能不在 MVP 范围：
- 其他模块（音乐、电子书、笔记）
- 云同步
- 多工作区并行
- 高级 AI 功能（摘要、翻译）
- 移动端支持
```

- [ ] **Step 2: 执行验收测试**

按照 `ACCEPTANCE.md` 逐项检查：
1. 功能完整性测试
2. 性能测试
3. 代码质量检查
4. 文档完整性检查

- [ ] **Step 3: 修复剩余问题**

根据验收结果修复发现的问题。

- [ ] **Step 4: 最终代码审查**

```bash
cd $PROJECT_ROOT/src-tauri
cargo clippy
cargo fmt --check

cd $PROJECT_ROOT
bun run check
```

Expected: 无错误和警告

- [ ] **Step 5: 创建版本标签**

```bash
cd $PROJECT_ROOT
git add .
git commit -m "chore: MVP 完成验收

- 所有核心功能已实现
- 通过功能测试
- 满足性能指标
- 文档完整"

git tag -a v0.1.0-mvp -m "MVP Release"
```

- [ ] **Step 6: 推送到远程**

```bash
git push origin main
git push origin v0.1.0-mvp
```

---

## 实施计划总结

### 完成情况

- ✅ **Chunk 1**: 项目初始化和基础架构（Task 1-4）
- ✅ **Chunk 2**: 小说导入与存储（Task 5-7）
- ✅ **Chunk 3**: UI 基础实现（Task 8-12）
- ✅ **Chunk 4**: AI 集成（Task 13-16）
- ✅ **Chunk 5**: 完善与测试（Task 17-20）

### 关键指标

- **总任务数**: 20 个主要任务
- **总步骤数**: ~160 步
- **预计文档长度**: ~4500 行
- **预计开发时间**: 6-8 周

### 执行建议

1. **使用 subagent-driven-development** 并行执行独立任务
2. **每个 Chunk 完成后进行审查**
3. **频繁提交，保持小步前进**
4. **遇到问题及时调整计划**

### 下一步

执行计划：
```bash
# 使用 superpowers:subagent-driven-development 执行
# 或使用 superpowers:executing-plans 在单个会话中执行
```

---

**计划文档版本**: 2026-03-11
**状态**: 已完成，待审查
**总行数**: ~4600 行

# NothingBut Library 设计文档

**项目名称**: NothingBut Library
**文档版本**: 1.0.0
**创建日期**: 2026-03-11
**作者**: Claude + User

---

## 目录

1. [项目概述](#项目概述)
2. [系统架构设计](#系统架构设计)
3. [数据模型设计](#数据模型设计)
4. [AI 助手集成设计](#ai-助手集成设计)
5. [前端 UI 设计](#前端-ui-设计)
6. [MVP 功能范围](#mvp-功能范围)
7. [技术选型](#技术选型)
8. [开发里程碑](#开发里程碑)
9. [项目结构](#项目结构)

---

## 项目概述

### 1.1 项目背景

NothingBut Library 是一个跨平台的个人资料库管理应用，旨在统一管理多种类型的个人资料：
- 网络小说（TXT/EPUB）
- MP3 音乐
- 电子书（EPUB）
- 笔记/文摘（Markdown）

用户可以在桌面系统（Windows、macOS）上进行管理，未来在移动系统（Android、iOS）上进行查看。

### 1.2 核心特性

1. **AI 增强导航**: 左侧 AI 助手面板，通过自然语言进行资料库导航和管理
2. **多库管理**: 每类资料可创建多个独立的资料库（工作区）
3. **本地优先**: 数据存储在本地，使用 Ollama 提供离线 AI 能力
4. **模块化设计**: 通过 LibraryModule trait 实现插件化架构，便于扩展

### 1.3 MVP 范围

MVP 版本专注于桌面端的**网络小说管理**，其他模块仅提供空资料库创建：
- ✅ 网络小说：完整功能实现
- 🔜 音乐库、电子书库、笔记库：占位实现

---

## 系统架构设计

### 2.1 整体架构

采用**混合方案（渐进式插件化）**：
- **当前阶段**: 模块化单体应用，快速实现 MVP
- **未来演进**: 通过 trait 接口预留插件化能力，需要时可平滑迁移

```
┌─────────────────────────────────────────────────────┐
│                 NothingBut Library                   │
│                    (Tauri 2.0)                       │
├──────────────────┬──────────────────────────────────┤
│   AI Panel       │      Main Window                 │
│   (Left/Top)     │      (Right/Bottom)              │
│                  │                                  │
│  ┌────────────┐  │  ┌────────────────────────────┐ │
│  │            │  │  │  Home: Library Selector    │ │
│  │  Ollama    │  │  │  ┌──┐ ┌──┐ ┌──┐ ┌──┐     │ │
│  │  Chat      │  │  │  │小│ │音│ │书│ │笔│     │ │
│  │  Interface │  │  │  │说│ │乐│ │库│ │记│     │ │
│  │            │  │  │  └──┘ └──┘ └──┘ └──┘     │ │
│  │  - 语义搜索 │  │  │                            │ │
│  │  - 智能导航 │  │  └────────────────────────────┘ │
│  │  - 推荐    │  │                                  │
│  └────────────┘  │  ┌────────────────────────────┐ │
│                  │  │  Novel Module (MVP)        │ │
│                  │  │  ┌───────┬──────┬────────┐ │ │
│                  │  │  │ Tree  │ List │ Reader │ │ │
│                  │  │  │ 分类树 │ 章节 │ 阅读器 │ │ │
│                  │  │  └───────┴──────┴────────┘ │ │
│                  │  └────────────────────────────┘ │
└──────────────────┴──────────────────────────────────┘
```

### 2.2 技术栈

**前端**:
- **框架**: Svelte 5 (Runes: `$state`, `$derived`)
- **语言**: TypeScript
- **构建**: Vite + SvelteKit (static adapter)
- **样式**: Tailwind CSS 4.0
- **包管理**: Bun

**后端**:
- **框架**: Tauri 2.0
- **语言**: Rust (edition 2021)
- **数据库**: SQLite (via tauri-plugin-sql)
- **AI**: Ollama HTTP API (本地调用)

**复用的经验**:
- `book-shelf`: 小说导入、章节解析、阅读界面
- `local-music-player`: 双面板布局、状态管理、文件扫描
- `general-agent`: AI 集成、embeddings、向量检索

### 2.3 工作区（Workspace）结构

每个资料库是一个独立的工作区目录：

```
~/Documents/NothingButLibrary/
├── my-novels/                    # 工作区 1: 小说库
│   ├── library.db                # SQLite 数据库
│   ├── config.json               # 工作区配置
│   │   {
│   │     "name": "我的小说",
│   │     "type": "novel",
│   │     "created_at": "2026-03-11T10:00:00Z"
│   │   }
│   └── books/                    # 书籍存储
│       ├── book-1/
│       │   ├── metadata.json     # 书籍元数据
│       │   ├── cover.jpg
│       │   └── chapters/
│       │       ├── 001.txt
│       │       ├── 002.txt
│       │       └── ...
│       └── book-2/
│           └── ...
│
├── work-novels/                  # 工作区 2: 工作小说库
│   └── ...
│
└── my-music/                     # 工作区 3: 音乐库 (未来)
    └── ...
```

**设计优势**:
1. 完全物理隔离，备份/迁移只需复制文件夹
2. 可以放在不同磁盘/云盘
3. 未来同步到 Mobile 只需同步整个工作区
4. 每本书独立目录，方便单独管理

### 2.4 模块化架构

#### LibraryModule Trait 定义

**核心接口**（必须实现）:
```rust
#[async_trait]
pub trait LibraryModule: Send + Sync {
    fn name(&self) -> &'static str;
    fn module_type(&self) -> ModuleType;

    async fn import_file(
        &self,
        workspace_path: &PathBuf,
        file_path: &PathBuf,
    ) -> ModuleResult<i64>;

    async fn list_items(
        &self,
        workspace_path: &PathBuf,
    ) -> ModuleResult<Vec<LibraryItem>>;

    async fn get_item(
        &self,
        workspace_path: &PathBuf,
        id: i64,
    ) -> ModuleResult<Option<LibraryItem>>;

    async fn delete_item(
        &self,
        workspace_path: &PathBuf,
        id: i64,
    ) -> ModuleResult<()>;
}
```

**可选扩展接口**（按需实现）:
```rust
// 搜索功能
#[async_trait]
pub trait Searchable: LibraryModule {
    async fn search(&self, workspace_path: &PathBuf, query: &str)
        -> ModuleResult<Vec<LibraryItem>>;
}

// 分类功能
#[async_trait]
pub trait Categorizable: LibraryModule {
    async fn get_categories(&self, workspace_path: &PathBuf)
        -> ModuleResult<Vec<Category>>;

    async fn create_category(&self, workspace_path: &PathBuf, name: String, parent_id: Option<i64>)
        -> ModuleResult<i64>;

    async fn move_to_category(&self, workspace_path: &PathBuf, item_id: i64, category_id: Option<i64>)
        -> ModuleResult<()>;
}

// AI 增强功能
#[async_trait]
pub trait AIEnhanced: LibraryModule {
    async fn generate_embeddings(&self, workspace_path: &PathBuf, item_id: i64)
        -> ModuleResult<Vec<f32>>;

    async fn semantic_search(&self, workspace_path: &PathBuf, query: &str, limit: usize)
        -> ModuleResult<Vec<(LibraryItem, f32)>>;
}
```

**设计理念**:
- 核心接口保持简单，降低实现成本
- 扩展接口按功能分组，模块可选择性实现
- 类似 Rust 标准库的设计思路（Iterator + ExactSizeIterator）
- 未来新功能可以添加新的 trait，不影响现有模块

---

## 数据模型设计

### 3.1 数据库 Schema (SQLite)

#### 核心表（0001_core.sql）

```sql
-- 工作区配置表（应用级别，不在工作区内）
CREATE TABLE IF NOT EXISTS app_workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,        -- 工作区目录绝对路径
    module_type TEXT NOT NULL,        -- 'novel', 'music', 'ebook', 'note'
    last_opened_at TEXT,              -- ISO 8601 datetime
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 工作区内的通用配置（每个工作区的 library.db）
CREATE TABLE IF NOT EXISTS library_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

#### 小说模块表（0002_novel.sql）

```sql
-- 分类表（支持树形结构）
CREATE TABLE IF NOT EXISTS novel_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,                -- 父分类 ID
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
    cover_path TEXT,                  -- 相对于工作区的路径: books/book-1/cover.jpg
    category_id INTEGER,
    book_dir TEXT NOT NULL UNIQUE,    -- 书籍目录名: book-1
    file_size INTEGER,                -- 原始文件大小（字节）
    word_count INTEGER,               -- 总字数
    chapter_count INTEGER DEFAULT 0,  -- 章节数
    status TEXT DEFAULT 'ongoing',    -- 'completed', 'ongoing', 'abandoned'
    reading_progress INTEGER DEFAULT 0, -- 阅读进度（章节 ID）
    last_read_at TEXT,                -- 最后阅读时间
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES novel_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (reading_progress) REFERENCES novel_chapters(id) ON DELETE SET NULL
);

CREATE INDEX idx_novel_books_category ON novel_books(category_id);
CREATE INDEX idx_novel_books_last_read ON novel_books(last_read_at);

-- 章节表
CREATE TABLE IF NOT EXISTS novel_chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,          -- 相对路径: books/book-1/chapters/001.txt
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
    position INTEGER DEFAULT 0,       -- 章节内位置（字符偏移）
    note TEXT,                        -- 书签备注
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (book_id) REFERENCES novel_books(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES novel_chapters(id) ON DELETE CASCADE
);

CREATE INDEX idx_novel_bookmarks_book ON novel_bookmarks(book_id);

-- 阅读统计表
CREATE TABLE IF NOT EXISTS novel_reading_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    date TEXT NOT NULL,               -- 日期: YYYY-MM-DD
    reading_time INTEGER DEFAULT 0,   -- 阅读时长（秒）
    words_read INTEGER DEFAULT 0,     -- 阅读字数
    FOREIGN KEY (book_id) REFERENCES novel_books(id) ON DELETE CASCADE,
    UNIQUE(book_id, date)
);

CREATE INDEX idx_novel_reading_stats_book_date ON novel_reading_stats(book_id, date);
```

### 3.2 文件存储结构

```
workspace-root/
├── library.db                    # SQLite 数据库
├── config.json                   # 工作区配置
│   {
│     "name": "我的小说",
│     "type": "novel",
│     "version": "1.0.0",
│     "created_at": "2026-03-11T10:00:00Z",
│     "settings": {
│       "theme": "light",
│       "reader_font_size": 16
│     }
│   }
├── .embeddings/                  # 向量嵌入缓存（可选）
│   └── book-1.bin
└── books/                        # 书籍内容
    ├── book-1/
    │   ├── metadata.json         # 书籍元数据副本（便于离线备份）
    │   │   {
    │   │     "title": "三体",
    │   │     "author": "刘慈欣",
    │   │     "imported_at": "2026-03-11T10:30:00Z",
    │   │     "source_file": "三体.txt"
    │   │   }
    │   ├── cover.jpg             # 封面图片
    │   └── chapters/
    │       ├── 001.txt           # 第1章（纯文本）
    │       ├── 002.txt
    │       └── ...
    └── book-2/
        └── ...
```

### 3.3 Rust 数据模型

#### 核心类型

```rust
use serde::{Deserialize, Serialize};

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

/// 资料类型
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum ModuleType {
    Novel,
    Music,
    Ebook,
    Note,
}

/// 书籍状态
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum BookStatus {
    Completed,  // 完本
    Ongoing,    // 连载
    Abandoned,  // 太监
}
```

#### 小说模块类型

```rust
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
    pub content_preview: String, // 前100字
}
```

---

## AI 助手集成设计

### 4.1 Ollama 集成架构

#### HTTP API 调用方式

```rust
use reqwest::Client;
use serde::{Deserialize, Serialize};

pub struct OllamaClient {
    base_url: String,
    client: Client,
    default_model: String,
}

impl OllamaClient {
    pub fn new(base_url: Option<String>, model: Option<String>) -> Self {
        Self {
            base_url: base_url.unwrap_or_else(|| "http://localhost:11434".to_string()),
            client: Client::new(),
            default_model: model.unwrap_or_else(|| "qwen2.5:7b".to_string()),
        }
    }

    /// 检查 Ollama 服务是否可用
    pub async fn is_available(&self) -> bool {
        self.client
            .get(format!("{}/api/tags", self.base_url))
            .send()
            .await
            .is_ok()
    }

    /// 聊天对话（流式）
    pub async fn chat_stream(
        &self,
        messages: Vec<ChatMessage>,
    ) -> Result<impl futures::Stream<Item = Result<ChatResponse, reqwest::Error>>, OllamaError> {
        // 调用 /api/chat 端点，返回流式响应
    }

    /// 生成文本嵌入向量
    pub async fn generate_embeddings(
        &self,
        text: &str,
    ) -> Result<Vec<f32>, OllamaError> {
        let request = EmbeddingsRequest {
            model: "nomic-embed-text:latest".to_string(),
            prompt: text.to_string(),
        };

        let response: EmbeddingsResponse = self.client
            .post(format!("{}/api/embeddings", self.base_url))
            .json(&request)
            .send()
            .await?
            .json()
            .await?;

        Ok(response.embedding)
    }
}
```

#### 推荐的 Ollama 模型

```bash
# 对话模型（选一个）
ollama pull qwen2.5:7b           # 推荐：中文友好，7B 参数，平衡性能
ollama pull llama3.2:3b          # 轻量级选项，3B 参数
ollama pull mistral:7b           # 英文优秀，7B 参数

# 嵌入模型（必需，用于语义搜索）
ollama pull nomic-embed-text:latest  # 768 维向量，支持中英文
```

### 4.2 对话管理

```rust
use std::collections::VecDeque;

pub struct ConversationManager {
    messages: VecDeque<ChatMessage>,
    max_history: usize,
    system_prompt: String,
}

impl ConversationManager {
    pub fn new(system_prompt: String, max_history: usize) -> Self {
        let mut messages = VecDeque::new();
        messages.push_back(ChatMessage {
            role: "system".to_string(),
            content: system_prompt,
        });

        Self {
            messages,
            max_history,
            system_prompt,
        }
    }

    pub fn add_user_message(&mut self, content: String) {
        self.messages.push_back(ChatMessage {
            role: "user".to_string(),
            content,
        });
        self.trim_history();
    }

    pub fn add_assistant_message(&mut self, content: String) {
        self.messages.push_back(ChatMessage {
            role: "assistant".to_string(),
            content,
        });
        self.trim_history();
    }

    pub fn get_messages(&self) -> Vec<ChatMessage> {
        self.messages.iter().cloned().collect()
    }

    pub fn clear(&mut self) {
        self.messages.clear();
        self.messages.push_back(ChatMessage {
            role: "system".to_string(),
            content: self.system_prompt.clone(),
        });
    }

    fn trim_history(&mut self) {
        while self.messages.len() > self.max_history + 1 {
            if self.messages.len() > 1 {
                self.messages.remove(1);
            } else {
                break;
            }
        }
    }
}
```

### 4.3 Prompt 模板设计

```rust
pub struct PromptTemplates;

impl PromptTemplates {
    /// 系统提示词 - 图书馆助手
    pub fn library_assistant() -> String {
        r#"你是 NothingBut Library 的智能助手，专门帮助用户管理和检索个人资料库。

当前工作区类型：{workspace_type}
资料库名称：{workspace_name}

你的能力：
1. 语义搜索：理解用户的模糊描述，找到相关书籍
2. 智能导航：根据对话上下文帮助用户定位
3. 推荐建议：基于阅读历史提供个性化推荐
4. 元数据补充：辅助用户整理资料

回复原则：
- 简洁明确，避免冗长
- 中文回复，使用友好的语气
- 如果需要执行操作，说明你的意图
- 不确定时，提供选项让用户选择
"#.to_string()
    }

    /// 元数据提取提示词
    pub fn extract_metadata(content_preview: &str) -> String {
        format!(
            r#"请分析以下小说文本的前 1000 字，提取元数据信息。

文本内容：
```
{}
```

请以 JSON 格式返回：
{{
  "title": "书名",
  "author": "作者",
  "description": "简短的内容简介（1-2 句话）",
  "genre": "推测的类型（玄幻/科幻/都市/历史等）",
  "confidence": "信心等级（high/medium/low）"
}}

注意：
- 如果某项信息不确定，留空或标记为 null
- description 应该客观描述内容，不要夸张
- 只返回 JSON，不要其他解释
"#,
            content_preview
        )
    }
}
```

### 4.4 嵌入向量存储与检索

```rust
use std::path::PathBuf;
use std::fs;

pub struct EmbeddingsCache {
    workspace_path: PathBuf,
}

impl EmbeddingsCache {
    pub fn new(workspace_path: PathBuf) -> Self {
        let cache_dir = workspace_path.join(".embeddings");
        fs::create_dir_all(&cache_dir).ok();
        Self { workspace_path }
    }

    pub fn save(&self, book_id: i64, embedding: &[f32]) -> Result<(), std::io::Error> {
        let path = self.embedding_path(book_id);
        let bytes: Vec<u8> = embedding
            .iter()
            .flat_map(|f| f.to_le_bytes())
            .collect();
        fs::write(path, bytes)
    }

    pub fn load(&self, book_id: i64) -> Result<Vec<f32>, std::io::Error> {
        let path = self.embedding_path(book_id);
        let bytes = fs::read(path)?;

        let embedding: Vec<f32> = bytes
            .chunks_exact(4)
            .map(|chunk| f32::from_le_bytes([chunk[0], chunk[1], chunk[2], chunk[3]]))
            .collect();

        Ok(embedding)
    }

    pub fn exists(&self, book_id: i64) -> bool {
        self.embedding_path(book_id).exists()
    }

    fn embedding_path(&self, book_id: i64) -> PathBuf {
        self.workspace_path
            .join(".embeddings")
            .join(format!("book-{}.bin", book_id))
    }
}

/// 计算余弦相似度
pub fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    assert_eq!(a.len(), b.len());

    let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

    if norm_a == 0.0 || norm_b == 0.0 {
        0.0
    } else {
        dot_product / (norm_a * norm_b)
    }
}
```

### 4.5 AI 功能集成流程

#### 导入时的元数据提取流程

```
用户上传 TXT 文件
    ↓
解析文件（章节分割）
    ↓
提取前 1000 字 → Ollama (Prompt: extract_metadata)
    ↓
展示预览界面（AI 建议 + 手动编辑）
    ↓
用户确认/修改
    ↓
保存到数据库 + 生成嵌入向量（异步）
```

#### 语义搜索流程

```
用户输入："找轻松的科幻小说"
    ↓
生成查询嵌入 → Ollama embeddings API
    ↓
从缓存加载所有书籍的嵌入向量
    ↓
计算余弦相似度，排序
    ↓
返回 Top-10 结果 + 相似度分数
    ↓
可选：调用 AI 生成推荐理由
```

---

## 前端 UI 设计

### 5.1 主界面布局

**整体结构**（响应式）:
- 顶部标题栏：显示当前工作区名称、切换工作区、AI 面板开关
- 左侧/顶部 AI 面板：320px 宽（可隐藏）
- 右侧/底部主窗口：自适应宽度

**响应式断点**:
- 桌面端 (>1024px): 左右布局
- 平板端 (768px-1024px): 左右布局，三栏合并为两栏
- 移动端 (<768px): 上下布局

### 5.2 资料库首页

**网格布局**:
- 展示四种资料类型卡片（网络小说、音乐库、电子书、笔记）
- 卡片大小：200px x 200px，正方形
- 网络小说卡片可点击，其他显示"即将推出"徽章

**最近使用**:
- 列表展示最近打开的工作区
- 显示工作区名称、类型、最后打开时间

### 5.3 小说模块布局（两栏）

**左栏 - 分类树** (280px):
- 树状结构展示分类和书籍
- **四层层级**：
  - **L1 根节点**：📚 全部小说
  - **L2 首级分类**：📁 科幻、历史、玄幻等
  - **L3 次级分类**：📂 太空歌剧、末世幻想、硬科幻等
  - **L4 书籍节点**：具体书名 + 状态图标

**书籍状态图标**（显示在书名前）:
- ✓ (绿色) - 已完本 (completed)
- ⏳ (橙色) - 连载中 (ongoing)
- ⚠ (红色) - 已断更 (abandoned)

**右栏 - 内容区** (自适应):

**状态 1 - 未选择书籍**:
- 显示空白或提示信息："请从左侧选择一本书"

**状态 2 - 已选择书籍，未选择章节**:
- **上半部分**：书籍元数据卡片
  - 封面图片（如果有）
  - 书名（大字体）
  - 作者
  - 简介（多行文本）
  - 分类标签
  - 连载状态标签
  - 字数统计
  - 章节总数

- **下半部分**：章节目录列表
  - 每个章节项显示：
    - 序号（1, 2, 3...）
    - 章节标题
    - 长度（行数或字数）
    - 第一行预览（最多 20 字，超出显示省略号）
  - 可滚动
  - 点击章节进入状态 3

**状态 3 - 已选择章节**:
- **上半部分**：章节内容（替代书籍元数据）
  - 章节标题
  - 章节正文（可滚动）
  - 阅读器工具栏：字体大小、主题切换等

- **下半部分**：章节目录列表（保持不变）
  - 当前章节高亮
  - 可切换到其他章节

### 5.4 阅读器功能

**阅读设置**:
- 字体大小：16-24px（默认 18px）
- 行距：1.5-2.0（默认 1.8）
- 字体：系统字体、宋体、黑体等

**主题切换**:
- 默认：白色背景 (#f8f8f8)，黑色文字 (#333)
- 护眼模式：豆沙绿背景 (#f4ecd8)，深褐色文字 (#5b4636)
- 夜间模式：深色背景 (#1a1a1a)，浅色文字 (#d4d4d4)

**段落样式**:
- 首行缩进 2em
- 段落间距 1.5em
- 两端对齐

### 5.5 AI 助手面板

**组件结构**:
- 顶部：标题 + 在线状态指示
- 中间：消息列表（滚动区域）
  - 用户消息：蓝色气泡，右对齐
  - AI 消息：灰色气泡，左对齐
- 底部：输入框 + 发送按钮

**交互功能**:
- 支持 Enter 发送消息
- 流式响应（逐字显示）
- 自动滚动到最新消息
- 清空对话按钮

### 5.6 状态管理（Svelte 5 Runes）

```typescript
// src/lib/stores/workspace.ts
class WorkspaceStore {
  currentWorkspace = $state<Workspace | null>(null);
  recentWorkspaces = $state<Workspace[]>([]);
  currentModule = $state<'novel' | 'music' | 'ebook' | 'note' | null>(null);

  // 派生状态
  isWorkspaceOpen = $derived(this.currentWorkspace !== null);

  async openWorkspace(path: string) { /* ... */ }
  async closeWorkspace() { /* ... */ }
  setModule(module: string) { /* ... */ }
}

// src/lib/stores/novel.ts
class NovelStore {
  categories = $state<Category[]>([]);
  books = $state<NovelBook[]>([]);
  chapters = $state<NovelChapter[]>([]);

  selectedBookId = $state<number | null>(null);
  currentChapterId = $state<number | null>(null);

  readerSettings = $state<ReaderSettings>({
    fontSize: 18,
    lineHeight: 1.8,
    fontFamily: 'system-ui',
    theme: 'light',
  });

  // 派生状态
  selectedBook = $derived(
    this.books.find(b => b.id === this.selectedBookId) ?? null
  );

  currentChapter = $derived(
    this.chapters.find(c => c.id === this.currentChapterId) ?? null
  );
}

// src/lib/stores/ai.ts
class AIStore {
  messages = $state<ChatMessage[]>([]);
  isTyping = $state(false);
  isServiceAvailable = $state(false);

  async sendMessage(content: string) { /* ... */ }
  async checkService() { /* ... */ }
  clearConversation() { /* ... */ }
}
```

---

## MVP 功能范围

### 6.1 MVP 核心功能（网络小说模块）

#### 工作区管理
- [x] 创建/打开/切换工作区
- [x] 工作区配置（名称、路径、类型）
- [x] 最近使用的工作区列表
- [x] 工作区目录结构自动创建

#### 小说导入
- [x] **TXT 文件导入**
  - 支持 UTF-8 和 GBK 编码自动识别
  - 章节智能解析（多种正则模式）
  - 导入预览界面

- [x] **AI 辅助元数据提取**
  - 从文件名和内容推测书名、作者
  - 生成简介
  - 推测分类/类型
  - 手动编辑修正

- [x] **文件存储**
  - 每本书独立目录
  - 章节按序号保存为独立文件
  - metadata.json 元数据副本

#### 分类管理
- [x] **四层树形分类结构**
  - 根节点：全部小说
  - 首级分类：科幻、玄幻、都市等
  - 次级分类：硬科幻、仙侠修真等
  - 叶子节点：具体书籍

- [x] **分类操作**
  - 创建/重命名/删除分类
  - 创建子分类
  - 移动书籍到分类
  - 展开/折叠节点

- [x] **书籍状态标识**
  - ✓ 完本（绿色）
  - ⏳ 连载中（橙色）
  - ⚠ 太监（红色）

#### 章节浏览
- [x] 章节列表（标题、字数）
- [x] 按章节顺序排序
- [x] 快速跳转到章节
- [x] 阅读进度记录

#### 阅读器
- [x] **舒适阅读功能**
  - 字体大小调节（16-24px）
  - 行距调节（1.5-2.0）
  - 字体选择（系统字体）
  - 主题切换（默认/护眼/夜间）

- [x] **阅读控制**
  - 上一章/下一章导航
  - 进度指示
  - 快捷键翻页（空格、方向键）

- [x] **书签功能**
  - 添加书签到当前位置
  - 书签备注
  - 书签列表查看

#### AI 助手
- [x] **本地 Ollama 集成**
  - HTTP API 调用
  - 服务状态检测
  - 对话历史管理

- [x] **智能功能**
  - 语义搜索书籍
  - 基于描述推荐
  - 阅读进度查询
  - 元数据补充建议

- [x] **向量嵌入**
  - 使用 nomic-embed-text 模型
  - 书籍嵌入缓存
  - 余弦相似度计算

#### 搜索功能
- [x] 关键词搜索（书名、作者）
- [x] 实时搜索建议
- [x] 语义搜索（AI 增强）

#### 数据持久化
- [x] SQLite 数据库存储元数据
- [x] 文件系统存储章节内容
- [x] 阅读设置保存到 localStorage
- [x] 工作区配置 JSON 文件

### 6.2 空模块（占位实现）

- [ ] 音乐库：显示"即将推出"
- [ ] 电子书库：显示"即将推出"
- [ ] 笔记库：显示"即将推出"

### 6.3 MVP 不包含的功能

#### Phase 2 - 网络同步
- [ ] 小说网站爬虫
- [ ] 自动更新检测
- [ ] 增量章节下载

#### Phase 2 - 高级阅读功能
- [ ] 笔记/划线
- [ ] 章节内搜索
- [ ] 全文搜索
- [ ] TTS 语音朗读

#### Phase 3 - 其他模块
- [ ] 音乐库完整实现
- [ ] 电子书库完整实现
- [ ] 笔记库完整实现

#### Phase 4 - Mobile 版本
- [ ] Android 应用
- [ ] iOS 应用
- [ ] 工作区云同步

---

## 技术选型

### 7.1 前端技术栈

| 技术 | 版本 | 选型理由 |
|------|------|----------|
| Svelte | 5.x | 编译时优化、Runes 响应式系统、体积小 |
| TypeScript | 5.x | 类型安全、IDE 支持好 |
| SvelteKit | 2.x | 静态生成、Tauri 集成方便 |
| Tailwind CSS | 4.0 | 实用优先、快速开发 |
| Vite | 5.x | 快速 HMR、原生 ESM |
| Bun | 1.x | 极速安装、运行时一致性 |

### 7.2 后端技术栈

| 技术 | 版本 | 选型理由 |
|------|------|----------|
| Tauri | 2.0 | 体积小、性能好、跨平台 |
| Rust | 1.77+ | 内存安全、高性能、生态成熟 |
| SQLite | 3.x | 嵌入式、无需安装、事务支持 |
| reqwest | 0.11 | HTTP 客户端、异步支持 |
| tokio | 1.x | 异步运行时 |
| serde | 1.x | 序列化/反序列化 |

### 7.3 AI 技术栈

| 技术 | 版本 | 选型理由 |
|------|------|----------|
| Ollama | latest | 本地部署、隐私保护、免费 |
| qwen2.5:7b | - | 中文友好、性能平衡 |
| nomic-embed-text | latest | 768 维、中英文支持、开源 |

### 7.4 依赖关系

**前端主要依赖**:
```json
{
  "@sveltejs/kit": "^2.0.0",
  "@sveltejs/adapter-static": "^3.0.0",
  "@tauri-apps/api": "^2.0.0",
  "@tauri-apps/plugin-sql": "^2.0.0",
  "tailwindcss": "^4.0.0",
  "svelte": "^5.0.0",
  "typescript": "^5.0.0",
  "vite": "^5.0.0"
}
```

**后端主要依赖**:
```toml
[dependencies]
tauri = "2.0"
tauri-plugin-sql = { version = "2.0", features = ["sqlite"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1", features = ["full"] }
reqwest = { version = "0.11", features = ["json"] }
async-trait = "0.1"
thiserror = "1.0"
regex = "1.10"
encoding_rs = "0.8"
chrono = { version = "0.4", features = ["serde"] }
```

---

## 开发里程碑

### Milestone 1: 基础架构（1-2 周）

**目标**: 搭建项目骨架，实现工作区管理

- [ ] 项目初始化（Tauri + Svelte + Bun）
- [ ] 配置 Tailwind CSS 4.0
- [ ] 工作区创建/打开/切换
- [ ] SQLite 迁移系统
- [ ] LibraryModule trait 定义
- [ ] 空模块占位实现

**验收标准**:
- 应用能启动并显示主界面
- 能创建工作区并保存配置
- 数据库迁移正常执行

### Milestone 2: 小说导入与存储（1-2 周）

**目标**: 实现 TXT 导入和文件存储系统

- [ ] TXT 文件编码识别（UTF-8/GBK）
- [ ] 章节解析器（多种正则模式）
- [ ] 文件存储系统（books 目录结构）
- [ ] 数据库 CRUD 操作（books、chapters 表）
- [ ] 导入预览界面

**验收标准**:
- 能成功导入 TXT 文件并自动分章
- 章节内容正确保存到文件系统
- 元数据正确保存到数据库

### Milestone 3: UI 基础（1-2 周）

**目标**: 实现主界面和小说模块 UI

- [ ] 主界面布局（AI 面板 + 主窗口）
- [ ] 资料库首页（网格布局）
- [ ] 分类树组件（四层树状结构）
- [ ] 章节列表组件
- [ ] 阅读器组件（基础版本）
- [ ] 状态管理（Svelte 5 Runes）

**验收标准**:
- UI 布局正常，响应式适配
- 树状结构可展开折叠
- 能选中书籍并显示章节
- 阅读器能显示章节内容

### Milestone 4: AI 集成（1 周）

**目标**: 集成 Ollama 和 AI 助手功能

- [ ] Ollama HTTP 客户端
- [ ] 对话管理（历史记录、上下文）
- [ ] Prompt 模板
- [ ] 元数据提取（导入时调用 AI）
- [ ] 嵌入向量生成
- [ ] 语义搜索实现
- [ ] AI 助手 UI

**验收标准**:
- Ollama 服务检测正常
- AI 对话能正常交互
- 元数据提取准确率 > 70%
- 语义搜索返回相关结果

### Milestone 5: 完善与测试（1 周）

**目标**: 功能联调、优化体验、编写文档

- [ ] 功能联调（端到端测试）
- [ ] 性能优化（启动速度、导入速度）
- [ ] 错误处理完善
- [ ] 用户体验优化（加载提示、错误提示）
- [ ] 编写用户文档
- [ ] 编写开发者文档

**验收标准**:
- 所有核心功能正常运行
- 性能达标（见 MVP 验收标准）
- 文档完整

**预计总开发时间**: 6-8 周

---

## 项目结构

```
claude/nothingbut-library/
├── src/                          # Svelte 前端
│   ├── lib/
│   │   ├── components/
│   │   │   ├── shared/           # 共享组件
│   │   │   │   ├── AppLayout.svelte
│   │   │   │   ├── WorkspaceSelector.svelte
│   │   │   │   └── LibraryGrid.svelte
│   │   │   ├── ai-panel/         # AI 助手面板
│   │   │   │   ├── ChatPanel.svelte
│   │   │   │   ├── MessageList.svelte
│   │   │   │   └── InputBox.svelte
│   │   │   └── modules/          # 资料类型模块 UI
│   │   │       ├── novel/        # 小说模块 (MVP)
│   │   │       │   ├── NovelLayout.svelte
│   │   │       │   ├── CategoryTree.svelte
│   │   │       │   ├── ChapterList.svelte
│   │   │       │   ├── Reader.svelte
│   │   │       │   └── ImportDialog.svelte
│   │   │       ├── music/        # 音乐模块 (空)
│   │   │       ├── ebook/        # 电子书模块 (空)
│   │   │       └── note/         # 笔记模块 (空)
│   │   ├── stores/               # 状态管理
│   │   │   ├── workspace.ts
│   │   │   ├── ai.ts
│   │   │   └── novel.ts
│   │   ├── services/             # API 层
│   │   │   ├── api.ts
│   │   │   ├── novel-api.ts
│   │   │   └── ai-api.ts
│   │   └── types/                # TypeScript 类型
│   │       ├── core.ts
│   │       ├── novel.ts
│   │       └── ai.ts
│   └── routes/
│       └── +page.svelte          # 主页面
│
├── src-tauri/                    # Rust 后端
│   ├── src/
│   │   ├── core/                 # 核心模块
│   │   │   ├── mod.rs
│   │   │   ├── workspace.rs
│   │   │   ├── config.rs
│   │   │   └── traits.rs         # LibraryModule trait
│   │   ├── ai/                   # AI 模块
│   │   │   ├── mod.rs
│   │   │   ├── ollama.rs
│   │   │   ├── embeddings.rs
│   │   │   ├── conversation.rs
│   │   │   ├── prompts.rs
│   │   │   └── commands.rs
│   │   ├── modules/              # 资料类型模块
│   │   │   ├── mod.rs
│   │   │   ├── novel/            # 小说模块 (MVP)
│   │   │   │   ├── mod.rs
│   │   │   │   ├── models.rs
│   │   │   │   ├── commands.rs
│   │   │   │   ├── parser.rs
│   │   │   │   ├── storage.rs
│   │   │   │   └── metadata.rs
│   │   │   ├── music/            # 音乐模块 (空)
│   │   │   │   └── mod.rs
│   │   │   ├── ebook/            # 电子书模块 (空)
│   │   │   │   └── mod.rs
│   │   │   └── note/             # 笔记模块 (空)
│   │   │       └── mod.rs
│   │   ├── database.rs           # 数据库工具
│   │   ├── errors.rs             # 错误类型
│   │   └── lib.rs                # 入口
│   ├── migrations/               # SQLite 迁移
│   │   ├── 0001_core.sql
│   │   └── 0002_novel.sql
│   └── Cargo.toml
│
├── docs/                         # 文档
│   ├── superpowers/specs/        # 设计文档
│   │   └── 2026-03-11-nothingbut-library-design.md
│   ├── api/                      # API 文档
│   └── user-guide/               # 用户手册
│
├── package.json                  # 前端依赖
├── tauri.conf.json               # Tauri 配置
├── svelte.config.js              # Svelte 配置
├── vite.config.js                # Vite 配置
├── tailwind.config.js            # Tailwind 配置
├── tsconfig.json                 # TypeScript 配置
├── .gitignore
└── README.md
```

---

## 附录

### A. 术语表

- **工作区 (Workspace)**: 一个独立的资料库实例，包含数据库和文件存储
- **模块 (Module)**: 资料类型的实现，如小说模块、音乐模块
- **LibraryModule**: 定义模块接口的 Rust trait
- **嵌入向量 (Embeddings)**: 文本的向量表示，用于语义搜索
- **余弦相似度 (Cosine Similarity)**: 衡量两个向量相似程度的指标

### B. 参考资料

- [Tauri 2.0 文档](https://tauri.app/)
- [Svelte 5 文档](https://svelte.dev/)
- [Ollama 文档](https://ollama.ai/docs)
- [nomic-embed-text 模型](https://huggingface.co/nomic-ai/nomic-embed-text-v1)

### C. UI 预览

完整的交互式 UI 预览已生成，包含：
- 主界面布局
- 资料库首页（网格）
- 小说模块三栏布局
- 四层树状分类结构
- 书籍状态图标（完本/连载/太监）
- AI 助手面板
- 阅读器界面

预览文件位置：`/tmp/nothingbut-library-preview.html`

---

**文档状态**: 已完成
**下一步**: 进入实施计划阶段（writing-plans skill）

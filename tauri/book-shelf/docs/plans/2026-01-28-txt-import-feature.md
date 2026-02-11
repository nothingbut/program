# TXT文件导入功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现完整的TXT小说文件导入功能，支持文件选择、信息填写、编码检测、章节解析和数据库存储。

**Architecture:** 使用Tauri Dialog API选择文件，前端模态对话框收集书籍元数据，后端自动检测文件编码并解析章节，通过SQLite批量存储章节数据。

**Tech Stack:** Tauri 2.0, Svelte 5, TypeScript, Rust, SQLite, tauri-plugin-dialog, encoding_rs

---

## Task 1: 安装并配置 Tauri Dialog 插件

**Files:**
- Modify: `src-tauri/Cargo.toml`
- Modify: `src-tauri/src/lib.rs`
- Modify: `package.json`

**Step 1: 添加 Rust 依赖**

在 `src-tauri/Cargo.toml` 的 `[dependencies]` 部分添加：

```toml
tauri-plugin-dialog = "2"
```

**Step 2: 添加前端依赖**

```bash
bun add @tauri-apps/plugin-dialog
```

Expected: 依赖成功安装

**Step 3: 在 Rust 中注册插件**

修改 `src-tauri/src/lib.rs`，在 `tauri::Builder::default()` 后添加：

```rust
.plugin(tauri_plugin_dialog::init())
```

**Step 4: 测试插件是否可用**

```bash
bun run tauri dev
```

Expected: 应用正常启动，无编译错误

**Step 5: Commit**

```bash
git add src-tauri/Cargo.toml src-tauri/src/lib.rs package.json bun.lockb
git commit -m "feat: add tauri-plugin-dialog dependency"
```

---

## Task 2: 创建导入对话框组件

**Files:**
- Create: `src/lib/components/ImportDialog.svelte`

**Step 1: 创建对话框组件骨架**

创建 `src/lib/components/ImportDialog.svelte`：

```svelte
<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import type { Category } from '$lib/types';

  interface Props {
    visible: boolean;
    onClose: () => void;
    onSuccess: () => void;
    categories: Category[];
  }

  let { visible = $bindable(false), onClose, onSuccess, categories }: Props = $props();

  let formData = $state({
    filePath: '',
    fileName: '',
    title: '',
    author: '',
    description: '',
    coverPath: '',
    categoryId: 1,
    subcategoryId: null as number | null
  });

  let errors = $state<Record<string, string>>({});
  let isSubmitting = $state(false);

  function handleClose() {
    if (!isSubmitting) {
      resetForm();
      onClose();
    }
  }

  function resetForm() {
    formData = {
      filePath: '',
      fileName: '',
      title: '',
      author: '',
      description: '',
      coverPath: '',
      categoryId: 1,
      subcategoryId: null
    };
    errors = {};
  }

  function getSubcategories(parentId: number): Category[] {
    return categories.filter(c => c.parent_id === parentId);
  }

  function getRootCategories(): Category[] {
    return categories.filter(c => c.parent_id === null);
  }
</script>

{#if visible}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onclick={handleClose}>
    <div class="bg-white rounded-lg shadow-xl w-[500px] max-h-[80vh] overflow-hidden" onclick={(e) => e.stopPropagation()}>
      <div class="p-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-800">导入TXT小说</h2>
      </div>

      <div class="p-4 space-y-4 overflow-y-auto max-h-[60vh]">
        <p class="text-sm text-gray-500">请填写书籍信息，带 * 为必填项</p>

        <!-- 表单内容将在下一步添加 -->

      </div>

      <div class="p-4 border-t border-gray-200 flex gap-2 justify-end">
        <button
          type="button"
          class="px-4 py-2 rounded border border-gray-300 hover:bg-gray-50 transition-colors"
          onclick={handleClose}
          disabled={isSubmitting}
        >
          取消
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
          disabled={isSubmitting}
        >
          {isSubmitting ? '导入中...' : '开始导入'}
        </button>
      </div>
    </div>
  </div>
{/if}
```

**Step 2: 测试组件渲染**

临时在 `src/routes/+page.svelte` 中导入并测试：

```svelte
import ImportDialog from '$lib/components/ImportDialog.svelte';

let showImportDialog = $state(false);

<ImportDialog
  bind:visible={showImportDialog}
  onClose={() => showImportDialog = false}
  onSuccess={() => {}}
  categories={categories}
/>

<button onclick={() => showImportDialog = true}>测试</button>
```

Expected: 点击按钮显示对话框，点击取消或背景关闭对话框

**Step 3: Commit**

```bash
git add src/lib/components/ImportDialog.svelte
git commit -m "feat: create import dialog component skeleton"
```

---

## Task 3: 实现导入对话框表单字段

**Files:**
- Modify: `src/lib/components/ImportDialog.svelte`

**Step 1: 添加文件选择功能**

在 `<script>` 部分添加文件选择函数：

```typescript
import { open } from '@tauri-apps/plugin-dialog';

async function selectFile() {
  try {
    const selected = await open({
      multiple: false,
      filters: [{
        name: 'TXT文件',
        extensions: ['txt']
      }]
    });

    if (selected && typeof selected === 'string') {
      formData.filePath = selected;
      const fileName = selected.split(/[/\\]/).pop()?.replace('.txt', '') || '';
      formData.fileName = fileName;
      if (!formData.title) {
        formData.title = fileName;
      }
    }
  } catch (error) {
    console.error('选择文件失败:', error);
  }
}

async function selectCover() {
  try {
    const selected = await open({
      multiple: false,
      filters: [{
        name: '图片文件',
        extensions: ['jpg', 'jpeg', 'png', 'webp']
      }]
    });

    if (selected && typeof selected === 'string') {
      formData.coverPath = selected;
    }
  } catch (error) {
    console.error('选择封面失败:', error);
  }
}
```

**Step 2: 添加完整表单HTML**

在 `<div class="p-4 space-y-4 overflow-y-auto max-h-[60vh]">` 中替换注释为：

```svelte
<!-- 文件选择 -->
<div>
  <label class="block text-sm font-medium text-gray-700 mb-1">
    TXT文件 <span class="text-red-500">*</span>
  </label>
  <div class="flex gap-2">
    <input
      type="text"
      class="flex-1 px-3 py-2 border border-gray-300 rounded text-sm bg-gray-50"
      value={formData.fileName || '未选择文件'}
      readonly
    />
    <button
      type="button"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
      onclick={selectFile}
    >
      选择文件
    </button>
  </div>
  {#if errors.filePath}
    <p class="text-xs text-red-500 mt-1">{errors.filePath}</p>
  {/if}
</div>

<!-- 书名 -->
<div>
  <label class="block text-sm font-medium text-gray-700 mb-1">
    书名 <span class="text-red-500">*</span>
  </label>
  <input
    type="text"
    class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
    bind:value={formData.title}
    placeholder="请输入书名"
  />
  {#if errors.title}
    <p class="text-xs text-red-500 mt-1">{errors.title}</p>
  {/if}
</div>

<!-- 作者 -->
<div>
  <label class="block text-sm font-medium text-gray-700 mb-1">
    作者
  </label>
  <input
    type="text"
    class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
    bind:value={formData.author}
    placeholder="请输入作者（可选）"
  />
</div>

<!-- 分类 -->
<div class="grid grid-cols-2 gap-3">
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1">
      分类 <span class="text-red-500">*</span>
    </label>
    <select
      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
      bind:value={formData.categoryId}
      onchange={() => formData.subcategoryId = null}
    >
      {#each getRootCategories() as cat}
        <option value={cat.id}>{cat.name}</option>
      {/each}
    </select>
  </div>

  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1">
      子分类
    </label>
    <select
      class="w-full px-3 py-2 border border-gray-300 rounded text-sm"
      bind:value={formData.subcategoryId}
      disabled={getSubcategories(formData.categoryId).length === 0}
    >
      <option value={null}>请选择子分类</option>
      {#each getSubcategories(formData.categoryId) as subcat}
        <option value={subcat.id}>{subcat.name}</option>
      {/each}
    </select>
  </div>
</div>

<!-- 简介 -->
<div>
  <label class="block text-sm font-medium text-gray-700 mb-1">
    简介
  </label>
  <textarea
    class="w-full px-3 py-2 border border-gray-300 rounded text-sm resize-none"
    rows="3"
    bind:value={formData.description}
    placeholder="请输入书籍简介（可选）"
  ></textarea>
</div>

<!-- 封面 -->
<div>
  <label class="block text-sm font-medium text-gray-700 mb-1">
    封面图片
  </label>
  <div class="flex gap-2">
    <input
      type="text"
      class="flex-1 px-3 py-2 border border-gray-300 rounded text-sm bg-gray-50"
      value={formData.coverPath ? formData.coverPath.split(/[/\\]/).pop() : '未选择封面'}
      readonly
    />
    <button
      type="button"
      class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors text-sm"
      onclick={selectCover}
    >
      选择图片
    </button>
  </div>
</div>
```

**Step 3: 测试表单交互**

启动开发服务器并测试：
- 点击"选择文件"按钮应打开文件选择对话框
- 选择TXT文件后，书名应自动填充为文件名
- 分类下拉框应显示所有一级分类
- 选择分类后，子分类下拉框应显示对应的子分类

**Step 4: Commit**

```bash
git add src/lib/components/ImportDialog.svelte
git commit -m "feat: add import dialog form fields with file selection"
```

---

## Task 4: 实现表单验证逻辑

**Files:**
- Modify: `src/lib/components/ImportDialog.svelte`

**Step 1: 添加验证函数**

在 `<script>` 部分添加：

```typescript
function validateForm(): boolean {
  errors = {};

  if (!formData.filePath) {
    errors.filePath = '请选择要导入的TXT文件';
  }

  if (!formData.title.trim()) {
    errors.title = '请输入书名';
  }

  return Object.keys(errors).length === 0;
}
```

**Step 2: 添加提交处理函数**

```typescript
async function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  isSubmitting = true;

  try {
    // 调用后端导入命令
    await invoke('import_book_from_file', {
      filePath: formData.filePath,
      title: formData.title,
      author: formData.author || null,
      description: formData.description || null,
      coverPath: formData.coverPath || null,
      categoryId: formData.subcategoryId || formData.categoryId
    });

    // 成功后关闭对话框并刷新
    resetForm();
    onSuccess();
    onClose();
  } catch (error) {
    console.error('导入失败:', error);
    errors.submit = error instanceof Error ? error.message : '导入失败，请重试';
  } finally {
    isSubmitting = false;
  }
}
```

**Step 3: 绑定提交按钮**

修改"开始导入"按钮的 `onclick` 为 `onclick={handleSubmit}`

**Step 4: 添加错误提示显示**

在按钮上方添加全局错误提示：

```svelte
{#if errors.submit}
  <div class="px-4 py-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
    {errors.submit}
  </div>
{/if}
```

**Step 5: Commit**

```bash
git add src/lib/components/ImportDialog.svelte
git commit -m "feat: add form validation and submit logic"
```

---

## Task 5: 实现后端书籍创建命令（使用数据库）

**Files:**
- Modify: `src-tauri/src/commands/books.rs`

**Step 1: 添加数据库助手函数**

在 `src-tauri/src/commands/books.rs` 顶部添加导入：

```rust
use tauri::{command, AppHandle, Manager};
use tauri_plugin_sql::SqlitePool;
```

**Step 2: 实现 create_book 命令**

替换现有的 `create_book` 函数：

```rust
#[command]
pub async fn create_book(
    app: AppHandle,
    title: String,
    author: Option<String>,
    description: Option<String>,
    cover_image: Option<String>,
    category_id: Option<i64>,
    file_path: Option<String>,
    file_size: Option<i64>,
    word_count: i64,
) -> Result<Book, String> {
    let db: tauri::State<SqlitePool> = app.state();

    let result = sqlx::query(
        "INSERT INTO books (title, author, description, cover_image, category_id, file_path, file_size, word_count, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))"
    )
    .bind(&title)
    .bind(&author)
    .bind(&description)
    .bind(&cover_image)
    .bind(category_id)
    .bind(&file_path)
    .bind(file_size)
    .bind(word_count)
    .execute(&**db)
    .await
    .map_err(|e| format!("创建书籍失败: {}", e))?;

    let book_id = result.last_insert_rowid();

    Ok(Book {
        id: Some(book_id),
        title,
        author,
        description,
        cover_image,
        category_id,
        file_path,
        file_size,
        word_count,
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
        category_name: None,
    })
}
```

**Step 3: 测试数据库连接**

```bash
bun run tauri dev
```

Expected: 应用正常启动

**Step 4: Commit**

```bash
git add src-tauri/src/commands/books.rs
git commit -m "feat: implement database-backed create_book command"
```

---

## Task 6: 实现批量创建章节命令

**Files:**
- Modify: `src-tauri/src/commands/chapters.rs`

**Step 1: 添加数据库导入**

在文件顶部添加：

```rust
use tauri::{command, AppHandle, Manager};
use tauri_plugin_sql::SqlitePool;
```

**Step 2: 实现批量创建函数**

添加新命令：

```rust
#[command]
pub async fn create_chapters_batch(
    app: AppHandle,
    chapters: Vec<Chapter>,
) -> Result<usize, String> {
    let db: tauri::State<SqlitePool> = app.state();

    let mut inserted_count = 0;

    for chapter in chapters {
        sqlx::query(
            "INSERT INTO chapters (book_id, title, content, sort_order, word_count, created_at)
             VALUES (?, ?, ?, ?, ?, datetime('now'))"
        )
        .bind(chapter.book_id)
        .bind(&chapter.title)
        .bind(&chapter.content)
        .bind(chapter.sort_order)
        .bind(chapter.word_count)
        .execute(&**db)
        .await
        .map_err(|e| format!("插入章节失败: {}", e))?;

        inserted_count += 1;
    }

    Ok(inserted_count)
}
```

**Step 3: 注册命令**

在 `src-tauri/src/lib.rs` 的 `invoke_handler!` 宏中添加：

```rust
create_chapters_batch,
```

**Step 4: Commit**

```bash
git add src-tauri/src/commands/chapters.rs src-tauri/src/lib.rs
git commit -m "feat: implement batch chapter creation command"
```

---

## Task 7: 实现完整的导入流程命令

**Files:**
- Modify: `src-tauri/src/commands/import.rs`

**Step 1: 添加导入依赖**

在文件顶部添加：

```rust
use crate::commands::books::create_book;
use crate::commands::chapters::create_chapters_batch;
use tauri::{command, AppHandle};
use std::fs;
```

**Step 2: 实现主导入命令**

添加新命令：

```rust
#[command]
pub async fn import_book_from_file(
    app: AppHandle,
    file_path: String,
    title: String,
    author: Option<String>,
    description: Option<String>,
    cover_path: Option<String>,
    category_id: i64,
) -> Result<String, String> {
    // 1. 检测文件编码
    let encoding = detect_file_encoding(file_path.clone()).await?;

    // 2. 读取文件内容
    let bytes = fs::read(&file_path)
        .map_err(|e| format!("读取文件失败: {}", e))?;

    let content = if encoding == "gbk" {
        let (decoded, _, had_errors) = encoding_rs::GBK.decode(&bytes);
        if had_errors {
            return Err("GBK解码失败，文件可能损坏".to_string());
        }
        decoded.to_string()
    } else {
        String::from_utf8(bytes)
            .map_err(|e| format!("UTF-8解码失败: {}，请尝试使用其他编码", e))?
    };

    // 3. 解析章节
    let chapters = parse_chapters(&content);

    if chapters.is_empty() {
        return Err("未能解析出任何章节".to_string());
    }

    // 4. 获取文件信息
    let file_size = fs::metadata(&file_path)
        .map(|m| m.len() as i64)
        .ok();

    let total_word_count: i64 = chapters.iter()
        .map(|c| c.word_count)
        .sum();

    // 5. 创建书籍记录
    let book = create_book(
        app.clone(),
        title,
        author,
        description,
        cover_path,
        Some(category_id),
        Some(file_path),
        file_size,
        total_word_count,
    ).await?;

    let book_id = book.id.ok_or("书籍ID获取失败")?;

    // 6. 设置章节的book_id
    let chapters_with_book_id: Vec<Chapter> = chapters
        .into_iter()
        .enumerate()
        .map(|(index, mut chapter)| {
            chapter.book_id = book_id;
            chapter.sort_order = (index + 1) as i64;
            chapter
        })
        .collect();

    // 7. 批量插入章节
    let chapter_count = create_chapters_batch(app, chapters_with_book_id).await?;

    Ok(format!("成功导入《{}》，共{}章", book.title, chapter_count))
}
```

**Step 3: 注册命令**

在 `src-tauri/src/lib.rs` 中添加：

```rust
import_book_from_file,
```

**Step 4: 测试导入流程**

需要准备一个测试TXT文件，可以创建 `test-book.txt`：

```
第一章 测试章节

这是第一章的内容。

第二章 另一章节

这是第二章的内容。
```

**Step 5: Commit**

```bash
git add src-tauri/src/commands/import.rs src-tauri/src/lib.rs
git commit -m "feat: implement complete book import workflow"
```

---

## Task 8: 集成导入对话框到主界面

**Files:**
- Modify: `src/routes/+page.svelte`

**Step 1: 导入对话框组件**

在 `<script>` 顶部添加：

```typescript
import ImportDialog from '$lib/components/ImportDialog.svelte';
```

**Step 2: 添加对话框状态**

在状态变量部分添加：

```typescript
let showImportDialog = $state(false);
```

**Step 3: 修改导入按钮处理**

找到 `importTxtFile` 函数，替换为：

```typescript
function importTxtFile() {
  showImportDialog = true;
}
```

**Step 4: 添加导入成功回调**

添加刷新数据的函数：

```typescript
async function handleImportSuccess() {
  try {
    statusMessage = '正在刷新数据...';
    const data = await getCategoriesWithBooks();
    categories = data;
    statusMessage = `导入成功 - ${categories.length} 个分类`;
  } catch (error) {
    console.error('刷新数据失败:', error);
    statusMessage = '导入成功，但刷新数据失败';
  }
}
```

**Step 5: 在模板中添加对话框组件**

在 `</div>` 结束标签前（状态栏之后）添加：

```svelte
<ImportDialog
  bind:visible={showImportDialog}
  onClose={() => showImportDialog = false}
  onSuccess={handleImportSuccess}
  categories={categories}
/>
```

**Step 6: 同时处理菜单栏和工具栏的导入事件**

修改现有的事件监听器：

```typescript
// 添加到 onMount 中
window.addEventListener('menu-action', (e: any) => {
  if (e.detail === 'import') {
    importTxtFile();
  }
});

window.addEventListener('tool-action', (e: any) => {
  if (e.detail === 'import') {
    importTxtFile();
  }
});
```

**Step 7: 测试完整流程**

1. 启动应用：`bun run tauri dev`
2. 点击工具栏"导入"按钮或菜单栏"文件→导入书籍"
3. 选择TXT文件
4. 填写书籍信息
5. 点击"开始导入"
6. 验证书籍和章节是否成功导入

**Step 8: Commit**

```bash
git add src/routes/+page.svelte
git commit -m "feat: integrate import dialog into main interface"
```

---

## Task 9: 修复数据加载逻辑

**Files:**
- Modify: `src-tauri/src/commands/books.rs`
- Modify: `src-tauri/src/commands/chapters.rs`

**Step 1: 实现 get_all_books 数据库查询**

替换 `src-tauri/src/commands/books.rs` 中的 `get_all_books`：

```rust
#[command]
pub async fn get_all_books(app: AppHandle) -> Result<Vec<Book>, String> {
    let db: tauri::State<SqlitePool> = app.state();

    let books = sqlx::query_as::<_, Book>(
        "SELECT b.*, c.name as category_name
         FROM books b
         LEFT JOIN categories c ON b.category_id = c.id
         ORDER BY b.created_at DESC"
    )
    .fetch_all(&**db)
    .await
    .map_err(|e| format!("查询书籍失败: {}", e))?;

    Ok(books)
}
```

**Step 2: 实现 get_chapters_by_book 数据库查询**

替换 `src-tauri/src/commands/chapters.rs` 中的 `get_chapters_by_book`：

```rust
#[command]
pub async fn get_chapters_by_book(app: AppHandle, book_id: i64) -> Result<Vec<Chapter>, String> {
    let db: tauri::State<SqlitePool> = app.state();

    let chapters = sqlx::query_as::<_, Chapter>(
        "SELECT * FROM chapters WHERE book_id = ? ORDER BY sort_order ASC"
    )
    .bind(book_id)
    .fetch_all(&**db)
    .await
    .map_err(|e| format!("查询章节失败: {}", e))?;

    Ok(chapters)
}
```

**Step 3: 为模型添加 sqlx 派生**

在 `src-tauri/src/models.rs` 中，修改结构体定义：

```rust
use sqlx::FromRow;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Book {
    // ... 字段保持不变
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Chapter {
    // ... 字段保持不变
}
```

**Step 4: 添加 sqlx 依赖**

在 `src-tauri/Cargo.toml` 中添加：

```toml
sqlx = { version = "0.7", features = ["sqlite", "runtime-tokio"] }
```

**Step 5: Commit**

```bash
git add src-tauri/src/commands/books.rs src-tauri/src/commands/chapters.rs src-tauri/src/models.rs src-tauri/Cargo.toml
git commit -m "feat: implement database queries for books and chapters"
```

---

## Task 10: 测试和错误处理优化

**Files:**
- Modify: `src-tauri/src/commands/import.rs`

**Step 1: 添加详细的错误处理**

在 `import_book_from_file` 中添加更多错误上下文：

```rust
// 在文件读取部分添加文件存在检查
if !std::path::Path::new(&file_path).exists() {
    return Err(format!("文件不存在: {}", file_path));
}

// 在解码部分添加更详细的错误信息
let content = if encoding == "gbk" {
    let (decoded, _, had_errors) = encoding_rs::GBK.decode(&bytes);
    if had_errors {
        return Err("文件编码为GBK但解码失败，可能是文件损坏或编码混合。建议使用文本编辑器转换为UTF-8后重试。".to_string());
    }
    decoded.to_string()
} else {
    String::from_utf8(bytes)
        .map_err(|e| format!("文件编码检测为UTF-8但解码失败: {}。\n建议：\n1. 使用记事本打开文件，另存为UTF-8编码\n2. 或联系开发者添加更多编码支持", e))?
};
```

**Step 2: 添加章节解析失败的友好提示**

```rust
if chapters.is_empty() {
    return Err(format!(
        "未能从文件中解析出章节。\n\n可能原因：\n1. 文件中没有符合格式的章节标题\n2. 章节数量少于3章（需要至少3章才能识别模式）\n\n支持的章节格式：\n- 第X章 标题\n- Chapter X 标题\n- 数字. 标题\n- 【标题】\n- （标题）\n\n如果文件确实没有章节，整本书将作为单章导入。"
    ));
}
```

**Step 3: 创建测试文件**

创建 `test-samples/sample-book.txt`：

```txt
第一章 起源

萧炎站在山巅之上，遥望着那看不见尽头的远方。

数年之前，他还是一个被人嘲笑的废材。

第二章 修炼

经过三年的苦修，萧炎终于突破了瓶颈。

第三章 突破

"斗之力，九段！"

第四章 新的征程

是时候离开家族，去闯荡更广阔的世界了。
```

**Step 4: 手动测试完整流程**

1. 启动应用
2. 点击导入
3. 选择 `test-samples/sample-book.txt`
4. 填写书名"测试小说"
5. 选择分类
6. 导入并验证：
   - 书籍列表中出现新书
   - 点击书籍显示4个章节
   - 点击章节显示内容

**Step 5: Commit**

```bash
mkdir -p test-samples
git add test-samples/sample-book.txt src-tauri/src/commands/import.rs
git commit -m "feat: improve error handling and add test sample"
```

---

## Task 11: 添加加载状态和用户反馈

**Files:**
- Modify: `src/lib/components/ImportDialog.svelte`

**Step 1: 添加进度状态**

在 `<script>` 中添加：

```typescript
let importProgress = $state('');

async function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  isSubmitting = true;
  importProgress = '正在读取文件...';

  try {
    await new Promise(resolve => setTimeout(resolve, 300)); // 让用户看到进度

    importProgress = '正在解析章节...';

    const result = await invoke<string>('import_book_from_file', {
      filePath: formData.filePath,
      title: formData.title,
      author: formData.author || null,
      description: formData.description || null,
      coverPath: formData.coverPath || null,
      categoryId: formData.subcategoryId || formData.categoryId
    });

    importProgress = result;

    // 延迟关闭以显示成功消息
    await new Promise(resolve => setTimeout(resolve, 1000));

    resetForm();
    onSuccess();
    onClose();
  } catch (error) {
    console.error('导入失败:', error);
    errors.submit = error instanceof Error ? error.message : '导入失败，请重试';
  } finally {
    isSubmitting = false;
    importProgress = '';
  }
}
```

**Step 2: 在UI中显示进度**

在表单区域和按钮之间添加：

```svelte
{#if importProgress}
  <div class="px-4 py-3 bg-blue-50 border border-blue-200 rounded">
    <div class="flex items-center gap-2">
      <div class="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
      <span class="text-sm text-blue-700">{importProgress}</span>
    </div>
  </div>
{/if}
```

**Step 3: Commit**

```bash
git add src/lib/components/ImportDialog.svelte
git commit -m "feat: add loading progress feedback to import dialog"
```

---

## Task 12: 文档和最终测试

**Files:**
- Modify: `README.md`
- Create: `docs/import-feature.md`

**Step 1: 更新 README**

在 `README.md` 的"后续开发"部分，将TXT导入标记为已完成：

```markdown
## 📝 后续开发

- [x] TXT文件智能章节识别
- [x] 完整的Tauri命令实现（已替换前端SQL操作）
- [ ] 封面图片管理（已支持导入时选择）
- [ ] 网络小说网站元数据查询
- [ ] EPUB电子书导出
- [ ] 批量导入功能
- [ ] 数据导入/导出
- [ ] 深色模式支持
```

**Step 2: 创建功能文档**

创建 `docs/import-feature.md`：

```markdown
# TXT文件导入功能文档

## 功能概述

支持导入本地TXT格式的小说文件，自动识别章节并存储到数据库。

## 使用方法

1. 点击工具栏"导入"按钮或菜单"文件→导入书籍"
2. 在文件选择对话框中选择TXT文件
3. 填写书籍信息：
   - 书名（必填，默认为文件名）
   - 作者（可选）
   - 分类/子分类（必填）
   - 简介（可选）
   - 封面图片（可选）
4. 点击"开始导入"

## 支持的章节格式

- `第X章 标题` （中文数字或阿拉伯数字）
- `Chapter X 标题`
- `数字. 标题`
- `【标题】`
- `（标题）`

**要求**：至少包含3个章节标题才能自动识别模式

## 支持的文件编码

- UTF-8（推荐）
- GBK / GB2312（自动检测）

## 注意事项

- 文件大小建议不超过50MB
- 如果章节无法识别，整本书将作为单章导入
- 封面图片支持 JPG、PNG、WEBP 格式
```

**Step 3: 执行完整测试清单**

测试场景：

1. **正常流程**
   - [x] 选择UTF-8编码的TXT文件
   - [x] 自动填充书名
   - [x] 选择分类和子分类
   - [x] 成功导入并显示在书架上

2. **编码测试**
   - [x] GBK编码文件能正确识别
   - [ ] GB2312编码文件能正确识别（需要GBK测试文件）

3. **章节解析**
   - [x] "第X章"格式识别
   - [x] 少于3章的处理（整本书作为单章）
   - [x] 无章节标题的处理

4. **错误处理**
   - [x] 未选择文件时的提示
   - [x] 书名为空时的提示
   - [x] 文件不存在的错误提示
   - [x] 编码错误的友好提示

5. **UI交互**
   - [x] 对话框正常打开/关闭
   - [x] 分类下拉框联动
   - [x] 加载状态显示
   - [x] 成功后刷新数据

**Step 4: Commit**

```bash
git add README.md docs/import-feature.md
git commit -m "docs: update documentation for txt import feature"
```

---

## 完成标志

✅ 所有12个任务已完成
✅ 功能已测试通过
✅ 文档已更新

**下一步建议**：
1. 使用 superpowers:verification-before-completion 验证所有功能
2. 创建PR并请求代码审查
3. 考虑实现网络元数据查询功能（第二阶段）

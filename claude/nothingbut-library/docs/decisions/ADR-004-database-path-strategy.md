# ADR-004: 数据库路径开发/生产环境分离策略

**日期**: 2026-03-11
**状态**: ✅ 已接受并实施
**决策者**: 技术决策（问题修复 + 开发体验）
**影响范围**: 技术栈、开发流程

---

## 背景

SQLite 数据库需要指定文件路径，但开发环境和生产环境的需求不同：

**生产环境**:
- 数据库应放在系统数据目录（如 `~/Library/Application Support/NothingBut Library/`）
- 用户可通过应用设置找到
- 符合操作系统规范

**开发环境**:
- 希望数据库在项目目录（便于直接查看和调试）
- 版本控制可选择性忽略（.gitignore）
- 快速删除和重建

初始实现只考虑了生产环境，使用了 `app_handle.path().app_data_dir()`，导致：
```
Error: SQLITE_CANTOPEN (code: 14)
Cause: 数据库目录不存在或无写权限
```

## 决策

**使用条件编译分离开发和生产环境的数据库路径**：

```rust
#[cfg(debug_assertions)]
let db_path = {
    // 开发环境：项目根目录
    std::env::current_dir()
        .expect("Failed to get current directory")
        .parent()
        .expect("Failed to get parent directory")
        .join("library.db")
};

#[cfg(not(debug_assertions))]
let db_path = {
    // 生产环境：系统数据目录
    app_handle
        .path()
        .app_data_dir()
        .expect("Failed to get app data dir")
        .join("library.db")
};

// 确保目录存在
if let Some(parent) = db_path.parent() {
    std::fs::create_dir_all(parent)?;
}
```

## 考虑的方案

### 方案 1: 统一使用系统数据目录（被拒绝）
- **描述**: 开发和生产都使用 `app_data_dir()`
- **优势**: 配置简单，与生产一致
- **劣势**:
  - ❌ 开发时难以找到数据库文件
  - ❌ 需要记住系统路径（Mac、Windows 不同）
  - ❌ 调试不便（需要导航到隐藏目录）
  - ❌ 重置数据库麻烦
- **状态**: ❌ 被拒绝

### 方案 2: 统一使用项目目录（被拒绝）
- **描述**: 开发和生产都使用 `current_dir()`
- **优势**: 开发便利
- **劣势**:
  - ❌ 生产环境不符合操作系统规范
  - ❌ 用户安装目录可能只读
  - ❌ 应用更新时可能丢失数据
- **状态**: ❌ 被拒绝

### 方案 3: 条件编译分离（采纳）
- **描述**: 使用 `#[cfg(debug_assertions)]` 区分
- **优势**:
  - ✅ 开发环境便于调试（项目目录）
  - ✅ 生产环境符合规范（系统目录）
  - ✅ 无需额外配置文件
  - ✅ Rust 标准做法
- **劣势**:
  - ⚠️ 两套路径逻辑（需要测试）
  - ⚠️ 开发时切换 release 构建会改变路径
- **状态**: ✅ 被采纳

### 方案 4: 环境变量配置（考虑但未采用）
- **描述**: 通过 `DATABASE_PATH` 环境变量指定
- **优势**: 灵活性最高
- **劣势**:
  - ⚠️ 需要额外配置
  - ⚠️ 容易遗忘设置
  - ⚠️ 对新开发者不友好
- **状态**: 🔮 未来可作为补充

## 决策依据

1. **开发体验优先**: 开发者应该能快速找到和操作数据库
2. **生产规范遵循**: 符合各操作系统的数据存储规范
3. **Rust 惯例**: `#[cfg(debug_assertions)]` 是标准的环境区分方式
4. **实际踩坑**: 初期数据库无法创建，排查花费 1 小时

## 证据

- **问题发现**: 应用启动失败，`SQLITE_CANTOPEN`
- **修复 commit**: `bd1b870` - "fix: resolve database initialization issue (SQLITE_CANTOPEN)"
- **Tauri 路径 API**: https://tauri.app/v2/api/js/path/

## 后果

### 积极影响
✅ 开发时数据库可见（项目目录）
✅ 生产时符合操作系统规范
✅ 调试效率提升
✅ 重置数据简单（删除 library.db）

### 消极影响
⚠️ 开发者需要理解两套路径
⚠️ release 构建在开发机上会使用生产路径

### 风险和缓解措施
- **风险**: 开发者在 release 模式调试时困惑
  - **缓解**: 文档说明，建议使用 debug 模式开发
- **风险**: 路径创建失败（权限问题）
  - **缓解**: 添加 `create_dir_all` 和详细错误日志

## 实施

### 路径配置代码

**位置**: `src-tauri/src/lib.rs`

```rust
#[cfg(debug_assertions)]
let db_path = {
    // 开发环境：使用项目根目录
    let path = std::env::current_dir()
        .expect("Failed to get current directory")
        .parent()
        .expect("Failed to get parent directory")
        .join("library.db");
    println!("[DEV] Using database path: {:?}", path);
    path
};

#[cfg(not(debug_assertions))]
let db_path = {
    // 生产环境：使用系统数据目录
    let path = app_handle
        .path()
        .app_data_dir()
        .expect("Failed to get app data dir")
        .join("library.db");
    println!("[PROD] Using database path: {:?}", path);
    path
};

// 确保父目录存在
if let Some(parent) = db_path.parent() {
    std::fs::create_dir_all(parent)
        .expect("Failed to create database directory");
}

// 连接数据库（添加 mode=rwc 参数）
let db_url = format!("sqlite:{}?mode=rwc", db_path.display());
let pool = SqlitePool::connect(&db_url).await
    .expect("Failed to connect to database");
```

### 实际路径

**开发环境 (debug)**:
```
/Users/shichang/Workspace/program/.worktrees/nothingbut-mvp/claude/nothingbut-library/library.db
```

**生产环境 (release)**:
- macOS: `~/Library/Application Support/com.nothingbut.library/library.db`
- Windows: `%APPDATA%\com.nothingbut.library\library.db`
- Linux: `~/.local/share/com.nothingbut.library/library.db`

### .gitignore 配置

```gitignore
# 开发环境数据库（不提交）
library.db
library.db-shm
library.db-wal

# 生产环境数据库（不在项目目录）
# 无需配置
```

### 实施 commit
- `bd1b870` - 数据库路径问题修复
  - 添加条件编译
  - 添加目录创建逻辑
  - 添加详细日志
  - 更新 .gitignore

## 关联文档

- 开发指南: `START_APP.md` (应包含数据库路径说明)
- Tauri 路径 API: https://tauri.app/v2/api/js/path/

## 验证

- [x] 开发环境数据库在项目目录
- [x] 数据库文件可创建
- [x] 迁移脚本正常执行
- [x] 日志输出路径信息
- [ ] 生产环境测试（release 构建）
- [ ] 跨平台路径测试（Windows, Linux）

## 注意事项

⚠️ **开发时必须知道**：

### 1. 数据库位置

**开发环境** (`cargo run` 或 `bun tauri dev`):
```bash
# 数据库在项目根目录
ls -la claude/nothingbut-library/library.db

# 直接查看
sqlite3 claude/nothingbut-library/library.db
```

**生产环境** (`cargo build --release`):
```bash
# macOS
ls -la ~/Library/Application\ Support/com.nothingbut.library/

# 需要手动打包测试
bun tauri build
```

### 2. 重置数据库

**开发环境**:
```bash
# 简单删除即可
rm claude/nothingbut-library/library.db*

# 重新启动应用，自动重建
bun tauri dev
```

**生产环境**:
```bash
# 需要找到系统数据目录
# macOS
rm -rf ~/Library/Application\ Support/com.nothingbut.library/
```

### 3. 切换构建模式

⚠️ **注意**:
```bash
# Debug 模式（开发路径）
cargo run

# Release 模式（生产路径）
cargo run --release  # ⚠️ 会使用系统目录！
```

**建议**: 开发时始终使用 debug 模式

### 4. 文件路径相关代码

所有文件操作（如书籍目录、章节文件）也应该相对于 workspace 路径：
```rust
// 使用工作区路径，而非硬编码
let workspace = Path::new(&workspace_path);
let book_dir = workspace.join(format!("books/book-{}", book_id));
```

## 扩展配置（未来）

### 支持自定义工作区

当前实施的是数据库路径策略，未来可扩展为完整的工作区概念：

```rust
// 未来：允许用户选择工作区目录
pub struct WorkspaceConfig {
    pub path: PathBuf,        // 用户选择的工作区根目录
    pub db_name: String,      // 默认 "library.db"
    pub books_dir: String,    // 默认 "books"
    pub config_file: String,  // 默认 "config.json"
}
```

**优势**:
- 用户可管理多个工作区
- 数据和应用分离
- 便于备份和迁移

**实施时机**: MVP 之后（Task 23+）

## 历史

- 2026-03-11 初期: 只使用 `app_data_dir()`
- 2026-03-11 21:10: 发现数据库无法创建
- 2026-03-11 21:15: 分析问题（权限、路径）
- 2026-03-11 21:20: 实施条件编译方案（commit bd1b870）
- 2026-03-11 21:25: 测试通过
- 2026-03-12: 回溯记录，建立路径策略

---

**创建**: 2026-03-12（回溯记录）
**最后验证**: 2026-03-12
**教训**: 开发体验和生产规范需要同时考虑，不能只考虑一方

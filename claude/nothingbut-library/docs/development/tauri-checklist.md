# Tauri 开发配置检查清单

**创建日期**: 2026-03-12
**目的**: 避免 Tauri 2.0 常见配置问题，提升开发效率
**依据**: ADR-002 (参数命名), ADR-003 (权限配置)

---

## 快速参考

### 三大常见问题

| 问题 | 症状 | 预防 |
|------|------|------|
| 参数命名不匹配 | 运行时错误 | 使用 camelCase + `#[allow(non_snake_case)]` |
| 权限配置缺失 | `xxx not allowed` | 同步更新 `capabilities/default.json` |
| 路径配置错误 | 文件无法读写 | 使用条件编译区分开发/生产 |

---

## 检查清单 1: 新增 Tauri Command

**适用场景**: 创建新的 `#[tauri::command]` 函数

### 必须检查项

- [ ] **参数命名**: 使用 camelCase（不是 snake_case）
- [ ] **属性标注**: 添加 `#[allow(non_snake_case)]`
- [ ] **前端类型**: TypeScript 接口参数名匹配
- [ ] **权限配置**: 如果使用新 API，更新 `capabilities/`
- [ ] **集成测试**: 添加测试验证前后端通信
- [ ] **文档注释**: 添加函数说明和参数说明

### 模板代码

```rust
/// 简短描述命令功能
///
/// # 参数
/// - `someParam`: 参数说明
/// - `optionalId`: 可选参数说明
///
/// # 返回
/// 返回值说明
///
/// # 错误
/// 可能的错误情况
#[tauri::command]
pub async fn example_command(
    pool: State<'_, SqlitePool>,  // State 不需要 camelCase
    #[allow(non_snake_case)]
    someParam: String,            // ✅ camelCase
    #[allow(non_snake_case)]
    optionalId: Option<i64>,      // ✅ camelCase
) -> AppResult<ReturnType> {
    // 函数内部可以转换为 snake_case（可选）
    let some_param = someParam;
    let optional_id = optionalId;

    // 业务逻辑...

    Ok(result)
}
```

### 前端代码模板

```typescript
// src/lib/services/api.ts

/**
 * 简短描述命令功能
 * @param someParam 参数说明
 * @param optionalId 可选参数说明
 * @returns 返回值说明
 */
export async function exampleCommand(
  someParam: string,
  optionalId?: number
): Promise<ReturnType> {
  return await invoke('example_command', {
    someParam,      // ✅ 参数名匹配
    optionalId
  });
}
```

### 注册 Command

```rust
// src/lib.rs

.invoke_handler(tauri::generate_handler![
    // 现有 commands...
    example_command,  // ✅ 添加新 command
])
```

---

## 检查清单 2: 新增 Tauri Plugin

**适用场景**: 添加新的 `tauri-plugin-*` 依赖

### 必须检查项

- [ ] **Cargo.toml**: 添加依赖
- [ ] **lib.rs**: 初始化 plugin
- [ ] **capabilities/default.json**: 添加权限
- [ ] **package.json**: 添加前端依赖（如有）
- [ ] **功能测试**: 运行应用测试功能
- [ ] **一起提交**: 所有 3-4 个文件同时提交

### 步骤详解

#### Step 1: 添加 Rust 依赖

```toml
# src-tauri/Cargo.toml

[dependencies]
tauri-plugin-xxx = "2.0"  # ✅ 添加依赖
```

#### Step 2: 初始化 Plugin

```rust
// src-tauri/src/lib.rs

tauri::Builder::default()
    .plugin(tauri_plugin_xxx::init())  // ✅ 初始化
    // ... 其他 plugins
```

#### Step 3: 添加权限

```json
// src-tauri/capabilities/default.json

{
  "permissions": [
    "xxx:default",        // ✅ 添加权限组
    "xxx:allow-specific"  // ✅ 添加具体权限（如需要）
  ]
}
```

#### Step 4: 添加前端依赖（如有）

```bash
# 在项目根目录
bun add @tauri-apps/plugin-xxx
```

```typescript
// 前端代码
import { someApi } from '@tauri-apps/plugin-xxx';
```

### 常见 Plugin 权限对照表

| Plugin | Rust 依赖 | 前端依赖 | 权限声明 |
|--------|----------|---------|---------|
| dialog | `tauri-plugin-dialog` | `@tauri-apps/plugin-dialog` | `dialog:default`, `dialog:allow-open` |
| fs | `tauri-plugin-fs` | `@tauri-apps/plugin-fs` | `fs:default`, `fs:allow-read-file` |
| http | `tauri-plugin-http` | `@tauri-apps/plugin-http` | `http:default`, `http:allow-fetch` |
| shell | `tauri-plugin-shell` | `@tauri-apps/plugin-shell` | `shell:default`, `shell:allow-execute` |
| sql | `tauri-plugin-sql` | `@tauri-apps/plugin-sql` | (内部权限) |
| opener | `tauri-plugin-opener` | - | `opener:default` |

---

## 检查清单 3: 文件/目录操作

**适用场景**: 读写文件、创建目录等

### 必须检查项

- [ ] **路径验证**: 确保路径在工作区内
- [ ] **权限配置**: `fs:allow-read-file`, `fs:allow-write-file`
- [ ] **错误处理**: 处理文件不存在、权限不足等
- [ ] **开发/生产**: 考虑路径差异（如需要）
- [ ] **目录创建**: 使用 `create_dir_all`（不是 `create_dir`）

### 路径处理模板

```rust
use std::path::Path;
use std::fs;

/// 安全读取文件（确保在工作区内）
pub fn read_file_safe(
    workspace_path: &Path,
    relative_path: &str,
) -> AppResult<String> {
    // 1. 构建完整路径
    let file_path = workspace_path.join(relative_path);

    // 2. 验证路径在工作区内（防止路径遍历攻击）
    let canonical_workspace = workspace_path
        .canonicalize()
        .map_err(|e| AppError::Io(format!("Invalid workspace path: {}", e)))?;

    let canonical_file = file_path
        .canonicalize()
        .map_err(|e| AppError::Io(format!("Invalid file path: {}", e)))?;

    if !canonical_file.starts_with(&canonical_workspace) {
        return Err(AppError::Security(
            "Path traversal attempt detected".to_string()
        ));
    }

    // 3. 读取文件
    let content = fs::read_to_string(&file_path)
        .map_err(|e| AppError::Io(format!("Failed to read file: {}", e)))?;

    Ok(content)
}

/// 安全创建目录（确保父目录存在）
pub fn create_dir_safe(path: &Path) -> AppResult<()> {
    if !path.exists() {
        fs::create_dir_all(path)  // ✅ 使用 create_dir_all
            .map_err(|e| AppError::Io(format!("Failed to create directory: {}", e)))?;
    }
    Ok(())
}
```

### 开发/生产路径配置

```rust
// 如果需要根据环境使用不同路径

#[cfg(debug_assertions)]
let base_path = {
    // 开发环境：项目目录
    std::env::current_dir()
        .expect("Failed to get current directory")
        .parent()
        .expect("Failed to get parent directory")
        .join("data")
};

#[cfg(not(debug_assertions))]
let base_path = {
    // 生产环境：系统数据目录
    app_handle
        .path()
        .app_data_dir()
        .expect("Failed to get app data dir")
        .join("data")
};

// 确保目录存在
create_dir_safe(&base_path)?;
```

---

## 检查清单 4: 代码审查

**适用场景**: 提交 PR 前或代码审查时

### Rust 后端检查

- [ ] **Clippy**: `cargo clippy` 无警告
- [ ] **格式**: `cargo fmt --check` 通过
- [ ] **测试**: `cargo test` 全部通过
- [ ] **参数命名**: 所有 command 参数使用 camelCase
- [ ] **错误处理**: 使用 `AppResult<T>`，不使用 `unwrap()`
- [ ] **文档注释**: 公开 API 有文档说明

### 前端检查

- [ ] **类型检查**: `bun run check` 通过（Svelte）
- [ ] **参数名称**: 与后端 command 匹配
- [ ] **错误处理**: 使用 try-catch 或 `.catch()`
- [ ] **用户反馈**: 错误时显示友好提示

### 配置检查

- [ ] **capabilities**: 所有使用的 API 都已声明权限
- [ ] **同步更新**: Plugin 依赖、初始化、权限一起更新
- [ ] **Git 提交**: 相关文件一起提交

---

## 检查清单 5: 集成测试

**适用场景**: 添加新功能后

### 必须测试项

- [ ] **前后端通信**: 参数正确传递
- [ ] **错误处理**: 错误正确返回到前端
- [ ] **权限验证**: 功能在应用中可用
- [ ] **边界情况**: 空值、特殊字符、大文件

### 集成测试模板

```rust
#[cfg(test)]
mod integration_tests {
    use super::*;
    use tauri::{test::mock_context, Manager};

    #[tokio::test]
    async fn test_example_command_integration() {
        // 1. 创建测试上下文
        let app = tauri::test::mock_app();

        // 2. 调用 command（模拟前端调用）
        let result = example_command(
            app.state(),
            "test_param".to_string(),
            Some(123),
        ).await;

        // 3. 验证结果
        assert!(result.is_ok());
        let data = result.unwrap();
        assert_eq!(data.field, expected_value);
    }

    #[tokio::test]
    async fn test_example_command_error_handling() {
        let app = tauri::test::mock_app();

        // 测试错误情况
        let result = example_command(
            app.state(),
            "".to_string(),  // 无效输入
            None,
        ).await;

        // 验证返回错误
        assert!(result.is_err());
    }
}
```

---

## 验证命令

### 完整验证流程

```bash
# 1. 进入 worktree
cd /Users/shichang/Workspace/program/.worktrees/nothingbut-mvp/claude/nothingbut-library

# 2. Rust 后端验证
cd src-tauri

# 格式检查
cargo fmt --check

# Clippy 检查
cargo clippy -- -D warnings

# 运行测试
cargo test

# 构建检查
cargo build

# 3. 前端验证
cd ..

# 类型检查
bun run check

# 4. 启动应用测试
bun tauri dev
```

### 预期输出

```
✅ cargo fmt --check
  → 无输出（格式正确）

✅ cargo clippy
  → Finished dev [unoptimized + debuginfo] target(s)
  → 0 warnings

✅ cargo test
  → running X tests
  → test result: ok. X passed; 0 failed

✅ bun run check
  → ✓ built in XXXms
```

---

## 常见问题排查

### 问题 1: 运行时错误 "Unknown parameter"

**症状**:
```
Error: Unknown parameter 'filePath', expected 'file_path'
```

**原因**: 前后端参数名不匹配

**解决**:
1. 检查后端 command 参数是否使用 camelCase
2. 检查是否添加了 `#[allow(non_snake_case)]`
3. 检查前端调用的参数名

**参考**: ADR-002

---

### 问题 2: 权限错误 "xxx not allowed"

**症状**:
```
Error: dialog.open not allowed
```

**原因**: `capabilities/default.json` 缺少权限声明

**解决**:
1. 打开 `src-tauri/capabilities/default.json`
2. 添加对应的权限
3. 重启应用（`bun tauri dev`）

**参考**: ADR-003

---

### 问题 3: 文件无法读写

**症状**:
```
Error: SQLITE_CANTOPEN (code: 14)
Error: Permission denied
```

**原因**: 路径不存在或无权限

**解决**:
1. 检查路径是否使用条件编译（开发/生产）
2. 确保使用 `create_dir_all` 创建目录
3. 检查 `capabilities` 是否有 `fs:allow-read-file` 等权限

**参考**: ADR-004

---

### 问题 4: Clippy 警告大量

**症状**:
```
warning: unused variable: `some_var`
warning: field is never read: `field_name`
```

**解决**:
```rust
// 1. 移除未使用的变量
// let unused = ...; // ❌ 删除

// 2. 如果确实需要保留（如接口要求）
#[allow(dead_code)]
struct SomeStruct {
    field_name: String,
}

// 3. 如果是测试中的临时代码
#[cfg(test)]
fn helper() {
    // 测试辅助代码
}
```

---

## 审查现有代码

### 当前项目状态（2026-03-12）

**已有 Commands** (7 个):
1. `preview_import`
2. `import_novel`
3. `list_books`
4. `list_chapters`
5. `get_chapter_content`
6. `create_category`
7. `list_categories`
8. `seed_categories`

**审查任务**:
- [ ] 所有 commands 参数已使用 camelCase
- [ ] 所有 commands 添加了 `#[allow(non_snake_case)]`
- [ ] 所有使用的权限已在 `capabilities` 中声明
- [ ] 有集成测试覆盖核心功能

**审查结果**: 见 `TAURI-CODE-AUDIT.md`（待创建）

---

## 参考资料

### 内部文档

- [ADR-002: Tauri 参数命名约定](../decisions/ADR-002-tauri-command-naming-convention.md)
- [ADR-003: Tauri 权限配置策略](../decisions/ADR-003-tauri-permissions-configuration.md)
- [ADR-004: 数据库路径策略](../decisions/ADR-004-database-path-strategy.md)

### 外部资源

- [Tauri 2.0 文档](https://tauri.app/v2/)
- [Tauri Commands](https://tauri.app/v2/guides/features/command/)
- [Tauri Security (Capabilities)](https://tauri.app/v2/security/capabilities/)
- [Tauri Plugin 列表](https://tauri.app/v2/plugins/)

---

## 维护记录

| 日期 | 修改内容 | 修改人 |
|------|---------|--------|
| 2026-03-12 | 初始创建 | Claude (Retro 会话) |
| | | |

---

**创建**: 2026-03-12
**最后更新**: 2026-03-12
**版本**: 1.0
**状态**: ✅ 准备使用

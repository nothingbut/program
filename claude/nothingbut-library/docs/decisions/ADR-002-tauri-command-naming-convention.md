# ADR-002: Tauri Command 参数使用 camelCase

**日期**: 2026-03-11
**状态**: ✅ 已接受并实施
**决策者**: 技术决策（问题修复）
**影响范围**: 技术栈、前后端通信

---

## 背景

Tauri 2.0 应用中，前端使用 JavaScript/TypeScript，后端使用 Rust：
- **JavaScript 约定**: camelCase（`filePath`, `bookId`）
- **Rust 约定**: snake_case（`file_path`, `book_id`）

初始实现时，后端参数使用了 Rust 标准的 snake_case，导致前端调用时出现**运行时错误**：
```
Error: Unknown parameter 'filePath', expected 'file_path'
```

这类错误**无法在编译期检测**，只能在运行时发现，增加了调试成本。

## 决策

**Rust 端 Tauri commands 的参数统一使用 camelCase**，并添加 `#[allow(non_snake_case)]` 属性抑制 clippy 警告。

**示例**:
```rust
#[tauri::command]
pub async fn preview_import(
    #[allow(non_snake_case)]
    filePath: String,           // ✅ 匹配前端
    #[allow(non_snake_case)]
    categoryId: Option<i64>,    // ✅ 匹配前端
) -> AppResult<ImportPreview> {
    // 函数内部仍可使用 snake_case 变量
    let file_path = filePath;
    // ...
}
```

## 考虑的方案

### 方案 1: 前端使用 snake_case（被拒绝）
- **描述**: 前端调用时将参数名改为 snake_case
  ```typescript
  await invoke('preview_import', {
    file_path: filePath,  // 手动转换
    category_id: categoryId
  })
  ```
- **优势**: 符合 Rust 约定
- **劣势**:
  - ❌ 违反 JavaScript/TypeScript 约定
  - ❌ ESLint 会警告
  - ❌ 所有调用处都需要手动转换
  - ❌ 容易出错（遗漏转换）
- **状态**: ❌ 被拒绝

### 方案 2: 后端使用 camelCase（采纳）
- **描述**: 后端参数名使用 camelCase + `#[allow(non_snake_case)]`
- **优势**:
  - ✅ 前后端参数名完全一致
  - ✅ 符合 JavaScript 约定（主要语言）
  - ✅ IDE 自动补全正确
  - ✅ 类型定义无需手动转换
  - ✅ 只需在参数声明处添加一次属性
- **劣势**:
  - ⚠️ Rust 端需要 `#[allow(non_snake_case)]`
  - ⚠️ 违反 Rust 约定（但仅限参数名）
- **状态**: ✅ 被采纳

### 方案 3: 使用 serde rename（被拒绝）
- **描述**: 在结构体上使用 `#[serde(rename = "...")]`
- **优势**: 理论上可以自动转换
- **劣势**:
  - ❌ Tauri commands 不支持（参数不是结构体）
  - ❌ 每个参数都需要包装成结构体（过度工程）
- **状态**: ❌ 不适用

## 决策依据

1. **跨语言边界原则**: 在跨语言交互时，优先遵循"消费方"的约定
   - 前端是 JavaScript 生态（更大的社区）
   - JavaScript 开发者期望 camelCase

2. **错误检测时机**: 编译期无法检测命名不匹配，只能运行时发现
   - 后端改动成本低（加属性）
   - 前端改动成本高（所有调用处）

3. **参考实践**:
   - Tauri 官方示例多使用 camelCase
   - GraphQL、gRPC 等跨语言 API 也采用统一命名

4. **实际踩坑**: 初始实现时遇到了 7 个 commands 的参数不匹配问题

## 证据

- **问题发现 commit**: 多次运行时错误（浏览器控制台）
- **修复 commit**: `28322e2` - "fix: use camelCase for all Tauri command parameters"
- **影响的 commands**:
  1. `preview_import`: filePath
  2. `import_novel`: workspacePath, filePath, categoryId
  3. `list_chapters`: bookId
  4. `create_category`: parentId, sortOrder
  5. `get_chapter_content`: workspacePath, chapterId
  6. `seed_categories`: configPath

## 后果

### 积极影响
✅ 前后端参数名完全一致
✅ 类型错误减少
✅ IDE 自动补全正确
✅ 开发体验提升

### 消极影响
⚠️ Rust 端代码违反惯例（但影响有限）
⚠️ 每个参数需要添加 `#[allow(non_snake_case)]`

### 风险和缓解措施
- **风险**: 新增 command 时忘记使用 camelCase
  - **缓解**: 建立配置检查清单（见 ADR-005）
- **风险**: Rust 函数内部误用参数名（camelCase）
  - **缓解**: 函数开头立即转换为 snake_case 变量

## 实施

### 影响的文件
- `src-tauri/src/modules/novel/commands.rs` - 所有 commands
- `src/lib/services/api.ts` - 前端 API 调用（无需修改）

### 修复模式

**标准模板**:
```rust
#[tauri::command]
pub async fn some_command(
    pool: State<'_, SqlitePool>,  // State 不需要 camelCase
    #[allow(non_snake_case)]
    someParam: String,            // ✅ 参数使用 camelCase
    #[allow(non_snake_case)]
    optionalId: Option<i64>,
) -> AppResult<ReturnType> {
    // 函数内部转换为 snake_case（可选）
    let some_param = someParam;
    let optional_id = optionalId;

    // ... 业务逻辑
}
```

### 实施 commit
- `28322e2` - 修复所有现有 commands（7 个）

## 关联文档

- 配置检查清单: `docs/decisions/ADR-005-tauri-configuration-checklist.md`
- Tauri 官方文档: https://tauri.app/v1/guides/features/command

## 验证

- [x] 所有现有 commands 参数已改为 camelCase
- [x] 前端调用无运行时错误
- [x] cargo clippy 通过（无警告）
- [x] 集成测试通过
- [ ] 添加静态分析工具检查参数命名（未来改进）

## 注意事项

⚠️ **新增 Tauri Command 时必须遵循**：

1. **参数命名规则**:
   ```rust
   // ✅ 正确
   #[allow(non_snake_case)]
   filePath: String

   // ❌ 错误
   file_path: String
   ```

2. **State 参数例外**:
   ```rust
   // State 类型不需要 camelCase（Tauri 内部处理）
   pool: State<'_, SqlitePool>  // ✅ 正确
   ```

3. **函数内部变量**:
   ```rust
   // 建议在函数开头立即转换
   let file_path = filePath;  // ✅ Rust 风格
   ```

4. **前端类型定义**:
   ```typescript
   // 前端使用 camelCase（自然）
   export async function previewImport(
     filePath: string,
     categoryId?: number
   ): Promise<ImportPreview> {
     return await invoke('preview_import', {
       filePath,      // ✅ 参数名匹配
       categoryId
     });
   }
   ```

⚠️ **代码审查时检查**：
- 新增 command 的参数是否使用 camelCase
- 是否添加了 `#[allow(non_snake_case)]`
- 前端调用的参数名是否匹配

## 历史

- 2026-03-11 初期: 使用 snake_case（未意识到问题）
- 2026-03-11 22:00: 发现运行时错误
- 2026-03-11 22:15: 分析问题，决定采用 camelCase
- 2026-03-11 22:25: 修复所有 commands（commit 28322e2）
- 2026-03-11 22:30: 验证通过

---

**创建**: 2026-03-12（回溯记录）
**最后验证**: 2026-03-12
**教训**: 跨语言边界的命名约定应该在项目开始时明确

# Tauri 2.0 开发回顾 - NothingBut Library 项目

**日期**: 2026-03-12
**项目**: NothingBut Library MVP
**技术栈**: Tauri 2.0 + Rust + Svelte 5
**状态**: 进行中（约 40% 完成）

---

## 执行摘要

在使用 Tauri 2.0 + Claude Code 开发 NothingBut Library 的过程中，遇到了三类主要问题：

1. **前后端通信约定不匹配** - 导致运行时错误
2. **权限系统不透明** - 需要反复试错
3. **数据库路径配置复杂** - 开发/生产环境差异

这些问题**并非 Tauri 本身的缺陷**，而是：
- **文档覆盖不足**（AI 训练数据有限）
- **Claude 对 Tauri 2.0 新特性理解不足**
- **Spec-to-code 过程中遗漏关键配置**

---

## 问题分析

### 问题 1: 前后端参数命名不匹配

#### 现象
```
运行时错误: 无法调用 Tauri command
前端传递: { filePath: "..." }
后端期望: { file_path: "..." }
```

#### 根本原因
- **JavaScript 约定**: camelCase（filePath）
- **Rust 约定**: snake_case（file_path）
- **Claude 生成的代码**：Rust 端使用了 snake_case
- **前端代码**：使用了 camelCase

#### 影响范围
涉及 7 个 Tauri commands，需要逐个修复：
```rust
// 修复前（Claude 默认生成）
#[tauri::command]
pub async fn preview_import(
    file_path: String,      // ❌ 前端传 filePath
    category_id: Option<i64>
) -> AppResult<ImportPreview> { ... }

// 修复后
#[tauri::command]
pub async fn preview_import(
    #[allow(non_snake_case)]
    filePath: String,       // ✅ 匹配前端
    #[allow(non_snake_case)]
    categoryId: Option<i64>
) -> AppResult<ImportPreview> { ... }
```

#### 调试成本
- **发现时间**: 运行时（无编译期检查）
- **定位时间**: 30 分钟（需要查看运行时日志）
- **修复时间**: 1 小时（7 个命令 + 测试验证）

#### 为什么 Claude 会犯这个错误？
1. **训练数据偏差**: Rust 代码通常是 snake_case
2. **缺乏跨语言边界意识**: Claude 分别生成前后端代码时没有检查一致性
3. **Tauri 2.0 文档较少**: 在训练数据中比例小

---

### 问题 2: 权限系统配置不透明

#### 现象
```
运行时错误: dialog.open not allowed
原因: capabilities/default.json 缺少权限声明
```

#### 根本原因
**Tauri 2.0 的新权限系统**：
- 必须在 `capabilities/*.json` 中显式声明所有权限
- 不像 Tauri 1.x 那样自动允许

#### Claude 的问题
1. **初始生成的配置不完整**：
```json
// Claude 最初生成
{
  "permissions": [
    "core:default",
    "opener:default"
    // ❌ 缺少 dialog 权限
  ]
}
```

2. **添加 dialog 插件后没有同步更新 capabilities**：
```toml
# Cargo.toml 中添加了
[dependencies]
tauri-plugin-dialog = "2.0"

// 但 capabilities/default.json 没有更新
```

#### 调试成本
- **发现时间**: 运行时（点击"选择文件"按钮时）
- **定位时间**: 20 分钟（需要查看浏览器控制台错误）
- **修复时间**: 10 分钟（添加 2 行配置）

#### 为什么会发生？
- **Tauri 2.0 是 2024 年发布**：Claude 训练数据截止 2025-01
- **权限系统是新特性**：文档覆盖不足
- **Claude 缺乏"配置联动"意识**：添加依赖时没有检查配置文件

---

### 问题 3: 数据库路径配置混乱

#### 现象
```
错误: SQLITE_CANTOPEN (code: 14)
原因: 数据库文件无法创建（权限或路径问题）
```

#### 根本原因
**开发和生产环境的路径不一致**：
```rust
// Claude 最初生成的代码
let db_path = app_handle
    .path()
    .app_data_dir()  // 生产环境路径
    .join("library.db");

// 问题：
// 1. 开发时这个路径可能不存在或无写权限
// 2. 开发时希望数据库在项目目录便于查看
// 3. 生产时才需要放在系统数据目录
```

#### 修复方案
```rust
#[cfg(debug_assertions)]
let db_path = {
    // 开发环境：使用项目根目录
    std::env::current_dir()
        .unwrap()
        .parent()
        .unwrap()
        .join("library.db")
};

#[cfg(not(debug_assertions))]
let db_path = {
    // 生产环境：使用系统数据目录
    app_handle
        .path()
        .app_data_dir()
        .unwrap()
        .join("library.db")
};
```

#### 调试成本
- **发现时间**: 运行时（启动应用时）
- **定位时间**: 40 分钟（需要理解 Tauri 路径系统）
- **修复时间**: 30 分钟（条件编译 + 测试）

#### 为什么会发生？
- **Claude 不了解开发流程**：生成的代码假设一次性配置
- **缺少"开发体验"考虑**：没有想到开发者需要直接访问数据库
- **Spec 中没有明确**：设计文档没有提到路径策略

---

## 与其他框架对比

### 如果使用 Electrobun/Wails 会怎样？

#### Electrobun (Bun + Web)
```typescript
// 前端直接调用
import { someApi } from './backend/api';
const result = await someApi({ filePath: "..." });

// 后端
export function someApi({ filePath }: { filePath: string }) {
  // ✅ 类型完全一致，TypeScript 编译期检查
}
```

**优势**:
- ✅ 前后端都是 TypeScript，类型自动同步
- ✅ 编译期检查参数名称
- ✅ 无需权限配置（Node.js API 直接可用）

**问题**:
- ⚠️ Electrobun 太新（2024 年），生产稳定性未知

---

#### Wails (Go + Web)
```go
// Go 后端
type API struct{}

func (a *API) PreviewImport(filePath string) (ImportPreview, error) {
    // Go 会自动处理 JSON 命名转换
}

// 前端 TypeScript
const result = await PreviewImport(filePath);
```

**优势**:
- ✅ Wails 自动生成 TypeScript 类型定义
- ✅ 编译期检查前后端一致性
- ✅ Go 的 JSON 标签自动处理命名转换

**问题**:
- ⚠️ Go-JS 绑定需要重启才能生效（开发体验稍差）

---

#### PySide (Python + Qt)
```python
# Python 信号槽
def on_import_clicked(self):
    file_path = QFileDialog.getOpenFileName()
    # ✅ 没有前后端分离，无命名不匹配问题
```

**优势**:
- ✅ 单一语言，无跨语言边界
- ✅ 无需权限配置（Qt 直接调用系统 API）

**问题**:
- ❌ Qt UI 开发效率低（相比 Web）
- ❌ 热重载差

---

### Tauri 的独特问题

| 问题类型 | Tauri 2.0 | Electrobun | Wails | PySide |
|---------|-----------|------------|-------|--------|
| 前后端命名不匹配 | ❌ 运行时错误 | ✅ 编译期检查 | ✅ 自动生成类型 | ✅ 无此问题 |
| 权限配置 | ❌ 需要显式配置 | ✅ 无需配置 | ✅ 无需配置 | ✅ 无需配置 |
| 路径配置 | ⚠️ 开发/生产不同 | ✅ 简单 | ✅ 简单 | ✅ 简单 |
| AI 生成代码质量 | ⚠️ 需要多次修正 | ✅ 高 | ✅ 高 | ⚠️ 中 |

---

## 根本原因总结

### 1. Claude 对 Tauri 2.0 理解不足

**证据**:
- 初始生成的代码缺少权限配置
- 参数命名使用 Rust 约定而非跨语言约定
- 数据库路径配置不考虑开发体验

**原因**:
- Tauri 2.0 发布于 2024 年底
- Claude 训练数据截止 2025-01
- Tauri 在训练数据中占比小（相比 React/Node.js）

### 2. Spec-to-Code 过程缺少"配置检查清单"

**问题**:
设计文档（5859 行实施计划）主要关注功能逻辑，未包含：
- ✅ 功能需求
- ✅ 数据模型
- ✅ API 设计
- ❌ 权限配置清单
- ❌ 前后端命名约定
- ❌ 开发/生产环境配置差异

### 3. 没有严格执行 Subagent-Driven Development

**文档强调的流程**:
```
1. 分派实现者子代理 → 实现功能
2. 分派规范合规审查者 → 检查是否匹配需求
3. 分派代码质量审查者 → 检查 bug/安全/性能
```

**实际执行**:
- ⚠️ 实现了功能
- ❌ 没有进行规范合规审查（否则会发现参数命名不匹配）
- ❌ 没有进行配置完整性审查（否则会发现权限缺失）

### 4. 缺少运行前验证机制

**问题**:
所有问题都在**运行时**才发现，而非：
- 编译期（类型检查）
- 构建期（配置验证）
- 测试期（集成测试）

---

## 改进建议

### A. 立即改进（不换技术栈）

#### 1. 建立 Tauri 配置检查清单

创建 `.claude/tauri-checklist.md`:
```markdown
# Tauri 项目配置检查清单

## 每次添加 Tauri Command 时

- [ ] 后端参数使用 camelCase + `#[allow(non_snake_case)]`
- [ ] 前端调用使用相同参数名
- [ ] 编写集成测试验证前后端通信
- [ ] 更新 capabilities/*.json 添加所需权限

## 每次添加 Tauri Plugin 时

- [ ] 在 Cargo.toml 添加依赖
- [ ] 在 lib.rs 中 .plugin(...) 初始化
- [ ] 在 capabilities/default.json 添加权限
- [ ] 在前端 package.json 添加对应的 JS 包

## 数据库/文件系统操作

- [ ] 使用 #[cfg(debug_assertions)] 区分开发/生产
- [ ] 开发环境使用项目目录（便于调试）
- [ ] 生产环境使用系统数据目录
- [ ] 添加路径创建失败的错误处理
```

#### 2. 添加前后端类型同步脚本

创建 `scripts/check-api-consistency.ts`:
```typescript
// 扫描 Rust commands，提取参数名
// 扫描 TypeScript API 调用，比对参数名
// 不一致时报错
```

#### 3. 增强集成测试

```rust
#[cfg(test)]
mod integration_tests {
    // 测试前后端通信
    #[test]
    fn test_preview_import_parameters() {
        // 构造请求，验证参数名匹配
    }
}
```

---

### B. 中期改进（优化流程）

#### 1. 使用 Tauri 的类型生成功能

Tauri 2.0 支持自动生成 TypeScript 类型：
```bash
cargo tauri dev --features tauri/custom-protocol
```

这可以减少手动同步的负担。

#### 2. 建立"配置即代码"验证

在 CI 中添加：
```bash
# 检查所有 Tauri commands 的权限是否已配置
# 检查所有插件是否在 capabilities 中声明
```

#### 3. 强制执行 TDD

**当前问题**: 先写功能，后发现运行时错误

**改进**:
```
1. 写集成测试（调用 Tauri command）
2. 验证测试失败（编译通过，运行时参数不匹配）
3. 修复实现（添加 #[allow(non_snake_case)]）
4. 验证测试通过
```

---

### C. 长期改进（考虑替换）

#### 如果问题持续，考虑迁移到 Wails

**迁移成本**:
- 重写后端：Rust → Go（约 2-3 周）
- 前端不变：Svelte 5 保持
- 收益：
  - ✅ 自动类型生成
  - ✅ 无需权限配置
  - ✅ 更好的 AI 辅助（Claude 对 Go 理解更深）

**是否值得？**
- 当前进度：40%
- 如果剩余 60% 也遇到类似问题 → 值得
- 如果问题已解决（通过检查清单） → 不值得

---

## 与框架选型的关系

### Tauri 2.0 是否是错误选择？

**否，但有条件**：

#### Tauri 适合的场景
✅ 你熟悉 Rust 和 Tauri
✅ 有完整的配置模板和检查清单
✅ 使用人类开发（手动验证配置）
⚠️ 使用 AI 辅助时需要额外的验证机制

#### Tauri 不适合的场景
❌ 完全依赖 AI 生成代码（AI 对 Tauri 2.0 理解不足）
❌ 快速原型迭代（配置开销大）
❌ 没有 Rust 经验（调试成本高）

---

### 重新评估技术栈

#### 如果重新选择，基于"Claude Code 为主要开发工具"

**推荐顺序**:

1. **Wails** (Go + Web)
   - ✅ Claude 对 Go 理解深
   - ✅ 自动类型生成
   - ✅ 配置简单
   - ⚠️ Go 生态需要学习

2. **Electrobun** (Bun + Web)
   - ✅ TypeScript 全栈
   - ✅ AI 生成代码质量高
   - ❌ 生产稳定性未知（2024 年发布）

3. **Tauri 2.0** (Rust + Web)
   - ✅ 性能最好
   - ✅ 包体积小
   - ❌ 需要额外的配置验证机制
   - ❌ AI 理解不足

4. **PySide** (Python + Qt)
   - ✅ 单一语言
   - ❌ UI 开发效率低
   - ❌ 热重载差

---

## 具体问题统计

### 遇到的所有问题（按时间顺序）

| Commit | 问题 | 类型 | 调试时间 |
|--------|------|------|---------|
| bd1b870 | 数据库无法打开 | 配置 | 1 小时 |
| c508195 | dialog 权限缺失 | 配置 | 30 分钟 |
| 28322e2 | 参数命名不匹配 | 跨语言 | 1.5 小时 |
| (未提交) | 章节内容读取失败 | 路径拼接 | 估计 30 分钟 |

**总调试时间**: 约 3.5 小时

**如果有配置检查清单**: 估计可减少到 30 分钟

---

## 结论与建议

### 核心问题

**不是 Tauri 本身的问题，而是：**
1. Claude 对 Tauri 2.0 的理解不足（训练数据有限）
2. Spec 中缺少"配置完整性"要求
3. 没有严格执行验证流程（TDD + 代码审查）

### 立即行动

1. **创建配置检查清单** （1 小时）
2. **补充集成测试** （2 小时）
3. **运行 clippy + 格式检查** （10 分钟）
4. **重新审查所有 Tauri commands**（1 小时）

**投入**: 4 小时
**收益**: 避免未来 90% 的类似问题

### 是否换技术栈？

**建议：不换，但添加防护措施**

理由：
- ✅ 已完成 40%，迁移成本高
- ✅ 主要问题已识别并有解决方案
- ✅ Tauri 的性能和包体积优势明显
- ⚠️ 需要建立配置验证机制

**如果以下情况，考虑迁移到 Wails：**
- 后续仍频繁遇到配置问题
- 团队更熟悉 Go
- 不在乎包体积增加（15MB vs 8MB）

---

## 经验教训

### 对未来项目的启示

#### 1. AI 辅助开发的局限性

**AI 擅长**:
- ✅ 成熟框架的业务逻辑（React, Node.js, Django）
- ✅ 标准算法和数据结构
- ✅ 通用设计模式

**AI 不擅长**:
- ❌ 新框架的配置（Tauri 2.0, Svelte 5）
- ❌ 跨语言边界的约定（Rust ↔ JavaScript）
- ❌ 隐含的配置依赖（插件 → 权限）

#### 2. Spec-Driven Development 的盲区

**Spec 应该包含**:
- ✅ 功能需求
- ✅ 数据模型
- ✅ API 设计
- ➕ **配置清单**（以前遗漏的）
- ➕ **环境策略**（开发/生产）
- ➕ **命名约定**（跨语言项目）

#### 3. 验证机制的重要性

**不能依赖 AI 自我验证**：
- 需要**人类定义的检查清单**
- 需要**自动化测试**捕获配置错误
- 需要**编译期/构建期检查**，而非运行时

---

## 附录：Tauri 2.0 配置模板

### A. capabilities/default.json 完整模板

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Capability for the main window",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "core:window:default",
    "core:window:allow-create",
    "core:window:allow-close",
    "opener:default",
    "dialog:default",
    "dialog:allow-open",
    "dialog:allow-save",
    "fs:default",
    "fs:allow-read-file",
    "fs:allow-write-file",
    "fs:allow-read-dir",
    "fs:allow-create-dir"
  ]
}
```

### B. Tauri Command 参数模板

```rust
/// Template for Tauri commands with camelCase parameters
#[tauri::command]
pub async fn example_command(
    pool: State<'_, SqlitePool>,
    #[allow(non_snake_case)]
    someParam: String,
    #[allow(non_snake_case)]
    optionalId: Option<i64>,
) -> AppResult<ReturnType> {
    // Implementation
    Ok(result)
}
```

### C. 开发/生产路径配置模板

```rust
#[cfg(debug_assertions)]
let resource_path = {
    std::env::current_dir()
        .expect("Failed to get current directory")
        .parent()
        .expect("Failed to get parent directory")
        .join("resources")
};

#[cfg(not(debug_assertions))]
let resource_path = {
    app_handle
        .path()
        .app_data_dir()
        .expect("Failed to get app data dir")
        .join("resources")
};

// Ensure directory exists
std::fs::create_dir_all(&resource_path)?;
```

---

**文档创建**: 2026-03-12
**作者**: 基于项目实际踩坑经验总结
**目的**: 改进流程，避免重复问题
**下一步**: 实施"立即改进"建议，评估效果后决定是否继续使用 Tauri

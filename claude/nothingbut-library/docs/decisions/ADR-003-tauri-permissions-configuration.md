# ADR-003: Tauri 2.0 显式权限配置策略

**日期**: 2026-03-11
**状态**: ✅ 已接受并实施
**决策者**: 技术决策（问题修复）
**影响范围**: 技术栈、安全、配置

---

## 背景

Tauri 2.0 引入了新的权限系统（Capabilities），要求开发者在 `capabilities/*.json` 中**显式声明**应用需要的所有权限。

这是对 Tauri 1.x 的重大变更：
- **Tauri 1.x**: 默认允许大部分 API 调用
- **Tauri 2.0**: 默认拒绝，必须显式允许

初始实施时，由于不了解这个机制，遇到了运行时错误：
```
Error: dialog.open not allowed
Cause: Missing permissions in capabilities/default.json
```

## 决策

**建立显式权限配置清单**，遵循以下原则：

1. **最小权限原则**: 只添加应用实际需要的权限
2. **声明即使用**: 添加 plugin 依赖时，同步更新 capabilities
3. **权限分组**: 使用 `xxx:default` 权限组简化配置
4. **定期审查**: 每个 Milestone 结束时审查权限配置

## 考虑的方案

### 方案 1: 使用宽松权限（被拒绝）
- **描述**: 添加所有可能用到的权限（如 `fs:allow-all`）
- **优势**: 开发时无需频繁修改配置
- **劣势**:
  - ❌ 违反安全最佳实践
  - ❌ 给予应用过多权限
  - ❌ 增加安全风险（如果应用被利用）
- **状态**: ❌ 被拒绝

### 方案 2: 按需添加权限（采纳）
- **描述**: 每次使用新 API 时，添加对应的权限声明
- **优势**:
  - ✅ 符合最小权限原则
  - ✅ 安全性高
  - ✅ 权限可追溯（知道为什么需要）
- **劣势**:
  - ⚠️ 开发时需要频繁修改配置
  - ⚠️ 容易遗忘（运行时才发现）
- **状态**: ✅ 被采纳

### 方案 3: 自动化权限检测（未来）
- **描述**: 通过静态分析检测代码中的 API 调用，自动生成权限配置
- **优势**: 减少人工配置
- **劣势**: 需要开发工具
- **状态**: 🔮 未来改进（见 ADR-005）

## 决策依据

1. **安全优先**: Tauri 2.0 的权限系统设计初衷是增强安全性
2. **最佳实践**: 参考 Android、iOS 的权限模型
3. **实际踩坑**: 初期遗漏 dialog 权限导致功能不可用
4. **Tauri 官方推荐**: 文档明确建议按需添加权限

## 证据

- **问题发现**: 文件选择对话框无法打开
- **浏览器控制台错误**: `dialog.open not allowed`
- **修复 commit**: `c508195` - "fix: add dialog plugin permissions"
- **Tauri 文档**: https://tauri.app/v2/security/capabilities/

## 后果

### 积极影响
✅ 应用安全性提升
✅ 权限可审计
✅ 符合安全最佳实践
✅ 用户信任度提升

### 消极影响
⚠️ 开发时需要手动配置
⚠️ 容易遗漏（运行时才发现）
⚠️ 配置文件维护成本

### 风险和缓解措施
- **风险**: 添加 plugin 时忘记配置权限
  - **缓解**: 建立配置检查清单（ADR-005）
- **风险**: 权限配置过于宽松
  - **缓解**: 定期审查（每个 Milestone）

## 实施

### 当前权限配置

**文件**: `src-tauri/capabilities/default.json`

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Capability for the main window",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "core:window:default",
    "opener:default",
    "dialog:default",        // 文件选择对话框
    "dialog:allow-open",     // 允许打开文件
    "dialog:allow-save",     // 允许保存文件
    "fs:default",            // 文件系统基础权限
    "fs:allow-read-file",    // 读取文件
    "fs:allow-write-file",   // 写入文件
    "fs:allow-read-dir",     // 读取目录
    "fs:allow-create-dir"    // 创建目录
  ]
}
```

### 权限添加流程

当需要使用新的 Tauri API 时：

1. **在 Cargo.toml 添加依赖**:
   ```toml
   [dependencies]
   tauri-plugin-dialog = "2.0"
   ```

2. **在 lib.rs 初始化 plugin**:
   ```rust
   tauri::Builder::default()
       .plugin(tauri_plugin_dialog::init())
   ```

3. **在 capabilities/default.json 添加权限**:
   ```json
   {
     "permissions": [
       "dialog:default",
       "dialog:allow-open"
     ]
   }
   ```

4. **验证**: 运行应用，测试功能是否正常

### 实施 commit
- `c508195` - 添加 dialog 权限

## 关联文档

- 配置检查清单: `docs/decisions/ADR-005-tauri-configuration-checklist.md`
- Tauri 安全指南: https://tauri.app/v2/security/capabilities/

## 验证

- [x] 文件选择对话框正常工作
- [x] 文件读写功能正常
- [x] 目录创建功能正常
- [x] 无多余权限声明
- [ ] 添加自动化权限审计（未来改进）

## 注意事项

⚠️ **添加新功能时必须检查**：

### 1. 常见 Plugin 权限对照表

| Plugin | 权限声明 | 说明 |
|--------|---------|------|
| tauri-plugin-dialog | `dialog:default`, `dialog:allow-open` | 文件选择对话框 |
| tauri-plugin-fs | `fs:default`, `fs:allow-read-file` | 文件系统 |
| tauri-plugin-http | `http:default`, `http:allow-fetch` | HTTP 请求 |
| tauri-plugin-shell | `shell:default`, `shell:allow-execute` | 执行外部命令 |
| tauri-plugin-sql | (内部权限) | 数据库（无需额外权限） |

### 2. 权限组 vs 细粒度权限

**推荐使用权限组** (如 `dialog:default`):
```json
// ✅ 推荐：使用权限组
"permissions": [
  "dialog:default",
  "dialog:allow-open"
]

// ❌ 不推荐：列举所有细节权限（除非需要限制）
"permissions": [
  "dialog:allow-open",
  "dialog:allow-save",
  "dialog:allow-message",
  // ... 20+ 个权限
]
```

**何时使用细粒度权限**：
- 需要严格限制功能（如只允许打开文件，不允许保存）
- 生产环境安全加固

### 3. 权限审查清单

**每次添加 plugin 时**:
- [ ] Cargo.toml 添加依赖
- [ ] lib.rs 初始化 plugin
- [ ] capabilities/default.json 添加权限
- [ ] 运行应用测试功能
- [ ] 提交 commit（包含所有 3 个文件）

**每个 Milestone 结束时**:
- [ ] 审查 capabilities/*.json
- [ ] 确认每个权限都有对应的使用场景
- [ ] 删除未使用的权限
- [ ] 记录审查结果

## 权限风险评估

### 当前权限风险等级

| 权限 | 风险等级 | 说明 |
|------|---------|------|
| `fs:allow-read-file` | 中 | 可读取用户文件，但限制在工作区内 |
| `fs:allow-write-file` | 高 | 可写入文件，需确保路径验证 |
| `dialog:allow-open` | 低 | 仅打开文件选择对话框 |
| `core:window:default` | 低 | 窗口管理，无敏感操作 |

### 缓解措施
- 文件路径验证：确保只访问工作区目录
- 输入验证：防止路径遍历攻击
- 错误处理：不泄露敏感路径信息

## 历史

- 2026-03-11 初期: 只有基础权限（core, opener）
- 2026-03-11 22:10: 发现 dialog 权限缺失
- 2026-03-11 22:12: 添加 dialog 权限（commit c508195）
- 2026-03-11 22:30: 测试通过
- 2026-03-12: 回溯记录，建立权限管理策略

---

**创建**: 2026-03-12（回溯记录）
**最后审查**: 2026-03-12
**下次审查**: Milestone 1 完成时
**教训**: Tauri 2.0 权限系统是新特性，需要主动学习和配置

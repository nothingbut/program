# General Agent V2 - Rust 重写

**状态:** 规划中
**开始日期:** 2026-03-09
**目标:** 使用 Rust 重写后端服务和 TUI 界面，提升性能、安全性和可维护性

---

## 项目目标

### 为什么重写？

1. **性能提升**
   - Rust 的零成本抽象和内存安全保证
   - 更快的启动时间和更低的内存占用
   - 原生并发支持（async/await + tokio）

2. **类型安全**
   - 编译时类型检查
   - 消除常见的运行时错误
   - 更好的 API 设计

3. **生产就绪**
   - 更好的错误处理机制
   - 内置的并发安全
   - 更容易的部署（单一二进制文件）

4. **维护性**
   - 强类型系统减少 bug
   - 更好的模块化设计
   - 清晰的所有权模型

### V2 范围

**包含：**
- ✅ 后端服务（REST API）
- ✅ TUI 界面（Ratatui）
- ✅ 核心功能（Phase 1-7）
- ✅ CLI 工具

**暂缓：**
- ⏸️ Web UI（使用 V1 的前端，通过 API 连接）
- ⏸️ Phase 8 新功能（等 V2 基础稳定后实施）

---

## 技术栈

### 核心技术

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| **Web 框架** | Axum 0.7+ | 高性能、类型安全、基于 Tokio |
| **异步运行时** | Tokio 1.35+ | 生态成熟、性能卓越 |
| **数据库** | SQLx + SQLite | 异步、编译时类型检查 |
| **TUI** | Ratatui 0.26+ | 现代化、维护活跃 |
| **序列化** | Serde | Rust 生态标准 |
| **配置** | config-rs | 多格式支持（YAML/TOML） |
| **日志** | tracing + tracing-subscriber | 结构化日志、分布式追踪 |
| **测试** | Tokio-test + mockito | 异步测试支持 |

### LLM 集成

| 功能 | 技术选型 |
|------|---------|
| **OpenAI** | async-openai |
| **Anthropic** | anthropic-sdk-rust (或 HTTP 直接调用) |
| **Ollama** | reqwest + 自定义客户端 |

### MCP 集成

- **策略:** 使用 V1 的 Python MCP 作为桥接
- **通信:** JSON-RPC over stdio/HTTP
- **未来:** 等 Rust MCP SDK 成熟后迁移

---

## 架构设计

### 分层架构

```
┌─────────────────────────────────────────────────┐
│              CLI / TUI Interface                 │
│                  (Ratatui)                       │
├─────────────────────────────────────────────────┤
│              REST API Layer                      │
│                 (Axum)                           │
├─────────────────────────────────────────────────┤
│              Service Layer                       │
│   (ChatService, SkillService, WorkflowService)  │
├─────────────────────────────────────────────────┤
│              Domain Layer                        │
│      (Models, Business Logic, Traits)           │
├─────────────────────────────────────────────────┤
│              Infrastructure Layer                │
│  (Database, LLM Client, MCP Bridge, Storage)    │
└─────────────────────────────────────────────────┘
```

### 核心模块

```
general-agent-v2/
├── Cargo.toml                    # 工作区配置
├── crates/
│   ├── agent-core/              # 核心领域模型
│   ├── agent-llm/               # LLM 客户端
│   ├── agent-skills/            # 技能系统
│   ├── agent-workflow/          # 工作流引擎
│   ├── agent-storage/           # 存储层
│   ├── agent-api/               # REST API
│   ├── agent-tui/               # TUI 界面
│   └── agent-cli/               # CLI 工具
├── docs/                        # 文档（从 V1 复制）
├── design/                      # 设计文档
├── skills/                      # 技能定义（复用 V1）
└── tests/                       # 集成测试
```

---

## 实施计划

### Week 1-2: 基础设施
- [ ] 创建 Cargo 工作区
- [ ] 数据库层（SQLx + SQLite）
- [ ] 基础 API（Axum）
- [ ] 会话管理

### Week 3-4: LLM 集成
- [ ] OpenAI/Anthropic/Ollama 客户端
- [ ] LLM 路由
- [ ] 流式响应

### Week 5-6: 技能系统
- [ ] Markdown 解析
- [ ] 技能注册和执行

### Week 7-8: TUI 界面
- [ ] Ratatui 框架
- [ ] 会话管理 UI

### Week 9-10: 工作流引擎
- [ ] DAG 编排
- [ ] 任务执行

### Week 11-12: 测试优化
- [ ] 测试覆盖率 > 80%
- [ ] 性能优化

---

## 下一步

1. 创建 Cargo 工作区
2. 复制 V1 文档
3. 编写详细架构设计
4. 实现数据库层

**创建日期:** 2026-03-09

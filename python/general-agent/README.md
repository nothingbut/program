# General Agent

通用Agent系统，支持：
- ✅ **Skill System**（技能系统，已完成）
- 🚧 **MCP客户端**（Model Context Protocol，计划中）
- 🚧 **RAG**（检索增强生成，计划中）

## 功能特性

### Phase 1: Foundation ✅
- 基础聊天功能
- 会话上下文管理
- 简洁Web界面
- SQLite持久化存储

### Phase 2: Skill System ✅
- 技能定义（YAML + Markdown）
- 技能加载器（.ignore支持）
- 技能注册表（命名空间解析）
- 技能执行器（参数验证、LLM集成）
- Router集成（@skill 和 /skill 语法）
- 5个示例技能（personal, productivity）

### 未来版本
- MCP集成（Phase 3）
- RAG引擎（Phase 4）
- 高级功能（Phase 5-6）

## 快速开始

### 1. 安装依赖

```bash
# 使用uv（推荐）
uv pip install -e ".[dev]"

# 或使用pip
pip install -e ".[dev]"
```

### 2. 运行测试

```bash
pytest
```

### 3. 启动服务

```bash
uvicorn src.main:app --reload
```

访问 http://localhost:8000

### 4. 使用技能（新功能！）

```bash
# 简单问候
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "@greeting", "session_id": "test"}'

# 创建提醒（带参数）
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "@reminder task=\"Buy milk\" time=\"5pm\"", "session_id": "test"}'
```

查看所有可用技能：
```bash
ls skills/personal/
ls skills/productivity/
```

详细文档见：[docs/skills.md](docs/skills.md)

### 5. API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API使用

### 聊天接口

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "session_id": "optional-session-id"
  }'
```

响应：
```json
{
  "response": "我收到了你的消息：「Hello」...",
  "session_id": "sess-abc123",
  "plan_type": "simple_query"
}
```

## 项目结构

```
general-agent/
├── src/
│   ├── core/          # 核心模块（router, executor, context, llm_client）
│   ├── skills/        # 技能系统（models, parser, loader, registry, executor）
│   ├── storage/       # 存储层（database, models）
│   ├── api/           # API路由
│   └── main.py        # 应用入口
├── skills/            # 技能定义
│   ├── personal/      # 个人生产力技能
│   ├── productivity/  # 工作和任务管理技能
│   └── .ignore        # 忽略模式
├── tests/             # 测试（130个测试，95%+覆盖率）
├── templates/         # HTML模板
├── static/            # 静态资源
└── docs/              # 文档
```

## 开发

### 运行测试（带覆盖率）

```bash
pytest --cov=src --cov-report=html
```

### 代码检查

```bash
ruff check src/
mypy src/
```

## 文档

- 📖 **[技能系统文档](docs/skills.md)** - 完整的技能系统指南
- 📋 **[设计文档](docs/plans/2026-03-02-general-agent-design.md)** - 系统架构设计
- 🚀 **[Phase 1 计划](docs/plans/2026-03-02-phase1-foundation.md)** - 基础设施实现
- 🎯 **[Phase 2 计划](docs/plans/2026-03-02-phase2-skill-system.md)** - 技能系统实现

## 技能系统快速入门

技能系统允许您定义可复用的提示词模板，并通过简单的语法调用：

```bash
# 使用技能
@greeting                                    # 简单问候
@reminder task='Buy milk' time='5pm'        # 创建提醒
@note content='Meeting notes' category='work'  # 记笔记
@task title='Review PR' priority='high'     # 任务管理
```

**创建自定义技能：**
1. 在 `skills/` 目录创建 `.md` 文件
2. 添加 YAML frontmatter 定义参数
3. 编写提示词模板（使用 `{param}` 占位符）
4. 重启服务即可使用

详见：[技能系统文档](docs/skills.md)

## 许可证

MIT

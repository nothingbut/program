# General Agent

通用Agent系统，支持：
- ✅ **Skill协议**（兼容Claude Code）
- ✅ **MCP客户端**（Model Context Protocol）
- ✅ **RAG**（检索增强生成）

## 功能特性

### Phase 1（当前版本）✅
- 基础聊天功能
- 会话上下文管理
- 简洁Web界面
- SQLite持久化存储

### 未来版本
- Skill System（Phase 2）
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

### 4. API文档

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
│   ├── core/          # 核心模块
│   ├── storage/       # 存储层
│   ├── api/           # API路由
│   └── main.py        # 应用入口
├── tests/             # 测试
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

## 架构

详见：
- 设计文档: `docs/plans/2026-03-02-general-agent-design.md`
- 实现计划: `docs/plans/2026-03-02-phase1-foundation.md`

## 许可证

MIT

# General Agent

通用Agent系统，支持：
- Skill协议（兼容Claude Code）
- MCP客户端（Model Context Protocol）
- RAG检索增强生成

## 快速开始

```bash
# 安装依赖
uv pip install -e ".[dev]"

# 运行测试
pytest

# 启动服务
uvicorn src.main:app --reload
```

## 架构

详见 `docs/plans/2026-03-02-general-agent-design.md`

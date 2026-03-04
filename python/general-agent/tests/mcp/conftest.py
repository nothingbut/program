"""Shared fixtures for MCP tests."""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock
import yaml


@pytest.fixture
def temp_mcp_config(tmp_path):
    """Create temporary MCP config file."""
    config = {
        "servers": {
            "filesystem": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    str(tmp_path)
                ],
                "security": {
                    "allowed_directories": [str(tmp_path)],
                    "allowed_operations": ["read_file", "list_directory"],
                    "denied_operations": ["delete_file"]
                },
                "timeout": 30.0,
                "health_check_interval": 60
            }
        },
        "global": {
            "enabled": True,
            "audit_log_retention_days": 90,
            "confirmation_timeout": 300
        }
    }

    config_file = tmp_path / "mcp_config.yaml"
    config_file.write_text(yaml.dump(config))
    return config_file


@pytest.fixture
def mock_mcp_connection():
    """Mock MCP connection for unit tests."""
    conn = AsyncMock()
    conn.call_tool = AsyncMock(return_value={"content": "test result"})
    conn.list_tools = AsyncMock(return_value=[
        {
            "name": "read_file",
            "description": "Read file contents",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                }
            }
        },
        {
            "name": "write_file",
            "description": "Write file contents",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                }
            }
        }
    ])
    return conn

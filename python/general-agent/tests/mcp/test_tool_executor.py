"""Tests for MCP tool executor."""
import pytest
from unittest.mock import AsyncMock
from src.mcp.tool_executor import MCPToolExecutor
from src.mcp.exceptions import PermissionDeniedError, ConfirmationRequired


@pytest.mark.asyncio
async def test_executor_initialization(mock_mcp_connection, monkeypatch):
    """Test tool executor can be initialized."""
    from src.mcp.connection_manager import MCPConnectionManager
    from src.mcp.security import MCPSecurityLayer, SecurityConfig

    # Mock manager
    manager = AsyncMock(spec=MCPConnectionManager)

    # Mock security
    config = SecurityConfig(
        allowed_directories=["/tmp"],
        allowed_operations=["read_file"],
        denied_operations=["delete_file"]
    )
    security = MCPSecurityLayer(config)

    # Mock database
    db = AsyncMock()

    executor = MCPToolExecutor(manager, security, db)

    assert executor is not None
    assert executor.manager is manager
    assert executor.security is security


@pytest.mark.asyncio
async def test_tool_discovery(mock_mcp_connection, monkeypatch):
    """Test tool discovery from server."""
    manager = AsyncMock()
    manager.get_connection = AsyncMock(return_value=mock_mcp_connection)

    security = AsyncMock()
    db = AsyncMock()

    from src.mcp.tool_executor import MCPToolExecutor
    executor = MCPToolExecutor(manager, security, db)

    tools = await executor.discover_tools("filesystem")

    assert len(tools) == 2
    assert tools[0]["name"] == "read_file"
    assert tools[1]["name"] == "write_file"

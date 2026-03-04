"""Tests for MCP connection manager."""
import pytest
from src.mcp.connection_manager import MCPConnectionManager
from src.mcp.exceptions import MCPServerDisabledError


@pytest.mark.asyncio
async def test_manager_initialization(temp_mcp_config):
    """Test connection manager can be initialized."""
    manager = MCPConnectionManager(str(temp_mcp_config))

    assert manager is not None
    assert len(manager.connections) == 0
    assert "filesystem" in manager.config.servers


@pytest.mark.asyncio
async def test_lazy_connection_creation(temp_mcp_config, mock_mcp_connection, monkeypatch):
    """Test connections are created lazily on first access."""
    manager = MCPConnectionManager(str(temp_mcp_config))

    # Mock the _start_server method
    async def mock_start(server_name):
        return mock_mcp_connection

    monkeypatch.setattr(manager, "_start_server", mock_start)

    # First call should create connection
    conn1 = await manager.get_connection("filesystem")
    assert conn1 is mock_mcp_connection
    assert len(manager.connections) == 1

    # Second call should reuse connection
    conn2 = await manager.get_connection("filesystem")
    assert conn2 is conn1
    assert len(manager.connections) == 1


@pytest.mark.asyncio
async def test_disabled_server_raises_error(temp_mcp_config):
    """Test accessing disabled server raises error."""
    manager = MCPConnectionManager(str(temp_mcp_config))
    manager._disabled_servers.add("filesystem")

    with pytest.raises(MCPServerDisabledError) as exc_info:
        await manager.get_connection("filesystem")

    assert "filesystem" in str(exc_info.value)

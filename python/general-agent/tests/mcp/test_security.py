"""Tests for MCP security layer."""
import pytest
from pathlib import Path
from src.mcp.security import MCPSecurityLayer, SecurityConfig


def test_security_layer_initialization():
    """Test security layer can be initialized."""
    config = SecurityConfig(
        allowed_directories=["/tmp", "/home/user/docs"],
        allowed_operations=["read_file", "list_directory"],
        denied_operations=["delete_file"]
    )

    security = MCPSecurityLayer(config)

    assert security is not None
    assert len(security.config.allowed_directories) == 2
    assert len(security.resolved_dirs) == 2


def test_resolved_directories_are_absolute():
    """Test directory paths are resolved to absolute."""
    config = SecurityConfig(
        allowed_directories=[".", "../test"],
        allowed_operations=[],
        denied_operations=[]
    )

    security = MCPSecurityLayer(config)

    # All resolved paths should be absolute
    for path in security.resolved_dirs:
        assert path.is_absolute()


@pytest.mark.asyncio
async def test_denied_operation_rejected():
    """Test denied operations are rejected."""
    config = SecurityConfig(
        allowed_directories=["/tmp"],
        allowed_operations=["read_file"],
        denied_operations=["delete_file"]
    )
    security = MCPSecurityLayer(config)

    allowed, reason = await security.check_permission(
        "filesystem",
        "delete_file",
        {"path": "/tmp/test.txt"}
    )

    assert allowed is False
    assert "denied by security policy" in reason


@pytest.mark.asyncio
async def test_allowed_operation_passes():
    """Test allowed operations pass without confirmation."""
    config = SecurityConfig(
        allowed_directories=["/tmp"],
        allowed_operations=["read_file"],
        denied_operations=[]
    )
    security = MCPSecurityLayer(config)

    allowed, reason = await security.check_permission(
        "filesystem",
        "read_file",
        {"path": "/tmp/test.txt"}
    )

    assert allowed is True
    assert reason is None


@pytest.mark.asyncio
async def test_undefined_operation_requires_confirmation():
    """Test undefined operations require confirmation."""
    config = SecurityConfig(
        allowed_directories=["/tmp"],
        allowed_operations=["read_file"],
        denied_operations=["delete_file"]
    )
    security = MCPSecurityLayer(config)

    # write_file is neither allowed nor denied
    allowed, reason = await security.check_permission(
        "filesystem",
        "write_file",
        {"path": "/tmp/test.txt"}
    )

    assert allowed is None  # Requires confirmation
    assert reason is None

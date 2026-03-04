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

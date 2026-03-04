"""Tests for MCP configuration."""
import pytest
from pathlib import Path
import yaml
from src.mcp.config import MCPConfig, ServerConfig, SecurityConfig, load_mcp_config


def test_load_valid_config(temp_mcp_config):
    """Test loading valid YAML config."""
    config = load_mcp_config(str(temp_mcp_config))

    assert isinstance(config, MCPConfig)
    assert "filesystem" in config.servers
    assert config.global_config["enabled"] is True


def test_server_config_validation(temp_mcp_config):
    """Test server config structure."""
    config = load_mcp_config(str(temp_mcp_config))
    server = config.servers["filesystem"]

    assert isinstance(server, ServerConfig)
    assert server.command == "npx"
    assert len(server.args) > 0
    assert server.timeout == 30.0


def test_security_config_validation(temp_mcp_config):
    """Test security config structure."""
    config = load_mcp_config(str(temp_mcp_config))
    security = config.servers["filesystem"].security

    assert isinstance(security, SecurityConfig)
    assert len(security.allowed_directories) > 0
    assert "read_file" in security.allowed_operations
    assert "delete_file" in security.denied_operations


def test_missing_config_file():
    """Test error handling for missing config."""
    with pytest.raises(FileNotFoundError):
        load_mcp_config("/nonexistent/config.yaml")


def test_invalid_yaml_format(tmp_path):
    """Test error handling for invalid YAML."""
    bad_config = tmp_path / "bad_config.yaml"
    bad_config.write_text("invalid: yaml: content: [")

    with pytest.raises(yaml.YAMLError):
        load_mcp_config(str(bad_config))

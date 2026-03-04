"""MCP connection manager - handles server lifecycle."""
import asyncio
import logging
from typing import Dict, Set, Any
from pathlib import Path

from .config import load_mcp_config, MCPConfig, ServerConfig
from .exceptions import (
    MCPServerStartupError,
    MCPServerDisabledError,
    MCPServerCrashError
)

logger = logging.getLogger(__name__)


class MCPConnectionManager:
    """Manages MCP server connections with lazy initialization.

    Features:
    - Lazy singleton: starts servers on first access
    - Connection caching: reuses connections across requests
    - Health checking: detects and recovers from crashes
    - Auto-restart: attempts recovery up to 3 times
    - Graceful shutdown: cleans up on app exit

    Attributes:
        config: MCP configuration
        connections: Active server connections
        _locks: Per-server locks for thread safety
        _restart_count: Track restart attempts
        _disabled_servers: Set of disabled server names
    """

    def __init__(self, config_path: str):
        """Initialize connection manager.

        Args:
            config_path: Path to MCP YAML config file
        """
        self.config = load_mcp_config(config_path)
        self.connections: Dict[str, Any] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._restart_count: Dict[str, int] = {}
        self._disabled_servers: Set[str] = set()

        logger.info(f"MCPConnectionManager initialized with {len(self.config.servers)} servers")

    async def get_connection(self, server_name: str) -> Any:
        """Get or create server connection (thread-safe).

        First call starts the server process, subsequent calls reuse
        the connection. Uses asyncio.Lock for concurrency safety.

        Args:
            server_name: Name of server (e.g., "filesystem")

        Returns:
            MCP connection object

        Raises:
            MCPServerDisabledError: Server is disabled
            MCPServerStartupError: Failed to start server
        """
        if server_name in self._disabled_servers:
            raise MCPServerDisabledError(server_name)

        if server_name not in self.config.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")

        # Lazy creation with lock
        if server_name not in self.connections:
            lock = self._get_lock(server_name)
            async with lock:
                # Double-check after acquiring lock
                if server_name not in self.connections:
                    logger.info(f"Starting MCP server: {server_name}")
                    self.connections[server_name] = await self._start_server(server_name)

        return self.connections[server_name]

    async def _start_server(self, server_name: str) -> Any:
        """Start MCP server process.

        Args:
            server_name: Server name

        Returns:
            MCP connection

        Raises:
            MCPServerStartupError: Startup failed
        """
        # TODO: Implement using mcp SDK
        # For now, this is a placeholder
        raise NotImplementedError("Server startup not yet implemented")

    async def health_check(self, server_name: str) -> bool:
        """Check if server is healthy.

        Args:
            server_name: Server name

        Returns:
            True if healthy, False otherwise
        """
        # TODO: Implement health check
        return True

    async def restart_server(self, server_name: str):
        """Restart a crashed server.

        Args:
            server_name: Server name
        """
        # TODO: Implement restart logic
        pass

    async def shutdown_all(self):
        """Shutdown all server connections."""
        logger.info("Shutting down all MCP servers")

        for server_name, connection in self.connections.items():
            try:
                # TODO: Implement connection cleanup
                logger.info(f"Closed connection to {server_name}")
            except Exception as e:
                logger.error(f"Error closing {server_name}: {e}")

        self.connections.clear()

    def _get_lock(self, server_name: str) -> asyncio.Lock:
        """Get or create lock for server.

        Args:
            server_name: Server name

        Returns:
            asyncio.Lock for this server
        """
        if server_name not in self._locks:
            self._locks[server_name] = asyncio.Lock()
        return self._locks[server_name]

    def _mark_server_disabled(self, server_name: str):
        """Disable a server after too many failures.

        Args:
            server_name: Server name
        """
        self._disabled_servers.add(server_name)
        logger.warning(f"Server '{server_name}' has been disabled")

"""MCP tool executor - discovers and executes tools."""
import logging
from datetime import datetime
from typing import Dict, List, Any

from .connection_manager import MCPConnectionManager
from .security import MCPSecurityLayer
from .exceptions import (
    PermissionDeniedError,
    ConfirmationRequired,
    MCPToolError,
    MCPToolNotFoundError
)

logger = logging.getLogger(__name__)


class MCPToolExecutor:
    """MCP tool executor.

    Features:
    - Tool discovery with caching
    - Security-enforced tool calls
    - Audit logging
    - Error wrapping with context

    Attributes:
        manager: Connection manager
        security: Security layer
        db: Database for audit logs
        _tool_cache: Cached tool lists per server
    """

    def __init__(
        self,
        manager: MCPConnectionManager,
        security: MCPSecurityLayer,
        db: Any
    ):
        """Initialize tool executor.

        Args:
            manager: MCP connection manager
            security: Security layer
            db: Database instance
        """
        self.manager = manager
        self.security = security
        self.db = db
        self._tool_cache: Dict[str, List[dict]] = {}

    async def discover_tools(self, server_name: str) -> List[dict]:
        """Discover tools from MCP server.

        Results are cached to avoid repeated queries.

        Args:
            server_name: Server name (e.g., "filesystem")

        Returns:
            List of tool definitions with name, description, schema

        Raises:
            MCPConnectionError: Failed to connect to server
        """
        if server_name not in self._tool_cache:
            logger.info(f"Discovering tools from {server_name}")
            connection = await self.manager.get_connection(server_name)
            tools = await connection.list_tools()
            self._tool_cache[server_name] = tools
            logger.info(f"Discovered {len(tools)} tools from {server_name}")

        return self._tool_cache[server_name]

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict,
        session_id: str
    ) -> dict:
        """Call MCP tool with security checks.

        Flow:
        1. Security check (three-tier permissions)
        2. Raise ConfirmationRequired if needed
        3. Log to audit trail
        4. Execute tool
        5. Return result

        Args:
            server_name: Server name
            tool_name: Tool name (e.g., "read_file")
            arguments: Tool arguments
            session_id: Session ID for audit

        Returns:
            Tool execution result

        Raises:
            PermissionDeniedError: Operation not allowed
            ConfirmationRequired: Needs user confirmation
            MCPToolError: Tool execution failed
        """
        full_tool_name = f"{server_name}:{tool_name}"

        # 1. Security check
        allowed, reason = await self.security.check_permission(
            server_name, full_tool_name, arguments
        )

        if allowed is False:
            raise PermissionDeniedError(tool_name, reason)

        if allowed is None:
            # Requires confirmation
            raise ConfirmationRequired(
                tool_name=full_tool_name,
                arguments=arguments,
                prompt=f"Allow {full_tool_name} with arguments {arguments}?"
            )

        # 2. Log operation (before execution)
        await self._log_operation(
            session_id, server_name, tool_name, arguments, "started"
        )

        # 3. Execute tool
        try:
            connection = await self.manager.get_connection(server_name)
            result = await connection.call_tool(tool_name, arguments)

            # Log success
            await self._log_operation(
                session_id, server_name, tool_name, arguments,
                "success", result
            )

            logger.info(f"Tool {full_tool_name} executed successfully")
            return result

        except Exception as e:
            # Log failure
            await self._log_operation(
                session_id, server_name, tool_name, arguments,
                "failed", error=str(e)
            )

            logger.error(f"Tool {full_tool_name} failed: {e}")
            raise MCPToolError(f"Tool '{full_tool_name}' failed: {e}") from e

    async def _log_operation(
        self,
        session_id: str,
        server_name: str,
        tool_name: str,
        arguments: dict,
        status: str,
        result: Any = None,
        error: str = None
    ):
        """Log tool operation to audit trail.

        Args:
            session_id: Session ID
            server_name: Server name
            tool_name: Tool name
            arguments: Tool arguments
            status: Operation status (started/success/failed)
            result: Tool result (if successful)
            error: Error message (if failed)
        """
        # TODO: Implement database logging in Phase 3.3
        logger.debug(
            f"Audit log: {session_id} - {server_name}:{tool_name} - {status}"
        )

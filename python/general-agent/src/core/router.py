"""Simple router for routing user input to execution plans.

This module provides a simple router that analyzes user input and determines
the appropriate execution plan. In the MVP version, all inputs are routed to
simple_query with LLM processing.
"""

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class ExecutionPlan:
    """Execution plan for processing user input.

    This is an immutable dataclass - all fields are frozen after creation.

    Attributes:
        type: Type of execution ('simple_query' | 'task' | 'skill' | 'mcp')
        requires_llm: Whether LLM processing is required
        requires_rag: Whether RAG (retrieval) is required
        requires_tools: Whether tool/function calling is required
        metadata: Optional metadata dictionary for additional context
    """

    type: Literal["simple_query", "task", "skill", "mcp"]
    requires_llm: bool
    requires_rag: bool = False
    requires_tools: bool = False
    metadata: dict[str, Any] | None = None


class SimpleRouter:
    """Simple router for user input.

    Routes user input to appropriate execution plans. In the MVP version,
    all inputs are routed to simple_query with requires_llm=True.

    Future versions will add:
    - Intent recognition (greeting, question, command)
    - Skill detection
    - MCP tool routing
    - RAG requirement detection
    """

    def route(self, user_input: str, context: Any = None) -> ExecutionPlan:
        """Route user input to an execution plan.

        Args:
            user_input: The user's input string to route
            context: Optional context for routing decisions (unused in MVP)

        Returns:
            ExecutionPlan with routing decisions

        Raises:
            ValueError: If user_input is empty or whitespace-only
        """
        # Validate input
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")

        # MVP: Route all inputs to simple_query with LLM
        # Future: Add intent recognition, skill detection, etc.
        return ExecutionPlan(
            type="simple_query",
            requires_llm=True,
            requires_rag=False,
            requires_tools=False,
            metadata=None
        )

"""Agent执行器

该模块提供AgentExecutor类，用于协调所有组件（数据库、路由、LLM）
来处理用户请求。这是系统的核心编排层。
"""
from typing import Dict, Any
from .router import SimpleRouter
from .llm_client import MockLLMClient
from .context import ContextManager
from ..storage.database import Database


class AgentExecutor:
    """Agent执行器 - 协调路由、上下文和LLM

    该类是系统的核心编排层，负责：
    1. 接收用户输入
    2. 管理会话上下文
    3. 路由到适当的执行计划
    4. 调用LLM处理请求
    5. 保存对话历史

    Attributes:
        db: 数据库实例，用于持久化会话和消息
        router: 路由器实例，用于决策执行计划
        llm_client: LLM客户端实例，用于生成响应
    """

    def __init__(
        self,
        db: Database,
        router: SimpleRouter,
        llm_client: MockLLMClient
    ) -> None:
        """初始化执行器

        Args:
            db: 数据库实例
            router: 路由器实例
            llm_client: LLM客户端实例
        """
        self.db = db
        self.router = router
        self.llm_client = llm_client

    async def execute(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """执行用户请求

        执行流程：
        1. 验证输入
        2. 获取会话上下文
        3. 保存用户消息
        4. 路由决策
        5. 执行计划（调用LLM）
        6. 保存助手响应
        7. 返回结果

        Args:
            user_input: 用户输入字符串
            session_id: 会话ID

        Returns:
            执行结果字典，包含以下字段：
            - response: 助手的响应内容
            - session_id: 会话ID
            - plan_type: 执行计划类型（如 "simple_query"）

        Raises:
            ValueError: 如果user_input为空或session_id为空
        """
        # 1. 验证输入
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")

        if not session_id or not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        # 2. 获取上下文（ContextManager会验证session_id）
        ctx = ContextManager(self.db, session_id)

        # 3. 保存用户消息
        await ctx.add_message("user", user_input)

        # 4. 路由决策
        plan = self.router.route(user_input, context=ctx)

        # 5. 执行计划
        if plan.type == "simple_query":
            response = await self._execute_simple_query(ctx)
        else:
            # 未来：处理其他类型（task、skill、mcp）
            response = "暂不支持该类型的请求"

        # 6. 保存助手回复
        await ctx.add_message("assistant", response)

        # 7. 返回结果
        return {
            "response": response,
            "session_id": session_id,
            "plan_type": plan.type
        }

    async def _execute_simple_query(self, ctx: ContextManager) -> str:
        """执行简单问答

        从上下文获取历史消息，调用LLM生成响应。

        Args:
            ctx: 上下文管理器实例

        Returns:
            LLM生成的响应字符串
        """
        # 获取历史消息（格式化为LLM输入格式）
        messages = await ctx.format_for_llm(limit=10)

        # 调用LLM
        response = await self.llm_client.chat(messages)

        return response

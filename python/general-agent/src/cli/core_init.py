"""Core component initialization for CLI"""
import os
import logging
from pathlib import Path
from typing import Optional

from ..storage.database import Database
from ..core.executor import AgentExecutor
from ..core.router import SimpleRouter
from ..core.llm_client import MockLLMClient
from ..core.ollama_client import OllamaClient
from ..core.config_loader import load_config
from ..skills.loader import SkillLoader
from ..skills.registry import SkillRegistry
from ..skills.executor import SkillExecutor
from ..mcp.connection_manager import MCPConnectionManager
from ..mcp.security import MCPSecurityLayer
from ..mcp.tool_executor import MCPToolExecutor
from ..mcp.config import load_mcp_config

logger = logging.getLogger(__name__)


async def initialize_database(db_path: Optional[Path] = None) -> Database:
    if db_path is None:
        db_path = Path("data/general_agent.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(db_path)
    await db.initialize()
    return db


async def initialize_executor(db: Database, verbose: bool = False) -> AgentExecutor:
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    router = SimpleRouter()

    # 加载配置
    config = load_config()
    llm_config = config.get("llm", {})
    provider = llm_config.get("provider", "mock")
    
    # 创建 LLM 客户端
    if provider == "ollama":
        ollama_cfg = llm_config.get("ollama", {})
        llm_client = OllamaClient(
            base_url=ollama_cfg.get("base_url", "http://localhost:11434"),
            model=ollama_cfg.get("model", "qwen2.5:7b"),
            timeout=ollama_cfg.get("timeout", 120)
        )
        logger.info(f"Using Ollama with model: {ollama_cfg.get('model')}")
    else:
        llm_client = MockLLMClient()
        logger.info("Using Mock LLM client")

    # Skills
    skill_executor = None
    registry = None
    skills_dir = Path("skills")
    if skills_dir.exists():
        try:
            loader = SkillLoader(skills_dir)
            skills = loader.load_all()
            registry = SkillRegistry()
            for skill in skills:
                registry.register(skill)
            skill_executor = SkillExecutor(llm_client)
            logger.info(f"Loaded {len(skills)} skills")
        except Exception as e:
            logger.warning(f"Failed to load skills: {e}")

    # MCP (disabled by default)
    mcp_executor = None

    executor = AgentExecutor(
        db, router, llm_client,
        skill_registry=registry if skill_executor else None,
        skill_executor=skill_executor,
        mcp_executor=mcp_executor
    )
    return executor

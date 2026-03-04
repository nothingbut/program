"""FastAPI application entry point"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .api import routes
from .storage.database import Database
from .core.executor import AgentExecutor
from .core.router import SimpleRouter
from .core.llm_client import MockLLMClient
from .core.ollama_client import OllamaClient, OllamaConfig
import os
from .skills.loader import SkillLoader
from .skills.registry import SkillRegistry
from .skills.executor import SkillExecutor

logger = logging.getLogger(__name__)

# Global singletons (MVP pattern)
_db: Database | None = None
_executor: AgentExecutor | None = None
_skill_registry: SkillRegistry | None = None


def get_db() -> Database:
    """Dependency to get database instance"""
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db


def get_executor() -> AgentExecutor:
    """Dependency to get executor instance"""
    global _executor
    if _executor is None:
        raise RuntimeError("Executor not initialized")
    return _executor


async def startup() -> None:
    """Initialize database, skills, and executor on startup"""
    global _db, _executor, _skill_registry

    # Initialize database
    db_path = Path("data/general_agent.db")
    _db = Database(db_path)
    await _db.initialize()

    # Initialize skill system
    skills_dir = Path("skills")
    if skills_dir.exists():
        try:
            # Load skills from filesystem
            loader = SkillLoader(skills_dir)
            skills = loader.load_all()

            # Register skills
            _skill_registry = SkillRegistry()
            for skill in skills:
                _skill_registry.register(skill)

            logger.info(f"Loaded {len(skills)} skills from {skills_dir}")

        except Exception as e:
            logger.warning(f"Failed to load skills: {e}")
            _skill_registry = None
    else:
        logger.info(f"Skills directory not found: {skills_dir}")
        _skill_registry = None

    # Initialize executor
    router_instance = SimpleRouter()

    # Use Ollama if configured, otherwise fall back to Mock
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    if use_ollama:
        ollama_config = OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.2:latest"),
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
        )
        llm_client = OllamaClient(config=ollama_config)
        logger.info(f"Using Ollama client with model: {ollama_config.model}")
    else:
        llm_client = MockLLMClient()
        logger.info("Using Mock LLM client")

    # Create skill executor if skills are loaded
    skill_executor = None
    if _skill_registry:
        skill_executor = SkillExecutor(llm_client)

    _executor = AgentExecutor(
        _db,
        router_instance,
        llm_client,
        skill_registry=_skill_registry,
        skill_executor=skill_executor
    )

    # Set dependencies for routes
    routes.set_dependencies(get_db, get_executor)


async def shutdown() -> None:
    """Close database on shutdown"""
    global _db
    if _db:
        await _db.close()


# Create FastAPI app
app = FastAPI(
    title="General Agent API",
    description="REST API for the General Agent system",
    version="0.1.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})


# Register API routes
app.include_router(routes.router)

# Lifecycle events
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

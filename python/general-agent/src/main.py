"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .api import routes
from .storage.database import Database
from .core.executor import AgentExecutor
from .core.router import SimpleRouter
from .core.llm_client import MockLLMClient

# Global singletons (MVP pattern)
_db: Database | None = None
_executor: AgentExecutor | None = None


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
    """Initialize database and executor on startup"""
    global _db, _executor

    # Initialize database
    db_path = Path("data/general_agent.db")
    _db = Database(db_path)
    await _db.initialize()

    # Initialize executor
    router_instance = SimpleRouter()
    llm_client = MockLLMClient()
    _executor = AgentExecutor(_db, router_instance, llm_client)

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

# Register routes
app.include_router(routes.router)

# Lifecycle events
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

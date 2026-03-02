"""General Agent main application entry point."""
from fastapi import FastAPI

app = FastAPI(
    title="General Agent",
    description="通用Agent系统，兼容Skill协议、MCP和RAG",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "General Agent is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

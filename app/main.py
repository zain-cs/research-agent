"""FastAPI entrypoint for ResearchAgent."""
from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="ResearchAgent API",
    description="A tool-using AI research agent (ReAct-style) with web search, "
                 "Wikipedia, arXiv, and calculator tools.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Simple liveness check used by Docker/CI and manual smoke testing."""
    return {
        "status": "ok",
        "env": settings.app_env,
        "model": settings.llm_model,
    }


@app.get("/")
def root():
    return {"message": "ResearchAgent API is running. See /docs for endpoints."}

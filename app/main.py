"""FastAPI entrypoint for ResearchAgent."""
from fastapi import FastAPI
from pydantic import BaseModel
from app.config import settings
from app.agent import run_agent

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


class ResearchRequest(BaseModel):
    question: str


@app.post("/research")
def research(request: ResearchRequest):
    """The main endpoint: ask the agent a question, get a reasoned answer
    with a trace of every tool it used along the way."""
    return run_agent(request.question)


@app.get("/")
def root():
    return {"message": "ResearchAgent API is running. See /docs for endpoints."}
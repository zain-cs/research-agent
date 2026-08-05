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
from app.llm_client import llm_client

@app.get("/test-llm")
def test_llm():
    """Temporary endpoint to confirm the Groq connection works. Will be removed later."""
    reply = llm_client.chat([
        {"role": "user", "content": "Say 'Hello from ResearchAgent!' and nothing else."}
    ])
    return {"reply": reply}


@app.get("/")
def root():
    return {"message": "ResearchAgent API is running. See /docs for endpoints."}

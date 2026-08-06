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

from app.tools.web_search import web_search as web_search_tool

@app.get("/test-search")
def test_search(q: str = "capital of France"):
    """Temporary endpoint to confirm the web search tool works via the API."""
    return {"results": web_search_tool(q)}

from app.tools.wikipedia_tool import wikipedia_search

@app.get("/test-wikipedia")
def test_wikipedia(q: str = "Marie Curie"):
    """Temporary endpoint to confirm the Wikipedia tool works via the API."""
    return {"result": wikipedia_search(q)}

from app.tools.arxiv_tool import arxiv_search

@app.get("/test-arxiv")
def test_arxiv(q: str = "retrieval augmented generation"):
    """Temporary endpoint to confirm the arXiv tool works via the API."""
    return {"result": arxiv_search(q)}


@app.get("/")
def root():
    return {"message": "ResearchAgent API is running. See /docs for endpoints."}

"""Web search tool using DuckDuckGo (no API key required).

Every tool in this package follows the same shape:
- a plain Python function that does the work and returns a string
- a `SCHEMA` dict describing the tool in the format Groq/OpenAI-style
  function calling expects, so the agent core can hand it straight
  to the LLM.
"""
from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    """Run a web search and return a compact, numbered summary of results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"Web search failed: {e}"

    if not results:
        return f"No web results found for '{query}'."

    lines = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "Untitled")
        body = r.get("body", "").strip()
        href = r.get("href", "")
        lines.append(f"{i}. {title}\n   {body}\n   Source: {href}")

    return "\n".join(lines)


SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for current, general-purpose information. "
            "Use this for recent events, facts not likely in an encyclopedia, "
            "or when you need multiple perspectives on a topic."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (default 5).",
                },
            },
            "required": ["query"],
        },
    },
}

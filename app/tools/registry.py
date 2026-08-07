"""Central registry of all tools available to the agent.

Adding a new tool later just means: write the tool module (function + SCHEMA,
following the pattern in web_search.py etc.), then register it here — nothing
else in the agent core needs to change.
"""
from app.tools.web_search import web_search, SCHEMA as WEB_SEARCH_SCHEMA
from app.tools.wikipedia_tool import wikipedia_search, SCHEMA as WIKIPEDIA_SCHEMA
from app.tools.arxiv_tool import arxiv_search, SCHEMA as ARXIV_SCHEMA
from app.tools.calculator import calculate, SCHEMA as CALCULATOR_SCHEMA

# name -> callable. The agent looks up and invokes tools through this dict.
TOOL_FUNCTIONS = {
    "web_search": web_search,
    "wikipedia_search": wikipedia_search,
    "arxiv_search": arxiv_search,
    "calculate": calculate,
}

# The list of schemas sent to the LLM so it knows what tools exist and
# what arguments each one takes.
TOOL_SCHEMAS = [
    WEB_SEARCH_SCHEMA,
    WIKIPEDIA_SCHEMA,
    ARXIV_SCHEMA,
    CALCULATOR_SCHEMA,
]


def execute_tool(name: str, arguments: dict) -> str:
    """Look up a tool by name and call it with the given arguments.
    Returns an error string (not an exception) on failure, since the agent
    loop feeds this straight back to the LLM as a tool result — it should
    always get a string it can reason about, never a crash.
    """
    if name not in TOOL_FUNCTIONS:
        return f"Error: unknown tool '{name}'. Available tools: {list(TOOL_FUNCTIONS.keys())}"
    try:
        return TOOL_FUNCTIONS[name](**arguments)
    except TypeError as e:
        return f"Error: invalid arguments for '{name}': {e}"
    except Exception as e:
        return f"Error: tool '{name}' failed: {e}"

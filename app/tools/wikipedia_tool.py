"""Wikipedia lookup tool.

Note: we call Wikipedia's REST API directly with `requests` rather than using
the `wikipedia` PyPI package — that package is unmaintained (last release ~2014)
and frequently breaks because it doesn't send a proper User-Agent header,
causing Wikipedia to reject requests in ways the library can't parse.

Good for stable, encyclopedic facts (history, science, biography, geography).
Prefer this over web_search when the question is the kind of thing an
encyclopedia article would directly answer.
"""
import requests

SEARCH_URL = "https://en.wikipedia.org/w/api.php"
SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

# Wikipedia's API requires a descriptive User-Agent identifying the app.
HEADERS = {
    "User-Agent": "ResearchAgent/0.1 (student portfolio project; "
                   "contact: mzainulabidin.cs@gmail.com)"
}


def wikipedia_search(query: str, sentences: int = 5) -> str:
    """Look up a topic on Wikipedia and return a short summary."""
    try:
        # Step 1: resolve the best-matching page title for the query.
        search_resp = requests.get(
            SEARCH_URL,
            params={
                "action": "opensearch",
                "search": query,
                "limit": 1,
                "namespace": 0,
                "format": "json",
            },
            headers=HEADERS,
            timeout=10,
        )
        search_resp.raise_for_status()
        titles = search_resp.json()[1]

        if not titles:
            return f"No Wikipedia page found for '{query}'."

        title = titles[0]

        # Step 2: fetch the page summary for that title.
        summary_resp = requests.get(
            SUMMARY_URL.format(title=title.replace(" ", "_")),
            headers=HEADERS,
            timeout=10,
        )
        summary_resp.raise_for_status()
        data = summary_resp.json()

        extract = data.get("extract", "").strip()
        if not extract:
            return f"No summary available for '{title}' on Wikipedia."

        # Trim to the requested number of sentences.
        parts = extract.split(". ")
        trimmed = ". ".join(parts[:sentences]).rstrip(".") + "."

        url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        return f"{trimmed}\n\nSource: {url}"

    except requests.exceptions.RequestException as e:
        return f"Wikipedia lookup failed (network error): {e}"
    except Exception as e:
        return f"Wikipedia lookup failed: {e}"


SCHEMA = {
    "type": "function",
    "function": {
        "name": "wikipedia_search",
        "description": (
            "Look up a topic on Wikipedia for stable, encyclopedic facts — "
            "history, science, biography, geography, definitions. "
            "Prefer this over web_search for well-established topics."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The topic or entity to look up.",
                },
                "sentences": {
                    "type": "integer",
                    "description": "Number of summary sentences to return (default 5).",
                },
            },
            "required": ["query"],
        },
    },
}

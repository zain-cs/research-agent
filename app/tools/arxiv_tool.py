"""arXiv paper search tool.

Useful for research-oriented questions where the agent should ground its
answer in actual published papers rather than general web content —
especially relevant given this project's ML/AI focus.
"""
import arxiv


def arxiv_search(query: str, max_results: int = 3) -> str:
    """Search arXiv for papers matching the query and return titles, authors,
    publication dates, and abstracts (trimmed) with links.
    """
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        results = list(client.results(search))
        if not results:
            return f"No arXiv papers found for '{query}'."

        formatted = []
        for i, paper in enumerate(results, 1):
            authors = ", ".join(a.name for a in paper.authors[:3])
            if len(paper.authors) > 3:
                authors += " et al."
            abstract = paper.summary.replace("\n", " ").strip()
            if len(abstract) > 400:
                abstract = abstract[:400].rsplit(" ", 1)[0] + "..."
            formatted.append(
                f"{i}. {paper.title}\n"
                f"   Authors: {authors}\n"
                f"   Published: {paper.published.strftime('%Y-%m-%d')}\n"
                f"   Abstract: {abstract}\n"
                f"   Link: {paper.entry_id}"
            )

        return "\n\n".join(formatted)

    except Exception as e:
        return f"arXiv search failed: {e}"


SCHEMA = {
    "type": "function",
    "function": {
        "name": "arxiv_search",
        "description": (
            "Search arXiv for academic papers on a topic. Use this for "
            "research-oriented, scientific, or technical questions where "
            "the answer should be grounded in published research rather "
            "than general web content."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The research topic or keywords to search for.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of papers to return (default 3).",
                },
            },
            "required": ["query"],
        },
    },
}

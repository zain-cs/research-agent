# ResearchAgent 🔎🤖

A tool-using AI research agent that reasons step-by-step (ReAct-style) and autonomously calls external tools — web search, Wikipedia, arXiv, and a calculator — to answer research questions with cited, structured responses.

> 🚧 **Status: Under active development.** Follow along as this is built out day by day.

## Why this project?

Most chatbots just retrieve and summarize. This agent *reasons about what it doesn't know*, decides which tool can fill that gap, calls it, observes the result, and iterates — the same loop that powers modern AI agents in production.

## Planned Architecture

```
User Question
      │
      ▼
 ┌─────────────┐      ┌──────────────────┐
 │  Agent Core │◄────►│   LLM (Groq API) │
 │ (ReAct loop)│      └──────────────────┘
 └──────┬──────┘
        │ selects & calls
        ▼
 ┌─────────────────────────────────────────┐
 │  Tools: Web Search │ Wikipedia │ arXiv │ Calculator │
 └─────────────────────────────────────────┘
        │
        ▼
 Cited, structured answer
```

## Tech Stack
- **Backend:** FastAPI, Python
- **LLM:** Groq API (Llama models, free tier)
- **Frontend:** Streamlit
- **Deployment:** Docker, Hugging Face Spaces
- **Testing:** pytest
- **CI:** GitHub Actions

## Roadmap
- [x] Project scaffold
- [ ] Tool implementations (search, Wikipedia, arXiv, calculator)
- [ ] ReAct agent core loop
- [ ] FastAPI endpoints
- [ ] Streamlit chat UI
- [ ] Tests + CI + Docker
- [ ] Live deployment + demo

## Setup
See [`.env.example`](.env.example) for required environment variables. Full setup instructions coming as the project develops.

## License
MIT — see [LICENSE](LICENSE)

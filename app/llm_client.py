"""Thin wrapper around the Groq chat completion API.

Keeping this isolated means the rest of the app (agent core, API layer)
never talks to the Groq SDK directly — if we ever swap providers, only
this file changes.
"""
import time
from groq import Groq, BadRequestError
from app.config import settings

# Occasionally the model generates a malformed tool call (e.g. wrong argument
# names) and Groq rejects it with a 400 'tool_use_failed' error. This is
# model non-determinism, not a bug in our request — retrying the same call
# usually succeeds on the next attempt.
MAX_RETRIES = 2


class LLMClient:
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key "
                "from https://console.groq.com/keys"
            )
        self._client = Groq(api_key=settings.groq_api_key)
        self.model = settings.llm_model

    def chat(self, messages: list[dict], temperature: float = 0.3) -> str:
        """Send a list of {role, content} messages, return the assistant's reply text."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def chat_with_tools(self, messages: list[dict], tools: list[dict], temperature: float = 0.3):
        """Send messages plus tool definitions; return the raw response message
        (may contain tool_calls the agent loop needs to inspect and execute).

        Retries on 'tool_use_failed' errors, since these are usually transient
        model mistakes rather than problems with our request.
        """
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=temperature,
                )
                return response.choices[0].message
            except BadRequestError as e:
                is_tool_use_failure = "tool_use_failed" in str(e)
                if is_tool_use_failure and attempt < MAX_RETRIES:
                    last_error = e
                    time.sleep(0.5)
                    continue
                raise
        raise last_error


llm_client = LLMClient()

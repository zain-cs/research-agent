"""The agent's core reasoning loop (ReAct-style: Reason -> Act -> Observe -> repeat).

Flow per query:
  1. Send the conversation + available tool schemas to the LLM.
  2. If the LLM's response includes tool_calls, execute each one via the
     registry, append the results to the conversation as tool messages,
     and go back to step 1.
  3. If the LLM responds with plain content instead, that's the final
     answer — return it.
  4. If MAX_AGENT_STEPS is reached without a final answer, stop and return
     whatever the LLM has so far, so the agent never hangs indefinitely.
"""
import json
from app.llm_client import llm_client
from app.tools.registry import TOOL_SCHEMAS, execute_tool
from app.config import settings

SYSTEM_PROMPT = (
    "You are ResearchAgent, an AI assistant that answers questions by "
    "reasoning step by step and calling tools when you need information "
    "you don't already know. You have access to: web search (current/general "
    "info), Wikipedia (stable encyclopedic facts), arXiv (academic papers), "
    "and a calculator (precise arithmetic). "
    "Call a tool whenever the question needs current information, specific "
    "facts, or exact numbers rather than guessing. Once you have enough "
    "information, give a clear, well-organized final answer and cite which "
    "sources/tools you used."
)


class AgentStep:
    """A single record of what happened at one loop iteration — used to
    build a trace so the frontend can show the agent's reasoning process.
    """
    def __init__(self, step_type: str, content: str, tool_name: str = None):
        self.step_type = step_type   # "tool_call" | "tool_result" | "final_answer"
        self.content = content
        self.tool_name = tool_name

    def to_dict(self):
        return {"type": self.step_type, "content": self.content, "tool": self.tool_name}


def run_agent(question: str) -> dict:
    """Run the ReAct loop for a single question. Returns the final answer
    plus a trace of every tool call made along the way.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace: list[AgentStep] = []

    for step_num in range(settings.max_agent_steps):
        response_message = llm_client.chat_with_tools(messages, TOOL_SCHEMAS)

        # No tool calls -> the model is giving its final answer.
        if not response_message.tool_calls:
            answer = response_message.content or "I wasn't able to reach a conclusion."
            trace.append(AgentStep("final_answer", answer))
            return {"answer": answer, "trace": [s.to_dict() for s in trace], "steps_used": step_num + 1}

        # Otherwise, execute every tool the model asked for.
        # Note: we build this dict manually rather than using
        # response_message.model_dump() — the SDK's full dump includes extra
        # fields (e.g. "annotations") that Groq's API rejects when they're
        # sent back in the next request.
        messages.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in response_message.tool_calls
            ],
        })

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            trace.append(AgentStep(
                "tool_call",
                f"Calling {tool_name}({tool_args})",
                tool_name=tool_name,
            ))

            result = execute_tool(tool_name, tool_args)

            trace.append(AgentStep("tool_result", result, tool_name=tool_name))

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    # Hit the step limit without a final answer. Rather than replaying the raw
    # conversation (which includes assistant tool_calls messages — some models,
    # like GPT-OSS, have built-in tools of their own and can get confused into
    # attempting one when they see tool-call history but no tools are passed),
    # we build a clean summary of what was learned and ask for a final answer
    # from that instead.
    findings = "\n\n".join(
        step.content for step in trace if step.step_type == "tool_result"
    )
    fallback_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Original question: {question}\n\n"
                f"Information gathered so far:\n{findings}\n\n"
                "Based only on the information above, give your best final answer now."
            ),
        },
    ]
    final_reply = llm_client.chat(fallback_messages)
    trace.append(AgentStep("final_answer", final_reply))
    return {"answer": final_reply, "trace": [s.to_dict() for s in trace], "steps_used": settings.max_agent_steps}

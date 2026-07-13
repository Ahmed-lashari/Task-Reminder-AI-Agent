"""
The agent "brain": a plain tool-calling loop against the Groq API.

Multi-user note: owner_id is a server-side-only value, supplied by
main.py from the request's identity, never something the LLM chooses.
_run_tool strips any "owner_id" key the model might hallucinate into a
tool call and replaces it with the real one every time.

Reliability note: Groq's tool-call parser for this model occasionally
fails silently - instead of raising an error, it returns a normal 200
response where message.content contains raw, malformed function-call
syntax (e.g. "(function=search_tasks>{...}</function") instead of a
structured tool_calls entry. If left unchecked, that garbled text gets
returned to the user as if it were a real answer, while no tool - and
therefore no actual task/reminder creation, search, or deletion - ever
ran. _looks_like_leaked_tool_call() catches this and forces a retry
instead of trusting it.
"""

import json
import os
import re
import time

from groq import Groq

from agent.planner import build_system_prompt
from agent.state import ConversationState
from storage.base import BaseStorage
from storage.chat_reminder_repository import ChatReminderRepository
from tools.registry import DISPATCH, TOOL_SCHEMAS

MAX_TOOL_ITERATIONS = 6
MAX_LLM_RETRIES = 2       # retries on an actual API exception
MAX_LEAK_RETRIES = 3      # retries on a "successful" response that leaked
                          # malformed function-call syntax into plain text
CHAT_REMINDER_TOOL = "create_chat_reminder"

_LEAKED_FUNCTION_CALL = re.compile(r"\(?<?function\s*=\s*\w+\s*>", re.IGNORECASE)


def _to_provider_tools(schemas: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": s["name"],
                "description": s["description"],
                "parameters": s["input_schema"],
            },
        }
        for s in schemas
    ]


class Agent:
    def __init__(self, storage: BaseStorage, chat_reminder_repository: ChatReminderRepository, verbose: bool = True):
        self.storage = storage
        self.chat_reminder_repository = chat_reminder_repository
        self.verbose = verbose
        self.client = Groq(api_key=os.environ["LLM_API_KEY"])
        self.model = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
        self.tools = _to_provider_tools(TOOL_SCHEMAS)
        self._conversations: dict[str, ConversationState] = {}

    def _state_for(self, owner_id: str) -> ConversationState:
        if owner_id not in self._conversations:
            self._conversations[owner_id] = ConversationState()
        return self._conversations[owner_id]

    def handle(self, user_text: str, owner_id: str) -> str:
        state = self._state_for(owner_id)
        state.add_user(user_text)

        leak_retries_used = 0
        for _ in range(MAX_TOOL_ITERATIONS):
            response = self._call_llm_with_retry(state)
            if response is None:
                if state.messages and state.messages[-1]["role"] == "user":
                    state.messages.pop()
                return "Sorry, I ran into a problem processing that - could you rephrase or try again?"

            message = response.choices[0].message
            tool_calls = message.tool_calls or []

            if not tool_calls and message.content and _LEAKED_FUNCTION_CALL.search(message.content):
                leak_retries_used += 1
                if self.verbose:
                    print(f"  [leaked function-call text, retry {leak_retries_used}/{MAX_LEAK_RETRIES}] "
                          f"{message.content[:200]!r}")
                if leak_retries_used >= MAX_LEAK_RETRIES:
                    if state.messages and state.messages[-1]["role"] == "user":
                        state.messages.pop()
                    return "Sorry, I had trouble completing that action - could you try again or rephrase it?"
                continue  # do NOT add this to history, do NOT return it - just retry

            state.add_assistant(message.content, tool_calls)

            if not tool_calls:
                return (message.content or "").strip()

            for call in tool_calls:
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = self._run_tool(call.function.name, args, owner_id)
                if self.verbose:
                    print(f"  [tool] {call.function.name}({args}) -> {result}")
                state.add_tool_result(call.id, result)

        return "Sorry, that took too many steps - can you rephrase or break it into smaller requests?"

    def _call_llm_with_retry(self, state: ConversationState):
        for attempt in range(MAX_LLM_RETRIES):
            try:
                return self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "system", "content": build_system_prompt()}] + state.messages,
                    tools=self.tools,
                    parallel_tool_calls=False,  # this model's tool-call parser breaks when it
                                                 # chains multiple calls into one completion
                )
            except Exception as e:  # noqa: BLE001
                if self.verbose:
                    print(f"  [llm error, attempt {attempt + 1}/{MAX_LLM_RETRIES}] {e}")
                time.sleep(0.5)
        return None

    def _run_tool(self, name: str, tool_input: dict, owner_id: str) -> dict:
        fn = DISPATCH.get(name)
        if not fn:
            return {"ok": False, "error": f"unknown_tool:{name}"}
        resource = self.chat_reminder_repository if name == CHAT_REMINDER_TOOL else self.storage
        tool_input.pop("owner_id", None)  # never trust an LLM-supplied owner_id
        try:
            return fn(resource, owner_id, **tool_input)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

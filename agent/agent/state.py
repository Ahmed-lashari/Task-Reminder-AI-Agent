"""
Short-term memory: the last N turns, used to resolve references like
"move it to friday" within a session.

Long-term memory (what actually happened - created/updated/deleted tasks)
already lives in storage as ConversationTurn rows via
storage.append_conversation. This class is just the in-memory working set
fed into each LLM call; it does not itself decide what's "meaningful enough"
to persist long-term - that's a Phase 2 refinement (e.g. only persisting
turns where a tool ran).
"""
from __future__ import annotations

import json


class ConversationState:
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.messages: list[dict] = []  # Anthropic message format

    def add_user(self, text: str):
        self.messages.append({"role": "user", "content": text})
        self._trim()

    def add_assistant(self, content: str | None, tool_calls: list = None):
        msg = {"role": "assistant", "content": content}
        if tool_calls:
            msg["tool_calls"] = [tc.model_dump() for tc in tool_calls]
        self.messages.append(msg)
        self._trim()

    def add_tool_result(self, tool_call_id: str, result: dict):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(result, default=str),
        })
        self._trim()

    def _trim(self):
        # keep it simple: cap total messages. A smarter version would
        # summarize older turns instead of dropping them.
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]

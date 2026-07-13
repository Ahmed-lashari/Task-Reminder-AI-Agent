"""
Abstract storage interface.

Every tool in tools/ talks to *this* interface, never to JSON or Hive
directly. Today, storage/json_store.py implements it with a file on disk.

All task/conversation reads and writes are scoped by owner_id - the
storage layer is where multi-user isolation is enforced, not the LLM or
the tools calling it. A caller can never read another owner's task by id:
get_task/update_task/delete_task/cancel_reminders_for_task all require a
matching owner_id or return nothing.

Reminder (task-linked) intentionally has no owner_id of its own -
ownership is derived through task_id -> Task.owner_id, since a reminder
without its task means nothing on its own.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from models.schemas import ConversationTurn, Reminder, Task


class BaseStorage(ABC):
    # ---- tasks ----
    @abstractmethod
    def create_task(self, task: Task) -> Task: ...

    @abstractmethod
    def get_task(self, task_id: str, owner_id: str) -> Optional[Task]: ...

    @abstractmethod
    def update_task(self, task_id: str, owner_id: str, **fields) -> Optional[Task]: ...

    @abstractmethod
    def delete_task(self, task_id: str, owner_id: str) -> bool: ...

    @abstractmethod
    def list_tasks(self, owner_id: str) -> list[Task]: ...

    @abstractmethod
    def search_tasks(
        self,
        owner_id: str,
        query: Optional[str] = None,
        status: Optional[str] = None,
        start_after: Optional[datetime] = None,
        start_before: Optional[datetime] = None,
    ) -> list[Task]: ...

    # ---- reminders (ownership derived via task_id) ----
    @abstractmethod
    def create_reminder(self, reminder: Reminder) -> Reminder: ...

    @abstractmethod
    def cancel_reminders_for_task(self, task_id: str, owner_id: str) -> int: ...

    @abstractmethod
    def list_due_reminders(self, now: datetime) -> list[Reminder]: ...

    @abstractmethod
    def mark_reminder_sent(self, reminder_id: str) -> None: ...

    # ---- conversation memory ----
    @abstractmethod
    def append_conversation(self, turn: ConversationTurn) -> None: ...

    @abstractmethod
    def recent_conversation(self, owner_id: str, limit: int = 20) -> list[ConversationTurn]: ...

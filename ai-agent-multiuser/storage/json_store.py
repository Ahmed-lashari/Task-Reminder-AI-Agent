"""
Temporary stand-in for Hive. Everything lives in one JSON file on disk,
loaded into memory on init and rewritten after every mutation.

Multi-user isolation lives here: get/update/delete/search/cancel/list all
require an owner_id and only ever touch that owner's records. A caller
guessing another user's task id gets exactly the same result as a
nonexistent id - None / False / empty list, never someone else's data.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime
from typing import Optional

from models.schemas import ConversationTurn, Reminder, ReminderStatus, Task
from storage.base import BaseStorage


class JsonStore(BaseStorage):
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._data = {"tasks": {}, "reminders": {}, "conversation": []}
        self._load()

    # ---------- persistence ----------
    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                raw = json.load(f)
            self._data["tasks"] = {
                tid: Task(**t) for tid, t in raw.get("tasks", {}).items()
            }
            self._data["reminders"] = {
                rid: Reminder(**r) for rid, r in raw.get("reminders", {}).items()
            }
            self._data["conversation"] = [
                ConversationTurn(**c) for c in raw.get("conversation", [])
            ]
        else:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

    def _save(self):
        raw = {
            "tasks": {tid: json.loads(t.model_dump_json()) for tid, t in self._data["tasks"].items()},
            "reminders": {rid: json.loads(r.model_dump_json()) for rid, r in self._data["reminders"].items()},
            "conversation": [json.loads(c.model_dump_json()) for c in self._data["conversation"]],
        }
        with open(self.path, "w") as f:
            json.dump(raw, f, indent=2, default=str)

    # ---------- tasks ----------
    def create_task(self, task: Task) -> Task:
        with self._lock:
            self._data["tasks"][task.id] = task
            self._save()
        return task

    def get_task(self, task_id: str, owner_id: str) -> Optional[Task]:
        task = self._data["tasks"].get(task_id)
        return task if task and task.owner_id == owner_id else None

    def update_task(self, task_id: str, owner_id: str, **fields) -> Optional[Task]:
        with self._lock:
            task = self._data["tasks"].get(task_id)
            if not task or task.owner_id != owner_id:
                return None
            updated = task.model_copy(update=fields)
            self._data["tasks"][task_id] = updated
            self._save()
            return updated

    def delete_task(self, task_id: str, owner_id: str) -> bool:
        with self._lock:
            task = self._data["tasks"].get(task_id)
            if not task or task.owner_id != owner_id:
                return False
            del self._data["tasks"][task_id]
            self._save()
            return True

    def list_tasks(self, owner_id: str) -> list[Task]:
        return [t for t in self._data["tasks"].values() if t.owner_id == owner_id]

    def search_tasks(
        self,
        owner_id: str,
        query: Optional[str] = None,
        status: Optional[str] = None,
        start_after: Optional[datetime] = None,
        start_before: Optional[datetime] = None,
    ) -> list[Task]:
        results = self.list_tasks(owner_id)
        if query:
            q = query.lower()
            results = [t for t in results if q in t.title.lower() or (t.description or "").lower().find(q) >= 0]
        if status:
            results = [t for t in results if t.status == status]
        if start_after:
            results = [t for t in results if t.start_time and t.start_time >= start_after]
        if start_before:
            results = [t for t in results if t.start_time and t.start_time <= start_before]
        return results

    # ---------- reminders ----------
    def create_reminder(self, reminder: Reminder) -> Reminder:
        with self._lock:
            self._data["reminders"][reminder.id] = reminder
            self._save()
        return reminder

    def cancel_reminders_for_task(self, task_id: str, owner_id: str) -> int:
        task = self._data["tasks"].get(task_id)
        if not task or task.owner_id != owner_id:
            return 0
        with self._lock:
            count = 0
            for rid, r in self._data["reminders"].items():
                if r.task_id == task_id and r.status == ReminderStatus.SCHEDULED:
                    self._data["reminders"][rid] = r.model_copy(update={"status": ReminderStatus.CANCELLED})
                    count += 1
            if count:
                self._save()
            return count

    def list_due_reminders(self, now: datetime) -> list[Reminder]:
        # Not owner-scoped: the scheduler polls across all users, then
        # main.py routes each delivery to the correct owner's socket by
        # looking up the linked task's owner_id.
        return [
            r for r in self._data["reminders"].values()
            if r.status == ReminderStatus.SCHEDULED and r.trigger_time <= now
        ]

    def mark_reminder_sent(self, reminder_id: str) -> None:
        with self._lock:
            r = self._data["reminders"].get(reminder_id)
            if r:
                self._data["reminders"][reminder_id] = r.model_copy(update={"status": ReminderStatus.SENT})
                self._save()

    # ---------- conversation memory ----------
    def append_conversation(self, turn: ConversationTurn) -> None:
        with self._lock:
            self._data["conversation"].append(turn)
            self._data["conversation"] = self._data["conversation"][-500:]
            self._save()

    def recent_conversation(self, owner_id: str, limit: int = 20) -> list[ConversationTurn]:
        owned = [c for c in self._data["conversation"] if c.owner_id == owner_id]
        return owned[-limit:]

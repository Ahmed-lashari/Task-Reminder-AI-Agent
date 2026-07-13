"""
Persists ChatReminder objects to a JSON file. Each reminder carries its
own owner_id (unlike task-linked Reminder, a chat reminder has no parent
object to derive ownership from). due() is intentionally NOT owner-scoped -
the scheduler polls across all users; main.py routes each delivery to the
correct owner's socket using reminder.owner_id.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime

from models.schemas import ChatReminder, ChatReminderStatus


class ChatReminderRepository:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._reminders: dict[str, ChatReminder] = {}
        self._load()

    def add(self, reminder: ChatReminder) -> ChatReminder:
        with self._lock:
            self._reminders[reminder.id] = reminder
            self._save()
        return reminder

    def due(self, now: datetime) -> list[ChatReminder]:
        return [
            r for r in self._reminders.values()
            if r.status == ChatReminderStatus.PENDING and r.due_time <= now
        ]

    def mark_delivered(self, reminder_id: str) -> None:
        with self._lock:
            reminder = self._reminders.get(reminder_id)
            if reminder:
                self._reminders[reminder_id] = reminder.model_copy(
                    update={"status": ChatReminderStatus.DELIVERED}
                )
                self._save()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                raw = json.load(f)
            self._reminders = {rid: ChatReminder(**r) for rid, r in raw.items()}
        else:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            self._save()

    def _save(self):
        raw = {rid: json.loads(r.model_dump_json()) for rid, r in self._reminders.items()}
        with open(self.path, "w") as f:
            json.dump(raw, f, indent=2, default=str)

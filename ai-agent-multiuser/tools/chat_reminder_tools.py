"""
Tool for standalone, non-task reminders - "remind me to X in Y". Delivered
as a plain chat message at due_time via ChatReminderScheduler, not tied to
any Task.
"""
from __future__ import annotations

from models.schemas import ChatReminder
from storage.chat_reminder_repository import ChatReminderRepository
from tools.task_tools import _parse_dt


def create_chat_reminder(repository: ChatReminderRepository, owner_id: str, message: str, due_time: str) -> dict:
    parsed_due_time = _parse_dt(due_time)
    if not parsed_due_time:
        return {"ok": False, "error": "could_not_parse_due_time"}

    reminder = ChatReminder(owner_id=owner_id, message=message, due_time=parsed_due_time)
    repository.add(reminder)
    return {"ok": True, "reminder": reminder.model_dump(mode="json")}

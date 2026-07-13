from __future__ import annotations

from datetime import timedelta

from models.schemas import Reminder, Task
from storage.base import BaseStorage


def schedule_reminders(storage: BaseStorage, task: Task) -> list[Reminder]:
    """Creates the default reminder for a task. Called automatically by
    task_tools on create/reschedule - not usually invoked directly by the LLM,
    but exposed here in case you want the agent to add extra reminders."""
    if not task.start_time:
        return []
    trigger = task.start_time - timedelta(minutes=task.default_reminder_minutes_before)
    reminder = Reminder(task_id=task.id, trigger_time=trigger)
    return [storage.create_reminder(reminder)]


def cancel_reminders(storage: BaseStorage, task_id: str, owner_id: str) -> dict:
    count = storage.cancel_reminders_for_task(task_id, owner_id)
    return {"ok": True, "cancelled": count}

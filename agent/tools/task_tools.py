"""
Task tools. Each function takes storage, then owner_id, then plain args
matching what the LLM produces as tool input. owner_id is injected by
Agent._run_tool from the authenticated request context - it is never a
field the LLM can see or set (see tools/registry.py: no owner_id in any
tool schema). Every storage call here is owner-scoped, so one user's
tools can never touch another user's tasks.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import dateparser

from models.schemas import Task, TaskStatus
from storage.base import BaseStorage
from tools.reminder_tools import cancel_reminders, schedule_reminders


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    dt = dateparser.parse(value, settings={"PREFER_DATES_FROM": "future"})
    if dt and dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)  # strip tz, treat everything as local naive time
    return dt


def create_task(
    storage: BaseStorage,
    owner_id: str,
    title: str,
    description: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    priority: Optional[str] = None,
    recurrence_rule: Optional[str] = None,
) -> dict:
    task = Task(
        owner_id=owner_id,
        title=title,
        description=description,
        start_time=_parse_dt(start_time),
        end_time=_parse_dt(end_time),
        priority=_clean_priority(priority),
        recurrence_rule=recurrence_rule,
    )
    task = storage.create_task(task)
    if task.start_time:
        schedule_reminders(storage, task)
    return {"ok": True, "task": task.model_dump(mode="json")}


def update_task(
    storage: BaseStorage,
    owner_id: str,
    task_id: Optional[str] = None,
    title_match: Optional[str] = None,
    **fields,
) -> dict:
    """
    task_id is preferred. If the agent only has a fuzzy reference (e.g. "the
    gym task"), pass title_match instead and we resolve it here.
    """
    resolved_id = task_id or _resolve_task_id(storage, owner_id, title_match)
    if not resolved_id:
        return {"ok": False, "error": "task_not_found"}

    clean_fields = {}
    if "start_time" in fields:
        clean_fields["start_time"] = _parse_dt(fields.pop("start_time"))
    if "end_time" in fields:
        clean_fields["end_time"] = _parse_dt(fields.pop("end_time"))
    clean_fields.update(fields)

    task = storage.update_task(resolved_id, owner_id, **clean_fields)
    if not task:
        return {"ok": False, "error": "task_not_found"}

    # if the time changed, reschedule reminders
    if "start_time" in clean_fields:
        cancel_reminders(storage, task.id, owner_id)
        if task.start_time:
            schedule_reminders(storage, task)

    return {"ok": True, "task": task.model_dump(mode="json")}


def complete_task(
    storage: BaseStorage, owner_id: str, task_id: Optional[str] = None, title_match: Optional[str] = None
) -> dict:
    resolved_id = task_id or _resolve_task_id(storage, owner_id, title_match)
    if not resolved_id:
        return {"ok": False, "error": "task_not_found"}
    task = storage.update_task(resolved_id, owner_id, status=TaskStatus.COMPLETED)
    cancel_reminders(storage, resolved_id, owner_id)
    return {"ok": True, "task": task.model_dump(mode="json")} if task else {"ok": False, "error": "task_not_found"}


def delete_task(
    storage: BaseStorage, owner_id: str, task_id: Optional[str] = None, title_match: Optional[str] = None
) -> dict:
    resolved_id = task_id or _resolve_task_id(storage, owner_id, title_match)
    if not resolved_id:
        return {"ok": False, "error": "task_not_found"}
    cancel_reminders(storage, resolved_id, owner_id)
    deleted = storage.delete_task(resolved_id, owner_id)
    return {"ok": deleted}


def delete_tasks_after(storage: BaseStorage, owner_id: str, anchor_title_match: str) -> dict:
    """Supports: 'remove everything after my doctor's appointment'."""
    anchor_id = _resolve_task_id(storage, owner_id, anchor_title_match)
    if not anchor_id:
        return {"ok": False, "error": "anchor_task_not_found"}
    anchor = storage.get_task(anchor_id, owner_id)
    if not anchor or not anchor.start_time:
        return {"ok": False, "error": "anchor_has_no_time"}

    later_tasks = storage.search_tasks(owner_id, start_after=anchor.start_time)
    deleted_ids = []
    for t in later_tasks:
        if t.id == anchor_id:
            continue
        cancel_reminders(storage, t.id, owner_id)
        storage.delete_task(t.id, owner_id)
        deleted_ids.append(t.id)
    return {"ok": True, "deleted_task_ids": deleted_ids, "count": len(deleted_ids)}


def search_tasks(
    storage: BaseStorage,
    owner_id: str,
    query: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    tasks = storage.search_tasks(
        owner_id,
        query=query or None,
        status=_clean_status(status),
        start_after=_parse_dt(date_from),
        start_before=_parse_dt(date_to),
    )
    return {"ok": True, "tasks": [t.model_dump(mode="json") for t in tasks], "count": len(tasks)}


def day_summary(storage: BaseStorage, owner_id: str, date: str) -> dict:
    target = _parse_dt(date)
    if not target:
        return {"ok": False, "error": "could_not_parse_date"}
    day_start = target.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = target.replace(hour=23, minute=59, second=59)
    tasks = storage.search_tasks(owner_id, start_after=day_start, start_before=day_end)
    return {"ok": True, "date": day_start.date().isoformat(), "tasks": [t.model_dump(mode="json") for t in tasks]}


# ---------- helpers ----------
def _resolve_task_id(storage: BaseStorage, owner_id: str, title_match: Optional[str]) -> Optional[str]:
    if not title_match:
        return None
    matches = storage.search_tasks(owner_id, query=title_match)
    if not matches:
        return None
    # naive: most recently created match wins. Good enough for Phase 1 -
    # this is exactly the kind of ambiguity-resolution logic worth improving
    # in Phase 2.
    matches.sort(key=lambda t: t.created_at, reverse=True)
    return matches[0].id


_VALID_STATUSES = {"pending", "completed", "cancelled"}
_VALID_PRIORITIES = {"low", "medium", "high"}


def _clean_status(value: Optional[str]) -> Optional[str]:
    """Anything not exactly one of our real statuses ("all", "", "none",
    a typo, etc.) is treated as no filter rather than raising."""
    return value if value in _VALID_STATUSES else None


def _clean_priority(value: Optional[str]) -> Optional[str]:
    return value if value in _VALID_PRIORITIES else None

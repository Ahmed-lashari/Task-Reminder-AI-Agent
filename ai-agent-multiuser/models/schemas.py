"""
Data models. These mirror the Dart models from the original plan
(Task, Reminder, Conversation) so that Phase 2's Hive layer can adopt
the same fields with minimal translation.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def new_id() -> str:
    return uuid.uuid4().hex[:12]


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReminderStatus(str, Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    CANCELLED = "cancelled"


class Task(BaseModel):
    id: str = Field(default_factory=new_id)
    owner_id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    priority: Optional[str] = None  # "low" | "medium" | "high"
    recurrence_rule: Optional[str] = None  # e.g. "FREQ=WEEKLY;BYDAY=MO"
    default_reminder_minutes_before: int = 30
    created_at: datetime = Field(default_factory=datetime.now)


class Reminder(BaseModel):
    id: str = Field(default_factory=new_id)
    task_id: str
    trigger_time: datetime
    status: ReminderStatus = ReminderStatus.SCHEDULED
    type: str = "default"  # e.g. "default", "recurring_instance"


class ConversationTurn(BaseModel):
    owner_id: str
    role: str  # "user" | "assistant" | "tool"
    message: str
    tool_calls: Optional[list] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatReminderStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ChatReminder(BaseModel):
    """A standalone, non-task reminder delivered as a plain chat message
    at due_time. Deliberately separate from Reminder (task-bound, fires
    before a task's start_time) - different trigger semantics."""
    id: str = Field(default_factory=new_id)
    owner_id: str
    message: str
    due_time: datetime
    status: ChatReminderStatus = ChatReminderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)

"""
Single source of truth for "what tools does the agent have".

Note: no `enum` constraints on string fields. Provider-side strict
validation (Groq, and others) will hard-reject a call before it even
reaches our code if the model sends something outside the enum - things
like "all", "", or a synonym it invented. We describe valid values in
text instead and normalize defensively in the tool functions themselves.
"""
from __future__ import annotations

from tools import chat_reminder_tools, task_tools

TOOL_SCHEMAS = [
    {
        "name": "create_task",
        "description": "Create a new task/reminder item. Use for things like 'remind me to X', 'add gym tomorrow', 'I have a doctor's appointment friday'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "start_time": {"type": "string", "description": "ISO-8601 datetime if you can compute it, otherwise natural language like 'tomorrow 9am'"},
                "end_time": {"type": "string"},
                "priority": {"type": "string", "description": "One of: low, medium, high. Omit if not mentioned - never guess."},
                "recurrence_rule": {"type": "string", "description": "e.g. FREQ=WEEKLY;BYDAY=MO"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "update_task",
        "description": "Update an existing task's fields (e.g. move its time, rename it, change priority). Use task_id if known, otherwise title_match to fuzzily identify it (e.g. 'the gym task').",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "title_match": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "start_time": {"type": "string"},
                "end_time": {"type": "string"},
                "priority": {"type": "string", "description": "One of: low, medium, high."},
                "recurrence_rule": {"type": "string"},
            },
        },
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "title_match": {"type": "string"},
            },
        },
    },
    {
        "name": "delete_task",
        "description": "Delete a single task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "title_match": {"type": "string"},
            },
        },
    },
    {
        "name": "delete_tasks_after",
        "description": "Delete every task scheduled after a given anchor task (e.g. 'remove everything after my doctor's appointment').",
        "input_schema": {
            "type": "object",
            "properties": {
                "anchor_title_match": {"type": "string"},
            },
            "required": ["anchor_title_match"],
        },
    },
    {
        "name": "search_tasks",
        "description": "Search/filter tasks by text, status, or date range. Use this to answer 'what do I have on friday', 'what's still pending', etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "status": {"type": "string", "description": "One of: pending, completed, cancelled. Omit this field entirely for all statuses - never pass 'all' or an empty string."},
                "date_from": {"type": "string"},
                "date_to": {"type": "string"},
            },
        },
    },
    {
        "name": "create_chat_reminder",
        "description": "Create a standalone reminder delivered as a chat message at the exact requested time (e.g. 'remind me to drink water in 20 minutes', 'remind me to call mom tomorrow at 5pm'). Use this instead of create_task when the user just wants to be told something later - not schedule an actual task with a start time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "What to remind the user of, in plain language."},
                "due_time": {"type": "string", "description": "When to deliver the reminder. ISO-8601 if you can compute it, otherwise natural language like 'in 20 minutes' or 'tomorrow at 5pm'."},
            },
            "required": ["message", "due_time"],
        },
    },
    {
        "name": "day_summary",
        "description": "Get all tasks for a specific day, e.g. 'today', 'tomorrow', a specific date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
            },
            "required": ["date"],
        },
    },
]

DISPATCH = {
    "create_task": task_tools.create_task,
    "update_task": task_tools.update_task,
    "complete_task": task_tools.complete_task,
    "delete_task": task_tools.delete_task,
    "delete_tasks_after": task_tools.delete_tasks_after,
    "search_tasks": task_tools.search_tasks,
    "day_summary": task_tools.day_summary,
    "create_chat_reminder": chat_reminder_tools.create_chat_reminder,
}
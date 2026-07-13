"""
Every N seconds: load due reminders, fire the on_due callback (defaults to
printing - used by cli.py), mark sent.

Runs in a background thread so the caller (CLI or FastAPI) stays responsive.
"""
from __future__ import annotations

import threading
from datetime import datetime

from storage.base import BaseStorage


class Scheduler:
    def __init__(self, storage: BaseStorage, interval_seconds: int = 10, on_due=None):
        self.storage = storage
        self.interval_seconds = interval_seconds
        self.on_due = on_due or self._default_print
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        while not self._stop.is_set():
            self._tick()
            self._stop.wait(self.interval_seconds)

    def _tick(self):
        due = self.storage.list_due_reminders(datetime.now())
        for reminder in due:
            task = self.storage.get_task(reminder.task_id)
            self.on_due(reminder, task)
            self.storage.mark_reminder_sent(reminder.id)

    @staticmethod
    def _default_print(reminder, task):
        title = task.title if task else "(deleted task)"
        print(f"\n🔔 REMINDER: {title}\nYou: ", end="", flush=True)
"""
Polls ChatReminderRepository for due reminders and hands each to on_due.
Mirrors scheduler.Scheduler's polling shape but operates on ChatReminder
instead of task-linked Reminder - kept separate rather than generalizing
Scheduler, since the two have different due-conditions and no shared state.
"""
from __future__ import annotations

import threading
from datetime import datetime

from storage.chat_reminder_repository import ChatReminderRepository


class ChatReminderScheduler:
    def __init__(self, repository: ChatReminderRepository, interval_seconds: int = 5, on_due=None):
        self.repository = repository
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
        for reminder in self.repository.due(datetime.now()):
            self.on_due(reminder)
            self.repository.mark_delivered(reminder.id)

    @staticmethod
    def _default_print(reminder):
        print(f"\n⏰ Reminder: {reminder.message}\nYou: ", end="", flush=True)

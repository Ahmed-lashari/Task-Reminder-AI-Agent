import os

from dotenv import load_dotenv

from agent.llm import Agent  # noqa: E402
from scheduler.scheduler import Scheduler  # noqa: E402
from scheduler.chat_reminder_scheduler import ChatReminderScheduler  # noqa: E402
from storage.json_store import JsonStore  # noqa: E402
from storage.chat_reminder_repository import ChatReminderRepository  # noqa: E402


CLI_OWNER_ID = "cli-local-user"


def main():
    data_file = os.environ.get("DATA_FILE", "data/store.json")
    reminders_file = os.environ.get("CHAT_REMINDERS_FILE", "data/reminders.json")
    interval = int(os.environ.get("SCHEDULER_INTERVAL_SECONDS", "10"))
    reminder_interval = int(os.environ.get("CHAT_REMINDER_INTERVAL_SECONDS", "5"))

    storage = JsonStore(data_file)
    chat_reminder_repository = ChatReminderRepository(reminders_file)
    agent = Agent(storage, chat_reminder_repository, verbose=True)

    scheduler = Scheduler(storage, interval_seconds=interval)
    chat_reminder_scheduler = ChatReminderScheduler(chat_reminder_repository, interval_seconds=reminder_interval)
    scheduler.start()
    chat_reminder_scheduler.start()

    print("Task AI. Ctrl+C to quit.\n")
    try:
        while True:
            user_text = input("You: ").strip()
            if not user_text:
                continue
            reply = agent.handle(user_text, CLI_OWNER_ID)
            print(f"Agent: {reply}\n")
    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        scheduler.stop()
        chat_reminder_scheduler.stop()


if __name__ == "__main__":
    load_dotenv()
    main()

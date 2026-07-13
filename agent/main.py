import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from agent.llm import Agent
from scheduler.scheduler import Scheduler
from scheduler.chat_reminder_scheduler import ChatReminderScheduler
from storage.json_store import JsonStore
from storage.chat_reminder_repository import ChatReminderRepository

storage = JsonStore(os.environ.get("DATA_FILE", "data/store.json"))
chat_reminder_repository = ChatReminderRepository(os.environ.get("CHAT_REMINDERS_FILE", "data/reminders.json"))
agent = Agent(storage, chat_reminder_repository, verbose=True)

# owner_id -> set of open websockets for that user. A reminder is only ever
# broadcast to sockets belonging to the same owner_id it was created under.
sockets_by_owner: dict[str, set[WebSocket]] = {}
main_loop = None


def _send_to_owner(owner_id: str, payload: dict):
    if main_loop is None:
        return
    for ws in list(sockets_by_owner.get(owner_id, set())):
        asyncio.run_coroutine_threadsafe(ws.send_json(payload), main_loop)


def broadcast_task_reminder(reminder, task):
    if not task:
        return  # task was deleted before the reminder fired - nothing to deliver or attribute
    _send_to_owner(task.owner_id, {
        "type": "reminder_due",
        "task_id": reminder.task_id,
        "title": task.title,
        "trigger_time": reminder.trigger_time.isoformat(),
    })


def broadcast_chat_reminder(reminder):
    _send_to_owner(reminder.owner_id, {
        "type": "chat_reminder",
        "message": f"⏰ Reminder: {reminder.message}",
    })


scheduler = Scheduler(
    storage,
    interval_seconds=int(os.environ.get("SCHEDULER_INTERVAL_SECONDS", "10")),
    on_due=broadcast_task_reminder,
)

chat_reminder_scheduler = ChatReminderScheduler(
    chat_reminder_repository,
    interval_seconds=int(os.environ.get("CHAT_REMINDER_INTERVAL_SECONDS", "5")),
    on_due=broadcast_chat_reminder,
)

app = FastAPI(title="Task AI Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup():
    global main_loop
    main_loop = asyncio.get_event_loop()
    scheduler.start()
    chat_reminder_scheduler.start()


@app.on_event("shutdown")
def shutdown():
    scheduler.stop()
    chat_reminder_scheduler.stop()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(payload: dict):
    owner_id = payload.get("owner_id")
    if not owner_id:
        return {"error": "owner_id is required"}, 400
    reply = agent.handle(payload.get("message", ""), owner_id)
    return {"reply": reply}


@app.websocket("/ws/reminders")
async def ws_reminders(websocket: WebSocket, owner_id: str):
    await websocket.accept()
    sockets_by_owner.setdefault(owner_id, set()).add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keeps connection alive, ignore content
    except WebSocketDisconnect:
        sockets_by_owner.get(owner_id, set()).discard(websocket)

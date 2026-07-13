# Task AI Backend (Phase 1 — Agent Only, Terminal Testing)

This is the **backend/agent half only**. No Flutter, no Hive, no FastAPI server
required to get started — you talk to the agent directly in the terminal.

## Why it's built this way

- **No LangGraph yet.** The agent is a plain "call Claude → if it wants a tool,
  run the tool → feed the result back → repeat" loop in `agent/llm.py`. This is
  the same pattern LangGraph wraps, just visible and easy to print/debug.
  Once this loop proves itself, swapping it for a LangGraph graph is a
  refactor of one file, not a redesign.

- **No Hive.** Hive is a Flutter-only database — it can't run in this Python
  process. For this phase, `storage/json_store.py` is a stand-in: a single
  JSON file on disk that implements the exact same interface
  (`storage/base.py`) that the Flutter-Hive layer will implement later.
  The tools never talk to JSON or Hive directly — they talk to the
  interface. That's the seam where Phase 2 plugs in.

- **No cloud, no auth, no REST APIs beyond what you need later.** Matches the
  original plan — single user, offline-first, effort goes into the agent.

## Folder structure

```
task_ai_backend/
├── README.md
├── requirements.txt
├── .env.example
├── cli.py                 # <-- run this. Terminal chat loop.
├── main.py                # empty FastAPI stub for Phase 2 (not needed yet)
├── agent/
│   ├── llm.py              # the tool-calling loop (the "brain")
│   ├── planner.py          # system prompt + date/time context
│   └── state.py            # short-term conversation memory
├── tools/
│   ├── registry.py          # tool schemas (what Claude sees) + dispatch table
│   ├── task_tools.py        # create/update/delete/complete/search tasks
│   └── reminder_tools.py    # schedule/cancel reminders, day summaries
├── storage/
│   ├── base.py              # abstract interface — the swap seam
│   └── json_store.py        # temporary JSON-file implementation
├── models/
│   └── schemas.py           # Task, Reminder, ConversationTurn (pydantic)
├── scheduler/
│   └── scheduler.py         # background thread, checks due reminders
└── data/
    └── store.json           # created automatically on first run
```

## Setup

```bash
cd task_ai_backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# put your Anthropic API key in .env
```

## Run

```bash
python cli.py
```

Try:

```
You: tomorrow gym at 6am
You: what's on my list for tomorrow?
You: move the gym task to friday
You: remove everything after my doctor's appointment
```

# Task AI Agent

A personal task and reminder assistant you talk to like a chatbot. Tell it
what you need done in plain English. It figures out what you meant,
saves it, and reminds you exactly when it's due, right inside the chat.

## What it can actually do

- Create tasks with a date/time ("gym tomorrow at 6am")
- Move, complete, or delete tasks, even with vague references ("move the gym one to Friday")
- Search or summarize tasks ("what do I have pending", "what's on Friday")
- Set one/off reminders that aren't tied to a task ("remind me to drink water in 20 minutes")
- Deliver reminders straight into the chat the moment they're due — no push notifications, no email
- Keep each person's tasks private from everyone else, without logins or passwords — just a name and a private phrase

## How it works, in one paragraph

You chat with an AI model that's been given a fixed set of tools —
create a task, search tasks, set a reminder, and so on. The AI decides
_when_ to use each tool based on what you type; your backend code is
what actually runs it and saves the result. A background process checks
every few seconds for anything due, and pushes it straight into your
chat the moment it's time.

## Tech stack

### Backend

| Piece                 | What it is                                                    |
| --------------------- | ------------------------------------------------------------- |
| Language              | Python                                                        |
| Web framework         | FastAPI                                                       |
| AI model              | Groq (Llama), swappable for any OpenAI-compatible model       |
| Data storage          | Plain JSON files on disk — no database                        |
| Real-time delivery    | WebSocket connection, pushes reminders the moment they're due |
| Background scheduling | A lightweight in-process loop, no external job queue          |

### Frontend

| Piece     | What it is                                                                |
| --------- | ------------------------------------------------------------------------- |
| Framework | Next.js (React)                                                           |
| Language  | TypeScript                                                                |
| Styling   | Tailwind CSS                                                              |
| Identity  | Name + private phrase, hashed in the browser — nothing sent to any server |
| Hosting   | Vercel                                                                    |

## Where things live

```
ai-agent/        backend: FastAPI server, the AI agent loop, storage, scheduler
task-ai-web/      frontend: the chat website
```

## Deployment

- **Backend** → Render (needs to run continuously in the background, which Vercel's serverless model doesn't support)
- **Frontend** → Vercel

Full step-by-step deployment instructions are in each project's own
README.

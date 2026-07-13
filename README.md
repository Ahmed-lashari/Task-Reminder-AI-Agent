# Task AI Agent

Task AI is an AI powered task and reminder assistant that understands natural language. Describe what you need in plain English and the agent will create, update, organize, and search tasks, schedule reminders, and deliver them directly in the chat when they become due.

## Features

- Create, update, complete, and delete tasks using natural language
- Schedule standalone reminders
- Search and summarize upcoming or completed tasks
- Receive reminders in real time through WebSockets
- Persistent task storage
- Lightweight user isolation without accounts or passwords

## Technology

### Backend

- Python
- FastAPI
- OpenAI compatible language model
- Pydantic
- JSON storage
- WebSocket communication
- Background reminder scheduler

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Project Structure

```text
task1/
├── agent/
├── frontend/
├── venv/
├── dev.sh
└── README.md
```

## Clone the Repository

```bash
cd task-agent
git clone https://github.com/Ahmed-lashari/Task-Reminder-AI-Agent.git
```

## Prerequisites

### macOS

Install Python and Node.js with Homebrew.

```bash
brew install python node
```

### Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip

curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install nodejs
```

## Backend Setup

From the project root:

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r agent/requirements.txt

cp agent/.env.example agent/.env
```

Update `agent/.env` with your API credentials.

## Frontend Setup

```bash
cd frontend

npm install

cp .env.example .env.local
```

Configure the backend URL.

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Return to the project root.

```bash
cd ..
```

## Running the Project

### Recommended

Start both the backend and frontend with a single command.

```bash
./dev.sh
```

### Manual

Backend:

```bash
cd agent

source ../venv/bin/activate

uvicorn main:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend

npm run dev
```

## Local Addresses

Frontend

```
http://localhost:3000
```

Backend

```
http://localhost:8000
```

API Documentation

```
http://localhost:8000/docs
```

## Deployment

Deploy the frontend and backend independently.

Frontend

- Vercel

Backend

- Railway
- Render
- Fly.io

Configure the frontend environment variable to point to the deployed backend.

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
```

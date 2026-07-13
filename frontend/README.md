# Task AI — Web Frontend

A minimal chat client for your existing Python AI backend. Three panes: a
static project description, the chat itself, and a tech-stack manifest.
No accounts, no passwords — a lightweight name + secret-phrase mechanism
keeps each visitor's tasks separate from everyone else's.

## What you need to supply

Only one thing: your backend's URL, in an environment variable.

```bash
cp .env.example .env.local
```
```
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.example.com
```

## Run locally

```bash
npm install
npm run dev
```
Open http://localhost:3000.

## Deploy to Vercel

1. Push this project to a Git repo (GitHub/GitLab/Bitbucket).
2. Import it in Vercel — it's a standard Next.js app, so Vercel's
   zero-config detection handles the build. No `vercel.json` needed.
3. In the Vercel project's Environment Variables settings, add
   `NEXT_PUBLIC_API_BASE_URL` pointing at your deployed backend.
4. Deploy.

That's it — no other setup required.

## How the no-login identity works

On first visit, you're asked for a name and a private phrase (a color,
a hometown, anything memorable). The browser runs both through SHA-256
(`lib/identityHash.ts`, using the Web Crypto API — nothing is sent to any
server for this step) and keeps only the resulting hash in
`localStorage`. The phrase itself is discarded immediately after hashing
and never stored or transmitted.

That hash becomes your `owner_id`. It's sent with every `/chat` request
and as a query parameter on the reminders WebSocket connection. The
**backend** is what actually enforces isolation — see the note below.
The identity prompt only reappears if `localStorage` is cleared, or in a
new browser/incognito session.

There's also a "reset session" link in the left sidebar for testing with
multiple identities without clearing storage manually.

## Backend contract this frontend expects

```
POST /chat
  body: { "message": string, "owner_id": string }
  response: { "reply": string }

WS /ws/reminders?owner_id=<string>
  server -> client messages:
    { "type": "chat_reminder", "message": string }
    { "type": "reminder_due", "task_id": string, "title": string, "trigger_time": string }
```

If your backend's `/chat` endpoint doesn't yet require `owner_id`, or
doesn't filter tasks/reminders by it, **this frontend alone does not
give you multi-user isolation** — the frontend only ever sends the
identifier; the backend has to actually use it to separate one user's
data from another's. If you're using the companion backend patch that
was provided alongside this frontend, that filtering is already in
place at the storage layer.

## Project structure

```
app/            Next.js App Router: layout, global styles, the one page
components/     IdentityGate, ProjectSidebar, TechStackSidebar, ChatPanel, ChatMessageBubble, ChatInput, TypingIndicator
hooks/          useIdentity (session/localStorage), useChat (message state), useReminderSocket (WebSocket)
services/       chatService.ts - the only file that knows the backend's HTTP shape
lib/            types.ts, identityHash.ts
config/         env.ts - the only place environment variables are read
```

## A note on `npm audit`

`npm audit` currently flags the pinned Next.js 14.2.x line for a set of
advisories whose fixes are only published on the Next.js 16 major
version. Most of the flagged vectors (Image Optimizer, Middleware,
i18n rewrites, CSP nonces) aren't exercised by this app — it's a single
client-rendered page with no middleware, no `next/image`, and no
server-side data fetching of user input. Worth re-running
`npm audit` yourself before a real production launch, and considering an
upgrade to Next 15/16 once you've had a chance to test App Router
compatibility on your own schedule — that migration wasn't attempted
here to avoid introducing untested breaking changes.

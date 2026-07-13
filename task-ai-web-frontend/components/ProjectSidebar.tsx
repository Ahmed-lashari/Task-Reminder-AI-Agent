interface ProjectSidebarProps {
  name: string;
  onReset: () => void;
}

export function ProjectSidebar({ name, onReset }: ProjectSidebarProps) {
  return (
    <aside className="flex h-full flex-col justify-between border-border bg-panel p-6 lg:border-r">
      <div>
        <p className="font-mono text-xs uppercase tracking-widest text-accent">task ai</p>
        <h1 className="mt-2 font-display text-xl font-medium text-ink">Task AI</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
  Your personal AI task agent. It interprets requests, decides which tools
  to use, manages tasks and reminders, answers questions about your schedule,
  updates existing plans, and sends real-time reminder notifications—all
  through a conversational interface.
</p>

        <dl className="mt-6 space-y-3 border-t border-border pt-4 font-mono text-xs">
  <div className="flex justify-between">
    <dt className="text-muted">Input</dt>
    <dd className="text-ink">Natural Language</dd>
  </div>

  <div className="flex justify-between">
    <dt className="text-muted">Planning</dt>
    <dd className="text-ink">Agent Tool Calling</dd>
  </div>

  <div className="flex justify-between">
    <dt className="text-muted">Memory</dt>
    <dd className="text-ink">Tasks & Reminders</dd>
  </div>

  <div className="flex justify-between">
    <dt className="text-muted">Notifications</dt>
    <dd className="text-ink">Real-time Events</dd>
  </div>
</dl>
      </div>

      <div className="mt-8 border-t border-border pt-4">
        <p className="font-mono text-xs uppercase tracking-widest text-muted">signed in as</p>
        <p className="mt-1 truncate text-sm text-ink">{name}</p>
        <button
          onClick={onReset}
          className="mt-3 font-mono text-xs text-muted underline decoration-dotted underline-offset-4 transition hover:text-accent"
        >
          not you? reset session
        </button>
      </div>
    </aside>
  );
}

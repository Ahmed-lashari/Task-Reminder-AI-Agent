import type { TechStackSection } from "@/lib/types";
const STACK: TechStackSection[] = [
  {
    label: "reasoning",
    items: [
      "LLM Agent",
      "Prompt Planner",
      "Context Memory",
    ],
  },
  {
    label: "toolchain",
    items: [
      "Function Calling",
      "Task Tools",
      "Reminder Tools",
      "Tool Dispatcher",
    ],
  },
  {
    label: "execution",
    items: [
      "FastAPI",
      "REST API",
      "WebSocket Stream",
      "Background Scheduler",
    ],
  },
  {
    label: "data",
    items: [
      "JSON Store",
      "Abstract Storage Layer",
      "Pydantic Schemas",
    ],
  },
  {
    label: "frontend",
    items: [
      "Next.js",
      "React",
      "TypeScript",
      "Tailwind CSS",
    ],
  },
];

export function TechStackSidebar() {
  return (
    <aside className="h-full border-border bg-panel p-6 lg:border-l">
      <p className="font-mono text-xs uppercase tracking-widest text-accent">manifest</p>
      <h2 className="mt-2 font-display text-lg font-medium text-ink">Stack</h2>

      <div className="mt-5 space-y-5">
        {STACK.map((section) => (
          <div key={section.label}>
            <p className="font-mono text-xs text-muted">[{section.label}]</p>
            <ul className="mt-1 space-y-1">
              {section.items.map((item) => (
                <li key={item} className="font-mono text-sm text-ink">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </aside>
  );
}

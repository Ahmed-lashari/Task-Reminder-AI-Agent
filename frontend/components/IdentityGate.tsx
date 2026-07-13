"use client";

import { useState } from "react";

interface IdentityGateProps {
  onSubmit: (name: string, secret: string) => Promise<void>;
}

export function IdentityGate({ onSubmit }: IdentityGateProps) {
  const [name, setName] = useState("");
  const [secret, setSecret] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canSubmit = name.trim().length > 0 && secret.trim().length > 0 && !isSubmitting;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    setIsSubmitting(true);
    await onSubmit(name, secret);
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-base px-4">
      <div className="w-full max-w-sm animate-fade-up rounded-lg border border-border bg-panel p-8">
        <p className="font-mono text-xs uppercase tracking-widest text-accent">session / new</p>
        <h1 className="mt-2 font-display text-2xl font-medium text-ink">Task AI</h1>
        <p className="mt-2 text-sm leading-relaxed text-muted">
          No accounts here. Give a name and a private phrase only you would know -
          we turn them into a session key that keeps your tasks separate from
          everyone else&apos;s. The phrase itself is never sent or stored.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="name" className="block font-mono text-xs uppercase tracking-wide text-muted">
              Name
            </label>
            <input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Hassam"
              className="mt-1 w-full rounded border border-border bg-base px-3 py-2 text-sm text-ink outline-none focus:border-accent"
              autoFocus
            />
          </div>

          <div>
            <label htmlFor="secret" className="block font-mono text-xs uppercase tracking-wide text-muted">
              Secret phrase
            </label>
            <input
              id="secret"
              type="password"
              value={secret}
              onChange={(e) => setSecret(e.target.value)}
              placeholder="e.g. your childhood street"
              className="mt-1 w-full rounded border border-border bg-base px-3 py-2 text-sm text-ink outline-none focus:border-accent"
            />
            <p className="mt-1 text-xs text-muted">
              Anything memorable: a favourite color, your hometown, a pet&apos;s name.
            </p>
          </div>

          <button
            type="submit"
            disabled={!canSubmit}
            className="w-full rounded bg-accent py-2 text-sm font-medium text-base transition disabled:cursor-not-allowed disabled:opacity-40"
          >
            {isSubmitting ? "Generating session key..." : "Enter"}
          </button>
        </form>
      </div>
    </div>
  );
}

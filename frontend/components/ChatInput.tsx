"use client";

import { useState } from "react";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  function handleSend() {
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex items-end gap-2 border-t border-border bg-panel p-4">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
        placeholder="Tell it what you need done..."
        className="max-h-32 flex-1 resize-none rounded border border-border bg-base px-3 py-2 text-sm text-ink outline-none focus:border-accent"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        className="rounded bg-accent px-4 py-2 text-sm font-medium text-base transition disabled:cursor-not-allowed disabled:opacity-40"
      >
        Send
      </button>
    </div>
  );
}

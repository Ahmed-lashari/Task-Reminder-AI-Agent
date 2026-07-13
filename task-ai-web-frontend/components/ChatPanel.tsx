"use client";

import { useEffect, useRef } from "react";
import { ChatMessageBubble } from "@/components/ChatMessageBubble";
import { ChatInput } from "@/components/ChatInput";
import { TypingIndicator } from "@/components/TypingIndicator";
import type { ChatMessage } from "@/lib/types";

interface ChatPanelProps {
  messages: ChatMessage[];
  isSending: boolean;
  error: string | null;
  onSend: (text: string) => void;
}

export function ChatPanel({ messages, isSending, error, onSend }: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isSending]);

  return (
    <main className="flex h-full flex-col bg-base">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-6">
        {messages.length === 0 && (
          <p className="mt-10 text-center font-mono text-sm text-muted">
            Say what you need done - a task, a reminder, or just a question.
          </p>
        )}
        {messages.map((message) => (
          <ChatMessageBubble key={message.id} message={message} />
        ))}
        {isSending && <TypingIndicator />}
      </div>

      {error && (
        <p className="border-t border-border bg-panel px-4 py-2 text-center text-xs text-accent">{error}</p>
      )}

      <ChatInput onSend={onSend} disabled={isSending} />
    </main>
  );
}

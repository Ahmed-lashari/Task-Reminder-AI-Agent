"use client";

import { useCallback, useState } from "react";
import { sendChatMessage } from "@/services/chatService";
import type { ChatMessage } from "@/lib/types";

function makeId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function useChat(ownerId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isSending) return;

      setError(null);
      setMessages((prev) => [
        ...prev,
        { id: makeId(), role: "user", text: trimmed, timestamp: Date.now() },
      ]);
      setIsSending(true);

      try {
        const reply = await sendChatMessage(ownerId, trimmed);
        setMessages((prev) => [
          ...prev,
          {
            id: makeId(),
            role: "assistant",
            text: reply || "(no response)",
            timestamp: Date.now(),
          },
        ]);
      } catch {
        setError("Couldn't reach the assistant. Check the API endpoint and try again.");
      } finally {
        setIsSending(false);
      }
    },
    [ownerId, isSending]
  );

  const receiveSystemMessage = useCallback((text: string) => {
    setMessages((prev) => [
      ...prev,
      { id: makeId(), role: "assistant", text, timestamp: Date.now() },
    ]);
  }, []);

  return { messages, isSending, error, send, receiveSystemMessage };
}

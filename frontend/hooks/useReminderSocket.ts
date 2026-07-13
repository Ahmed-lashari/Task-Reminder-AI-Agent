"use client";

import { useEffect, useRef } from "react";
import { getWebSocketUrl } from "@/config/env";

export function useReminderSocket(ownerId: string, onReminder: (text: string) => void) {
  const handlerRef = useRef(onReminder);
  handlerRef.current = onReminder;

  useEffect(() => {
    const url = getWebSocketUrl(ownerId);
    if (!url) return;

    let socket: WebSocket;
    try {
      socket = new WebSocket(url);
    } catch {
      return;
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data as string) as { type?: string; message?: string; title?: string };
        if (data.type === "chat_reminder" && data.message) {
          handlerRef.current(data.message);
        } else if (data.type === "reminder_due" && data.title) {
          handlerRef.current(`🔔 Reminder: ${data.title}`);
        }
      } catch {
        // ignore malformed frames
      }
    };

    return () => socket.close();
  }, [ownerId]);
}

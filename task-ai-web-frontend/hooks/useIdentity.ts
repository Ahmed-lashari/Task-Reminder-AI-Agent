"use client";

import { useCallback, useEffect, useState } from "react";
import { deriveOwnerId } from "@/lib/identityHash";
import type { Identity } from "@/lib/types";

const STORAGE_KEY = "task-ai-identity";

export function useIdentity() {
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) setIdentity(JSON.parse(raw) as Identity);
    } catch {
      // corrupted or inaccessible storage - treat as no identity yet
    } finally {
      setIsLoaded(true);
    }
  }, []);

  const establishIdentity = useCallback(async (name: string, secret: string) => {
    const ownerId = await deriveOwnerId(name, secret);
    const next: Identity = { name: name.trim(), ownerId };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    setIdentity(next);
    return next;
  }, []);

  const clearIdentity = useCallback(() => {
    window.localStorage.removeItem(STORAGE_KEY);
    setIdentity(null);
  }, []);

  return { identity, isLoaded, establishIdentity, clearIdentity };
}

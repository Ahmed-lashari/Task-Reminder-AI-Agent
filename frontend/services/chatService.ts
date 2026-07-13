import { config } from "@/config/env";

/**
 * The only place in the app that knows the backend's HTTP contract. If the
 * backend's request/response shape ever changes, this is the one file to
 * touch.
 */
export async function sendChatMessage(ownerId: string, message: string): Promise<string> {
  if (!config.apiBaseUrl) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured.");
  }

  const response = await fetch(`${config.apiBaseUrl}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, owner_id: ownerId }),
  });

  if (!response.ok) {
    throw new Error(`Backend responded with status ${response.status}`);
  }

  const data = (await response.json()) as { reply?: string };
  return data.reply ?? "";
}

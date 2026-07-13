export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "",
};

export function getWebSocketUrl(ownerId: string): string {
  if (!config.apiBaseUrl) return "";
  const wsBase = config.apiBaseUrl.replace(/^http/, "ws");
  return `${wsBase}/ws/reminders?owner_id=${encodeURIComponent(ownerId)}`;
}

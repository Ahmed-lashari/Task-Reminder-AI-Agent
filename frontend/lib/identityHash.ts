/**
 * Derives a deterministic, non-reversible owner_id from a name and a
 * user-chosen secret phrase. The secret itself is never stored anywhere -
 * only this hash leaves the browser. Same name+secret always produces the
 * same id, which is exactly what lets the backend tell "this is still the
 * same person" without any account system.
 */
export async function deriveOwnerId(name: string, secret: string): Promise<string> {
  const normalized = `${name.trim().toLowerCase()}::${secret.trim().toLowerCase()}`;
  const bytes = new TextEncoder().encode(normalized);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  const hex = Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  // Shortened - this is an isolation key, not a cryptographic secret in
  // its own right, so a truncated hex digest is plenty of collision
  // resistance for an MVP's expected user count.
  return hex.slice(0, 24);
}

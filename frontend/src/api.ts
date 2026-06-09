import type { Stats } from "./types";

const BASE = "/api";

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Upload failed");
  return res.json() as Promise<{ session_id: string; filename: string; chunks: number }>;
}

export async function sendChat(sessionId: string | null, query: string) {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, query }),
  });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Chat failed");
  return res.json() as Promise<{ answer: string; used_web: boolean }>;
}

export async function scrapeUrl(url: string) {
  const res = await fetch(`${BASE}/scrape`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Scrape failed");
  return res.json() as Promise<{ session_id: string; name: string; chunks: number }>;
}

export async function activatePublicBot(botType: string) {
  const res = await fetch(`${BASE}/public-bot/${botType}`, { method: "POST" });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Bot activation failed");
  return res.json() as Promise<{ session_id: string; name: string; chunks: number }>;
}

export async function deleteSession(sessionId: string) {
  await fetch(`${BASE}/session/${sessionId}`, { method: "DELETE" });
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${BASE}/stats`);
  return res.json();
}

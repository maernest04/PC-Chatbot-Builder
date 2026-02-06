const API_BASE = import.meta.env.VITE_API_URL || '';

export type Session = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type Message = {
  role: string;
  content: string;
  created_at: string;
};

export type BuildPart = {
  id: string;
  category: string;
  name: string;
  price_usd: number;
  link?: string;
};

export type Build = {
  id: string;
  parts: BuildPart[];
  subtotal: number;
  tax_rate: number;
  total: number;
};

export type SessionDetail = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  build: Build | null;
};

export async function postChat(sessionId: string | null, message: string): Promise<{ session_id: string; reply: string; build: Build | null }> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE}/api/sessions`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionDetail> {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatResponse {
  conversation_id: string;
  user_question: string;
  answer: string | null;
  reasoning: string | null;
  confidence: "high" | "medium" | "low" | null;
  section_referenced: string | null;
  sources: string[];
  status: string;
}

export interface UploadResponse {
  status: string;
  filename: string;
  chunks_ingested: number;
  collection_name: string;
}

export interface HealthResponse {
  status: string;
  collections: number;
}

export interface Collection {
  name: string;
  count: number;
}

export async function sendMessage(
  question: string,
  collection: string = "docubot",
  conversationId: string,
  userId: string
): Promise<ChatResponse> {
  const body = {
    question,
    collection_name: collection,
    conversation_id: conversationId,
    user_id: userId,
  };

  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Chat request failed: ${res.status}`);
  }

  return res.json();
}

export async function uploadPDF(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Upload failed: ${res.status}`);
  }

  return res.json();
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function getCollections(): Promise<Collection[]> {
  const res = await fetch(`${API_BASE}/collections`);
  if (!res.ok) throw new Error(`Collections fetch failed: ${res.status}`);
  const data = await res.json();
  return data.collections || [];
}

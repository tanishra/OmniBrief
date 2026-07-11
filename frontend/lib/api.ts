const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "https://omni-brief.vercel.app";

export async function post(endpoint: string, data: Record<string, unknown>): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(body.detail || `Request failed (${response.status})`);
  }

  return body;
}

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/** Safely extract a human-readable message from a caught value (unknown in catch under strict TS). */
export function errorMessage(value: unknown, fallback = "请求失败"): string {
  if (value instanceof Error) return value.message;
  if (typeof value === "string") return value;
  return fallback;
}

async function readError(response: Response, method: string, path: string) {
  const text = await response.text();
  return new Error(`${method} ${path} failed: ${response.status}${text ? ` ${text}` : ""}`);
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw await readError(response, "GET", path);
  }
  return response.json() as Promise<T>;
}

export async function apiJson<T>(path: string, body: unknown, method = "POST"): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw await readError(response, method, path);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function apiDelete(path: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}${path}`, { method: "DELETE" });
  if (!response.ok) {
    throw await readError(response, "DELETE", path);
  }
}

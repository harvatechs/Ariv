import { env, requireArivApiBaseUrl } from "@/lib/env";

export async function forwardToAriv<T>(path: string, init?: RequestInit): Promise<T> {
  const url = new URL(path, requireArivApiBaseUrl());
import { env } from "@/lib/env";

export async function forwardToAriv<T>(path: string, init?: RequestInit): Promise<T> {
  const url = new URL(path, env.ARIV_API_BASE_URL);

  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(env.ARIV_API_KEY ? { Authorization: `Bearer ${env.ARIV_API_KEY}` } : {}),
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`ARIV backend error (${response.status}): ${body}`);
  }

  return response.json() as Promise<T>;
}

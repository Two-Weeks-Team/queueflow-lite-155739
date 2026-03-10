async function throwApiError(res: Response, fallback: string): Promise<never> {
  const raw = await res.text();
  const parsed = raw ? safeParseJson(raw) : null;
  const message = parsed?.error?.message ?? parsed?.detail ?? parsed?.message ?? raw ?? fallback;
  throw new Error(message || fallback);
}

function safeParseJson(raw: string): any {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export type JoinRequest = {
  name: string;
  party_size: number;
  contact_info: { phone: string };
};

export type JoinResponse = {
  queue_position: number;
  estimated_wait_time: number;
};

export type PositionResponse = {
  current_position: number;
  estimated_wait_time: number;
};

const API_BASE = '/api';

/**
 * Fetch the current queue position (or join the queue if body is supplied).
 * When `body` is provided, a POST /queue/{queue_id}/join is performed.
 * When `body` is omitted, a GET /queue/{queue_id}/position is performed.
 */
export async function fetchQueuePosition(
  queueId: string,
  body?: JoinRequest
): Promise<JoinResponse | PositionResponse> {
  const url = `${API_BASE}/queue/${queueId}/${body ? 'join' : 'position'}`;
  const opts: RequestInit = body
    ? {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }
    : { method: 'GET' };
  const res = await fetch(url, opts);
  if (!res.ok) {
    await throwApiError(res, "API error");
  }
  return (await res.json()) as JoinResponse | PositionResponse;
}

/** Fetch the AI‑predicted wait time (unused in demo but kept for completeness) */
export async function fetchWaitTime(restaurantId: string, partySize: number): Promise<number> {
  const res = await fetch(`${API_BASE}/queue/predict-wait-time`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ restaurant_id: restaurantId, party_size: partySize }),
  });
  if (!res.ok) {
    await throwApiError(res, "AI error");
  }
  const data = await res.json();
  return data.predicted_wait_time;
}

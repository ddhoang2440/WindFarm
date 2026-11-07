import type { ApiConfig, EventInput, EventRecordUI } from "../types/windfarm";
import { cleanBaseUrl, getHeaders } from "./config.service";

export async function fetchEvents(
  config: ApiConfig,
  assetId?: number,
  limit = 200
): Promise<EventRecordUI[]> {
  const query =
    assetId !== undefined
      ? `?asset_id=${assetId}&limit=${limit}`
      : `?limit=${limit}`;
  const res = await fetch(
    `${cleanBaseUrl(config.baseUrl)}/api/v1/events${query}`,
    {
      method: "GET",
      headers: getHeaders(config),
    }
  );
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errText}`);
  }
  return res.json();
}

export async function createEvent(
  config: ApiConfig,
  payload: EventInput
): Promise<{ status: string; event_id: number; id?: string }> {
  const res = await fetch(`${cleanBaseUrl(config.baseUrl)}/api/v1/events`, {
    method: "POST",
    headers: getHeaders(config),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Error logging event (${res.status}): ${errText}`);
  }
  return res.json();
}


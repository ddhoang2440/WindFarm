import type { ApiConfig, TelemetryInput } from "../types/windfarm";
import { cleanBaseUrl, getHeaders } from "./config.service";

export interface PostTelemetryResponse {
  status: string;
  id: string;
  is_anomaly?: boolean;
  anomaly_probability?: number;
}

export async function sendTelemetry(
  config: ApiConfig,
  payload: TelemetryInput
): Promise<PostTelemetryResponse> {
  const res = await fetch(`${cleanBaseUrl(config.baseUrl)}/api/v1/telemetry`, {
    method: "POST",
    headers: getHeaders(config),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errText}`);
  }
  return res.json();
}


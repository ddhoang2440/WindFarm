import type { ApiConfig } from "../types/windfarm";
import { cleanBaseUrl } from "./config.service";

export async function checkBackendHealth(
  config: ApiConfig
): Promise<{ online: boolean; message: string }> {
  try {
    const res = await fetch(`${cleanBaseUrl(config.baseUrl)}/`, {
      headers: { "ngrok-skip-browser-warning": "1" },
    });
    if (!res.ok) {
      return { online: false, message: `HTTP ${res.status}` };
    }
    const data = await res.json();
    return { online: true, message: data.message || "Backend is running" };
  } catch (err) {
    return {
      online: false,
      message: err instanceof Error ? err.message : "Network error",
    };
  }
}


import type { ApiConfig } from "../types/windfarm";

const CONFIG_STORAGE_KEY = "windfarm_api_config_v1";

export const DEFAULT_API_CONFIG: ApiConfig = {
  baseUrl: (import.meta.env.VITE_BACKEND_URL as string) || "http://127.0.0.1:8000",
  apiToken: (import.meta.env.VITE_API_TOKEN as string) || "EnoDncjaHecKAaU_4ev-UA7_oRhMamg9mW1vEDqwfzI",
  autoRefresh: true,
  refreshIntervalSec: 5,
};

export function loadApiConfig(): ApiConfig {
  try {
    const raw = localStorage.getItem(CONFIG_STORAGE_KEY);
    if (!raw) return DEFAULT_API_CONFIG;
    const parsed = JSON.parse(raw);
    return {
      baseUrl: parsed.baseUrl || DEFAULT_API_CONFIG.baseUrl,
      apiToken: parsed.apiToken || DEFAULT_API_CONFIG.apiToken,
      autoRefresh:
        typeof parsed.autoRefresh === "boolean"
          ? parsed.autoRefresh
          : DEFAULT_API_CONFIG.autoRefresh,
      refreshIntervalSec:
        Number(parsed.refreshIntervalSec) || DEFAULT_API_CONFIG.refreshIntervalSec,
    };
  } catch {
    return DEFAULT_API_CONFIG;
  }
}

export function saveApiConfig(config: ApiConfig): void {
  localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(config));
}

export function cleanBaseUrl(url: string): string {
  return url.trim().replace(/\/+$/, "");
}

export function getHeaders(config: ApiConfig): HeadersInit {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${config.apiToken.trim()}`,
    "ngrok-skip-browser-warning": "1",
  };
}


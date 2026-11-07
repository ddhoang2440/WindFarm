// Khớp chính xác với EventInput & EventRecord trong backend/src/models/event.py
export interface EventInput {
  event_id: number;
  asset_id: number;
  event_label: string;
  event_start: string; // ISO 8601 datetime
  event_end: string;   // ISO 8601 datetime
  event_description: string;
}

export interface EventRecordUI extends EventInput {
  id?: string;
  created_at?: string;
}

// Khớp với TelemetryInput trong backend/src/models/telemetry.py
export interface TelemetryInput {
  asset_id: number;
  time_stamp: string; // ISO 8601
  wind_speed: number;
  power_output: number;
  ambient_temp: number;
  status_type_id: number;
}

export interface CsvParsedRow extends TelemetryInput {
  rowNumber: number;
}

export interface ApiConfig {
  baseUrl: string;
  apiToken: string;
  autoRefresh: boolean;
  refreshIntervalSec: number;
}

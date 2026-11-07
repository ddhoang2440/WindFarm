import type { CsvParsedRow } from "../types/windfarm";

/**
 * Parses a CSV string into an array of Telemetry records.
 * Supports case-insensitive header matching and comma / semicolon delimiters.
 */
export function parseTelemetryCsv(csvText: string): {
  rows: CsvParsedRow[];
  errors: string[];
} {
  const lines = csvText.split(/\r?\n/).map((l) => l.trim()).filter((l) => l.length > 0);
  if (lines.length < 2) {
    return { rows: [], errors: ["CSV file is empty (requires at least 1 header line and 1 data row)."] };
  }

  // Detect delimiter (, or ;)
  const firstLine = lines[0];
  const delimiter = firstLine.includes(";") && !firstLine.includes(",") ? ";" : ",";

  const rawHeaders = firstLine.split(delimiter).map((h) => h.trim().replace(/^["']|["']$/g, "").toLowerCase());

  // Find column indexes
  const findCol = (candidates: string[]): number => {
    return rawHeaders.findIndex((h) => candidates.includes(h));
  };

  const assetIdx = findCol(["asset_id", "asset", "turbine_id", "turbine"]);
  const timeIdx = findCol(["time_stamp", "timestamp", "time", "date_time", "datetime"]);
  const windIdx = findCol(["wind_speed", "windspeed", "wind", "speed"]);
  const powerIdx = findCol(["power_output", "power", "poweroutput", "kw"]);
  const tempIdx = findCol(["ambient_temp", "temperature", "temp", "ambient"]);
  const statusIdx = findCol(["status_type_id", "status_id", "status", "status_type"]);

  const errors: string[] = [];
  const rows: CsvParsedRow[] = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (!line) continue;
    const cols = line.split(delimiter).map((c) => c.trim().replace(/^["']|["']$/g, ""));

    // Skip incomplete row
    if (cols.length < 3) continue;

    const rowNum = i;

    // Parse values
    const asset_id = assetIdx >= 0 && cols[assetIdx] !== "" ? parseInt(cols[assetIdx], 10) : 0;
    
    let rawTime = timeIdx >= 0 ? cols[timeIdx] : "";
    let time_stamp = new Date().toISOString();
    if (rawTime) {
      if (rawTime.includes(" ")) {
        time_stamp = rawTime.replace(" ", "T") + (rawTime.endsWith("Z") ? "" : "Z");
      } else if (rawTime.includes("T")) {
        time_stamp = rawTime.endsWith("Z") ? rawTime : rawTime + "Z";
      } else {
        time_stamp = rawTime;
      }
    }

    const wind_speed = windIdx >= 0 ? parseFloat(cols[windIdx]) : NaN;
    const power_output = powerIdx >= 0 ? parseFloat(cols[powerIdx]) : NaN;
    const ambient_temp = tempIdx >= 0 && cols[tempIdx] !== "" ? parseFloat(cols[tempIdx]) : 22.0;
    const status_type_id = statusIdx >= 0 && cols[statusIdx] !== "" ? parseInt(cols[statusIdx], 10) : 1;

    if (Number.isNaN(wind_speed) || Number.isNaN(power_output)) {
      errors.push(`Row ${rowNum}: Skipped due to invalid wind_speed or power_output value.`);
      continue;
    }

    rows.push({
      rowNumber: rowNum,
      asset_id: Number.isNaN(asset_id) ? 0 : asset_id,
      time_stamp,
      wind_speed,
      power_output,
      ambient_temp: Number.isNaN(ambient_temp) ? 22.0 : ambient_temp,
      status_type_id: Number.isNaN(status_type_id) ? 1 : status_type_id,
    });
  }

  return { rows, errors };
}


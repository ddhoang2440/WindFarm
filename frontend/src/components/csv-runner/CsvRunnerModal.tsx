import React, { useEffect, useRef, useState } from "react";
import { toast } from "react-toastify";
import {
  UploadCloud,
  X,
  FolderOpen,
  AlertTriangle,
  Play,
  Pause,
  RotateCcw,
  Activity,
  CheckCircle,
  AlertCircle,
  Radio,
  CheckCircle2,
  FileText,
  Trash2,
} from "lucide-react";
import { sendTelemetry } from "../../services";
import type { ApiConfig, CsvParsedRow } from "../../types/windfarm";
import { parseTelemetryCsv } from "../../utils/csvParser";
import type { CsvFileInfo } from "./CsvStreamerBanner";

interface CsvRunnerModalProps {
  apiConfig: ApiConfig;
  isOpen: boolean;
  onClose: () => void;
  onEventLogged: () => void;
  onStatusChange?: (status: CsvFileInfo | null) => void;
}

interface LogEntry {
  id: number;
  time: string;
  type: "info" | "success" | "warning" | "error";
  text: string;
}

export function CsvRunnerModal({
  apiConfig,
  isOpen,
  onClose,
  onEventLogged,
  onStatusChange,
}: CsvRunnerModalProps) {
  const [fileName, setFileName] = useState<string>("");
  const [csvRows, setCsvRows] = useState<CsvParsedRow[]>([]);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  // Execution state
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [delayMs, setDelayMs] = useState<number>(3000); // Default 3s

  // Counters
  const [successCount, setSuccessCount] = useState<number>(0);
  const [errorCount, setErrorCount] = useState<number>(0);

  // Terminal log
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const terminalBodyRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const timerRef = useRef<number | null>(null);

  // Auto scroll terminal safely without jittering parent modal/window
  useEffect(() => {
    if (terminalBodyRef.current) {
      terminalBodyRef.current.scrollTop = terminalBodyRef.current.scrollHeight;
    }
  }, [logs]);

  // Sync loaded file status to banner
  useEffect(() => {
    if (!fileName || csvRows.length === 0) {
      onStatusChange?.(null);
    } else {
      onStatusChange?.({
        fileName,
        rowCount: csvRows.length,
        isRunning,
        currentIndex,
      });
    }
  }, [fileName, csvRows.length, isRunning, currentIndex, onStatusChange]);

  const addLog = (type: LogEntry["type"], text: string) => {
    const time = new Date().toLocaleTimeString("en-US", { hour12: false });
    setLogs((prev) => [
      ...prev.slice(-200),
      { id: Date.now() + Math.random(), time, type, text },
    ]);
  };

  const handleClearLogs = () => {
    setLogs([]);
  };

  // Process CSV file
  const processCsvFile = (file: File) => {
    if (!file.name.toLowerCase().endsWith(".csv")) {
      toast.error("Please select a file with .csv format!");
      return;
    }

    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target?.result as string;
      if (!text) {
        toast.warning("Selected CSV file is empty!");
        return;
      }

      const { rows, errors } = parseTelemetryCsv(text);
      if (rows.length === 0) {
        toast.error("Could not parse any valid telemetry rows from the CSV file.");
        setParseErrors(errors);
        return;
      }

      setFileName(file.name);
      setCsvRows(rows);
      setParseErrors(errors);
      setCurrentIndex(0);
      setSuccessCount(0);
      setErrorCount(0);
      setIsRunning(false);

      addLog(
        "info",
        `[INFO] Loaded "${file.name}" with ${rows.length} valid telemetry rows.`
      );
      toast.success(`Loaded ${rows.length} rows from ${file.name}!`);
    };

    reader.readAsText(file, "UTF-8");
  };

  // Handle file select
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processCsvFile(file);
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) processCsvFile(file);
  };

  // Send single row to backend
  const sendRow = async (idx: number) => {
    if (idx >= csvRows.length) {
      setIsRunning(false);
      addLog("success", `[COMPLETE] Finished streaming all ${csvRows.length} rows!`);
      toast.success("Finished streaming CSV file!");
      onEventLogged();
      return;
    }

    const row = csvRows[idx];
    const payload = {
      asset_id: row.asset_id,
      time_stamp: row.time_stamp,
      wind_speed: row.wind_speed,
      power_output: row.power_output,
      ambient_temp: row.ambient_temp,
      status_type_id: row.status_type_id,
    };

    try {
      const res = await sendTelemetry(apiConfig, payload);
      setSuccessCount((prev) => prev + 1);

      const isAnomaly = res.is_anomaly === true;
      const probText =
        typeof res.anomaly_probability === "number"
          ? ` (prob: ${(res.anomaly_probability * 100).toFixed(2)}%)`
          : "";

      if (isAnomaly) {
        addLog(
          "warning",
          `[ANOMALY DETECTED] Row #${row.rowNumber} (Asset ${row.asset_id}): Wind ${row.wind_speed} m/s, Power ${row.power_output} kW -> Status 200 [ML ANOMALY${probText}]`
        );
        onEventLogged();
      } else {
        addLog(
          "success",
          `[OK] Row #${row.rowNumber} (Asset ${row.asset_id}): Wind ${row.wind_speed} m/s, Power ${row.power_output} kW -> Status 200 OK [Normal${probText}]`
        );
        onEventLogged();
      }
    } catch (err) {
      setErrorCount((prev) => prev + 1);
      const msg = err instanceof Error ? err.message : "Network error";
      addLog("error", `[ERROR] Row #${row.rowNumber}: Failed to send telemetry -> ${msg}`);
    }
  };

  // Runner loop
  useEffect(() => {
    if (!isRunning) {
      if (timerRef.current) window.clearTimeout(timerRef.current);
      return;
    }

    if (currentIndex >= csvRows.length) {
      setIsRunning(false);
      return;
    }

    timerRef.current = window.setTimeout(async () => {
      await sendRow(currentIndex);
      setCurrentIndex((prev) => prev + 1);
    }, delayMs);

    return () => {
      if (timerRef.current) window.clearTimeout(timerRef.current);
    };
  }, [isRunning, currentIndex, csvRows, delayMs]);

  // Actions
  const handleStart = () => {
    if (csvRows.length === 0) {
      toast.warning("Please select a CSV file first!");
      return;
    }
    if (currentIndex >= csvRows.length) {
      setCurrentIndex(0);
      setSuccessCount(0);
      setErrorCount(0);
    }
    setIsRunning(true);
    addLog(
      "info",
      `[START] Streaming started at speed ${delayMs / 1000}s per row...`
    );
  };

  const handlePause = () => {
    setIsRunning(false);
    addLog("warning", `[PAUSED] Streaming paused at row ${currentIndex}.`);
  };

  const handleReset = () => {
    setIsRunning(false);
    setCurrentIndex(0);
    setSuccessCount(0);
    setErrorCount(0);
    addLog("info", `[RESET] Progress reset to row 0.`);
  };

  const progressPct =
    csvRows.length > 0 ? Math.round((currentIndex / csvRows.length) * 100) : 0;

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="glass-card modal-card csv-runner-modal mockup-style-modal"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="card-header runner-modal-header">
          <div className="runner-header-brand">
            <div className="runner-cloud-icon-badge">
              <UploadCloud size={20} />
            </div>
            <div>
              <h3 className="card-title">
                Upload & Stream Telemetry CSV (CSV Runner)
              </h3>
              <p className="card-subtitle">
                Upload a CSV file and automatically stream rows sequentially to trigger real-time AI anomaly detection.
              </p>
            </div>
          </div>
          <button
            type="button"
            className="runner-close-circle"
            onClick={onClose}
            title="Close console"
          >
            <X size={16} />
          </button>
        </div>

        {/* 2-Column Responsive Body */}
        <div className="csv-runner-grid">
          {/* ================= LEFT COLUMN: CSV INPUT & CONTROLS ================= */}
          <div className="csv-runner-col csv-runner-left">
            {/* Drag & Drop Upload Zone */}
            <div
              className={`mockup-dropzone ${isDragging ? "dragging" : ""}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                style={{ display: "none" }}
                onChange={handleFileChange}
              />

              <div className="dropzone-cloud-icon">
                <UploadCloud size={36} strokeWidth={1.8} />
              </div>
              <div className="dropzone-primary-text">
                Drag & drop your CSV file here
              </div>
              <div className="dropzone-divider">or</div>

              <button
                type="button"
                className="btn-ruby-pill"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
              >
                <FolderOpen size={15} />
                <span>Select CSV File from Computer...</span>
              </button>

              {fileName && (
                <div
                  className="file-info-badge mockup-file-badge"
                  onClick={(e) => e.stopPropagation()}
                >
                  <FolderOpen size={13} />
                  <span>
                    Selected: <strong>{fileName}</strong>
                  </span>
                  <span className="mono-num">({csvRows.length} valid rows)</span>
                </div>
              )}
            </div>

            {parseErrors.length > 0 && (
              <div className="csv-parse-warning">
                <AlertTriangle size={14} />
                <span>
                  Detected {parseErrors.length} malformed lines in CSV file:{" "}
                  <small>{parseErrors.slice(0, 2).join(" • ")}</small>
                </span>
              </div>
            )}

            {/* Execution Toolbar: Start / Reset / Speed Selector */}
            <div className="mockup-action-row">
              <div className="mockup-action-buttons">
                {!isRunning ? (
                  <button
                    type="button"
                    className="btn-glow-crimson"
                    onClick={handleStart}
                    disabled={csvRows.length === 0}
                  >
                    <Play size={13} fill="currentColor" />
                    <span>Start CSV Stream</span>
                  </button>
                ) : (
                  <button
                    type="button"
                    className="btn-glow-crimson"
                    onClick={handlePause}
                  >
                    <Pause size={13} />
                    <span>Pause Stream</span>
                  </button>
                )}

                <button
                  type="button"
                  className="btn-dark-capsule"
                  onClick={handleReset}
                  disabled={csvRows.length === 0}
                >
                  <RotateCcw size={13} />
                  <span>Reset Stream</span>
                </button>
              </div>

              {/* Stream Interval Speed Selector Capsule */}
              <div className="mockup-interval-capsule">
                <span className="interval-label">Stream Interval:</span>
                <div className="interval-chips-group">
                  {[
                    { label: "3s/row", val: 3000 },
                    { label: "1s/row", val: 1000 },
                    { label: "0.5s/row", val: 500 },
                  ].map((s) => (
                    <button
                      key={s.val}
                      type="button"
                      className={`interval-chip ${
                        delayMs === s.val ? "active" : ""
                      }`}
                      onClick={() => setDelayMs(s.val)}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Progress Bar & Badges Card */}
            <div className="mockup-progress-card">
              <div className="mockup-progress-header">
                <div className="mockup-progress-info">
                  <span className="mockup-equalizer-icon">
                    <Activity size={15} />
                  </span>
                  <span>
                    Progress: <strong>{currentIndex}</strong> /{" "}
                    <strong>{csvRows.length}</strong> rows ({progressPct}%)
                  </span>
                </div>
                <div className="mockup-badges-wrap">
                  <span className="pill-badge-success">
                    <CheckCircle size={12} />
                    <span>Success: {successCount}</span>
                  </span>
                  {errorCount > 0 && (
                    <span className="pill-badge-danger">
                      <AlertCircle size={12} />
                      <span>Errors: {errorCount}</span>
                    </span>
                  )}
                  <span className="pill-badge-ready">
                    {isRunning ? (
                      <>
                        <Radio size={12} className="spin-slow" />
                        <span>Streaming...</span>
                      </>
                    ) : currentIndex >= csvRows.length && csvRows.length > 0 ? (
                      <>
                        <CheckCircle2 size={12} />
                        <span>Finished</span>
                      </>
                    ) : (
                      <>
                        <Pause size={12} />
                        <span>Ready</span>
                      </>
                    )}
                  </span>
                </div>
              </div>
              <div className="progress-track mockup-progress-track">
                <div
                  className="progress-fill mockup-progress-fill"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
            </div>
          </div>

          {/* ================= RIGHT COLUMN: LIVE TERMINAL LOG ================= */}
          <div className="csv-runner-col csv-runner-right">
            <div className="runner-terminal mockup-terminal">
              <div className="terminal-header mockup-terminal-header">
                <div className="terminal-header-title">
                  <span className="mockup-pulse-red" />
                  <span>
                    LIVE TERMINAL LOG{" "}
                    <span className="text-crimson-endpoint">
                      (POST /api/v1/telemetry)
                    </span>
                  </span>
                </div>
                <div className="terminal-header-actions">
                  <span className="terminal-count-badge mockup-logs-badge">
                    <FileText size={12} />
                    <span>{logs.length} logs</span>
                  </span>
                  {logs.length > 0 && (
                    <button
                      type="button"
                      className="btn-glass btn-xs"
                      onClick={handleClearLogs}
                      title="Clear terminal log window"
                    >
                      <Trash2 size={12} />
                      <span>Clear</span>
                    </button>
                  )}
                </div>
              </div>
              <div className="terminal-body mockup-terminal-body" ref={terminalBodyRef}>
                {logs.length === 0 ? (
                  <div className="mockup-terminal-initial">
                    <p className="terminal-info-line">
                      <span className="log-tag-info">[INFO]</span> Waiting for events...
                    </p>
                    <p className="terminal-info-line">
                      <span className="log-tag-info">[INFO]</span> Select a CSV file and click "Start CSV Stream"
                    </p>
                    <p className="terminal-info-line">
                      <span className="log-tag-info">[INFO]</span> to watch real-time AI anomaly detection
                    </p>
                    <p className="terminal-info-line">
                      <span className="log-tag-info">[INFO]</span> and ML predictions.
                    </p>
                    <span className="mockup-blinking-cursor">|</span>
                  </div>
                ) : (
                  logs.map((lg) => (
                    <div
                      key={lg.id}
                      className={`terminal-line terminal-${lg.type}`}
                    >
                      <span className="terminal-time">[{lg.time}]</span>{" "}
                      {lg.text}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Bottom Close Console Button */}
            <div className="mockup-terminal-bottom-actions">
              <button
                type="button"
                className="btn-close-console"
                onClick={onClose}
              >
                <X size={14} />
                <span>Close Console</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

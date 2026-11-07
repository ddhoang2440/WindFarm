import React, { useState } from "react";
import {
  BarChart3,
  Target,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import type { EventRecordUI } from "../../types/windfarm";
import { formatDateTime } from "../../utils/formatters";

interface KpiSummaryProps {
  events: EventRecordUI[];
  anomalyCount: number;
  lastFetchedAt: string;
}

export const KpiSummary: React.FC<KpiSummaryProps> = ({
  events,
  anomalyCount,
  lastFetchedAt,
}) => {
  const [isDescExpanded, setIsDescExpanded] = useState<boolean>(false);
  const latestEvent = events[0];

  return (
    <section className="kpi-grid-3">
      {/* CARD 1: TOTAL LOGGED EVENTS */}
      <div className="glass-card kpi-card">
        <div className="kpi-top">
          <span className="kpi-label">TOTAL LOGGED EVENTS (MONGODB)</span>
          <span className="kpi-icon">
            <BarChart3 size={16} />
          </span>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value mono-num">{events.length}</span>
          <span className="kpi-unit">events</span>
        </div>
        <div className="kpi-meta-row">
          <span className="mono-num">Updated: {lastFetchedAt}</span>
        </div>
      </div>

      {/* CARD 2: EVENT CLASSIFICATION (Only show red border if anomaly > 0) */}
      <div
        className={`glass-card kpi-card ${
          anomalyCount > 0 ? "card-anomaly-border" : ""
        }`}
      >
        <div className="kpi-top">
          <span className="kpi-label">EVENT CLASSIFICATION (ANOMALY / NORMAL)</span>
          <span className="kpi-icon">
            <Target size={16} />
          </span>
        </div>
        <div className="kpi-value-row">
          <span
            className={`kpi-value mono-num ${
              anomalyCount > 0 ? "text-danger" : "text-cyan"
            }`}
          >
            {anomalyCount}
          </span>
          <span className="kpi-unit">
            anomalies / {Math.max(0, events.length - anomalyCount)} normal
          </span>
        </div>
        <div className="kpi-meta-row">
          <span>RandomForest ML Model</span>
          <span
            className={`status-pill ${
              anomalyCount > 0 ? "badge-danger" : "badge-normal"
            }`}
          >
            {anomalyCount > 0 ? (
              <>
                <AlertTriangle size={13} />
                <span>{anomalyCount} Anomalies</span>
              </>
            ) : (
              <>
                <CheckCircle2 size={13} />
                <span>100% Normal</span>
              </>
            )}
          </span>
        </div>
      </div>

      {/* CARD 3: LATEST EVENT (Full description with instant tooltip & expand toggle) */}
      <div className="glass-card kpi-card">
        <div className="kpi-top">
          <span className="kpi-label">LATEST EVENT</span>
          <span className="kpi-icon">
            <Clock size={16} />
          </span>
        </div>
        {latestEvent ? (
          <>
            <div className="kpi-value-row">
              <span
                className={`status-pill ${
                  (latestEvent.event_label || "").toLowerCase() === "anomaly"
                    ? "badge-danger"
                    : "badge-normal"
                }`}
              >
                {(latestEvent.event_label || "").toLowerCase() === "anomaly" ? (
                  <>
                    <AlertTriangle size={13} />
                    <span>ANOMALY</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={13} />
                    <span>NORMAL</span>
                  </>
                )}
              </span>
              <span className="mono-num text-cyan">
                Turbine #{latestEvent.asset_id} • #{latestEvent.event_id}
              </span>
            </div>
            <div className="kpi-meta-row mono-num kpi-latest-meta">
              <span>{formatDateTime(latestEvent.event_end)}</span>
              <div className="event-desc-wrapper">
                <span
                  className={`truncate-text ${
                    isDescExpanded ? "expanded" : ""
                  }`}
                  onClick={() => setIsDescExpanded((prev) => !prev)}
                  title="Click to view full description / collapse"
                >
                  {latestEvent.event_description || "No description"}
                </span>
                {latestEvent.event_description &&
                  latestEvent.event_description.length > 20 && (
                    <button
                      type="button"
                      className="btn-desc-toggle"
                      onClick={() => setIsDescExpanded((prev) => !prev)}
                      title={isDescExpanded ? "Collapse description" : "View full details"}
                    >
                      {isDescExpanded ? (
                        <>
                          <ChevronUp size={11} />
                          <span>Collapse</span>
                        </>
                      ) : (
                        <>
                          <ChevronDown size={11} />
                          <span>Details</span>
                        </>
                      )}
                    </button>
                  )}
                {/* Instant SCADA Tooltip */}
                <div className="scada-desc-tooltip">
                  <div className="tooltip-header">
                    Turbine #{latestEvent.asset_id} — Event #{latestEvent.event_id}
                  </div>
                  <div className="tooltip-body">
                    {latestEvent.event_description}
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="kpi-meta-row">
            <span className="text-muted">No events recorded in database yet</span>
          </div>
        )}
      </div>
    </section>
  );
};


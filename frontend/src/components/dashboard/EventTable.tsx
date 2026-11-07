import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  RefreshCw,
  CheckCircle2,
  Plus,
  ChevronsLeft,
  ChevronLeft,
  ChevronRight,
  ChevronsRight,
} from "lucide-react";
import type { ApiConfig, EventRecordUI } from "../../types/windfarm";
import { formatDateTime } from "../../utils/formatters";
import { EventFilters } from "./EventFilters";

interface EventTableProps {
  events: EventRecordUI[];
  filteredEvents: EventRecordUI[];
  loading: boolean;
  apiConfig: ApiConfig;
  searchQuery: string;
  onSearchChange: (val: string) => void;
  assetFilter: string;
  onAssetChange: (val: string) => void;
  labelFilter: string;
  onLabelChange: (val: string) => void;
  uniqueAssets: number[];
  uniqueLabels: string[];
  onClearFilters: () => void;
  onRefresh: () => void;
  onOpenLogModal: () => void;
}

export const EventTable: React.FC<EventTableProps> = ({
  events,
  filteredEvents,
  loading,
  apiConfig,
  searchQuery,
  onSearchChange,
  assetFilter,
  onAssetChange,
  labelFilter,
  onLabelChange,
  uniqueAssets,
  uniqueLabels,
  onClearFilters,
  onRefresh,
  onOpenLogModal,
}) => {
  // Pagination State
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  // Reset to page 1 whenever filters or search query changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, assetFilter, labelFilter, pageSize]);

  // Pagination calculation
  const totalEvents = filteredEvents.length;
  const totalPages = Math.max(1, Math.ceil(totalEvents / pageSize));
  const validPage = Math.min(currentPage, totalPages);
  const startIndex = (validPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalEvents);
  const currentEvents = filteredEvents.slice(startIndex, endIndex);

  return (
    <section className="glass-card events-section-card">
      <div className="card-header">
        <div>
          <h3 className="card-title">
            <AlertTriangle size={18} className="text-danger" />
            <span>Turbine Event & Incident Log</span>
          </h3>
        </div>

        <button
          type="button"
          className="btn-gradient"
          onClick={onRefresh}
          disabled={loading}
        >
          <RefreshCw size={14} className={loading ? "spin-icon" : ""} />
          <span>{loading ? "Loading..." : "Refresh Data"}</span>
        </button>
      </div>

      {/* Filter toolbar */}
      <EventFilters
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        assetFilter={assetFilter}
        onAssetChange={onAssetChange}
        labelFilter={labelFilter}
        onLabelChange={onLabelChange}
        uniqueAssets={uniqueAssets}
        uniqueLabels={uniqueLabels}
        onClearFilters={onClearFilters}
      />

      {/* Event Table (Clean sharp borders, unboxed IDs) */}
      <div className="table-responsive">
        <table className="scada-table">
          <thead>
            <tr>
              <th>EVENT ID (event_id)</th>
              <th>TURBINE (asset_id)</th>
              <th>LABEL (event_label)</th>
              <th>START TIME (event_start)</th>
              <th>DETECTED / END (event_end)</th>
              <th>DESCRIPTION (event_description)</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="empty-table-cell">
                  <div className="empty-state-content">
                    <div className="pulse-dot" />
                    <p>Loading event records from Backend API...</p>
                  </div>
                </td>
              </tr>
            ) : currentEvents.length > 0 ? (
              currentEvents.map((ev, idx) => {
                const isAnomaly =
                  (ev.event_label || "").toLowerCase() === "anomaly";
                return (
                  <tr
                    key={ev.id || `${ev.event_id}-${idx}`}
                    className={isAnomaly ? "table-row-anomaly" : ""}
                  >
                    <td className="mono-num font-bold">#{ev.event_id}</td>
                    <td className="mono-num turbine-id-cell">
                      Turbine #{ev.asset_id}
                    </td>
                    <td>
                      <span
                        className={`status-pill ${
                          isAnomaly
                            ? "badge-danger"
                            : (ev.event_label || "").toLowerCase() === "normal"
                            ? "badge-normal"
                            : "badge-warning"
                        }`}
                      >
                        {isAnomaly ? (
                          <>
                            <AlertTriangle size={12} />
                            <span>ANOMALY</span>
                          </>
                        ) : (
                          <>
                            <CheckCircle2 size={12} />
                            <span>{(ev.event_label || "NORMAL").toUpperCase()}</span>
                          </>
                        )}
                      </span>
                    </td>
                    <td className="mono-num">
                      {formatDateTime(ev.event_start)}
                    </td>
                    <td className="mono-num">
                      {formatDateTime(ev.event_end)}
                    </td>
                    <td className="desc-cell" title={ev.event_description}>
                      {ev.event_description || "—"}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={6} className="empty-table-cell">
                  <div className="empty-state-content">
                    <p>
                      {events.length === 0
                        ? "No event records found in MongoDB. Events will automatically appear when Backend / ML Service detects an anomaly, or when you click '+ Log Anomaly Event'."
                        : "No events match the current filter criteria."}
                    </p>
                    <button
                      type="button"
                      className="btn-glass"
                      onClick={onOpenLogModal}
                    >
                      <Plus size={14} />
                      <span>Log New Event</span>
                    </button>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="table-pagination-bar">
        <div className="pagination-left">
          <label className="pagination-page-size">
            <span>Rows per page:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </label>
          <span className="pagination-range-text">
            Showing <strong>{totalEvents > 0 ? startIndex + 1 : 0}</strong>–
            <strong>{endIndex}</strong> of <strong>{totalEvents}</strong> events
          </span>
        </div>

        <div className="pagination-controls">
          <button
            type="button"
            className="btn-glass btn-sm"
            onClick={() => setCurrentPage(1)}
            disabled={validPage <= 1}
            title="First Page"
          >
            <ChevronsLeft size={13} />
            <span className="pagination-btn-text">First</span>
          </button>
          <button
            type="button"
            className="btn-glass btn-sm"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={validPage <= 1}
            title="Previous Page"
          >
            <ChevronLeft size={13} />
            <span className="pagination-btn-text">Prev</span>
          </button>

          <span className="pagination-current-page">
            Page <strong>{validPage}</strong> / <strong>{totalPages}</strong>
          </span>

          <button
            type="button"
            className="btn-glass btn-sm"
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={validPage >= totalPages}
            title="Next Page"
          >
            <span className="pagination-btn-text">Next</span>
            <ChevronRight size={13} />
          </button>
          <button
            type="button"
            className="btn-glass btn-sm"
            onClick={() => setCurrentPage(totalPages)}
            disabled={validPage >= totalPages}
            title="Last Page"
          >
            <span className="pagination-btn-text">Last</span>
            <ChevronsRight size={13} />
          </button>
        </div>
      </div>

      <div className="table-footer-meta">
        <span>
          Total Loaded from Backend: <strong>{events.length}</strong> events
        </span>
        <span className="mono-num">
          Endpoint: <span className="endpoint-tag">GET {apiConfig.baseUrl}/api/v1/events</span>
        </span>
      </div>
    </section>
  );
};

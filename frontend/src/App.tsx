import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./components/layout/layout.css";
import "./App.css";

// Components
import { Header, Footer } from "./components/layout";
import { KpiSummary, EventTable } from "./components/dashboard";
import {
  CsvStreamerBanner,
  CsvRunnerModal,
  type CsvFileInfo,
} from "./components/csv-runner";
import { SettingsModal, LogEventModal } from "./components/modals";

// Services & Types
import {
  createEvent,
  fetchEvents,
  loadApiConfig,
  saveApiConfig,
} from "./services";
import type { ApiConfig, EventInput, EventRecordUI } from "./types/windfarm";

function App() {
  const [apiConfig, setApiConfig] = useState<ApiConfig>(() => loadApiConfig());

  // Real events fetched from Backend
  const [events, setEvents] = useState<EventRecordUI[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [lastFetchedAt, setLastFetchedAt] = useState<string>("—");

  // Filter & Search state
  const [searchQuery, setSearchQuery] = useState<string>("all");
  const [assetFilter, setAssetFilter] = useState<string>("all");
  const [labelFilter, setLabelFilter] = useState<string>("all");

  // Modals state
  const [showLogModal, setShowLogModal] = useState<boolean>(false);
  const [showSettingsModal, setShowSettingsModal] = useState<boolean>(false);
  const [showCsvRunnerModal, setShowCsvRunnerModal] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  // CSV Runner File Status (Item 4)
  const [selectedCsvStatus, setSelectedCsvStatus] = useState<CsvFileInfo | null>(null);

  // Search query initialize as empty
  useEffect(() => {
    setSearchQuery("");
  }, []);

  // Fetch real data from Backend API
  const handleFetchEvents = useCallback(
    async (silent = false) => {
      if (!silent) setLoading(true);

      try {
        const data = await fetchEvents(apiConfig, undefined, 200);
        setEvents(data);
        setFetchError(null);
        setLastFetchedAt(
          new Date().toLocaleTimeString("en-US", { hour12: false })
        );
        if (!silent) {
          toast.success(`Loaded ${data.length} event records from Backend!`, {
            autoClose: 1500,
          });
        }
      } catch (err) {
        const errMsg =
          err instanceof Error ? err.message : "Connection error to Backend";
        setFetchError(errMsg);
        if (!silent) {
          toast.error(`Failed to fetch GET /api/v1/events: ${errMsg}`);
        }
      } finally {
        setLoading(false);
      }
    },
    [apiConfig]
  );

  // Initial fetch on mount
  useEffect(() => {
    handleFetchEvents(false);
  }, [handleFetchEvents]);

  // Periodic polling if autoRefresh is enabled
  useEffect(() => {
    if (!apiConfig.autoRefresh) return;
    const interval = Math.max(2, apiConfig.refreshIntervalSec) * 1000;
    const timer = window.setInterval(() => {
      handleFetchEvents(true);
    }, interval);
    return () => window.clearInterval(timer);
  }, [apiConfig.autoRefresh, apiConfig.refreshIntervalSec, handleFetchEvents]);

  // Unique asset IDs purely from real fetched events
  const uniqueAssets = useMemo(() => {
    const set = new Set<number>();
    events.forEach((e) => {
      if (typeof e.asset_id === "number") set.add(e.asset_id);
    });
    return Array.from(set).sort((a, b) => a - b);
  }, [events]);

  // Unique labels purely from real fetched events
  const uniqueLabels = useMemo(() => {
    const set = new Set<string>();
    events.forEach((e) => {
      if (e.event_label) set.add(e.event_label.trim());
    });
    return Array.from(set).sort();
  }, [events]);

  // Filtered event list
  const filteredEvents = useMemo(() => {
    return events.filter((ev) => {
      if (assetFilter !== "all" && ev.asset_id !== Number(assetFilter)) {
        return false;
      }
      if (
        labelFilter !== "all" &&
        ev.event_label?.toLowerCase() !== labelFilter.toLowerCase()
      ) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchId = String(ev.event_id).includes(q);
        const matchDesc = (ev.event_description || "").toLowerCase().includes(q);
        const matchAsset = String(ev.asset_id).includes(q);
        const matchLabel = (ev.event_label || "").toLowerCase().includes(q);
        return matchId || matchDesc || matchAsset || matchLabel;
      }
      return true;
    });
  }, [events, assetFilter, labelFilter, searchQuery]);

  // Anomaly count
  const anomalyCount = useMemo(
    () =>
      events.filter((e) => (e.event_label || "").toLowerCase() === "anomaly")
        .length,
    [events]
  );

  // Auto-refresh toggle
  const handleToggleAutoRefresh = () => {
    const updated = {
      ...apiConfig,
      autoRefresh: !apiConfig.autoRefresh,
    };
    setApiConfig(updated);
    saveApiConfig(updated);
  };

  // Save settings
  const handleSaveSettings = (newConfig: ApiConfig) => {
    setApiConfig(newConfig);
    saveApiConfig(newConfig);
    setShowSettingsModal(false);
    toast.success("Saved API & Bearer Token settings!");
    handleFetchEvents(false);
  };

  // Submit manual event
  const handleCreateEvent = async (eventForm: EventInput) => {
    if (!eventForm.event_description.trim()) {
      toast.warning("Please enter an event description!");
      return;
    }
    setSubmitting(true);
    try {
      await createEvent(apiConfig, eventForm);
      toast.success(
        `Saved Event #${eventForm.event_id} for Turbine #${eventForm.asset_id} into MongoDB!`
      );
      setShowLogModal(false);
      await handleFetchEvents(true);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Error submitting POST /api/v1/events"
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="windfarm-app">
      {/* 1. TOP HEADER / NAVBAR */}
      <Header
        apiConfig={apiConfig}
        isBackendOffline={Boolean(fetchError)}
        onToggleAutoRefresh={handleToggleAutoRefresh}
        onOpenSettings={() => setShowSettingsModal(true)}
      />

      {/* 2. MAIN SCADA CONSOLE */}
      <main className="scada-main">
        {/* 3 KPI SUMMARY CARDS */}
        <KpiSummary
          events={events}
          anomalyCount={anomalyCount}
          lastFetchedAt={lastFetchedAt}
        />

        {/* CSV TELEMETRY RUNNER BANNER */}
        <CsvStreamerBanner
          selectedCsvStatus={selectedCsvStatus}
          onOpenRunner={() => setShowCsvRunnerModal(true)}
        />

        {/* EVENT LOG & FILTER SECTION */}
        <EventTable
          events={events}
          filteredEvents={filteredEvents}
          loading={loading}
          apiConfig={apiConfig}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          assetFilter={assetFilter}
          onAssetChange={setAssetFilter}
          labelFilter={labelFilter}
          onLabelChange={setLabelFilter}
          uniqueAssets={uniqueAssets}
          uniqueLabels={uniqueLabels}
          onClearFilters={() => {
            setAssetFilter("all");
            setLabelFilter("all");
            setSearchQuery("");
          }}
          onRefresh={() => handleFetchEvents(false)}
          onOpenLogModal={() => setShowLogModal(true)}
        />
      </main>

      {/* 3. SITE FOOTER */}
      <Footer />

      {/* 4. MODALS */}
      <SettingsModal
        isOpen={showSettingsModal}
        apiConfig={apiConfig}
        onClose={() => setShowSettingsModal(false)}
        onSave={handleSaveSettings}
      />

      <LogEventModal
        isOpen={showLogModal}
        onClose={() => setShowLogModal(false)}
        onSubmit={handleCreateEvent}
        defaultAssetId={
          assetFilter !== "all" ? Number(assetFilter) : uniqueAssets[0] ?? 0
        }
        defaultLabel={uniqueLabels[0] ?? "anomaly"}
        submitting={submitting}
      />

      <CsvRunnerModal
        apiConfig={apiConfig}
        isOpen={showCsvRunnerModal}
        onClose={() => setShowCsvRunnerModal(false)}
        onEventLogged={() => handleFetchEvents(true)}
        onStatusChange={setSelectedCsvStatus}
      />
    </div>
  );
}

export default App;

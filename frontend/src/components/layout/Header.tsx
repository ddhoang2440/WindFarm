import React from "react";
import { Wind, RefreshCw, Settings } from "lucide-react";
import type { ApiConfig } from "../../types/windfarm";

interface HeaderProps {
  apiConfig: ApiConfig;
  onToggleAutoRefresh: () => void;
  onOpenSettings: () => void;
  isBackendOffline?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  apiConfig,
  onToggleAutoRefresh,
  onOpenSettings,
  isBackendOffline,
}) => {
  return (
    <header className="site-header">
      <div className="header-inner scada-header-inner">
        <div className="logo">
          <div className="logo-icon">
            <Wind size={18} strokeWidth={2.5} />
          </div>
          <div>
            <span className="logo-text">WindFarm HKT</span>
            <span className="scada-version-badge">
              Turbine Event & Anomaly Console
            </span>
          </div>
        </div>

        <div className="header-controls">
          {/* Auto-Refresh Toggle */}
          <button
            type="button"
            className={`btn-glass ${apiConfig.autoRefresh ? "active-poll" : ""}`}
            onClick={onToggleAutoRefresh}
          >
            <RefreshCw
              size={13}
              className={apiConfig.autoRefresh ? "spin-poll-icon" : ""}
            />
            <span>
              Auto-Poll:{" "}
              {apiConfig.autoRefresh
                ? `${apiConfig.refreshIntervalSec}s (ON)`
                : "OFF"}
            </span>
          </button>

          {/* Settings Button */}
          <button
            type="button"
            className="btn-glass"
            onClick={onOpenSettings}
          >
            <Settings size={14} />
            <span>API Settings</span>
            {isBackendOffline && (
              <span
                className="api-offline-indicator"
                title="Backend chưa kết nối hoặc đang offline"
              >
                ● Offline
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};


import React from "react";
import { AlertTriangle, RefreshCw, Settings } from "lucide-react";

interface ErrorBannerProps {
  error: string;
  baseUrl: string;
  onRetry: () => void;
  onOpenSettings: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  error,
  baseUrl,
  onRetry,
  onOpenSettings,
}) => {
  return (
    <div className="error-banner">
      <div className="error-banner-content">
        <div className="error-banner-title-row">
          <AlertTriangle size={18} className="text-danger" />
          <span>
            <strong>Backend Connection Error:</strong> {error}
          </span>
        </div>
        <span className="error-banner-hint">
          Ensure FastAPI Backend is running at <code>{baseUrl}</code> and Bearer Token is correct.
        </span>
      </div>
      <div className="error-banner-actions">
        <button
          type="button"
          className="btn-glass btn-sm"
          onClick={onRetry}
        >
          <RefreshCw size={13} />
          <span>Retry</span>
        </button>
        <button
          type="button"
          className="btn-glass btn-sm"
          onClick={onOpenSettings}
        >
          <Settings size={13} />
          <span>Change URL / Token</span>
        </button>
      </div>
    </div>
  );
};


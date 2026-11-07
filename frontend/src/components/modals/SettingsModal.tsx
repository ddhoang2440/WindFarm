import React, { useState, useEffect } from "react";
import { Settings, X, Save } from "lucide-react";
import type { ApiConfig } from "../../types/windfarm";

interface SettingsModalProps {
  isOpen: boolean;
  apiConfig: ApiConfig;
  onClose: () => void;
  onSave: (newConfig: ApiConfig) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  apiConfig,
  onClose,
  onSave,
}) => {
  const [formConfig, setFormConfig] = useState<ApiConfig>(apiConfig);

  useEffect(() => {
    setFormConfig(apiConfig);
  }, [apiConfig, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formConfig);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="glass-card modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Settings size={18} />
              <span>API Backend & Bearer Token Settings</span>
            </h3>
            <p className="card-subtitle">Configure connection to FastAPI Backend</p>
          </div>
          <button type="button" className="btn-glass" onClick={onClose} title="Close">
            <X size={15} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="scada-form">
          <label className="form-field">
            <span>Backend Base URL</span>
            <input
              type="text"
              value={formConfig.baseUrl}
              onChange={(e) =>
                setFormConfig({ ...formConfig, baseUrl: e.target.value })
              }
              placeholder="http://127.0.0.1:8000"
              required
            />
          </label>

          <label className="form-field">
            <span>Bearer API_TOKEN (Authorization Header)</span>
            <input
              type="text"
              value={formConfig.apiToken}
              onChange={(e) =>
                setFormConfig({ ...formConfig, apiToken: e.target.value })
              }
              required
            />
          </label>

          <div className="form-row-2">
            <label className="form-field">
              <span>Auto-Fetch (Auto-Poll)</span>
              <select
                value={formConfig.autoRefresh ? "on" : "off"}
                onChange={(e) =>
                  setFormConfig({
                    ...formConfig,
                    autoRefresh: e.target.value === "on",
                  })
                }
              >
                <option value="on">Enabled</option>
                <option value="off">Disabled</option>
              </select>
            </label>

            <label className="form-field">
              <span>Polling Interval (seconds)</span>
              <input
                type="number"
                min={2}
                max={60}
                value={formConfig.refreshIntervalSec}
                onChange={(e) =>
                  setFormConfig({
                    ...formConfig,
                    refreshIntervalSec: Number(e.target.value),
                  })
                }
              />
            </label>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-glass" onClick={onClose}>
              <X size={14} />
              <span>Cancel</span>
            </button>
            <button type="submit" className="btn-gradient">
              <Save size={14} />
              <span>Save & Re-fetch API</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};


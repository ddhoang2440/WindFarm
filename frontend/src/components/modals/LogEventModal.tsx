import React, { useState, useEffect } from "react";
import { AlertTriangle, X, Send, Loader2 } from "lucide-react";
import type { EventInput } from "../../types/windfarm";

interface LogEventModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (event: EventInput) => Promise<void>;
  defaultAssetId: number;
  defaultLabel: string;
  submitting: boolean;
}

export const LogEventModal: React.FC<LogEventModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  defaultAssetId,
  defaultLabel,
  submitting,
}) => {
  const [eventForm, setEventForm] = useState<EventInput>({
    event_id: Math.floor(Date.now() / 1000),
    asset_id: defaultAssetId,
    event_label: defaultLabel || "anomaly",
    event_start: new Date().toISOString().slice(0, 19),
    event_end: new Date().toISOString().slice(0, 19),
    event_description: "",
  });

  useEffect(() => {
    if (isOpen) {
      const nowIso = new Date().toISOString().slice(0, 19);
      setEventForm({
        event_id: Math.floor(Date.now() / 1000),
        asset_id: defaultAssetId,
        event_label: defaultLabel || "anomaly",
        event_start: nowIso,
        event_end: nowIso,
        event_description: "",
      });
    }
  }, [isOpen, defaultAssetId, defaultLabel]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(eventForm);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="glass-card modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <AlertTriangle size={18} className="text-danger" />
              <span>Log New Event (POST /api/v1/events)</span>
            </h3>
            <p className="card-subtitle">
              Save an <span className="text-cyan">EventInput</span> record directly into MongoDB collection{" "}
              <span className="text-cyan">events</span>
            </p>
          </div>
          <button type="button" className="btn-glass" onClick={onClose} title="Close">
            <X size={15} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="scada-form">
          <div className="form-row-2">
            <label className="form-field">
              <span>Event ID (event_id)</span>
              <input
                type="number"
                value={eventForm.event_id}
                onChange={(e) =>
                  setEventForm({
                    ...eventForm,
                    event_id: Number(e.target.value),
                  })
                }
                required
              />
            </label>

            <label className="form-field">
              <span>Turbine Asset ID (asset_id)</span>
              <input
                type="number"
                value={eventForm.asset_id}
                onChange={(e) =>
                  setEventForm({
                    ...eventForm,
                    asset_id: Number(e.target.value),
                  })
                }
                required
              />
            </label>
          </div>

          <label className="form-field">
            <span>Event Label (event_label)</span>
            <input
              type="text"
              placeholder="e.g. anomaly, normal, warning, storm_load"
              value={eventForm.event_label}
              onChange={(e) =>
                setEventForm({
                  ...eventForm,
                  event_label: e.target.value,
                })
              }
              required
            />
          </label>

          <div className="form-row-2">
            <label className="form-field">
              <span>Start Time (event_start)</span>
              <input
                type="text"
                value={eventForm.event_start}
                onChange={(e) =>
                  setEventForm({
                    ...eventForm,
                    event_start: e.target.value,
                  })
                }
                required
              />
            </label>

            <label className="form-field">
              <span>End Time (event_end)</span>
              <input
                type="text"
                value={eventForm.event_end}
                onChange={(e) =>
                  setEventForm({
                    ...eventForm,
                    event_end: e.target.value,
                  })
                }
                required
              />
            </label>
          </div>

          <label className="form-field">
            <span>Event Description (event_description)</span>
            <textarea
              rows={3}
              placeholder="Enter anomaly or operational details from turbine or ML model..."
              value={eventForm.event_description}
              onChange={(e) =>
                setEventForm({
                  ...eventForm,
                  event_description: e.target.value,
                })
              }
              required
            />
          </label>

          <div className="modal-actions">
            <button type="button" className="btn-glass" onClick={onClose}>
              <X size={14} />
              <span>Cancel</span>
            </button>
            <button
              type="submit"
              className="btn-gradient"
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <Loader2 size={14} className="spin-icon" />
                  <span>Submitting...</span>
                </>
              ) : (
                <>
                  <Send size={14} />
                  <span>Submit POST /api/v1/events</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};


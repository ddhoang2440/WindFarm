import React from "react";
import {
  Rocket,
  FileSpreadsheet,
  FolderArchive,
  Zap,
  Pause,
  Settings2,
  UploadCloud,
} from "lucide-react";

export interface CsvFileInfo {
  fileName: string;
  rowCount: number;
  isRunning: boolean;
  currentIndex: number;
}

interface CsvStreamerBannerProps {
  selectedCsvStatus?: CsvFileInfo | null;
  onOpenRunner: () => void;
}

export const CsvStreamerBanner: React.FC<CsvStreamerBannerProps> = ({
  selectedCsvStatus,
  onOpenRunner,
}) => {
  return (
    <div className="runner-quick-banner">
      <div className="runner-quick-info">
        <span className="runner-quick-icon">
          <Rocket size={26} strokeWidth={2.2} />
        </span>
        <div className="runner-quick-text-wrap">
          <div className="runner-quick-title">
            Telemetry CSV Streamer (Dataset Runner)
          </div>
          <div className="runner-quick-desc">
            Upload your CSV file to sequentially stream sensor records to Backend and trigger AI anomaly detection.
          </div>
          {/* File Status Display */}
          <div className="runner-file-status-row">
            {selectedCsvStatus ? (
              <span className="file-status-chip active">
                <span className="file-icon">
                  <FileSpreadsheet size={15} />
                </span>
                <span>
                  File đã chọn: <strong>{selectedCsvStatus.fileName}</strong> ({selectedCsvStatus.rowCount} dòng dữ liệu)
                </span>
                <span
                  className={`file-run-badge ${
                    selectedCsvStatus.isRunning ? "running" : "ready"
                  }`}
                >
                  {selectedCsvStatus.isRunning ? (
                    <>
                      <Zap size={11} />
                      <span>Đang stream: {selectedCsvStatus.currentIndex}/{selectedCsvStatus.rowCount}</span>
                    </>
                  ) : (
                    <>
                      <Pause size={11} />
                      <span>Sẵn sàng stream</span>
                    </>
                  )}
                </span>
              </span>
            ) : (
              <span className="file-status-chip idle">
                <span className="file-icon">
                  <FolderArchive size={15} />
                </span>
                <span>Trạng thái: Chưa nạp file CSV (Nhấn để chọn và chạy)</span>
              </span>
            )}
          </div>
        </div>
      </div>
      <button
        type="button"
        className="btn-glow-crimson"
        onClick={onOpenRunner}
      >
        {selectedCsvStatus ? (
          <>
            <Settings2 size={15} />
            <span>Quản lý & Tiếp tục Stream</span>
          </>
        ) : (
          <>
            <UploadCloud size={15} />
            <span>Upload & Start CSV Stream</span>
          </>
        )}
      </button>
    </div>
  );
};


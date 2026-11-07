import React from "react";
import { Search, X } from "lucide-react";

interface EventFiltersProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  assetFilter: string;
  onAssetChange: (value: string) => void;
  labelFilter: string;
  onLabelChange: (value: string) => void;
  uniqueAssets: number[];
  uniqueLabels: string[];
  onClearFilters: () => void;
}

export const EventFilters: React.FC<EventFiltersProps> = ({
  searchQuery,
  onSearchChange,
  assetFilter,
  onAssetChange,
  labelFilter,
  onLabelChange,
  uniqueAssets,
  uniqueLabels,
  onClearFilters,
}) => {
  const hasActiveFilters =
    assetFilter !== "all" || labelFilter !== "all" || Boolean(searchQuery.trim());

  return (
    <div className="filter-toolbar">
      {/* Search Input */}
      <div className="search-input-wrap">
        <Search size={15} className="search-icon-svg" />
        <input
          type="text"
          placeholder="Search by event_id, asset_id, label, or description..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        {searchQuery && (
          <button
            type="button"
            className="btn-clear-search"
            onClick={() => onSearchChange("")}
            title="Clear search input"
          >
            <X size={13} />
          </button>
        )}
      </div>

      {/* Dropdown Filters */}
      <div className="filter-selects">
        <label className="filter-select-item">
          <span>Turbine (asset_id):</span>
          <select
            value={assetFilter}
            onChange={(e) => onAssetChange(e.target.value)}
          >
            <option value="all">
              All Turbines {uniqueAssets.length > 0 ? `(${uniqueAssets.length})` : ""}
            </option>
            {uniqueAssets.map((id) => (
              <option key={id} value={String(id)}>
                Turbine #{id} (asset_id: {id})
              </option>
            ))}
          </select>
        </label>

        <label className="filter-select-item">
          <span>Label (event_label):</span>
          <select
            value={labelFilter}
            onChange={(e) => onLabelChange(e.target.value)}
          >
            <option value="all">
              All Labels {uniqueLabels.length > 0 ? `(${uniqueLabels.length})` : ""}
            </option>
            {uniqueLabels.map((lbl) => (
              <option key={lbl} value={lbl}>
                {lbl}
              </option>
            ))}
          </select>
        </label>

        {hasActiveFilters && (
          <button
            type="button"
            className="btn-glass btn-sm"
            onClick={onClearFilters}
          >
            <X size={13} />
            <span>Clear Filters</span>
          </button>
        )}
      </div>
    </div>
  );
};


# 📋 Functional Specifications — WindFarm HKT

This document specifies user interactions, functional requirements, and behavioral logic across all modules of the **WindFarm HKT SCADA Console**.

---

## 1. Overview & SCADA KPI Summary Cards

The top section of the dashboard features 3 industrial KPI summary cards adhering to mission-critical SCADA design standards:

### 1.1. Card 1: Total Logged Events (MongoDB Count)
* **Displayed Metric:** Total number of operational events currently recorded in MongoDB Atlas.
* **Timestamp Indicator:** Displays the most recent sync time (`Updated: HH:MM:SS`).
* **Behavior:** When the backend receives new events (via CSV streaming or manual submission), this counter updates automatically on the next auto-polling cycle.

### 1.2. Card 2: Event Classification (Anomaly vs Normal)
* **Displayed Metrics:**
  - Total number of events classified as anomalies (`anomalies`).
  - Total number of normal operational events (`normal`).
  - Model classification attribution (`RandomForest ML Model`).
* **Dynamic Border Alert Rules:**
  - **When `anomalyCount == 0`:** Displays a standard neutral cyan SCADA border and a green badge `"100% Normal"` with a `CheckCircle2` icon. **Prevents alarming red borders when the cluster is operating normally.**
  - **When `anomalyCount > 0`:** Automatically activates a prominent alert border (`.card-anomaly-border` — `1.5px solid #ef4444`), shifts the count to `text-danger`, and displays a red warning badge `"X Anomalies"` with an `AlertTriangle` icon.

### 1.3. Card 3: Latest Event
* **Displayed Metrics:**
  - Status pill for the most recent incident (`ANOMALY` in red or `NORMAL` in green).
  - Turbine ID and Event ID identifiers (`Turbine #X • #EventID`).
  - Standardized incident end timestamp (`YYYY-MM-DD HH:mm:ss`).
* **Full Description Inspection Mechanism:**
  - **Truncation:** Lengthy descriptions are neatly truncated with an ellipsis (`...`).
  - **Instant SCADA Tooltip:** Hovering over the text triggers a frosted-glass tooltip showing the full description.
  - **Expand / Collapse Toggle:** Clicking `"Details"` or `"Collapse"` expands or contracts the text inline without navigating away.

---

## 2. In-Browser CSV Telemetry Streamer & Runner

Provides a client-side dataset runner allowing operators to simulate live sensor streaming directly in the browser without external scripts.

### 2.1. Quick Status Banner (CSV Streamer Banner)
* **Icon:** Industrial `Rocket` icon.
* **Loaded File Status Badge:**
  - **No File Loaded:** Displays an idle badge `"Status: No CSV file loaded (Click to select and run)"`.
  - **File Loaded:** Shows selected file name and row count (e.g., `Selected file: turbine_telemetry.csv (100 data rows)`).
  - **Stream State Badge:** Displays streaming status (`Streaming: 24/100` with `Zap` icon) or readiness (`Ready to stream` with `Pause` icon).
* **Action Button:** Opens the CSV Runner modal.

### 2.2. CSV Runner Modal (CsvRunnerModal)
Structured in a two-column responsive layout:
* **Left Column (Controls & Upload):**
  - **Dropzone:** Drag and drop `.csv` files directly or browse via file picker.
  - **Client-Side CSV Parser:** Parses columns (`asset_id`, `wind_speed`, `power_output`, `ambient_temp`, `status_type_id`), validates types, and displays error summaries if invalid rows exist.
  - **Action Toolbar:**
    - **Start CSV Stream** / **Pause Stream**: Initiates or pauses sequential streaming.
    - **Reset Stream**: Resets progress back to row 0.
  - **Stream Interval Selector:**
    - Segmented capsule chips: `3s/row`, `1s/row`, `0.5s/row`.
    - Allows changing speed on the fly while streaming is in progress.
  - **Progress Card:**
    - Visual percentage progress bar.
    - Successful transmission counter vs total rows.
    - Status pills: `Ready`, `Streaming...`, `Paused`, `Completed`.
* **Right Column (Live Terminal Log):**
  - Header displays active target endpoint: `POST /api/v1/telemetry` and total log count.
  - Dark-mode terminal console styled with `JetBrains Mono` monospace typography.
  - Color-coded log entries:
    - `[INFO]`: Cyan text for system milestones and file loading.
    - `[OK]`: Green text for normal operational readings.
    - `[ANOMALY DETECTED]`: Red highlight with model probability score (e.g., `🚨 [ANOMALY DETECTED] Row #14: ... (prob: 94.50%)`).
    - `[ERROR]`: Deep red text for connection or network timeouts.
  - **Clear Logs** button to reset the terminal output.

---

## 3. Event Log Management & Filters (EventTable & Filters)

### 3.1. Search & Filter Bar (EventFilters)
* **Full-Text Search:**
  - Filters across descriptions, turbine IDs, and event labels in real time.
  - High-brightness placeholder (`#e2e8f0`, `opacity: 1`) for high readability in industrial lighting.
  - Auto-appearing `[X]` button to clear search input instantly.
* **Turbine Asset Dropdown:** Dynamically populates with unique turbine IDs found in the dataset (`Turbine #1`, `Turbine #2`, etc.).
* **Classification Dropdown:** Filters by `All`, `ANOMALY`, `NORMAL`, `WARNING`, `INFO`.
* **Reset Filters Button:** Reverts all filters and search input back to defaults.
* **Manual Event Logging Button:** Opens the manual event logging modal.

### 3.2. SCADA Data Table (EventTable)
* **Zebra Striping:**
  - Odd rows: Background `#080f1e`.
  - Even rows: Background `#0d1a31`.
  - Hover effect: Background transitions smoothly to `#152747` to maintain row tracking across wide tables.
* **Anomaly Row Highlighting:**
  - Rows labeled `ANOMALY` automatically receive an alert tint (`rgba(239, 68, 68, 0.12)`) and a red indicator border (`border-left: 4px solid #ef4444`).
* **Table Columns:**
  1. `EVENT ID`: Monospace event identifier.
  2. `TURBINE ID`: Turbine badge with wind icon.
  3. `CLASSIFICATION`: Color-coded status badge (`AlertTriangle` for Anomaly, `CheckCircle2` for Normal).
  4. `EVENT START`: ISO start timestamp formatted in monospace.
  5. `EVENT END`: ISO end timestamp formatted in monospace.
  6. `DESCRIPTION`: Full event description with tooltip.

### 3.3. Responsive Pagination
* **Desktop ($\ge 640\text{px}$):**
  - Left: Page size dropdown (`10`, `20`, `50`, `100` rows) and range indicator (`Showing 1–10 of 45 events`).
  - Right: Full navigation controls with text: `[« First] [< Prev] Page 1 / 5 [Next >] [Last »]`.
* **Mobile & Small Viewports ($\le 640\text{px}$):**
  - Stacks into a two-deck layout.
  - Top deck: Rows per page on the left, event count on the right.
  - Bottom deck: Centered icon-only controls `[ « ] [ < ] Page 1 / 5 [ > ] [ » ]`, preventing awkward wrapping or broken buttons.

---

## 4. Manual Event Logging Modal (LogEventModal)
* Enables field operators to record unscheduled maintenance, blade inspections, or mechanical faults:
  - `Asset ID`: Select target turbine.
  - `Event ID`: Auto-generated random integer identifier.
  - `Classification`: Select `anomaly`, `normal`, `warning`, `maintenance`.
  - `Event Start` & `Event End`: Datetime pickers.
  - `Description`: Multi-line textarea detailing symptoms or maintenance observations.
* Dispatched via `POST /api/v1/events` with Bearer Token authentication and persisted into MongoDB Atlas.

---

## 5. System Configuration & Auto-Polling (SettingsModal)
* **Backend Base URL:** Allows changing the target API endpoint (default: `http://127.0.0.1:8000` or cloud tunneling URLs).
* **Bearer Token:** Configures the authentication token required by the backend.
* **Auto-Refresh Toggle:** Enables/disables background event synchronization at configurable intervals (`3s`, `5s`, `10s`).
* **LocalStorage Persistence:** All settings are persisted in browser storage and restored upon page reload.
* **Offline Connectivity Indicator:** When backend requests fail or the token is invalid, a subtle red `OFFLINE` badge appears in the header without disrupting the layout.

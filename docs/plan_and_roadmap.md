# 🗺️ Implementation Plan & Roadmap — WindFarm HKT

This document records development milestones, resolved engineering and UX challenges, and future enhancement roadmaps for **WindFarm HKT**.

---

## 1. Development Lifecycle Overview

The project was executed through iterative Agile sprints with the goal of evolving an initial prototype into an industrial-grade SCADA monitoring console equipped with AI anomaly detection.

```
[Phase 1: Backend Foundation] ➔ [Phase 2: ML & APM Integration] ➔ [Phase 3: SCADA UI Redesign] ➔ [Phase 4: Modular Refactoring] ➔ [Phase 5: Responsive UX Polish]
```

---

## 2. Completed Milestones

### 📍 Phase 1: Backend Architecture & Data Persistence
* **Objective:** Construct a high-throughput telemetry ingestion service with dynamic feature calculations and database persistence.
* **Delivered Features:**
  - Initialized FastAPI API Gateway on port `8000`.
  - Connected MongoDB Atlas using Beanie ODM and asynchronous Motor driver.
  - Implemented the **Dynamic Feature Engineering Pipeline**: computes 6-hour rolling mean wind speed (`wind_speed_roll_mean_6h`), 6-hour power standard deviation (`power_roll_std_6h`), and theoretical power index (`theoretical_power_index`).
  - Implemented centralized Bearer Token authentication across all operational endpoints.

### 📍 Phase 2: Machine Learning & Datadog APM Integration
* **Objective:** Enable real-time automated anomaly detection using machine learning and cloud infrastructure monitoring.
* **Delivered Features:**
  - Trained a high-accuracy `RandomForestClassifier` on turbine sensor telemetry datasets.
  - Serialized the model artifact into `wind_turbine_anomaly_model.joblib` and created the independent `ML Service` on port `8001`.
  - Established asynchronous inter-service REST communication between Backend and ML Service using HTTPX.
  - Forwarded telemetry metrics and real-time alert events to Datadog APM via Datadog API Client.

### 📍 Phase 3: Industrial SCADA Redesign
* **Objective:** Replace flashy demo themes with mission-critical SCADA design standards.
* **Delivered Features:**
  - Implemented the **Midnight Blue + Cyan SCADA** palette (`#060b17`, `#0b1426`, `#0891b2`, `#38bdf8`).
  - Removed eye-straining neon glows and excessive animations to maximize contrast and instant anomaly visibility.
  - Replaced hardcoded emojis with [Lucide React](https://lucide.dev/) digital vector icons.
  - Built the in-browser CSV telemetry streaming tool (`In-Browser CSV Runner`).

### 📍 Phase 4: Modular Codebase Refactoring
* **Objective:** Decouple monolithic components and services into clean, feature-driven modules.
* **Delivered Features:**
  - Modularized `services/` into dedicated clients: `config.service.ts`, `telemetry.service.ts`, `event.service.ts`, and `health.service.ts` with barrel exports.
  - Reorganized `components/` into structured subdirectories:
    - [`components/layout/`](file:///c:/WindFarm/frontend/src/components/layout): Header, Footer, connectivity indicators.
    - [`components/dashboard/`](file:///c:/WindFarm/frontend/src/components/dashboard): KpiSummary, EventTable, EventFilters.
    - [`components/csv-runner/`](file:///c:/WindFarm/frontend/src/components/csv-runner): CsvStreamerBanner, CsvRunnerModal.
    - [`components/modals/`](file:///c:/WindFarm/frontend/src/components/modals): SettingsModal, LogEventModal, ErrorBanner.
  - Removed all obsolete loose files from the root of `components/`.

### 📍 Phase 5: Responsive UX Polish & Bug Fixes
* **Objective:** Resolve user feedback items regarding layout responsiveness and UI legibility.
* **Delivered Features:** (Detailed in the resolution table below).

---

## 3. Engineering Challenge Resolution Matrix

Below is a detailed summary of user feedback items and the technical solutions applied:

| Component | Reported Issue | Technical Solution Applied | Status |
| :--- | :--- | :--- | :---: |
| **Header** | Header height was overly tall, consuming excessive vertical space | Reduced `min-height` from `48px` to `42px`, trimmed padding to `6px 20px`, and scaled logo icon down to `26px`. | ✅ Resolved |
| **Summary Cards** | Inadequate spacing between metric values and description text | Increased `.kpi-value-row` margin to `10px 0 4px 0`, increased `.kpi-meta-row` margin-top to `18px` with `12px` top padding. | ✅ Resolved |
| **Classification** | Alarming red border appeared when anomaly count was 0 | Added dynamic border condition `anomalyCount > 0 ? "card-anomaly-border" : ""`. When `anomaly == 0`, displays a neutral cyan border and green `"100% Normal"` badge. | ✅ Resolved |
| **CSV Streamer** | Needed clear visual indicator of selected CSV file status | Integrated file info chip on the banner: shows file name, total row count, and live streaming progress (`Streaming: x/y` or `Ready to stream`). | ✅ Resolved |
| **Search Input** | Search placeholder text was dark and hard to read on SCADA theme | Increased placeholder text color brightness to `#e2e8f0` with `opacity: 1` for high legibility. | ✅ Resolved |
| **SCADA Table** | Needed zebra striping and smooth row hover effects | Added distinct alternating row backgrounds (`#080f1e` / `#0d1a31`), smooth hover background (`#152747`), and red left indicator border (`4px solid #ef4444`) for anomaly rows. | ✅ Resolved |
| **Latest Event** | Event descriptions were cut off without full text view | Added an instant frosted-glass tooltip on hover and an inline `"Details"` / `"Collapse"` button toggle. | ✅ Resolved |
| **Pagination Bar** | Navigation buttons wrapped awkwardly into two broken lines on mobile | Redesigned pagination into a 2-deck layout on screens $\le 640\text{px}$, hiding text labels to display compact icon buttons `[«] [<] Page 1/1 [>] [»]`, with `flex-wrap: nowrap`. | ✅ Resolved |
| **CSV Modal Header** | Close button `[X]` was pushed below the title on narrow viewports | Enforced `flex-wrap: nowrap !important` on `.runner-modal-header` to keep `[X]` pinned to the top right. | ✅ Resolved |
| **Interval Chips** | Speed selector chips stretched with huge awkward whitespace | Wrapped chips inside `.interval-chips-group` with a tight `3px` gap to maintain a cohesive segmented pill control. | ✅ Resolved |
| **Network Error UI** | White error box overlaid and disrupted the SCADA dashboard | Replaced intrusive error banners with a subtle red `OFFLINE` badge in the header and smart React-Toastify notifications. | ✅ Resolved |

---

## 4. Verification & Testing Matrix

* **Frontend Build & TypeScript Validation:**
  - Build command: `npm run build` (`tsc -b && vite build`)
  - Result: **2082 modules transformed**, built cleanly in **2.73s**, **0 errors, 0 warnings**.
* **Device Responsiveness Testing:**
  - Desktop ($1920\times 1080$, $1440\times 900$): Balanced 3-column SCADA layout with full controls.
  - Tablet ($1024\times 768$, $768\times 1024$): Fluid adaptation of KPI grid and modal layout.
  - Mobile ($375\times 667$, $414\times 896$, $360\times 740$): Compact icon-only pagination, scaled modal padding, and horizontal scrollbars on data tables without broken viewports.

---

## 5. Future Roadmap

### 🚀 Phase 6: Real-Time Bidirectional WebSockets
* **WebSocket Ingestion:** Implement full-duplex WebSocket connections (`ws://`) between Backend and Frontend to replace HTTP polling, reducing latency below `50ms`.
* **Live Waveform Charts:** Stream active power curves against theoretical aerodynamic limits using Canvas/SVG time-series charts.

### 🚀 Phase 7: Multi-Farm Geospatial Monitoring (GIS Map)
* **Interactive Satellite Map:** Visualize multiple wind farm locations on an interactive geospatial map with green/red LED cluster status.
* **Role-Based Access Control (RBAC):** Define granular permissions for Operators, Maintenance Technicians, and System Administrators.

### 🚀 Phase 8: Explainable AI (XAI)
* **SHAP / LIME Value Integration:** Provide feature attribution breakdown charts for each detected anomaly (e.g., whether caused by pitch angle deviation or bearing temperature spikes), facilitating rapid Root Cause Analysis.

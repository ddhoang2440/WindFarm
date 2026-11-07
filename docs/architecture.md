# 📐 System Architecture — WindFarm HKT

This document specifies the end-to-end system architecture, distributed microservices topology, real-time data flow pipelines, and database schemas for **WindFarm HKT**.

---

## 1. High-Level System Topology

The system is architected as a **distributed microservices** platform ensuring high availability, service decoupling, and independent horizontal scalability:

```mermaid
flowchart TD
    subgraph Client["Presentation Layer (SCADA Console)"]
        UI["React 19 + TypeScript SCADA Console\n(Port 5173)\n- Dashboard KPI Cards\n- In-Browser CSV Streamer\n- Event Management & Filters"]
    end

    subgraph Gateway["Core Processing Layer (API Gateway)"]
        BE["FastAPI Backend Service\n(Port 8000)\n- Bearer Token Auth\n- Feature Engineering (6h Rolling)\n- Telemetry & Event Ingestion API"]
    end

    subgraph MLService["Artificial Intelligence Layer (ML Service)"]
        ML["FastAPI ML Service\n(Port 8001)\n- Model: RandomForest Classifier (Joblib)\n- Input: 7 Features\n- Output: is_anomaly, anomaly_probability"]
    end

    subgraph DataStore["Persistence Layer"]
        DB[("MongoDB Atlas Database\n- Collection: telemetry_records\n- Collection: event_records")]
    end

    subgraph APM["Observability & Alerting Layer"]
        DD["Datadog Cloud Platform\n- APM Tracing (ddtrace)\n- Alert Events (Datadog API)"]
    end

    UI -->|"HTTP POST /api/v1/telemetry (Bearer Token)"| BE
    UI -->|"HTTP GET /api/v1/events (Auto-poll 3s)"| BE
    UI -->|"HTTP POST /api/v1/events (Manual Log)"| BE

    BE -->|"HTTP POST /predict (7 Features)"| ML
    BE -->|"Async Read/Write (Motor + Beanie)"| DB
    ML -->|"Forward Alert Events upon Anomaly"| DD
    BE -->|"Synchronize Metrics & Latency Traces"| DD
```

---

## 2. Real-Time Sequence Data Flow

The following sequence diagram illustrates the lifecycle of a sensor telemetry record from ingestion through AI inference, database persistence, and SCADA dashboard display:

```mermaid
sequenceDiagram
    autonumber
    actor Operator as Field Engineer / Operator
    participant UI as SCADA Console (React)
    participant BE as Backend API (FastAPI:8000)
    participant ML as ML Service (FastAPI:8001)
    participant DB as MongoDB Atlas
    participant DD as Datadog APM

    Operator->>UI: Start CSV Stream or Submit Telemetry
    UI->>BE: POST /api/v1/telemetry (with Bearer Token)
    Note over BE: Validate Bearer Token authentication
    BE->>DB: Query 6-hour historical telemetry for turbine
    DB-->>BE: Recent historical records
    Note over BE: Compute 3 Dynamic Derived Features:<br/>- wind_speed_roll_mean_6h<br/>- power_roll_std_6h<br/>- theoretical_power_index
    BE->>ML: POST /predict (7 Features)
    Note over ML: Execute RandomForestClassifier inference
    ML-->>BE: {"is_anomaly": true, "anomaly_probability": 0.94}
    
    alt If Anomaly Detected (is_anomaly == True)
        ML->>DD: Dispatch Alert Event "Turbine Anomaly Detected"
        BE->>DB: Automatically record into `event_records`
    end
    
    BE->>DB: Persist telemetry record into `telemetry_records`
    BE-->>UI: Response {"status": "success", "is_anomaly": true, ...}
    UI->>Operator: Update Live Terminal & Highlight Anomaly Row on SCADA Table
```

---

## 3. Microservices Component Breakdown

### 3.1. Frontend SCADA Console
* **Directory:** [`frontend/`](file:///c:/WindFarm/frontend)
* **Core Technologies:** React 19, TypeScript, Vite 8, Lucide React, React-Toastify.
* **Design Philosophy:** Midnight Blue & Cyan SCADA industrial theme (`#060b17`, `#0b1426`, `#0891b2`, `#38bdf8`), high data legibility, zero glare, and immediate visual distinction of anomalies.
* **Modular Structure:**
  - `components/layout/`: Header with real-time backend connection monitor, Footer.
  - `components/dashboard/`: 3 KPI summary cards, SCADA data table, search & filtering strip.
  - `components/csv-runner/`: Quick status banner and in-browser CSV telemetry streaming modal.
  - `components/modals/`: API Bearer token settings modal, manual event logging modal.
  - `services/`: Decoupled API service clients (`telemetry`, `event`, `config`, `health`).

### 3.2. Backend API Gateway & Feature Engine
* **Directory:** [`backend/src/`](file:///c:/WindFarm/backend/src)
* **Core Technologies:** FastAPI, Beanie ODM, Motor, Pydantic v2.
* **Service Port:** `8000`
* **Core Responsibilities:**
  - Telemetry ingestion through `POST /api/v1/telemetry`.
  - Centralized security verification via Bearer Token middleware (`core/security.py`).
  - **Dynamic Feature Engineering Pipeline:** Computes 6-hour rolling aggregations on the fly before passing features to the ML Service.
  - Event management and query filtering through `GET /api/v1/events`.
  - Manual incident creation via `POST /api/v1/events`.

### 3.3. Machine Learning Prediction Service
* **Directory:** [`backend/ml_service/`](file:///c:/WindFarm/backend/ml_service)
* **Core Technologies:** FastAPI, Scikit-learn 1.6.1, Pandas, Joblib.
* **Service Port:** `8001`
* **Model Artifact:** `RandomForestClassifier` serialized in `wind_turbine_anomaly_model.joblib`.
* **7 Input Features:**
  1. `wind_speed` (m/s): Instantaneous wind velocity.
  2. `power_output` (kW): Active turbine electrical power generated.
  3. `ambient_temp` (°C): Ambient environmental temperature.
  4. `status_type_id`: Integer turbine operational status code.
  5. `wind_speed_roll_mean_6h`: 6-hour rolling mean of wind speed.
  6. `power_roll_std_6h`: 6-hour rolling standard deviation of power output.
  7. `theoretical_power_index`: Ratio index comparing theoretical power curve against actual output.
* **Outputs:** Binary classification `is_anomaly` (boolean) and confidence score `anomaly_probability` (float).

---

## 4. Database Schema (MongoDB Atlas)

The system utilizes MongoDB Atlas with two core collections managed through Beanie ODM documents:

### 4.1. Collection `telemetry_records`
Stores high-frequency sensor readings alongside calculated derived features:
```json
{
  "_id": "ObjectId('...')",
  "asset_id": 1,
  "time_stamp": "2026-11-04T08:30:00Z",
  "wind_speed": 12.4,
  "power_output": 1850.5,
  "ambient_temp": 24.2,
  "status_type_id": 1,
  "wind_speed_roll_mean_6h": 11.8,
  "power_roll_std_6h": 142.3,
  "theoretical_power_index": 0.96,
  "is_anomaly": false,
  "anomaly_probability": 0.05,
  "created_at": "2026-11-04T08:30:01Z"
}
```

### 4.2. Collection `event_records`
Stores operational incidents, automatic AI anomaly alarms, and manual maintenance logs:
```json
{
  "_id": "ObjectId('...')",
  "event_id": 1024,
  "asset_id": 3,
  "event_label": "anomaly",
  "event_start": "2026-11-04T09:15:00Z",
  "event_end": "2026-11-04T09:45:00Z",
  "event_description": "Blade Pitch Control Angle Mismatch detected under high wind velocity",
  "created_at": "2026-11-04T09:15:02Z"
}
```

---

## 5. Frontend Modular Architecture

Frontend components and services follow a strict Separation of Concerns (SoC) design:

```mermaid
flowchart LR
    subgraph UIComponents["components/ directory"]
        L["layout/\nHeader.tsx, Footer.tsx"]
        D["dashboard/\nKpiSummary.tsx, EventTable.tsx, EventFilters.tsx"]
        C["csv-runner/\nCsvStreamerBanner.tsx, CsvRunnerModal.tsx"]
        M["modals/\nSettingsModal.tsx, LogEventModal.tsx, ErrorBanner.tsx"]
    end

    subgraph CoreServices["services/ directory"]
        S1["config.service.ts"]
        S2["telemetry.service.ts"]
        S3["event.service.ts"]
        S4["health.service.ts"]
    end

    subgraph StateAndTypes["State & Utilities"]
        App["App.tsx (Main State Orchestrator)"]
        T["types/windfarm.ts"]
        U["utils/csvParser.ts, formatters.ts"]
    end

    App --> UIComponents
    UIComponents --> CoreServices
    CoreServices --> T
    UIComponents --> U
```

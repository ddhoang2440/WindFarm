# 🌬️ WindFarm HKT — Wind Turbine Monitoring & Real-Time AI Anomaly Detection Console

> **SCADA-Grade Wind Turbine Monitoring & Real-time AI Anomaly Detection Console**  
> A distributed microservices-based wind turbine monitoring system featuring real-time AI anomaly detection, dynamic feature engineering, and observability via Datadog APM and MongoDB Atlas.

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Tech Stack](#-tech-stack)
3. [System Architecture](#-system-architecture)
4. [Installation & Setup Guide](#-installation--setup-guide)
   - [Prerequisites](#1-prerequisites)
   - [Environment Configuration (.env)](#2-environment-configuration-env)
   - [Running the Backend API (Port 8000)](#3-running-the-backend-api-port-8000)
   - [Running the ML Prediction Service (Port 8001)](#4-running-the-ml-prediction-service-port-8001)
   - [Running the Frontend SCADA Console (Port 5173)](#5-running-the-frontend-scada-console-port-5173)
   - [Simulating Telemetry Data (CSV Streaming)](#6-simulating-telemetry-data-csv-streaming)
5. [Project Directory Structure](#-project-directory-structure)
6. [Detailed Documentation (Docs)](#-detailed-documentation-docs)
7. [Team Members & Role Assignments](#-team-members--role-assignments)

---

## 📖 Project Overview

The **WindFarm HKT** system is engineered to solve the critical challenge of continuous condition monitoring and predictive maintenance for wind turbine clusters operating under harsh environmental conditions:
* **IoT Sensor Telemetry Ingestion:** Ingests live operational metrics including wind speed, active power output, ambient temperature, and turbine status flags.
* **Dynamic Feature Engineering:** Continuously computes dynamic time-window features: 6-hour rolling mean wind speed (`wind_speed_roll_mean_6h`), 6-hour power standard deviation (`power_roll_std_6h`), and theoretical power index (`theoretical_power_index`).
* **Real-Time AI Anomaly Detection:** Forwards engineered features to an independent **ML Service** powered by a trained **RandomForest Classifier** to predict operational anomalies (`Normal` vs `Anomaly`) along with risk probability scores.
* **Automated Event Logging:** Automatically logs detected anomalies and operational incidents into **MongoDB Atlas** for historical tracking and auditing.
* **Industrial SCADA Console:** A high-contrast, zero-glare Midnight Blue & Cyan SCADA web interface compatible across Desktop, Tablet, and Mobile devices, featuring an in-browser CSV dataset runner.
* **Cloud Observability & APM:** Synchronizes metrics, latency traces, and critical alert events to the **Datadog** platform.

---

## 🛠️ Tech Stack

### 1. Frontend (SCADA Operator Console)
* **Framework:** [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
* **Build Tool:** [Vite 8](https://vite.dev/) (Instant HMR, highly optimized production bundles)
* **Design System:** Midnight Blue & Industrial Cyan SCADA theme (high contrast, zero neon glare, optimized for mission-critical telemetry monitoring)
* **Iconography:** [Lucide React](https://lucide.dev/) (consistent, crisp digital vector icons)
* **Notifications:** [React-Toastify](https://fkhadra.github.io/react-toastify/)
* **Streaming Engine:** Client-side CSV parser and sequential HTTP stream engine utilizing Web Streams API

### 2. Backend API Gateway & Processing (Port 8000)
* **Framework:** [Python 3.11+](https://www.python.org/) + [FastAPI](https://fastapi.tiangolo.com/)
* **ASGI Server:** [Uvicorn](https://www.uvicorn.org/)
* **Database ODM:** [Beanie ODM](https://beanie-odm.dev/) + [Motor](https://motor.readthedocs.io/) (Asynchronous MongoDB Driver)
* **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/) & Pydantic-Settings
* **Security:** Centralized Bearer Token Authentication Middleware
* **HTTP Client:** [HTTPX](https://www.python-httpx.org/) (Async requests to ML Service)

### 3. Machine Learning Service (Port 8001)
* **Framework:** FastAPI
* **Model:** [Scikit-learn 1.6.1](https://scikit-learn.org/) (`RandomForestClassifier` packaged in `.joblib` format)
* **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Monitoring:** Datadog API Client (`datadog-api-client`, `ddtrace`)

### 4. Database & Cloud Infrastructure
* **Database:** [MongoDB Atlas](https://www.mongodb.com/atlas) (Collections: `telemetry_records`, `event_records`)
* **APM & Monitoring:** [Datadog](https://www.datadoghq.com/) (APM Tracing, Metrics, Alert Events)
* **Public Tunneling:** Ngrok (Remote webhook and multi-service demonstration)

---

## 🏗️ System Architecture

```
+--------------------------------------------------------------------------+
|                       FRONTEND: SCADA DASHBOARD                          |
|  (React 19 + Vite + TypeScript - Port 5173 / Mobile & Desktop SCADA)     |
+--------------------------------------------------------------------------+
       |                                                    |
       | POST /api/v1/telemetry (CSV Streamer)              | GET /api/v1/events
       | Authorization: Bearer <Token>                      | (Auto-poll 3s/5s/10s)
       v                                                    v
+--------------------------------------------------------------------------+
|                         BACKEND SERVICE (FastAPI)                        |
|                               (Port 8000)                                |
|  - Bearer Token Verification                                             |
|  - Ingestion Pipeline: Calculates Rolling Mean 6h, Std 6h, Power Index   |
|  - Stores Raw & Engineered Telemetry into MongoDB                        |
+--------------------------------------------------------------------------+
       |                                                    |
       | POST /predict (7 Features)                         | Store Events
       v                                                    v
+-------------------------------+              +----------------------------+
|      ML SERVICE (FastAPI)     |              |       MONGODB ATLAS        |
|          (Port 8001)          |              |                            |
|  - Random Forest Classifier   |              | - telemetry_records        |
|  - Anomaly Prediction (0/1)   |              | - event_records            |
|  - Alert Event to Datadog     |              +----------------------------+
+-------------------------------+                            |
       |                                                     |
       +--------------------+                                |
                            | Forward Metrics & Logs         |
                            v                                v
               +------------------------------------------------+
               |              DATADOG MONITORING                |
               |      (APM Traces, Alerts, Live Dashboards)     |
               +------------------------------------------------+
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
* **Node.js:** version `18.x` or `20.x+` (with npm or yarn)
* **Python:** version `3.11+`
* **MongoDB:** MongoDB Atlas account or local MongoDB instance (port `27017`)

---

### 2. Environment Configuration (.env)
Create a `.env` file at `backend/.env` with the following configuration:

```env
# MongoDB Atlas Connection
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=windfarm

# API Security Token (Bearer Token Authentication)
API_TOKEN=secret-token-123

# Service Endpoints
ML_SERVICE_URL=http://127.0.0.1:8001
BACKEND_URL=http://127.0.0.1:8000

# Datadog Integration (Optional)
DD_API_KEY=your_datadog_api_key
DD_APP_KEY=your_datadog_app_key
DD_SITE=datadoghq.com
```

---

### 3. Running the Backend API (Port 8000)

1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI Backend server:
   ```bash
   python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   * Interactive Swagger Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * Health Check: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

### 4. Running the ML Prediction Service (Port 8001)

1. Open a second terminal window and activate the virtual environment:
   ```bash
   cd backend
   .\venv\Scripts\activate
   ```
2. Verify that `wind_turbine_anomaly_model.joblib` exists in `backend/ml_service/`.
3. Start the ML Service:
   ```bash
   python -m uvicorn ml_service.main:app --host 127.0.0.1 --port 8001 --reload
   ```
   * ML Service Swagger Documentation: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

---

### 5. Running the Frontend SCADA Console (Port 5173)

1. Open a third terminal window and navigate to `frontend`:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to: [http://localhost:5173](http://localhost:5173)

> **In-App API Configuration:**
> * Click the **"API Settings"** button on the top header.
> * Set Backend URL: `http://127.0.0.1:8000`
> * Set Bearer Token: `secret-token-123` (must match `API_TOKEN` in `.env`)
> * Click **Save Configuration**. The header status will turn green (`ONLINE`).

---

### 6. Simulating Telemetry Data (CSV Streaming)

Two methods are available for streaming test telemetry data:

* **Method 1: In-Browser CSV Streamer (Recommended)**
  1. Click **"Upload & Start CSV Stream"** on the dashboard quick banner.
  2. Drag and drop `backend/turbine_telemetry.csv` into the dropzone.
  3. Select stream speed (`3s/row`, `1s/row`, or `0.5s/row`).
  4. Click **Start CSV Stream** to watch live telemetry transmission and real-time AI anomaly detection.

* **Method 2: Standalone Python Script**
  ```bash
  cd backend
  python stimulator_csv.py
  ```

---

## 📂 Project Directory Structure

```
WindFarm/
├── README.md                          # Primary project documentation
├── docs/                              # In-depth technical documentation
│   ├── README.md                      # Documentation index & guide
│   ├── architecture.md                # System architecture & technical specs
│   ├── functional_specifications.md   # Functional requirements & UX specifications
│   └── plan_and_roadmap.md            # Development roadmap & engineering changelog
│
├── backend/                           # Backend API & Machine Learning services
│   ├── .env                           # Environment configuration
│   ├── requirements.txt               # Python package dependencies
│   ├── stimulator_csv.py              # CSV simulation streaming script
│   ├── turbine_telemetry.csv          # Sample 5-turbine sensor dataset
│   │
│   ├── src/                           # Backend Gateway service (Port 8000)
│   │   ├── main.py                    # FastAPI entry point & CORS configuration
│   │   ├── config/                    # MongoDB Atlas & app settings
│   │   ├── core/                      # Bearer token security middleware
│   │   ├── models/                    # Beanie ODM schemas (Telemetry, Event)
│   │   └── modules/                   # Feature modules
│   │       ├── telemetry/             # Ingestion & statistics endpoints
│   │       └── event/                 # Event management & queries
│   │
│   └── ml_service/                    # AI Anomaly Prediction service (Port 8001)
│       ├── main.py                    # FastAPI /predict endpoint
│       ├── ml_service.py              # Model inference logic
│       ├── datadog_client.py          # Datadog metrics and alert forwarding
│       └── wind_turbine_anomaly_model.joblib # Trained RandomForest model
│
└── frontend/                          # SCADA Dashboard application (Port 5173)
    ├── package.json                   # React 19 + TypeScript package dependencies
    ├── vite.config.ts                 # Vite build configuration
    └── src/
        ├── App.tsx                    # Main SCADA console state orchestrator
        ├── App.css                    # Industrial SCADA stylesheets & responsive layout
        ├── index.css                  # CSS reset & global styling
        │
        ├── components/                # Modular component structure
        │   ├── index.ts               # Master barrel export
        │   ├── layout/                # Header, Footer, connectivity status
        │   ├── dashboard/             # KpiSummary, EventTable, EventFilters
        │   ├── csv-runner/            # CsvStreamerBanner, CsvRunnerModal
        │   └── modals/                # SettingsModal, LogEventModal, ErrorBanner
        │
        ├── services/                  # Decoupled API service layer
        │   ├── index.ts               # Barrel export
        │   ├── config.service.ts      # LocalStorage API config management
        │   ├── telemetry.service.ts   # POST /api/v1/telemetry client
        │   ├── event.service.ts       # Event queries & manual log API
        │   └── health.service.ts      # Backend health ping service
        │
        ├── types/                     # TypeScript data interfaces (WindFarm)
        └── utils/                     # Client-side CSV parser & date formatters
```

---

## 📚 Detailed Documentation (Docs)

For architectural blueprints, data flow diagrams, and full functional specifications, consult the documents in the [`docs/`](file:///c:/WindFarm/docs) directory:

* 📐 [**docs/architecture.md**](file:///c:/WindFarm/docs/architecture.md): Microservices topology (Mermaid diagrams), dynamic feature engineering pipelines, and database schemas.
* 📋 [**docs/functional_specifications.md**](file:///c:/WindFarm/docs/functional_specifications.md): Functional breakdown of SCADA KPI cards, event filters, in-browser CSV runner, and responsive layout behavior.
* 🗺️ [**docs/plan_and_roadmap.md**](file:///c:/WindFarm/docs/plan_and_roadmap.md): Milestone development history, resolved technical challenges, and future roadmap.

---

## 👥 Team Members & Role Assignments

This project was developed by the 3-member **HKT Team**:

| Member | Primary Role | Core Responsibilities |
| :--- | :--- | :--- |
| **Long** | **ML Service & Datadog** | • Built and deployed the **ML Service** API (FastAPI - Port `8001`) for anomaly inference.<br/>• Integrated **Datadog APM**, metrics collection, and automated alert event triggers upon anomaly detection. |
| **Hoa** | **Train Model (Machine Learning)** | • Researched, preprocessed, and engineered features from raw wind turbine sensor telemetry.<br/>• **Trained the AI model (Train Model)** using `RandomForestClassifier` with high accuracy and packaged the model artifact into `.joblib`. |
| **Hoàng** | **Backend & Frontend** | • Designed and developed the **Backend Gateway** (FastAPI - Port `8000`), MongoDB Atlas connection, Bearer token authentication, ingestion pipeline, and dynamic feature engineering (6-hour rolling calculations).<br/>• Developed the complete **Frontend SCADA Console** (React 19 + TypeScript + Vite), in-browser CSV streaming engine, responsive UI design, and modularized code architecture. |

# 🌬️ WindFarm Backend & ML Service (HKT Team)

A distributed microservices architecture for wind turbine condition monitoring, featuring real-time AI anomaly detection and cloud observability via Datadog.

## 🏗️ System Architecture & Responsibilities
The system consists of components developed by the 3 team members:
1. **Backend & Frontend (Hoàng):** Backend Gateway running on port `8000` (FastAPI, MongoDB Atlas, dynamic 6h rolling feature engineering, statistics API) and Frontend SCADA Console (React 19).
2. **ML Service & Datadog (Long):** Running on port `8001` (FastAPI), consumes engineered telemetry from Backend, executes AI model inference for anomaly detection, and forwards metrics and alerts to Datadog.
3. **Train Model AI (Hoa):** Researched and processed wind turbine sensor telemetry, trained the high-accuracy `RandomForestClassifier` model, and packaged the artifact into `wind_turbine_anomaly_model.joblib`.

## 🛠️ Tech Stack
*   **Backend:** Python 3.11+, FastAPI, Beanie (MongoDB ODM), Motor.
*   **ML Service:** Scikit-learn 1.6.1, Pandas, NumPy, Joblib.
*   **Monitoring & APM:** Datadog (Metrics, APM Tracing & Alert Events).
*   **Database:** MongoDB Atlas.
*   **Public Tunneling:** Ngrok.

---

## 🚀 Setup & Execution Guide

### Prerequisites
* **Python 3.11+**
* **MongoDB Atlas** account or local MongoDB instance (port `27017`).

Create a `.env` file in the `backend/` directory:
```env
# Database
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
DATABASE_NAME=windfarm

# Security
API_TOKEN=secret-token-123

# Services
ML_SERVICE_URL=http://127.0.0.1:8001
BACKEND_URL=http://127.0.0.1:8000

# Datadog
DD_API_KEY=your_datadog_api_key
DD_APP_KEY=your_datadog_app_key
DD_SITE=datadoghq.com
```

### Installation
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### Running the Services
1. **Start Backend Gateway (Port 8000):**
   ```bash
   python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   * Swagger Docs: http://127.0.0.1:8000/docs

2. **Start ML Service (Port 8001):**
   ```bash
   python -m uvicorn ml_service.main:app --host 127.0.0.1 --port 8001 --reload
   ```
   * Swagger Docs: http://127.0.0.1:8001/docs

# 🌬️ WindFarm HKT — Hệ Thống Giám Sát & Phát Hiện Bất Thường Tuabin Gió

> **SCADA-Grade Wind Turbine Monitoring & Real-time AI Anomaly Detection Console**  
> Dự án giám sát vận hành các cụm tuabin gió theo kiến trúc Microservices phân tán, tích hợp mô hình Học máy (Machine Learning) phát hiện bất thường theo thời gian thực và quản trị chỉ số qua Datadog APM & MongoDB Atlas.

---

## 📌 Mục Lục
1. [Giới Thiệu Dự Án](#-giới-thiệu-dự-án)
2. [Tech Stack](#-tech-stack)
3. [Kiến Trúc Tổng Quan](#-kiến-trúc-tổng-quan)
4. [Hướng Dẫn Cài Đặt & Chạy Dự Án](#-hướng-dẫn-cài-đặt--chạy-dự-án)
   - [Yêu Cầu Môi Trường](#1-yêu-cầu-môi-trường)
   - [Cấu Hình Biến Môi Trường (.env)](#2-cấu-hình-biến-môi-trường-env)
   - [Khởi Chạy Backend API (Port 8000)](#3-khởi-chạy-backend-api-port-8000)
   - [Khởi Chạy ML Prediction Service (Port 8001)](#4-khởi-chạy-ml-prediction-service-port-8001)
   - [Khởi Chạy Frontend SCADA Console (Port 5173)](#5-khởi-chạy-frontend-scada-console-port-5173)
   - [Mô Phỏng Dữ Liệu Cảm Biến (CSV Streaming)](#6-mô-phỏng-dữ-liệu-cảm-biến-csv-streaming)
5. [Cấu Trúc Thư Mục Dự Án](#-cấu-trúc-thư-mục-dự-án)
6. [Tài Liệu Chi Tiết (Docs)](#-tài-liệu-chi-tiết-docs)
7. [Tác Giả & Đóng Góp](#-tác-giả--đóng-góp)

---

## 📖 Giới Thiệu Dự Án

Hệ thống **WindFarm HKT** được xây dựng nhằm giải quyết bài toán giám sát liên tục tình trạng vận hành của các cụm tuabin điện gió trong điều kiện thực tế khắc nghiệt:
* **Thu thập dữ liệu cảm biến (Telemetry):** Tốc độ gió, công suất phát điện, nhiệt độ môi trường, trạng thái tuabin từ cảm biến IoT/SCADA.
* **Tính toán đặc trưng động (Feature Engineering):** Tính trung bình trượt tốc độ gió 6 giờ (`wind_speed_roll_mean_6h`), độ lệch chuẩn công suất 6 giờ (`power_roll_std_6h`), và chỉ số công suất lý thuyết (`theoretical_power_index`).
* **Phát hiện bất thường tức thì bằng AI:** Gửi đặc trưng sang **ML Service** chạy mô hình **RandomForest Classifier** để phân loại (`Normal` hoặc `Anomaly`) và trả về xác suất rủi ro.
* **Lưu trữ & Tự động ghi nhận sự kiện (Event Logging):** Lưu trữ telemetry và tự động tạo sự kiện cảnh báo vào **MongoDB Atlas** khi phát hiện bất thường.
* **Giao diện SCADA Console chuyên nghiệp:** Giao diện tối ưu theo chuẩn Midnight Blue + Cyan SCADA, tương thích hoàn toàn trên Desktop, Tablet và Mobile, hỗ trợ nạp CSV trực tiếp trên trình duyệt để stream dữ liệu kiểm thử.
* **Giám sát hệ thống (APM & Observability):** Đồng bộ hóa chỉ số và sự kiện quan trọng lên nền tảng **Datadog**.

---

## 🛠️ Tech Stack

### 1. Frontend (Giao diện điều khiển SCADA)
* **Framework:** [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
* **Build Tool:** [Vite 8](https://vite.dev/) (Tối ưu biên dịch siêu tốc, HMR)
* **Design Theme:** Midnight Blue & Industrial Cyan SCADA Design (High contrast, không lóa mắt, tối ưu quan sát dữ liệu công nghiệp)
* **Iconography:** [Lucide React](https://lucide.dev/) (Icon vector SVG kỹ thuật số, đồng bộ)
* **Notifications:** [React-Toastify](https://fkhadra.github.io/react-toastify/)
* **Data Streaming:** Trình phân tích & streamer CSV trực tiếp trên Client bằng Web Streams API

### 2. Backend API Gateway & Processing (Port 8000)
* **Framework:** [Python 3.11+](https://www.python.org/) + [FastAPI](https://fastapi.tiangolo.com/)
* **ASGI Server:** [Uvicorn](https://www.uvicorn.org/)
* **Database ODM:** [Beanie ODM](https://beanie-odm.dev/) + [Motor](https://motor.readthedocs.io/) (Asynchronous MongoDB Driver)
* **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/) & Pydantic-Settings
* **Security:** Bearer Token Authentication Middleware
* **HTTP Client:** [HTTPX](https://www.python-httpx.org/) (Async requests sang ML Service)

### 3. Machine Learning Service (Port 8001)
* **Framework:** FastAPI
* **Model:** [Scikit-learn 1.6.1](https://scikit-learn.org/) (Mô hình huấn luyện `RandomForestClassifier` lưu dạng `.joblib`)
* **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Monitoring:** Datadog API Client (`datadog-api-client`, `ddtrace`)

### 4. Database & Cloud Infrastructure
* **Database:** [MongoDB Atlas](https://www.mongodb.com/atlas) (Collections: `telemetry_records`, `event_records`)
* **APM & Monitoring:** [Datadog](https://www.datadoghq.com/) (Dashboards, Metrics, Alert Events)
* **Public Tunneling:** Ngrok (Hỗ trợ remote webhook / demo)

---

## 🏗️ Kiến Trúc Tổng Quan

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

## 🚀 Hướng Dẫn Cài Đặt & Chạy Dự Án

### 1. Yêu Cầu Môi Trường
* **Node.js:** phiên bản `18.x` hoặc `20.x+` (kèm npm hoặc yarn)
* **Python:** phiên bản `3.11+`
* **MongoDB:** Tài khoản MongoDB Atlas hoặc MongoDB chạy local (cổng `27017`)

---

### 2. Cấu Hình Biến Môi Trường (.env)
Tạo file `.env` tại thư mục `backend/.env` với nội dung mẫu:

```env
# MongoDB Atlas Connection
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=windfarm

# API Security Token (Dùng xác thực Bearer Token)
API_TOKEN=secret-token-123

# Service Endpoints
ML_SERVICE_URL=http://127.0.0.1:8001
BACKEND_URL=http://127.0.0.1:8000

# Datadog Integration (Tùy chọn)
DD_API_KEY=your_datadog_api_key
DD_APP_KEY=your_datadog_app_key
DD_SITE=datadoghq.com
```

---

### 3. Khởi Chạy Backend API (Port 8000)

1. Mở terminal và chuyển vào thư mục `backend`:
   ```bash
   cd backend
   ```
2. Khởi tạo môi trường ảo Python (khuyến nghị):
   ```bash
   python -m venv venv
   # Trên Windows:
   .\venv\Scripts\activate
   # Trên macOS/Linux:
   source venv/bin/activate
   ```
3. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
4. Khởi chạy server FastAPI Backend:
   ```bash
   python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   * Backend Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * Kiểm tra tình trạng: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

### 4. Khởi Chạy ML Prediction Service (Port 8001)

1. Mở một cửa sổ terminal mới và kích hoạt môi trường ảo:
   ```bash
   cd backend
   .\venv\Scripts\activate
   ```
2. Đảm bảo file mô hình `wind_turbine_anomaly_model.joblib` đã nằm trong thư mục `backend/ml_service/`.
3. Chạy ML Service:
   ```bash
   python -m uvicorn ml_service.main:app --host 127.0.0.1 --port 8001 --reload
   ```
   * ML Service Swagger API Docs: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

---

### 5. Khởi Chạy Frontend SCADA Console (Port 5173)

1. Mở một cửa sổ terminal mới và chuyển vào thư mục `frontend`:
   ```bash
   cd frontend
   ```
2. Cài đặt các gói phụ thuộc npm:
   ```bash
   npm install
   ```
3. Khởi chạy giao diện ở chế độ Development:
   ```bash
   npm run dev
   ```
4. Mở trình duyệt truy cập: [http://localhost:5173](http://localhost:5173)

> **Cấu hình kết nối trên giao diện:**
> * Nhấn vào nút **"API Settings"** ở góc trên thanh Header.
> * Điền Backend URL: `http://127.0.0.1:8000`
> * Điền Bearer Token: `secret-token-123` (khớp với giá trị `API_TOKEN` trong file `.env`)
> * Nhấn **Save Configuration**. Trạng thái hệ thống sẽ chuyển sang màu xanh lá (`ONLINE`).

---

### 6. Mô Phỏng Dữ Liệu Cảm Biến (CSV Streaming)

Hệ thống hỗ trợ 2 cách stream dữ liệu kiểm thử:

* **Cách 1: Trực tiếp qua giao diện Web (Khuyến nghị)**
  1. Trên dashboard, nhấn nút **"Khám phá & Nạp CSV"** trên thanh Quick Banner.
  2. Kéo thả file `backend/turbine_telemetry.csv` vào khu vực Dropzone.
  3. Chọn tốc độ stream (`3s/row`, `1s/row`, hoặc `0.5s/row`).
  4. Nhấn **Start CSV Stream** để xem dữ liệu được gửi theo thời gian thực kèm log trực tiếp từ terminal.

* **Cách 2: Chạy Script Python độc lập**
  ```bash
  cd backend
  python stimulator_csv.py
  ```

---

## 📂 Cấu Trúc Thư Mục Dự Án

```
WindFarm/
├── README.md                          # Tài liệu hướng dẫn chính của dự án
├── docs/                              # Thư mục tài liệu chi tiết của dự án
│   ├── README.md                      # Mục lục & hướng dẫn tra cứu tài liệu
│   ├── architecture.md                # Đặc tả kiến trúc hệ thống & thiết kế kỹ thuật
│   ├── functional_specifications.md   # Đặc tả chi tiết các tính năng chức năng
│   └── plan_and_roadmap.md            # Kế hoạch triển khai, tiến độ & roadmap tương lai
│
├── backend/                           # Dịch vụ Backend & Học máy
│   ├── .env                           # Biến môi trường kết nối Database, API Token
│   ├── requirements.txt               # Danh sách thư viện Python cần thiết
│   ├── stimulator_csv.py              # Script mô phỏng nạp telemetry từ CSV
│   ├── turbine_telemetry.csv          # Dữ liệu telemetry mẫu 5 tuabin
│   │
│   ├── src/                           # Backend API chính (Port 8000)
│   │   ├── main.py                    # Điểm khởi chạy FastAPI & CORS
│   │   ├── config/                    # Cấu hình Database MongoDB & Settings
│   │   ├── core/                      # Middleware bảo mật, xác thực Bearer Token
│   │   ├── models/                    # Khai báo cấu trúc Beanie ODM (Telemetry, Event)
│   │   └── modules/                   # Các module xử lý logic nghiệp vụ
│   │       ├── telemetry/             # Xử lý Telemetry Ingestion & Thống kê
│   │       └── event/                 # Quản lý sự kiện Event & Truy vấn MongoDB
│   │
│   └── ml_service/                    # Dịch vụ Trí Tuệ Nhân Tạo (Port 8001)
│       ├── main.py                    # FastAPI endpoint /predict
│       ├── ml_service.py              # Logic load model & dự đoán bất thường
│       ├── datadog_client.py          # Kết nối gửi cảnh báo sang Datadog
│       └── wind_turbine_anomaly_model.joblib # Mô hình RandomForest đã huấn luyện
│
└── frontend/                          # Giao diện SCADA Dashboard (Port 5173)
    ├── package.json                   # Cấu hình dự án React 19 + TypeScript
    ├── vite.config.ts                 # Cấu hình Vite bundler
    └── src/
        ├── App.tsx                    # Component tổng điều phối trạng thái Console
        ├── App.css                    # Toàn bộ Style SCADA, Animations & Responsive
        ├── index.css                  # CSS Variables & Thiết lập Reset gốc
        │
        ├── components/                # Cấu trúc Component được phân chia bài bản
        │   ├── index.ts               # Master Barrel export
        │   ├── layout/                # Header, Footer, Thanh trạng thái kết nối
        │   ├── dashboard/             # KpiSummary, EventTable, EventFilters
        │   ├── csv-runner/            # CsvStreamerBanner, CsvRunnerModal
        │   └── modals/                # SettingsModal, LogEventModal, ErrorBanner
        │
        ├── services/                  # Tầng giao tiếp API tách biệt theo module
        │   ├── index.ts               # Barrel export
        │   ├── config.service.ts      # Quản lý localStorage cấu hình API & Token
        │   ├── telemetry.service.ts   # Gửi dữ liệu cảm biến POST /api/v1/telemetry
        │   ├── event.service.ts       # Lấy danh sách sự kiện & tạo sự kiện thủ công
        │   └── health.service.ts      # Ping kiểm tra sức khỏe server FastAPI
        │
        ├── types/                     # Định nghĩa TypeScript interface (WindFarm)
        └── utils/                     # Xử lý parse CSV client-side & format ngày giờ
```

---

## 📚 Tài Liệu Chi Tiết (Docs)

Để tìm hiểu sâu hơn về quy trình thiết kế, kiến trúc luồng dữ liệu và lộ trình phát triển, vui lòng tham khảo các tài liệu trong thư mục [`docs/`](file:///c:/WindFarm/docs):

* 📐 [**docs/architecture.md**](file:///c:/WindFarm/docs/architecture.md): Sơ đồ kiến trúc chi tiết (Mermaid Diagrams), luồng xử lý Feature Engineering và lược đồ cơ sở dữ liệu.
* 📋 [**docs/functional_specifications.md**](file:///c:/WindFarm/docs/functional_specifications.md): Đặc tả chi tiết từng tính năng: SCADA KPI, Bộ lọc sự kiện, In-Browser CSV Runner, Auto-polling và chế độ Responsive.
* 🎬 [**docs/video_demo_script.md**](file:///c:/WindFarm/docs/video_demo_script.md): Kịch bản quay video demo dự án chuẩn 5-7 phút, phân cảnh chi tiết từng giây, lời thoại thuyết minh (voiceover) và checklist chuẩn bị trước khi bấm máy.
* 🗺️ [**docs/plan_and_roadmap.md**](file:///c:/WindFarm/docs/plan_and_roadmap.md): Lịch sử quá trình thực hiện, các cải tiến UI/UX đã giải quyết và kế hoạch mở rộng tương lai.

---

## 👥 Nhóm Tác Giả & Phân Công Dự Án (HKT Team)
* **Phan Minh Hoàng:** Phụ trách phát triển Kiến trúc Backend Gateway (FastAPI, MongoDB Atlas, Feature Engineering, Ingestion Pipeline).
* **Trương Hữu Long:** Phụ trách Huấn luyện Mô hình Machine Learning (RandomForest), ML Service API và tích hợp giám sát Datadog.
* **HKT Frontend & SCADA Engineering:** Thiết kế và hoàn thiện toàn bộ Giao diện SCADA Dashboard, In-Browser CSV Streaming Engine, tối ưu Responsive đa thiết bị và modular hóa kiến trúc mã nguồn.


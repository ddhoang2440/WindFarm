# 🌬️ WindFarm Monitoring System (HKT Team)

Dự án giám sát hệ thống tuabin gió (WindFarm) theo kiến trúc Microservices, tích hợp Trí tuệ nhân tạo (AI) để phát hiện bất thường và giám sát trực quan qua Datadog.

## 🏗️ Kiến trúc hệ thống
Hệ thống bao gồm 2 server độc lập:
1. **Backend (Hoàng):** Chạy ở cổng `8000`. Nhận dữ liệu, lưu trữ MongoDB, tính toán features phái sinh và cung cấp API thống kê.
2. **ML Service (Long):** Chạy ở cổng `8001`. Nhận dữ liệu từ Backend, chạy mô hình AI (RandomForest) để dự đoán bất thường, và gửi cảnh báo lên Datadog.

## 🛠️ Công nghệ sử dụng
*   **Backend:** Python, FastAPI, Beanie (MongoDB ODM), Motor.
*   **ML Service:** Scikit-learn, Pandas, Joblib.
*   **Monitoring:** Datadog (Metrics & Events).
*   **Database:** MongoDB Atlas.
*   **Public API:** Ngrok.

---

## 🚀 Hướng dẫn cài đặt và chạy dự án

### Bước 1: Chuẩn bị môi trường
Yêu cầu máy tính đã cài đặt **Python 3.11+** và **MongoDB** (hoặc có tài khoản MongoDB Atlas).

Tạo file `.env` ở thư mục gốc với nội dung sau:
```env
# Database
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
DATABASE_NAME=windfarm

# Security
API_TOKEN=secret-token-123

# Services
ML_SERVICE_URL=http://127.0.0.1:8001
BACKEND_URL=https://muricate-lorna-jerkily.ngrok-free.dev/

# Datadog
DD_API_KEY=your_datadog_api_key
DD_APP_KEY=your_datadog_app_key
DD_SITE=ap1.datadoghq.com
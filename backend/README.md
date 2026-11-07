# 🌬️ WindFarm Monitoring System (HKT Team)

Dự án giám sát hệ thống tuabin gió (WindFarm) theo kiến trúc Microservices, tích hợp Trí tuệ nhân tạo (AI) để phát hiện bất thường và giám sát trực quan qua Datadog.

## 🏗️ Kiến trúc hệ thống & Phân công
Hệ thống bao gồm các thành phần do 3 thành viên phụ trách:
1. **Backend & Frontend (Đào Duy Hoàng):** Backend chạy ở cổng `8000` (FastAPI, MongoDB, tính toán features phái sinh, API thống kê) và Frontend SCADA Console (React 19).
2. **ML Service & Datadog (Đào Duy Long):** Chạy ở cổng `8001` (FastAPI), nhận dữ liệu từ Backend, chạy mô hình AI để dự đoán bất thường và gửi cảnh báo lên Datadog.
3. **Train Model AI (Đào Ngọc Hoa):** Xử lý tập dữ liệu cảm biến tuabin gió và huấn luyện mô hình Machine Learning (RandomForest) tối ưu xuất file `.joblib`.

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
BACKEND_URL=http://127.0.0.1:8000

# Datadog
DD_API_KEY=your_datadog_api_key
DD_APP_KEY=your_datadog_app_key
DD_SITE=    
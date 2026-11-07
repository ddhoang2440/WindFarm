# 🗺️ Kế Hoạch & Tiến Độ Triển Khai (Plan & Roadmap) — WindFarm HKT

Tài liệu này ghi nhận toàn bộ quá trình phát triển, các giai đoạn đã hoàn thành, danh mục các vấn đề kỹ thuật và giao diện đã được giải quyết, cùng với lộ trình phát triển tương lai của dự án **WindFarm HKT**.

---

## 1. Tổng Quan Quá Trình Phát Triển

Dự án được triển khai theo mô hình Agile lặp nhiều vòng (Iterative Development) với mục tiêu đưa một hệ thống giám sát tuabin gió từ ý tưởng ban đầu trở thành một trung tâm điều khiển SCADA đạt chuẩn công nghiệp, có khả năng phát hiện bất thường bằng Trí Tuệ Nhân Tạo.

```
[Giai Đoạn 1: Nền Tảng Backend] ➔ [Giai Đoạn 2: Tích Hợp Machine Learning] ➔ [Giai Đoạn 3: Thiết Kế Chuẩn SCADA] ➔ [Giai Đoạn 4: Tái Cấu Trúc Modular] ➔ [Giai Đoạn 5: Tối Ưu Responsive & Hoàn Thiện]
```

---

## 2. Chi Tiết Các Giai Đoạn Đã Hoàn Thành

### 📍 Giai Đoạn 1: Thiết Kế Nền Tảng Backend & Lưu Trữ Dữ Liệu
* **Mục tiêu:** Xây dựng máy chủ nhận dữ liệu telemetry, tính toán đặc trưng và lưu trữ MongoDB.
* **Kết quả đạt được:**
  - Khởi tạo kiến trúc FastAPI Gateway ở cổng `8000`.
  - Kết nối cơ sở dữ liệu MongoDB Atlas thông qua Beanie ODM và Motor bất đồng bộ.
  - Xây dựng pipeline xử lý đặc trưng phái sinh: tính trung bình trượt 6 giờ tốc độ gió (`wind_speed_roll_mean_6h`), độ lệch chuẩn công suất (`power_roll_std_6h`), và chỉ số công suất lý thuyết (`theoretical_power_index`).
  - Thiết lập middleware bảo mật kiểm tra Bearer Token trên toàn bộ các endpoint nhạy cảm.

### 📍 Giai Đoạn 2: Tích Hợp Dịch Vụ Machine Learning & Datadog APM
* **Mục tiêu:** Phát hiện bất thường tự động dựa trên mô hình học máy và giám sát hạ tầng.
* **Kết quả đạt được:**
  - Huấn luyện mô hình phân loại `RandomForestClassifier` đạt độ chính xác cao trên tập dữ liệu telemetry cảm biến tuabin gió.
  - Đóng gói mô hình thành file `.joblib` và xây dựng microservice độc lập `ML Service` chạy ở cổng `8001`.
  - Tích hợp gọi REST nội bộ không đồng bộ giữa Backend Gateway và ML Service qua HTTPX.
  - Gửi các sự kiện bất thường tự động sang nền tảng Datadog APM thông qua Datadog API Client.

### 📍 Giai Đoạn 3: Thiết Kế Lại Giao Diện Theo Chuẩn SCADA Công Nghiệp
* **Mục tiêu:** Xóa bỏ phong cách giao diện demo hào nhoáng, chuyển dịch sang giao diện giám sát vận hành thực tế.
* **Kết quả đạt được:**
  - Áp dụng bộ màu **Midnight Blue + Cyan SCADA** (`#060b17`, `#0b1426`, `#0891b2`, `#38bdf8`).
  - Triệt tiêu toàn bộ hiệu ứng glow neon gây mỏi mắt, ưu tiên độ tương phản và khả năng phát hiện bất thường ngay lập tức.
  - Thay thế toàn bộ emoji ký tự thông thường bằng thư viện icon vector kỹ thuật số chuyên nghiệp [Lucide React](https://lucide.dev/).
  - Bổ sung công cụ nạp và stream file CSV trực tiếp trên trình duyệt (`In-Browser CSV Runner`).

### 📍 Giai Đoạn 4: Tái Cấu Trúc & Modular Hóa Mã Nguồn (Refactoring)
* **Mục tiêu:** Tách các file code đơn lẻ thành các module nhỏ theo tính năng để dễ dàng bảo trì và mở rộng.
* **Kết quả đạt được:**
  - Tách tầng dịch vụ `services/` thành các file độc lập: `config.service.ts`, `telemetry.service.ts`, `event.service.ts`, `health.service.ts` kèm barrel export `index.ts`.
  - Tách tầng giao diện `components/` thành các thư mục tính năng rõ ràng:
    - [`components/layout/`](file:///c:/WindFarm/frontend/src/components/layout): Header, Footer, Thanh trạng thái.
    - [`components/dashboard/`](file:///c:/WindFarm/frontend/src/components/dashboard): KpiSummary, EventTable, EventFilters.
    - [`components/csv-runner/`](file:///c:/WindFarm/frontend/src/components/csv-runner): CsvStreamerBanner, CsvRunnerModal.
    - [`components/modals/`](file:///c:/WindFarm/frontend/src/components/modals): SettingsModal, LogEventModal, ErrorBanner.
  - Xóa bỏ toàn bộ các file lộn xộn ở root `components/`, đảm bảo dự án ngăn nắp.

### 📍 Giai Đoạn 5: Tối Ưu Hóa Trải Nghiệm Người Dùng & Responsive Đa Thiết Bị
* **Mục tiêu:** Hoàn thiện từng chi tiết theo danh sách phản hồi thực tế của người dùng.
* **Kết quả đạt được:** (Xem chi tiết bảng tổng kết bên dưới).

---

## 3. Bảng Tổng Hợp Các Yêu Cầu Cải Tiến Đã Giải Quyết

Dưới đây là bảng đối chiếu chi tiết các phản hồi thực tế và giải pháp kỹ thuật đã thực hiện:

| Khu vực | Vấn đề được phản hồi | Giải pháp kỹ thuật đã xử lý | Kết quả |
| :--- | :--- | :--- | :---: |
| **Header** | Chiều cao header hơi dày, chiếm nhiều diện tích dọc | Giảm `min-height` từ `48px` xuống `42px`, tinh chỉnh padding từ `8px 24px` xuống `6px 20px`, giảm kích thước logo icon từ `28px` xuống `26px`. | ✅ Đạt |
| **Summary Cards** | Khoảng cách giữa số liệu KPI và dòng mô tả quá sát nhau | Tăng `margin` của `.kpi-value-row` lên `10px 0 4px 0`, tăng `margin-top` của `.kpi-meta-row` lên `18px` và padding lên `12px`. | ✅ Đạt |
| **Classification** | Viền đỏ xuất hiện khi số lượng bất thường bằng 0 gây hiểu lầm | Thiết lập điều kiện viền động `anomalyCount > 0 ? "card-anomaly-border" : ""`. Khi `anomaly == 0`, hiển thị viền xanh SCADA tiêu chuẩn và nhãn `"100% Normal"`. | ✅ Đạt |
| **CSV Streamer** | Cần hiển thị trạng thái file CSV đã chọn | Tích hợp chip trạng thái chi tiết trên thanh Banner: hiển thị tên file, số dòng, tiến trình stream (`Đang stream: x/y` hoặc `Sẵn sàng stream`). | ✅ Đạt |
| **Search Input** | Placeholder ô tìm kiếm bị tối, khó đọc trên nền SCADA | Tăng độ sáng placeholder lên `#e2e8f0` với `opacity: 1`, đảm bảo đọc rõ ràng ở mọi góc nhìn. | ✅ Đạt |
| **SCADA Table** | Cần phân biệt dòng chẵn/lẻ và thêm hiệu ứng hover | Bổ sung Zebra Striping với nền `#080f1e` (lẻ) và `#0d1a31` (chẵn); hiệu ứng hover chuyển mượt sang `#152747`. Nổi bật dòng bất thường với viền đỏ `4px solid #ef4444`. | ✅ Đạt |
| **Latest Event** | Cần hiển thị đầy đủ mô tả sự kiện | Tích hợp tooltip kính mờ hiển thị tức thì khi hover kèm nút bấm `"Chi tiết"` / `"Thu gọn"` để mở rộng trực tiếp dòng mô tả. | ✅ Đạt |
| **Pagination Bar** | Nút bấm phân trang bị rớt dòng, vỡ layout trên mobile | Tái cấu trúc thành 2 tầng trên màn hình $\le 640\text{px}$, ẩn nhãn chữ và chỉ giữ lại icon `[«] [<] Page 1/1 [>] [»]`, khóa `flex-wrap: nowrap`. | ✅ Đạt |
| **CSV Modal Header** | Nút đóng `[X]` bị rớt xuống dưới tiêu đề trên điện thoại | Đặt `flex-wrap: nowrap !important` trên header modal, neo cố định nút `[X]` ở góc trên bên phải. | ✅ Đạt |
| **Interval Chips** | Các nút chọn tốc độ stream bị dãn khoảng cách kỳ quặc | Gom các chip `[3s/row]`, `[1s/row]`, `[0.5s/row]` vào cụm `.interval-chips-group` dạng segmented control gắn kết với `gap: 3px`. | ✅ Đạt |
| **Lỗi Mạng UI** | Hộp lỗi màu trắng `http://127.0.0.1:8000` đè lên giao diện | Loại bỏ banner lỗi choán chỗ, thay thế bằng nhãn đỏ `OFFLINE` tinh tế trên thanh Header và thông báo Toast thông minh. | ✅ Đạt |

---

## 4. Ma Trận Kiểm Thử Kỹ Thuật (Testing & Verification Matrix)

* **Biên dịch Frontend (Vite + TypeScript):**
  - Lệnh kiểm tra: `npm run build` (`tsc -b && vite build`)
  - Kết quả: **2082 modules transformed**, built thành công trong **3.06s**, **0 lỗi, 0 cảnh báo**.
* **Kiểm tra Tương thích Thiết bị (Responsive Testing):**
  - Desktop màn hình lớn ($1920\times 1080$, $1440\times 900$): Hiển thị lưới SCADA 3 cột chuẩn mực, các thanh điều khiển dàn trải cân đối.
  - Laptop / Tablet ($1024\times 768$, $768\times 1024$): Grid KPI tự động thích ứng 2 hoặc 1 cột, modal CSV runner tự co giãn mượt mà.
  - Mobile Phones ($375\times 667$, $414\times 896$, $360\times 740$): Thanh phân trang tự co gọn dạng icon, dropzone modal thu nhỏ padding, toàn bộ các bảng có thanh trượt ngang không bị bể layout.

---

## 5. Lộ Trình Phát Triển Tương Lai (Future Roadmap)

### 🚀 Giai Đoạn 6: Nâng Cấp Thời Gian Thực (Real-Time Push)
* **WebSocket Ingestion:** Bổ sung kết nối WebSocket hai chiều (`ws://`) giữa Backend và Frontend để thay thế cơ chế Auto-polling HTTP, giảm tải băng thông và độ trễ xuống dưới `50ms`.
* **Biểu Đồ Sóng Đo Lường (Real-Time Telemetry Waveforms):** Tích hợp biểu đồ Canvas/SVG theo dõi trực tiếp đường cong công suất thực tế so với đường cong công suất danh định (Power Curve).

### 🚀 Giai Đoạn 7: Mở Rộng Quản Trị Đa Trang Trại Gió (Multi-Farm Management)
* **Bản Đồ Địa Lý Tương Tác (GIS Map):** Tích hợp bản đồ vệ tinh hiển thị vị trí các trang trại gió (Bình Thuận, Ninh Thuận, Bạc Liêu,...) với trạng thái đèn LED xanh/đỏ cho từng tuabin.
* **Phân Quyền Vai Trò (Role-Based Access Control — RBAC):** Phân chia quyền hạn kỹ sư vận hành (Operator), chuyên viên bảo trì (Maintenance Technician) và quản lý hệ thống (Administrator).

### 🚀 Giai Đoạn 8: Giải Thích Mô Hình AI (Explainable AI — XAI)
* **SHAP / LIME Value Integration:** Khi mô hình AI dự đoán một điểm bất thường, hệ thống tự động xuất biểu đồ đóng góp của từng đặc trưng (ví dụ: do tốc độ gió vượt ngưỡng hay do nhiệt độ ổ trục tăng bất thường) giúp kỹ sư xác định chính xác nguyên nhân gốc rễ (Root Cause Analysis).


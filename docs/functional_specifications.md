# 📋 Đặc Tả Chức Năng (Functional Specifications) — WindFarm HKT

Tài liệu này mô tả chi tiết các yêu cầu chức năng, hành vi người dùng, giao diện và logic xử lý của từng phân hệ trên bảng điều khiển **WindFarm HKT SCADA Console**.

---

## 1. Màn Hình Tổng Quan & Thẻ Chỉ Số KPI (SCADA KPI Summary)

Khu vực trên cùng của giao diện bao gồm 3 thẻ KPI theo chuẩn hiển thị thông số công nghiệp SCADA:

### 1.1. Thẻ 1: Tổng Số Sự Kiện Đã Ghi Nhận (Total Logged Events)
* **Dữ liệu hiển thị:** Tổng số lượng bản ghi sự kiện hiện có trong cơ sở dữ liệu MongoDB Atlas.
* **Thời gian cập nhật:** Hiển thị mốc thời gian cập nhật gần nhất (`Updated: HH:MM:SS`).
* **Hành vi:** Khi Backend nhận thêm sự kiện mới qua stream hoặc ghi nhận thủ công, số đếm tự động cập nhật ngay chu kỳ auto-poll tiếp theo.

### 1.2. Thẻ 2: Phân Loại Sự Kiện (Event Classification — Anomaly / Normal)
* **Dữ liệu hiển thị:**
  - Số lượng bản ghi được phân loại là bất thường (`anomalies`).
  - Số lượng bản ghi vận hành bình thường (`normal`).
  - Tỉ lệ phân loại của mô hình `RandomForest ML Model`.
* **Quy chuẩn hiển thị viền cảnh báo:**
  - **Khi `anomaly == 0`:** Hiển thị viền xanh cyan công nghiệp tiêu chuẩn, huy hiệu màu xanh lục `"100% Normal"` với icon `CheckCircle2`. **Không hiển thị viền đỏ gây hiểu nhầm khi hệ thống đang an toàn.**
  - **Khi `anomaly > 0`:** Tự động kích hoạt viền đỏ cảnh báo nổi bật (`.card-anomaly-border` — `1.5px solid #ef4444`), số đếm đổi sang màu đỏ `text-danger`, kèm huy hiệu cảnh báo nguy cấp `"X Anomalies"` với icon `AlertTriangle`.

### 1.3. Thẻ 3: Sự Kiện Gần Nhất (Latest Event)
* **Dữ liệu hiển thị:**
  - Huy hiệu phân loại của sự kiện mới nhất (`ANOMALY` màu đỏ hoặc `NORMAL` màu xanh lục).
  - Định danh tuabin và mã sự kiện: `Turbine #X • #EventID`.
  - Mốc thời gian kết thúc sự kiện định dạng chuẩn quốc tế `YYYY-MM-DD HH:mm:ss`.
* **Cơ chế xem mô tả đầy đủ:**
  - **Rút gọn thông minh:** Văn bản mô tả dài được tự động rút gọn với dấu `...`.
  - **Tooltip SCADA tức thì:** Khi di chuột qua mô tả, một tooltip kính mờ hiển thị toàn văn nội dung mô tả sự kiện.
  - **Nút Xem chi tiết / Thu gọn:** Cho phép người dùng bấm trực tiếp vào nút `"Chi tiết"` hoặc `"Thu gọn"` để mở rộng dòng văn bản mà không cần chuyển trang.

---

## 2. Trình Nạp & Giả Lập Dữ Liệu Cảm Biến (In-Browser CSV Streamer)

Hệ thống cung cấp công cụ giả lập stream dữ liệu telemetry chuyên dụng ngay trên trình duyệt mà không cần cài đặt thêm phần mềm phụ trợ.

### 2.1. Thanh Trạng Thái Nhanh (CSV Streamer Banner)
* **Biểu tượng:** Icon tên lửa `Rocket` phong cách SCADA.
* **Huy hiệu trạng thái file đã nạp:**
  - **Chưa nạp file:** Hiển thị chip màu xám `"Trạng thái: Chưa nạp file CSV (Nhấn để chọn và chạy)"`.
  - **Đã nạp file:** Hiển thị tên file đã chọn, số lượng dòng dữ liệu (ví dụ: `File đã chọn: turbine_telemetry.csv (100 dòng dữ liệu)`).
  - **Huy hiệu luồng stream:** Hiển thị trạng thái đang chạy (`Đang stream: 24/100`) kèm icon tia chớp `Zap` hoặc trạng thái sẵn sàng (`Sẵn sàng stream`).
* **Nút bấm kích hoạt:** Nút mở modal trung tâm điều khiển stream.

### 2.2. Modal Điều Khiển CSV Runner (CsvRunnerModal)
Bố cục 2 cột chuyên nghiệp:
* **Cột Trái (Điều khiển & Nạp dữ liệu):**
  - **Vùng Kéo Thả (Dropzone):** Hỗ trợ kéo thả trực tiếp file `.csv` hoặc bấm nút `"Select CSV File from Computer..."`.
  - **Client-Side CSV Parser:** Tự động bóc tách các cột dữ liệu `asset_id`, `wind_speed`, `power_output`, `ambient_temp`, `status_type_id`, kiểm tra định dạng và báo lỗi nếu dữ liệu không đúng chuẩn.
  - **Thanh Công Cụ Thực Thi:**
    - Nút **Start CSV Stream** / **Pause Stream**: Khởi động hoặc tạm dừng gửi từng dòng dữ liệu.
    - Nút **Reset Stream**: Đưa tiến trình về dòng đầu tiên.
  - **Bộ Chọn Tốc Độ Stream (Stream Interval):**
    - Cụm chip segmented control gắn kết: `3s / row`, `1s / row`, `0.5s / row`.
    - Cho phép thay đổi tốc độ stream ngay trong lúc đang truyền dữ liệu.
  - **Thẻ Tiến Độ (Progress Card):**
    - Thanh tiến trình phần trăm đồ họa (`% completed`).
    - Số dòng đã gửi thành công / tổng số dòng.
    - Huy hiệu trạng thái: `Ready`, `Streaming...`, `Paused`, `Completed`.
* **Cột Phải (Live Terminal Log):**
  - Header hiển thị endpoint đang gửi: `POST /api/v1/telemetry` và số lượng log.
  - Màn hình terminal nền tối giả lập console công nghiệp với font chữ `JetBrains Mono`.
  - Phân loại màu log:
    - `[INFO]`: Màu xanh dương cyan.
    - `[NORMAL]`: Màu xanh lục (kết quả dự đoán an toàn).
    - `[ANOMALY]`: Màu đỏ cảnh báo kèm xác suất rủi ro (ví dụ: `🚨 Anomaly Detected (p=96.4%)`).
    - `[ERROR]`: Màu đỏ đậm khi có lỗi kết nối mạng hoặc lỗi server.
  - Nút **Clear Logs** để làm sạch màn hình terminal.

---

## 3. Quản Lý Sự Kiện & Bộ Lọc Dữ Liệu (Event Table & Filters)

### 3.1. Thanh Tìm Kiếm & Bộ Lọc Nhanh (EventFilters)
* **Tìm kiếm toàn văn (Search Input):**
  - Hỗ trợ gõ từ khóa tìm theo mô tả sự kiện, mã tuabin, mã biến cố.
  - Placeholder màu sáng rõ nét (`#e2e8f0`), đạt độ tương phản tối đa trên nền tối SCADA.
  - Tự động hiển thị nút xóa nhanh `[X]` khi người dùng đã nhập ký tự.
* **Bộ lọc tuabin (Filter by Turbine):** Dropdown tự động tổng hợp danh sách các ID tuabin duy nhất hiện có trong dữ liệu (ví dụ: `Turbine #1`, `Turbine #2`,...).
* **Bộ lọc phân loại (Filter by Classification):**
  - Lọc nhanh các trạng thái: `Tất cả`, `ANOMALY (Bất thường)`, `NORMAL (Bình thường)`, `WARNING`, `INFO`.
* **Nút Reset Filters:** Đưa tất cả bộ lọc về mặc định chỉ với một cú nhấp chuột.
* **Nút Ghi Nhận Thủ Công (Log Event):** Mở modal ghi nhận sự kiện khẩn cấp từ kỹ sư vận hành.

### 3.2. Bảng Dữ Liệu SCADA (EventTable)
* **Thiết kế phân biệt dòng chẵn / lẻ (Zebra Striping):**
  - Dòng lẻ: Nền `#080f1e`.
  - Dòng chẵn: Nền `#0d1a31`.
  - Hiệu ứng rê chuột (Hover): Nổi bật với nền `#152747` giúp người xem không bị lệch dòng khi đối chiếu dữ liệu nhiều cột.
* **Nổi bật dòng bất thường (Anomaly Row Highlight):**
  - Các dòng có nhãn `ANOMALY` tự động nhận nền đỏ cảnh báo trong suốt (`rgba(239, 68, 68, 0.12)`) cùng vạch chỉ báo đỏ cố định bên trái (`border-left: 4px solid #ef4444`).
* **Các cột dữ liệu tiêu chuẩn:**
  1. `EVENT ID`: Mã định danh sự kiện (Font monospace).
  2. `TURBINE ID`: Huy hiệu số hiệu tuabin có icon quạt gió.
  3. `CLASSIFICATION`: Huy hiệu trạng thái có icon trực quan (`AlertTriangle` cho Anomaly, `CheckCircle2` cho Normal).
  4. `EVENT START`: Mốc thời gian bắt đầu (Monospace).
  5. `EVENT END`: Mốc thời gian kết thúc (Monospace).
  6. `DESCRIPTION`: Toàn văn mô tả chi tiết sự kiện kèm tooltip đầy đủ.

### 3.3. Phân Trang Tương Thích Responsive (Responsive Pagination)
* **Desktop ($\ge 640\text{px}$):**
  - Phía trái: Lựa chọn số hàng hiển thị (`10`, `20`, `50`, `100` dòng/trang) và thông báo khoảng hiển thị (`Showing 1–10 of 45 events`).
  - Phía phải: Đầy đủ các nút điều hướng kèm văn bản: `[« First] [< Prev] Page 1 / 5 [Next >] [Last »]`.
* **Mobile & Màn Hình Nhỏ ($\le 640\text{px}$):**
  - Tự động chuyển thành bố cục 2 tầng dọc.
  - Tầng 1: Số hàng mỗi trang căn trái, số lượng sự kiện căn phải.
  - Tầng 2: Cụm điều hướng căn giữa với các nút icon tối giản `[ « ] [ < ] Page 1 / 5 [ > ] [ » ]`, đảm bảo không bao giờ bị tràn dòng hay vỡ giao diện.

---

## 4. Modal Ghi Nhận Sự Kiện Thủ Công (LogEventModal)
* Cho phép kỹ sư vận hành ghi nhận biến cố bảo trì, hỏng hóc hoặc kiểm tra định kỳ:
  - Trường `Asset ID`: Chọn tuabin cần ghi nhận sự kiện.
  - Trường `Event ID`: Sinh mã tự động ngẫu nhiên theo chuẩn số nguyên.
  - Trường `Classification`: Lựa chọn `anomaly`, `normal`, `warning`, `maintenance`.
  - Trường `Event Start` & `Event End`: Lựa chọn ngày giờ chính xác qua bộ chọn datetime.
  - Trường `Description`: Ô nhập liệu chi tiết nguyên nhân, vị trí phát sinh sự cố.
* Dữ liệu được gửi qua `POST /api/v1/events` có xác thực Bearer Token và lưu ngay vào MongoDB.

---

## 5. Cấu Hình Hệ Thống & Bảo Mật (SettingsModal & Connectivity)
* **Cấu hình địa chỉ Backend:** Cho phép thay đổi linh hoạt URL máy chủ Backend (mặc định `http://127.0.0.1:8000` hoặc domain Ngrok).
* **Bearer Token:** Nhập mã bí mật ủy quyền truy cập API.
* **Auto-Refresh Toggle:** Bật/tắt chế độ tự động đồng bộ sự kiện định kỳ (hỗ trợ các chu kỳ `3s`, `5s`, `10s`).
* **Lưu trữ cục bộ (LocalStorage):** Toàn bộ cấu hình được lưu tại trình duyệt của người dùng, không bị mất đi khi tải lại trang.
* **Chỉ báo Ngoại tuyến (Offline Indicator):** Khi Backend gặp sự cố hoặc sai token, thanh Header hiển thị nhãn đỏ `OFFLINE` tinh tế, không làm che khuất hay đẩy lệch giao diện làm việc.


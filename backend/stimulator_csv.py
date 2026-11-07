import httpx
import time
import csv

# Cấu hình API
API_URL = "https://muricate-lorna-jerkily.ngrok-free.dev/api/v1/telemetry"
TOKEN = "EnoDncjaHecKAaU_4ev-UA7_oRhMamg9mW1vEDqwfzI"

def send_data_from_csv(file_path):
    print(f"--- Bắt đầu gửi dữ liệu từ file {file_path} ---")
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Chuyển đổi time_stamp sang chuẩn ISO 8601
            time_stamp = row['time_stamp'].replace(' ', 'T') + 'Z'
            
            # Tạo payload JSON
            payload = {
                "asset_id": int(row['asset_id']),
                "time_stamp": time_stamp,
                "wind_speed": float(row['wind_speed']),
                "power_output": float(row['power_output']),
                "ambient_temp": float(row['ambient_temp']),
                "status_type_id": int(row['status_type_id'])
            }
            
            try:
                response = httpx.post(
                    API_URL, 
                    json=payload, 
                    headers={
                        "Authorization": f"Bearer {TOKEN}",
                        "ngrok-skip-browser-warning": "1" # Bắt buộc phải có khi dùng Ngrok
                    },
                    timeout=15.0 # Tăng thời gian chờ
                )
                print(f"Đã gửi dòng {row['id']}: Gió {payload['wind_speed']}m/s -> Status: {response.status_code}")
            except Exception as e:
                print(f"Lỗi gửi dòng {row['id']}: {e}")
            
            time.sleep(3) # Đợi 1 giây

if __name__ == "__main__":
    send_data_from_csv("turbine_telemetry.csv")
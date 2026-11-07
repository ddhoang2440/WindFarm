import httpx
import time
import csv

# API Configuration
API_URL = "https://muricate-lorna-jerkily.ngrok-free.dev/api/v1/telemetry"
TOKEN = "EnoDncjaHecKAaU_4ev-UA7_oRhMamg9mW1vEDqwfzI"

def send_data_from_csv(file_path):
    print(f"--- Starting data stream from file {file_path} ---")
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Format time_stamp to ISO 8601
            time_stamp = row['time_stamp'].replace(' ', 'T') + 'Z'
            
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
                        "ngrok-skip-browser-warning": "1"
                    },
                    timeout=15.0
                )
                print(f"Sent row #{row['id']}: Wind {payload['wind_speed']} m/s -> Status: {response.status_code}")
            except Exception as e:
                print(f"Error sending row #{row['id']}: {e}")
            
            time.sleep(3)

if __name__ == "__main__":
    send_data_from_csv("turbine_telemetry.csv")

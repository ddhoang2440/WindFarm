from datetime import datetime, timezone, timedelta
import time
import httpx
from config.settings import settings
from models.telemetry import TelemetryInput, TelemetryRecord
from models.event import EventRecord

async def calculate_derived_features(asset_id: int, current_time):
    """
    Calculate 3 derived features using MongoDB Aggregation.
    """
    six_hours_ago = current_time - timedelta(hours=6)
    
    # 1. MongoDB aggregation for rolling mean and std
    pipeline = [
        {"$match": {
            "asset_id": asset_id,
            "time_stamp": {"$gte": six_hours_ago}
        }},
        {"$group": {
            "_id": None,
            "wind_speed_roll_mean_6h": {"$avg": "$wind_speed"},
            "power_roll_std_6h": {"$stdDevPop": "$power_output"}
        }}
    ]
    
    result = await TelemetryRecord.aggregate(pipeline).to_list()
    
    # If not enough data in the 6h window
    if not result:
        return {
            "wind_speed_roll_mean_6h": 0.0,
            "power_roll_std_6h": 0.0,
            "theoretical_power_index": 0.0
        }
    
    stats = result[0]
    theoretical_power_index = stats["wind_speed_roll_mean_6h"] * 10.0 
    
    return {
        "wind_speed_roll_mean_6h": round(stats["wind_speed_roll_mean_6h"], 4),
        "power_roll_std_6h": round(stats["power_roll_std_6h"], 4),
        "theoretical_power_index": round(theoretical_power_index, 4)
    }

async def process_telemetry(data: TelemetryInput):
    # 1. Save raw telemetry to DB
    record = TelemetryRecord(**data.model_dump())
    await record.insert()
    print(f"[BACKEND] Saved telemetry for turbine {data.asset_id}")
    
    # 2. Compute 3 derived features
    derived = await calculate_derived_features(data.asset_id, data.time_stamp)
    
    # 3. Form 7-feature payload for ML model
    ml_payload = {
        "asset_id": data.asset_id,
        "time_stamp": data.time_stamp.isoformat(),
        "wind_speed": data.wind_speed,
        "power_output": data.power_output,
        "ambient_temp": data.ambient_temp,
        "status_type_id": data.status_type_id,
        "wind_speed_roll_mean_6h": derived["wind_speed_roll_mean_6h"],
        "power_roll_std_6h": derived["power_roll_std_6h"],
        "theoretical_power_index": derived["theoretical_power_index"],
    }
    
    # 4. Call ML Service
    ml_result = {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/predict",
                json=ml_payload,
                headers={"ngrok-skip-browser-warning": "1"},
                timeout=10.0
            )
            ml_result = response.json()
            print(f"[BACKEND] ML returned: {ml_result}")
        except Exception as e:
            print(f"[BACKEND] Error calling ML: {e}")
    
    # 5. Save Event for BOTH normal and anomaly
    is_anomaly = bool(ml_result.get("is_anomaly", False)) if isinstance(ml_result, dict) else False
    event_label = "anomaly" if is_anomaly else "normal"
    
    if is_anomaly:
        desc = f"ML detected anomaly. Wind: {data.wind_speed} m/s, Power: {data.power_output} kW"
    else:
        desc = f"Normal operation. Wind: {data.wind_speed} m/s, Power: {data.power_output} kW"
    
    event_id = int(time.time() * 1000) % 1000000000
    event_record = EventRecord(
        event_id=event_id,
        asset_id=data.asset_id,
        event_label=event_label,
        event_start=data.time_stamp,
        event_end=datetime.now(timezone.utc),
        event_description=desc
    )
    await event_record.insert()
    print(f"[BACKEND] Recorded Event ({event_label}) ID #{event_id} into MongoDB")
    
    return {
        "record": record,
        "ml_result": ml_result,
        "event": event_record
    }

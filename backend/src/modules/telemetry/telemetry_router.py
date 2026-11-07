from fastapi import APIRouter, Depends
from core.security import verify_token
from models.telemetry import TelemetryInput
from modules.telemetry.telemetry_service import process_telemetry

router = APIRouter(prefix="/api/v1/telemetry", tags=["Telemetry"])

@router.post("", dependencies=[Depends(verify_token)])
async def post_telemetry(payload: TelemetryInput):
    # Gọi service thật
    result = await process_telemetry(payload)
    record = result["record"]
    ml_result = result.get("ml_result", {})
    event = result.get("event")
    return {
        "status": "success",
        "id": str(record.id),
        "is_anomaly": ml_result.get("is_anomaly", False),
        "anomaly_probability": ml_result.get("anomaly_probability"),
        "event_id": event.event_id if event else None,
        "event_label": event.event_label if event else None,
    }

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from beanie import Document

# Validates raw telemetry input payload
class TelemetryInput(BaseModel):
    asset_id: int
    time_stamp: datetime
    wind_speed: float
    power_output: float
    ambient_temp: float
    status_type_id: int

# Persisted MongoDB Document
class TelemetryRecord(Document, TelemetryInput):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "telemetry"

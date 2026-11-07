from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from core.security import verify_token
from models.event import EventInput, EventRecord
from modules.event.event_service import process_event

router = APIRouter(prefix="/api/v1/events", tags=["Events"])

@router.post("", dependencies=[Depends(verify_token)])
async def log_event(payload: EventInput):
    record = await process_event(payload)
    return {"status": "success", "event_id": payload.event_id, "id": str(record.id)}

@router.get("", dependencies=[Depends(verify_token)])
async def get_events(
    asset_id: Optional[int] = Query(None, description="Filter by turbine asset ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events")
):
    query = EventRecord.find(EventRecord.asset_id == asset_id) if asset_id is not None else EventRecord.find_all()
    records = await query.sort(-EventRecord.event_start).limit(limit).to_list()
    return [
        {
            "id": str(r.id),
            "event_id": r.event_id,
            "asset_id": r.asset_id,
            "event_label": r.event_label,
            "event_start": r.event_start.isoformat() if isinstance(r.event_start, datetime) else str(r.event_start),
            "event_end": r.event_end.isoformat() if isinstance(r.event_end, datetime) else str(r.event_end),
            "event_description": r.event_description,
            "created_at": r.created_at.isoformat() if isinstance(r.created_at, datetime) else str(r.created_at) if r.created_at else None,
        }
        for r in records
    ]

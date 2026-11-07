from models.event import EventInput, EventRecord

async def process_event(data: EventInput):
    # 1. Save to DB
    record = EventRecord(**data.model_dump())
    await record.insert()
    print(f"[BACKEND] Saved Event #{data.event_id} into DB")
    
    # 2. Datadog notification (optional)
    
    return record

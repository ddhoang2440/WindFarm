import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config.settings import settings
from models.telemetry import TelemetryRecord
from models.event import EventRecord

async def init_db():
    print("[BACKEND] Connecting to MongoDB...")
    # THÊM tlsCAFile=certifi.where() ĐỂ SỬA LỖI SSL VỚI MONGODB ATLAS
    client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        tls=True,
        tlsCAFile=certifi.where()
    )
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[TelemetryRecord, EventRecord]
    )
    print("[BACKEND] Kết nối MongoDB thành công!")

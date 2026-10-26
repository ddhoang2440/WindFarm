from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb+srv://ddhoang2440_db_user:dZnUN0yDeWkF9EVM@windfarm.fxgf0y1.mongodb.net"
    DATABASE_NAME: str = "windfarm"
    API_TOKEN: str = "EnoDncjaHecKAaU_4ev-UA7_oRhMamg9mW1vEDqwfzI"
    ML_SERVICE_URL: str = "http://127.0.0.1:8001"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        extra = "ignore"  # Bỏ qua các biến trong .env không khai báo ở đây

settings = Settings()
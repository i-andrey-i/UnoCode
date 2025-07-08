from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ALFA_BANK_SERVICE_URL: str = "http://localhost:8001"
    ONEC_SERVICE_URL: str = "http://localhost:8002"
    CACHE_TTL: int = 300  # 5 минут кэширования
    REDIS_URL: str = "redis://localhost"

    class Config:
        env_file = ".env"

settings = Settings() 
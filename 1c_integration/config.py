from typing import Dict, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # База данных
    DATABASE_PATH: str | None = None
    
    # OData настройки
    ODATA_BASE_URL: str | None = None
    ODATA_VERSION: str = "4.0"
    ODATA_PASSWORD: str | None = None  # Basic auth key
    
    # Справочники 1С
    DOCUMENT_TYPES: Dict[str, str] = {
        "income": "ПриходнаяНакладная",
        "expense": "РасходнаяНакладная"
    }
    
    # Маппинг операций
    OPERATIONS: List[str] = ["Поступление", "Расход"]
    METHODS: List[str] = ["Закупка", "Перемещение", "Реализация", "Списание"]
    
    class Config:
        env_file = ".env"
        # env_prefix = "ODATA_"

settings = Settings() 
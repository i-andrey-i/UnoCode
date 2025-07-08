from typing import Dict, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # База данных
    DATABASE_PATH: str = "/app/data/products.db"
    
    # OData настройки
    ODATA_BASE_URL: str | None = None
    ODATA_VERSION: str | None = None
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

settings = Settings() 
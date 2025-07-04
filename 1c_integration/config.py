from pydantic import BaseSettings

class Settings(BaseSettings):
    # База данных
    DATABASE_PATH: str = "app.db"
    
    # OData настройки
    ODATA_BASE_URL: str = "http://your-1c-server/base_name/odata/standard.odata/"
    ODATA_VERSION: str = "4.0"
    ODATA_USER: str = "your_user"
    ODATA_PASSWORD: str = "your_password"
    
    # Справочники 1С
    DOCUMENT_TYPES = {
        "income": "ПриходнаяНакладная",
        "expense": "РасходнаяНакладная"
    }
    
    # Маппинг операций
    OPERATIONS = ["Поступление", "Расход"]
    METHODS = ["Закупка", "Перемещение", "Реализация", "Списание"]
    
    class Config:
        env_file = ".env"

settings = Settings() 
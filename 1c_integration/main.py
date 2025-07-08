import uvicorn
import logging
from datetime import datetime
from .db import init_products_db
from .api import OneCAPI

# Настройка логирования
logging.basicConfig(
    filename='1c_products.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def sync_1c_products(start_date=None, end_date=None):
    """
    Синхронизация данных о товарных операциях из 1C
    
    Args:
        start_date (str, optional): Дата начала в формате YYYY-MM-DD
        end_date (str, optional): Дата окончания в формате YYYY-MM-DD
    """
    logging.info("Запуск синхронизации товарных операций с 1C")
    
    try:
        api = OneCAPI()
        result = await api.sync_data(
            date_from=datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        )
        
        logging.info(f"Синхронизация завершена: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Ошибка синхронизации товарных операций: {str(e)}"
        logging.error(error_msg)
        return {
            "status": "error",
            "error": error_msg
        }

if __name__ == "__main__":
    # Инициализация БД при запуске
    init_products_db()
    
    # Запуск FastAPI приложения
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
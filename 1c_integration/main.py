import logging
import json
from datetime import datetime, timedelta
from .db import init_products_db, save_product_transaction, get_daily_product_summary
from .api import fetch_1c_products, parse_1c_products

# Настройка логирования
logging.basicConfig(
    filename='1c_products.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def sync_1c_products(start_date=None, end_date=None):
    """
    Синхронизация данных о товарных операциях из 1C
    
    Args:
        start_date (str, optional): Дата начала в формате YYYY-MM-DD
        end_date (str, optional): Дата окончания в формате YYYY-MM-DD
    """
    logging.info("Запуск синхронизации товарных операций с 1C")
    
    try:
        # Инициализация БД при необходимости
        init_products_db()
        
        # Если даты не указаны, берем данные за последние 7 дней
        if not start_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Получение данных из 1C
        raw_data = fetch_1c_products(start_date, end_date)
        
        # Сохранение сырых данных в файл для отладки
        with open("raw_1c_products.json", "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        
        # Парсинг и сохранение данных
        transactions = parse_1c_products(raw_data)
        logging.info(f"Получено {len(transactions)} товарных операций")

        # Сохранение каждой операции
        for tx in transactions:
            try:
                save_product_transaction(tx)
            except ValueError as e:
                logging.error(f"Ошибка валидации транзакции {tx['external_id']}: {str(e)}")
            except Exception as e:
                logging.error(f"Ошибка сохранения транзакции {tx['external_id']}: {str(e)}")

        # Получение сводки за последний день
        today_summary = get_daily_product_summary(datetime.now().strftime("%Y-%m-%d"))
        logging.info(f"Сводка за сегодня: {json.dumps(today_summary, ensure_ascii=False)}")

        logging.info("Синхронизация товарных операций завершена успешно")
        return {
            "status": "success",
            "processed": len(transactions),
            "summary": today_summary
        }

    except Exception as e:
        error_msg = f"Ошибка синхронизации товарных операций: {str(e)}"
        logging.error(error_msg)
        return {
            "status": "error",
            "error": error_msg
        }

if __name__ == "__main__":
    sync_1c_products() 
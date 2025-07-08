import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
from config import settings

logger = logging.getLogger(__name__)

def init_products_db():
    """
    Инициализация базы данных для товарных операций
    """
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()
    
    try:
        # Создаем таблицу, если она не существует
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization TEXT NOT NULL,
                operation TEXT CHECK(operation IN ('Поступление', 'Расход')) NOT NULL,
                method TEXT CHECK(method IN ('Закупка', 'Перемещение', 'Реализация', 'Списание')) NOT NULL,
                item TEXT NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                external_id TEXT UNIQUE NOT NULL
            )
        """)
        
        # Создаем индексы для оптимизации запросов
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_transactions_date 
            ON product_transactions(date)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_transactions_organization 
            ON product_transactions(organization)
        """)
        
        conn.commit()
        logger.info("База данных продуктов успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {str(e)}")
        raise
    finally:
        conn.close()

def validate_transaction(tx: Dict) -> None:
    """
    Валидация данных транзакции
    
    Args:
        tx: Данные транзакции
    
    Raises:
        ValueError: Если данные не валидны
    """
    # Проверка обязательных полей
    required_fields = ['organization', 'operation', 'method', 'item', 'date', 'external_id']
    missing_fields = [field for field in required_fields if field not in tx]
    if missing_fields:
        raise ValueError(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
    
    # Проверка значений операции и метода
    if tx['operation'] not in settings.OPERATIONS:
        raise ValueError(f"Недопустимое значение operation: {tx['operation']}")
    if tx['method'] not in settings.METHODS:
        raise ValueError(f"Недопустимое значение method: {tx['method']}")
    
    # Проверка формата даты
    try:
        if isinstance(tx['date'], str):
            datetime.strptime(tx['date'], '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Неверный формат даты: {tx['date']}")

async def save_product_transaction(tx: Dict) -> None:
    """
    Сохранение товарной операции в базу данных
    
    Args:
        tx: Данные транзакции
    """
    try:
        # Валидация данных
        validate_transaction(tx)
        
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO product_transactions (
                    organization, operation, method, item, date, external_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tx["organization"],
                tx["operation"],
                tx["method"],
                tx["item"],
                tx["date"],
                tx["external_id"]
            ))
            conn.commit()
            logger.info(f"Сохранена товарная операция: {tx['external_id']}")
            
        except sqlite3.IntegrityError:
            logger.debug(f"Пропущен дубликат операции: {tx['external_id']}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении операции {tx['external_id']}: {str(e)}")
            raise
        finally:
            conn.close()
            
    except ValueError as e:
        logger.error(f"Ошибка валидации данных: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при сохранении операции: {str(e)}")
        raise

async def get_product_transactions(date=None, organization=None):
    """
    Получение товарных операций с возможностью фильтрации по дате и организации
    
    Args:
        date: Дата для фильтрации
        organization: Организация для фильтрации
    """
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()
    
    try:
        query = "SELECT * FROM product_transactions WHERE 1=1"
        params = []
        
        if date:
            query += " AND date = ?"
            params.append(date)
        
        if organization:
            query += " AND organization = ?"
            params.append(organization)
        
        query += " ORDER BY date DESC, created_at DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        columns = ['id', 'organization', 'operation', 'method', 'item', 'date', 'created_at', 'external_id']
        return [dict(zip(columns, row)) for row in rows]
        
    except Exception as e:
        logger.error(f"Ошибка при получении транзакций: {str(e)}")
        raise
    finally:
        conn.close()

async def get_daily_product_summary(date: str):
    """
    Получение сводки по товарным операциям за день
    
    Args:
        date: Дата для формирования сводки
    """
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                organization,
                operation,
                COUNT(*) as count,
                GROUP_CONCAT(item, ', ') as items
            FROM product_transactions 
            WHERE date = ?
            GROUP BY organization, operation
        """, (date,))
        
        rows = cur.fetchall()
        return [
            {
                'organization': row[0],
                'operation': row[1],
                'count': row[2],
                'items': row[3]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Ошибка при получении сводки за {date}: {str(e)}")
        raise
    finally:
        conn.close()

async def get_product_transactions_by_date_range(
    start_date: str,
    end_date: str,
    organization: Optional[str] = None
) -> List[Dict]:
    """
    Получение товарных операций за период
    
    Args:
        start_date: Начальная дата в формате YYYY-MM-DD
        end_date: Конечная дата в формате YYYY-MM-DD
        organization: Организация для фильтрации
    """
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()
    
    try:
        query = """
            SELECT 
                organization,
                operation,
                method,
                item,
                date,
                external_id
            FROM product_transactions
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        if organization:
            query += " AND organization = ?"
            params.append(organization)
            
        query += " ORDER BY date DESC, created_at DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        return [
            {
                "organization": row[0],
                "operation": row[1],
                "method": row[2],
                "item": row[3],
                "date": row[4],
                "external_id": row[5]
            }
            for row in rows
        ]
        
    except Exception as e:
        logging.error(f"Ошибка при получении транзакций за период: {str(e)}")
        raise
    finally:
        conn.close() 
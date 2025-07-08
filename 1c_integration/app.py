from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from .db import init_products_db, get_product_transactions, get_daily_product_summary
from .api import OneCAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при старте
    init_products_db()
    yield

app = FastAPI(
    title="1C Integration API",
    description="API для интеграции с 1C и получения данных о товарных операциях",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/products")
async def get_products(
    organization: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
) -> Dict:
    """
    Получение списка товарных операций с фильтрацией
    """
    try:
        transactions = await get_product_transactions(
            date=end_date,
            organization=organization
        )
        
        return {
            "status": "success",
            "data": transactions[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/summary")
async def get_summary(date: Optional[str] = None) -> Dict:
    """
    Получение сводки по товарным операциям за день
    """
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        summary = await get_daily_product_summary(date)
        return {
            "status": "success",
            "date": date,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync")
async def sync_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict:
    """
    Запуск синхронизации данных с 1C
    """
    try:
        api = OneCAPI()
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            # По умолчанию синхронизируем за последние 7 дней
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        result = await api.sync_data(
            date_from=datetime.strptime(start_date, "%Y-%m-%d")
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check() -> Dict:
    """
    Проверка работоспособности сервиса
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    } 
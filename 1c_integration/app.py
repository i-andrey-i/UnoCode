from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timedelta
from typing import Optional
from db import init_products_db, get_product_transactions, get_daily_product_summary
from api import OneCAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from schemas import (
    ProductsResponse,
    DailySummaryResponse,
    SyncResponse,
    HealthCheckResponse,
    ProductOperation
)

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

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/products", response_model=ProductsResponse)
async def get_products(
    organization: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
) -> ProductsResponse:
    """
    Получение списка товарных операций с фильтрацией
    """
    try:
        transactions = await get_product_transactions(
            date=end_date,
            organization=organization
        )
        
        return ProductsResponse(
            status="success",
            data=transactions[:limit],
            total=len(transactions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/summary", response_model=DailySummaryResponse)
async def get_summary(date: Optional[str] = None) -> DailySummaryResponse:
    """
    Получение сводки по товарным операциям за день
    """
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        summary = await get_daily_product_summary(date)
        return DailySummaryResponse(
            status="success",
            date=date,
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync", response_model=SyncResponse)
async def sync_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> SyncResponse:
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
        
        return SyncResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Проверка работоспособности сервиса
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now()
    )
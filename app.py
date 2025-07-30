from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import os
import json
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Импорты для 1C
from OneC_integration.db import init_products_db, get_product_transactions, get_daily_product_summary, get_monthly_product_summary
from OneC_integration.api import OneCAPI
from OneC_integration.schemas import (
    ProductsResponse,
    DailySummaryResponse,
    SyncResponse as OneCSync,
    HealthCheckResponse,
    ProductOperation,
    MonthlySummaryResponse
)

# Импорты для Альфа-банка
from alfa_bank_integration.db import init_db, save_transaction, update_monthly_balance
from alfa_bank_integration.api import fetch_bank_transactions
from alfa_bank_integration.main import parse_transactions, validate_transaction, detect_organization, normalize_method
from alfa_bank_integration.config import settings
from alfa_bank_integration.schemas import (
    TransactionsResponse,
    TransactionSummaryResponse,
    DailyReportResponse,
    MonthlyBalanceResponse,
    SyncResponse as AlfaSync,
    MethodType
)

# Лайфспан для 1C
@asynccontextmanager
async def one_c_lifespan(app: FastAPI):
    init_products_db()
    yield

# Лайфспан для Альфа-банка
@asynccontextmanager
async def alfa_lifespan(app: FastAPI):
    init_db()
    yield

# Создаем два отдельных приложения
one_c_app = FastAPI(
    title="1C Integration API",
    description="API для интеграции с 1C и получения данных о товарных операциях",
    version="1.0.0",
    lifespan=one_c_lifespan
)

alfa_app = FastAPI(
    title="Alfa Bank API",
    lifespan=alfa_lifespan
)

# Добавляем CORS middleware для обоих приложений
for app in [one_c_app, alfa_app]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 1C эндпоинты
@one_c_app.get("/products", response_model=ProductsResponse)
async def get_products(
    organization: Optional[str] = Query(None, min_length=1, max_length=100, description="Название организации"),
    start_date: Optional[str] = Query(None, description="Начальная дата в формате YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Конечная дата в формате YYYY-MM-DD"),
    limit: int = Query(default=100, gt=0, le=1000, description="Максимальное количество записей")
) -> ProductsResponse:
    """Получение списка товарных операций с фильтрацией"""
    try:
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="start_date должна быть в формате YYYY-MM-DD")
        
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="end_date должна быть в формате YYYY-MM-DD")

        if organization:
            organization = organization.strip()
            
        transactions = await get_product_transactions(
            date=end_date,
            organization=organization
        )
        
        return ProductsResponse(
            status="success",
            data=transactions[:limit],
            total=len(transactions)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@one_c_app.get("/products/summary", response_model=DailySummaryResponse)
async def get_summary(
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD")
) -> DailySummaryResponse:
    """Получение сводки по товарным операциям за день"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="date должна быть в формате YYYY-MM-DD")
            
        summary = await get_daily_product_summary(date)
        return DailySummaryResponse(
            status="success",
            date=date,
            data=summary
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@one_c_app.get("/products/monthly-summary", response_model=MonthlySummaryResponse)
async def get_monthly_summary(
    month: Optional[str] = Query(None, description="Месяц в формате YYYY-MM")
) -> MonthlySummaryResponse:
    """Получение сводки по товарным операциям за месяц"""
    try:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        else:
            try:
                date = datetime.strptime(month, "%Y-%m")
                month = date.strftime("%Y-%m")
            except ValueError:
                raise HTTPException(status_code=400, detail="month должен быть в формате YYYY-MM")
            
        summary = await get_monthly_product_summary(month)
        
        return MonthlySummaryResponse(
            status="success",
            month=month,
            data=summary
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@one_c_app.post("/sync", response_model=OneCSync)
async def sync_one_c_data(
    start_date: Optional[str] = Query(None, description="Начальная дата в формате YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Конечная дата в формате YYYY-MM-DD")
) -> OneCSync:
    """Запуск синхронизации данных с 1C"""
    try:
        api = OneCAPI()
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Даты должны быть в формате YYYY-MM-DD")
        
        result = await api.sync_data(
            date_from=datetime.strptime(start_date, "%Y-%m-%d")
        )
        
        return OneCSync(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@one_c_app.get("/health", response_model=HealthCheckResponse)
async def one_c_health_check() -> HealthCheckResponse:
    """Проверка работоспособности сервиса 1C"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now()
    )

# Альфа-банк эндпоинты
@alfa_app.get("/transactions", response_model=TransactionsResponse)
def get_transactions(
    organization: Optional[str] = Query(None, min_length=1, max_length=100),
    limit: int = Query(100, gt=0)
):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()

    if organization:
        cur.execute("""
            SELECT organization, operation, method, amount, date, external_id, created_at, counterparty, purpose
            FROM finance_transactions
            WHERE organization = ?
            ORDER BY date DESC
            LIMIT ?
        """, (organization.strip(), limit))
    else:
        cur.execute("""
            SELECT organization, operation, method, amount, date, external_id, created_at, counterparty, purpose
            FROM finance_transactions
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))

    rows = cur.fetchall()
    conn.close()

    result = [
        {
            "organization": row[0],
            "operation": row[1],
            "method": row[2],
            "amount": row[3],
            "date": row[4],
            "external_id": row[5],
            "created_at": row[6],
            "counterparty": row[7],
            "purpose": row[8]
        }
        for row in rows
    ]
    return {"data": result}

@alfa_app.get("/transactions/summary", response_model=TransactionSummaryResponse)
def get_transaction_summary(
    organization: Optional[str] = Query(None, min_length=1, max_length=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, gt=0)
):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()

    base_query = """
        SELECT date, operation, method, amount, organization, counterparty, purpose, created_at
        FROM finance_transactions
    """
    filters = []
    params = []

    if organization:
        filters.append("organization = ?")
        params.append(organization.strip())
    if start_date:
        filters.append("date >= ?")
        params.append(start_date)
    if end_date:
        filters.append("date <= ?")
        params.append(end_date)

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)

    cur.execute(base_query, tuple(params))
    rows = cur.fetchall()
    conn.close()

    result = [
        {
            "date": row[0],
            "operation": row[1],
            "method": row[2],
            "amount": row[3],
            "organization": row[4],
            "counterparty": row[5],
            "purpose": row[6],
            "created_at": row[7]
        }
        for row in rows
    ]
    return {"data": result}

@alfa_app.get("/api/daily_report", response_model=DailyReportResponse)
def get_daily_report():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT date, organization,
            SUM(CASE WHEN operation = 'Поступление' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN operation = 'Списание' THEN amount ELSE 0 END) as total_expense
        FROM finance_transactions
        GROUP BY date, organization
        ORDER BY date DESC
    """)
    rows = cur.fetchall()
    conn.close()

    result = [
        {
            "date": row[0],
            "organization": row[1],
            "total_income": round(row[2], 2),
            "total_expense": round(row[3], 2)
        }
        for row in rows
    ]
    return {"data": result}

@alfa_app.get("/api/monthly_balance", response_model=MonthlyBalanceResponse)
def get_monthly_balance(
    organization: Optional[str] = Query(None, min_length=1, max_length=100)
):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()

    if organization:
        cur.execute("""
            SELECT organization, date, balance
            FROM monthly_balance
            WHERE organization = ?
            ORDER BY date
        """, (organization.strip(),))
    else:
        cur.execute("""
            SELECT organization, date, balance
            FROM monthly_balance
            ORDER BY organization, date
        """)

    rows = cur.fetchall()
    conn.close()

    result = [
        {
            "organization": row[0],
            "date": row[1],
            "balance": round(row[2], 2)
        }
        for row in rows
    ]
    return {"data": result}

@alfa_app.get("/api/incoming_raw")
def get_incoming_raw():
    raw_path = "raw_transactions.json"
    if not os.path.exists(raw_path):
        return JSONResponse(status_code=404, content={"error": "Файл raw_transactions.json не найден"})

    with open(raw_path, "r", encoding="utf-8") as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError:
            return JSONResponse(status_code=500, content={"error": "Ошибка чтения JSON из файла"})
    return raw_data

@alfa_app.post("/api/sync", response_model=AlfaSync)
def sync_alfa_data():
    try:
        data = fetch_bank_transactions()

        with open("raw_transactions.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        transactions = parse_transactions(data)

        with open("validated_transactions.json", "w", encoding="utf-8") as f:
            json.dump(transactions, f, ensure_ascii=False, indent=2)

        saved_count = 0
        for tx in transactions:
            save_transaction(tx)
            saved_count += 1

        update_monthly_balance()

        return {
            "status": "success",
            "raw_count": len(data.get("transactions", [])),
            "validated_count": len(transactions),
            "saved_count": saved_count,
            "organizations": list({tx["organization"] for tx in transactions})
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Запуск приложений
if __name__ == "__main__":
    import uvicorn
    import multiprocessing

    def run_one_c():
        uvicorn.run(one_c_app, host="0.0.0.0", port=8000)

    def run_alfa():
        uvicorn.run(alfa_app, host="0.0.0.0", port=8001)

    p1 = multiprocessing.Process(target=run_one_c)
    p2 = multiprocessing.Process(target=run_alfa)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
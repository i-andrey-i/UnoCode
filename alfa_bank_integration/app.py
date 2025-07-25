import os
import json
import sqlite3
from fastapi import FastAPI, Query
from db import init_db, save_transaction, update_monthly_balance
from api import fetch_bank_transactions
from contextlib import asynccontextmanager
from typing import Optional
from main import parse_transactions, validate_transaction, detect_organization, normalize_method
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from schemas import (
    TransactionsResponse,
    TransactionSummaryResponse,
    DailyReportResponse,
    MonthlyBalanceResponse,
    SyncResponse,
    MethodType
)

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title="Alfa Bank API", lifespan=lifespan)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/transactions", response_model=TransactionsResponse)
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

@app.get("/transactions/summary", response_model=TransactionSummaryResponse)
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

@app.get("/api/daily_report", response_model=DailyReportResponse)
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

@app.get("/api/monthly_balance", response_model=MonthlyBalanceResponse)
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

@app.get("/api/incoming_raw")
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

@app.post("/api/sync", response_model=SyncResponse)
def sync_data():
    try:
        data = fetch_bank_transactions()

        # Сохраняем "сырые" данные
        with open("raw_transactions.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        transactions = parse_transactions(data)

        # Сохраняем нормализованные данные
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
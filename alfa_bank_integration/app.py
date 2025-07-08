from fastapi import FastAPI, HTTPException
from db import init_db
import os
import json
import sqlite3
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi.responses import JSONResponse
from datetime import datetime
from api import fetch_bank_transactions

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title="Alfa Bank API", lifespan=lifespan)

@app.get("/health")
async def health_check():
    try:
        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        conn.close()
        return {"status": "healthy"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/sync")
async def sync_data():
    """
    Синхронизация данных с банком
    """
    try:
        # Получаем новые транзакции из банка
        transactions = fetch_bank_transactions()
        
        # Сохраняем в БД только уникальные транзакции
        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()
        
        new_count = 0
        error_count = 0
        
        for tx in transactions:
            # Проверяем существование транзакции
            cur.execute(
                "SELECT 1 FROM finance_transactions WHERE external_id = ?",
                (tx["external_id"],)
            )
            
            if not cur.fetchone():  # Если транзакция новая
                try:
                    cur.execute("""
                        INSERT INTO finance_transactions 
                        (organization, operation, method, amount, date, external_id, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tx["organization"],
                        tx["operation"],
                        tx["method"],
                        tx["amount"],
                        tx["date"],
                        tx["external_id"],
                        datetime.now().isoformat()
                    ))
                    new_count += 1
                except Exception as e:
                    error_count += 1
                    continue
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "processed": len(transactions),
                "new": new_count,
                "errors": error_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions")
def get_transactions(organization: Optional[str] = None, limit: int = 100):
    """
    Получение банковских транзакций
    """
    conn = sqlite3.connect("bank_data.db")
    cur = conn.cursor()

    if organization:
        cur.execute("""
            SELECT organization, operation, method, amount, date, external_id
            FROM finance_transactions
            WHERE organization = ?
            ORDER BY date DESC
            LIMIT ?
        """, (organization, limit))
    else:
        cur.execute("""
            SELECT organization, operation, method, amount, date, external_id
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
            "external_id": row[5]
        }
        for row in rows
    ]
    return result

@app.get("/transactions/summary")
def get_transaction_summary(
    organization: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    conn = sqlite3.connect("bank_data.db")
    cur = conn.cursor()

    base_query = """
        SELECT date, operation, method, amount, organization, counterparty, purpose
        FROM finance_transactions
    """
    filters = []
    params = []

    if organization:
        filters.append("organization = ?")
        params.append(organization)
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
            "purpose": row[6]
        }
        for row in rows
    ]
    return result

# === GET /api/daily_report ===
@app.get("/api/daily_report")
def get_daily_report():
    conn = sqlite3.connect("bank_data.db")
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
    return result


# === GET /api/monthly_balance ===
@app.get("/api/monthly_balance")
def get_monthly_balance():
    conn = sqlite3.connect("bank_data.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT organization,
            SUM(CASE WHEN operation = 'Поступление' THEN amount ELSE 0 END) -
            SUM(CASE WHEN operation = 'Списание' THEN amount ELSE 0 END) as current_balance
        FROM finance_transactions
        GROUP BY organization
    """)
    rows = cur.fetchall()
    conn.close()

    result = [
        {
            "organization": row[0],
            "current_balance": round(row[1], 2)
        }
        for row in rows
    ]
    return result


# === GET /api/incoming_raw ===
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
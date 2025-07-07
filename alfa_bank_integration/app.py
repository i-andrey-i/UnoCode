from fastapi import FastAPI
from db import init_db
import sqlite3
from contextlib import asynccontextmanager
from typing import Optional

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title="Alfa Bank API", lifespan=lifespan)

@app.get("/transactions")
def get_transactions(organization: str = None, limit: int = 100):
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
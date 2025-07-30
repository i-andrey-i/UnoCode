import sqlite3
import os
from .config import settings

def init_db():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()

    # Таблица финансовых транзакций
    cur.execute("""
        CREATE TABLE IF NOT EXISTS finance_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization TEXT,
            operation TEXT,
            method TEXT,
            amount REAL,
            date TEXT,
            counterparty TEXT,
            purpose TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            external_id INTEGER UNIQUE
        )
    """)

    # Таблица ежедневных балансов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS monthly_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization TEXT,
            date TEXT,
            balance REAL
        )
    """)

    conn.commit()
    conn.close()

def save_transaction(tx):
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO finance_transactions (
                organization, operation, method, amount, date, counterparty, purpose, external_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx["organization"],
            tx["operation"],
            tx["method"],
            tx["amount"],
            tx["date"],
            tx.get("counterparty"),
            tx.get("purpose"),
            tx["external_id"]
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Дубликат — не сохраняем
    finally:
        conn.close()

def update_monthly_balance():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cur = conn.cursor()

    # Получаем все уникальные даты и организации из транзакций
    cur.execute("SELECT DISTINCT date FROM finance_transactions ORDER BY date")
    dates = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT organization FROM finance_transactions")
    organizations = [row[0] for row in cur.fetchall()]

    for org in organizations:
        last_balance = 0.0

        # Получаем последнюю запись из monthly_balance перед первой датой
        cur.execute("""
            SELECT balance FROM monthly_balance
            WHERE organization = ? AND date < ?
            ORDER BY date DESC LIMIT 1
        """, (org, dates[0]))
        row = cur.fetchone()
        if row:
            last_balance = row[0]

        for day in dates:
            # Суммируем поступления и списания за день
            cur.execute("""
                SELECT
                    SUM(CASE WHEN operation = 'Поступление' THEN amount ELSE 0 END),
                    SUM(CASE WHEN operation = 'Списание' THEN amount ELSE 0 END)
                FROM finance_transactions
                WHERE organization = ? AND date = ?
            """, (org, day))
            income, expense = cur.fetchone()
            income = income or 0.0
            expense = expense or 0.0

            daily_balance = last_balance + income - expense
            last_balance = daily_balance

            # Обновляем или вставляем баланс на день
            cur.execute("""
                SELECT 1 FROM monthly_balance WHERE organization = ? AND date = ?
            """, (org, day))
            exists = cur.fetchone()

            if exists:
                cur.execute("""
                    UPDATE monthly_balance SET balance = ? WHERE organization = ? AND date = ?
                """, (daily_balance, org, day))
            else:
                cur.execute("""
                    INSERT INTO monthly_balance (organization, date, balance)
                    VALUES (?, ?, ?)
                """, (org, day, daily_balance))

    conn.commit()
    conn.close()
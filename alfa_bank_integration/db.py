import sqlite3
from datetime import datetime, date

def init_db():
    conn = sqlite3.connect("bank_data.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS finance_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization TEXT,
            operation TEXT,
            method TEXT,
            amount REAL,
            date DATE NOT NULL,
            counterparty TEXT,
            purpose TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            external_id TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def save_transaction(tx):
    conn = sqlite3.connect("bank_data.db")
    cur = conn.cursor()
    try:
        # Преобразование даты если нужно
        if isinstance(tx["date"], str):
            tx_date = datetime.strptime(tx["date"], '%Y-%m-%d').date()
        elif isinstance(tx["date"], datetime):
            tx_date = tx["date"].date()
        elif isinstance(tx["date"], date):
            tx_date = tx["date"]
        else:
            raise ValueError(f"Неверный тип даты: {type(tx['date'])}")

        cur.execute("""
            INSERT INTO finance_transactions (
                organization, operation, method, amount, date, counterparty, purpose, external_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx["organization"],
            tx["operation"],
            tx["method"],
            tx["amount"],
            tx_date.isoformat(),  # Сохраняем дату в формате ISO
            tx.get("counterparty"),
            tx.get("purpose"),
            tx["external_id"]
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Дубликат — не сохраняем
    finally:
        conn.close()
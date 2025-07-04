import sqlite3

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
            date TEXT,
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
        cur.execute("""
            INSERT INTO finance_transactions (
                organization, operation, method, amount, date, external_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tx["organization"],
            tx["operation"],
            tx["method"],
            tx["amount"],
            tx["date"],
            tx["external_id"]
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Дубликат — не сохраняем
    finally:
        conn.close()
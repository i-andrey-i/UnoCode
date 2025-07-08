import logging
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from db import init_db, save_transaction
from api import fetch_bank_transactions

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# Сопоставление ИНН с организациями
INN_ORG_MAP = {
    "1234567890": "ООО",
    "9876543210": "ИП1",
    "1122334455": "ИП2",
    "5566778899": "ИП3"
}

@app.on_event("startup")
async def startup_event():
    init_db()
    logging.info("База данных инициализирована")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/sync")
async def sync_transactions():
    try:
        data = fetch_bank_transactions()
        transactions = parse_transactions(data)
        
        for tx in transactions:
            save_transaction(tx)
            logging.info(f"Сохранена транзакция: {tx['external_id']}")
        
        return {"status": "success", "count": len(transactions)}
    except Exception as e:
        logging.error(f"Ошибка синхронизации: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def detect_organization(item):
    inn = item.get("inn")
    return INN_ORG_MAP.get(inn, "Неизвестно")

def normalize_method(raw_value):
    val = str(raw_value).strip().lower()
    if "qr" in val:
        return "QR"
    elif "налич" in val:
        return "Наличка"
    elif "карт" in val:
        return "Карта"
    elif "счет" in val or "счёт" in val:
        return "Счет"
    else:
        return "Счет"

def validate_transaction(item):
    try:
        tx_id = str(item["id"])
        amount = float(item["amount"])
        if amount == 0:
            return False, "Сумма = 0"

        date = datetime.strptime(item["date"], "%Y-%m-%d").date()

        tx = {
            "external_id": tx_id,
            "organization": detect_organization(item),
            "operation": "Поступление" if amount > 0 else "Списание",
            "method": normalize_method(item.get("payment_type", "Счет")),
            "amount": abs(amount),
            "date": str(date),
            "counterparty": item.get("counterparty"),
            "purpose": item.get("purpose")
        }
        return True, tx

    except (KeyError, ValueError, TypeError) as e:
        return False, f"Ошибка валидации: {e}"

def parse_transactions(raw_data):
    parsed = []
    for item in raw_data.get("transactions", []):
        valid, result = validate_transaction(item)
        if valid:
            parsed.append(result)
        else:
            logging.warning(f"Пропущена транзакция: {result}")
    return parsed
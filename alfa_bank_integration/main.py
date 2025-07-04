import logging
import json
from db import init_db, save_transaction
from api import fetch_bank_transactions

# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Сопоставление ИНН с организациями
INN_ORG_MAP = {
    "1234567890": "ООО",
    "9876543210": "ИП1",
    "1122334455": "ИП2",
    "5566778899": "ИП3"
}

def detect_organization(item):
    inn = item.get("inn")
    return INN_ORG_MAP.get(inn, "Неизвестно")

def parse_transactions(raw_data):
    parsed = []
    for item in raw_data.get("transactions", []):
        tx = {
            "organization": detect_organization(item),
            "operation": "Поступление" if item["amount"] > 0 else "Списание",
            "method": item.get("payment_type", "Счет"),
            "amount": abs(item["amount"]),
            "date": item["date"],
            "external_id": item["id"]
        }
        parsed.append(tx)
    return parsed

def main():
    logging.info("Запуск скрипта интеграции Альфа-Банка")
    try:
        init_db()
        data = fetch_bank_transactions()
        
        # Сохраняем сырые данные в файл
        with open("raw_transactions.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        transactions = parse_transactions(data)
        logging.info(f"Получено {len(transactions)} транзакций")

        for tx in transactions:
            save_transaction(tx)
            logging.info(f"Сохранена транзакция: {tx['external_id']}")

        logging.info("Работа завершена успешно")

    except Exception as e:
        logging.error(f"Ошибка выполнения скрипта: {e}")

if __name__ == "__main__":
    main()
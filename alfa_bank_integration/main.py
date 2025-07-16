import logging
import json
from datetime import datetime
from db import init_db, save_transaction, update_monthly_balance
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

def normalize_method(raw_value):
    val = str(raw_value).strip().lower()
    if "qr" in val:
        return "QR"
    if "налич" in val or "cash" in val:
        return "Наличка"
    if "карт" in val or "card" in val or "mcc" in val:
        return "Карта"
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

def main():
    logging.info("Запуск скрипта интеграции Альфа-Банка")
    try:
        init_db()
        data = fetch_bank_transactions()

        # Сохраняем сырые данные в файл для отладки
        with open("raw_transactions.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        transactions = parse_transactions(data)

        # Сохраняем валидационные/нормализованные данные для фронта
        with open("validated_transactions.json", "w", encoding="utf-8") as f:
            json.dump(transactions, f, ensure_ascii=False, indent=2)

        logging.info(f"Получено {len(transactions)} валидных транзакций")

        for tx in transactions:
            save_transaction(tx)
            logging.info(f"Сохранена транзакция: {tx['external_id']}")

        logging.info("Работа завершена успешно")

        update_monthly_balance()
        logging.info("Обновлены записи в monthly_balance")

    except Exception as e:
        logging.error(f"Ошибка выполнения скрипта: {e}")

if __name__ == "__main__":
    main()
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from config import settings
from models import (
    ProductResponse,
    ProductSummaryResponse,
    SyncResponse,
    ErrorResponse,
    BankResponse,
    DailyReport
)

def validate_date(date: Optional[str] = None) -> Optional[str]:
    """Validates date format YYYY-MM-DD"""
    if date is None:
        return None
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return date
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                message="Invalid date format. Use YYYY-MM-DD",
                timestamp=datetime.now().isoformat()
            ).dict()
        )

app = FastAPI(
    title="Business Dashboard API Gateway",
    description="API Gateway для объединения данных из Альфа-Банка и 1С",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def proxy_request(service_url: str, path: str, params: dict = None, method: str = "GET") -> Dict:
    """
    Проксирование запроса к сервису
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if method == "GET":
                response = await client.get(f"{service_url}/{path}", params=params)
            else:
                response = await client.post(f"{service_url}/{path}", json=params)
            
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail=ErrorResponse(
                    message=f"Timeout при запросе к {path}",
                    timestamp=datetime.now().isoformat()
                ).dict()
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=ErrorResponse(
                    message=f"Ошибка сервиса при запросе к {path}: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).dict()
            )

@app.get(
    "/api/products",
    response_model=ProductResponse,
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Некорректные параметры", "model": ErrorResponse},
        502: {"description": "Ошибка сервиса 1С", "model": ErrorResponse},
        504: {"description": "Таймаут сервиса 1С", "model": ErrorResponse}
    }
)
async def get_products(
    organization: Optional[str] = Query(None, description="Организация"),
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD"),
    limit: int = Query(default=100, le=1000, description="Ограничение количества записей")
):
    """
    Получение списка товарных операций из 1С

    - **organization**: Фильтр по организации
    - **date**: Фильтр по дате в формате YYYY-MM-DD
    - **limit**: Ограничение количества возвращаемых записей
    """
    date = validate_date(date)
    params = {
        "organization": organization,
        "date": date,
        "limit": limit
    }
    return await proxy_request(settings.ONEC_SERVICE_URL, "products", params)

@app.get(
    "/api/products/summary",
    response_model=ProductSummaryResponse,
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Некорректные параметры", "model": ErrorResponse},
        502: {"description": "Ошибка сервиса 1С", "model": ErrorResponse},
        504: {"description": "Таймаут сервиса 1С", "model": ErrorResponse}
    }
)
async def get_products_summary(
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD")
):
    """
    Получение сводки по товарным операциям из 1С

    - **date**: Фильтр по дате в формате YYYY-MM-DD
    """
    date = validate_date(date)
    return await proxy_request(
        settings.ONEC_SERVICE_URL,
        "products/summary",
        {"date": date}
    )

@app.post("/api/products/sync")
async def sync_products(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Синхронизация данных с 1С
    """
    return await proxy_request(
        settings.ONEC_SERVICE_URL,
        "sync",
        {"start_date": start_date, "end_date": end_date},
        method="POST"
    )

@app.get(
    "/api/transactions",
    response_model=BankResponse,
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Некорректные параметры", "model": ErrorResponse},
        502: {"description": "Ошибка сервиса Альфа-Банка", "model": ErrorResponse},
        504: {"description": "Таймаут сервиса Альфа-Банка", "model": ErrorResponse}
    }
)
async def get_transactions(
    organization: Optional[str] = Query(None, description="Организация"),
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD"),
    limit: int = Query(default=100, le=1000, description="Ограничение количества записей")
):
    """
    Получение банковских транзакций

    - **organization**: Фильтр по организации
    - **date**: Фильтр по дате в формате YYYY-MM-DD
    - **limit**: Ограничение количества возвращаемых записей
    """
    date = validate_date(date)
    params = {
        "organization": organization,
        "date": date,
        "limit": limit
    }
    return await proxy_request(
        settings.ALFA_BANK_SERVICE_URL,
        "transactions",
        params
    )

@app.get(
    "/api/transactions/summary",
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Некорректные параметры", "model": ErrorResponse},
        502: {"description": "Ошибка сервиса Альфа-Банка", "model": ErrorResponse},
        504: {"description": "Таймаут сервиса Альфа-Банка", "model": ErrorResponse}
    }
)
async def get_transactions_summary(
    organization: Optional[str] = Query(None, description="Организация"),
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD"),
    limit: int = Query(default=100, le=1000, description="Ограничение количества записей")
):
    """
    Получение сводки по банковским транзакциям

    - **organization**: Фильтр по организации
    - **date**: Фильтр по дате в формате YYYY-MM-DD
    - **limit**: Ограничение количества возвращаемых записей
    """
    date = validate_date(date)
    params = {
        "organization": organization,
        "date": date,
        "limit": limit
    }
    return await proxy_request(
        settings.ALFA_BANK_SERVICE_URL,
        "transactions/summary",
        params
    )

@app.get(
    "/api/monthly_balance",
    responses={
        200: {"description": "Успешный ответ"},
        502: {"description": "Ошибка сервиса Альфа-Банка", "model": ErrorResponse},
        504: {"description": "Таймаут сервиса Альфа-Банка", "model": ErrorResponse}
    }
)
async def get_monthly_balance(
    organization: Optional[str] = Query(None, description="Организация")
):
    """
    Получение месячного баланса по организации

    - **organization**: Фильтр по организации
    """
    return await proxy_request(
        settings.ALFA_BANK_SERVICE_URL,
        "monthly_balance",
        {"organization": organization}
    )

@app.get(
    "/api/incoming_raw",
    responses={
        200: {"description": "Успешный ответ"},
        502: {"description": "Ошибка сервиса Альфа-Банка", "model": ErrorResponse},
        504: {"description": "Таймаут сервиса Альфа-Банка", "model": ErrorResponse}
    }
)
async def get_incoming_raw():
    """
    Получение сырых данных из банка
    """
    return await proxy_request(
        settings.ALFA_BANK_SERVICE_URL,
        "incoming_raw"
    )

@app.get(
    "/api/daily_report",
    response_model=DailyReport,
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Некорректные параметры", "model": ErrorResponse},
        500: {"description": "Внутренняя ошибка сервера", "model": ErrorResponse}
    }
)
async def get_daily_report(
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD")
):
    """
    Получение агрегированного дневного отчета

    - **date**: Дата отчета в формате YYYY-MM-DD. Если не указана, используется текущая дата.
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        date = validate_date(date)

    try:
        # Получаем данные параллельно
        bank_data_task = proxy_request(
            settings.ALFA_BANK_SERVICE_URL,
            "transactions/summary",
            {"date": date}
        )
        product_data_task = proxy_request(
            settings.ONEC_SERVICE_URL,
            "products/summary",
            {"date": date}
        )

        bank_data, product_data = await asyncio.gather(
            bank_data_task,
            product_data_task
        )

        # Агрегируем данные по организациям
        result = {}
        organizations = ["ИП1", "ИП2", "ИП3", "ООО"]

        for org in organizations:
            # Фильтруем транзакции для организации
            org_bank_in = [
                tx for tx in bank_data.get("data", [])
                if tx["organization"] == org and tx["operation"] == "Поступление"
            ]
            org_bank_out = [
                tx for tx in bank_data.get("data", [])
                if tx["organization"] == org and tx["operation"] == "Списание"
            ]
            org_products_in = [
                tx for tx in product_data.get("data", [])
                if tx["organization"] == org and tx["operation"] == "Поступление"
            ]
            org_products_out = [
                tx for tx in product_data.get("data", [])
                if tx["organization"] == org and tx["operation"] == "Расход"
            ]

            result[org] = {
                "finance": {
                    "in_amount": sum(tx["amount"] for tx in org_bank_in),
                    "out_amount": sum(tx["amount"] for tx in org_bank_out),
                    "details": {
                        "Счет": sum(tx["amount"] for tx in org_bank_in + org_bank_out if tx["method"] == "Счет"),
                        "Карта": sum(tx["amount"] for tx in org_bank_in + org_bank_out if tx["method"] == "Карта"),
                        "Наличка": sum(tx["amount"] for tx in org_bank_in + org_bank_out if tx["method"] == "Наличка"),
                        "QR": sum(tx["amount"] for tx in org_bank_in + org_bank_out if tx["method"] == "QR")
                    }
                },
                "products": {
                    "in_count": len(org_products_in),
                    "out_count": len(org_products_out),
                    "details": {
                        "Закупка": len([tx for tx in org_products_in if tx["method"] == "Закупка"]),
                        "Перемещение": len([tx for tx in org_products_in if tx["method"] == "Перемещение"]),
                        "Реализация": len([tx for tx in org_products_out if tx["method"] == "Реализация"]),
                        "Списание": len([tx for tx in org_products_out if tx["method"] == "Списание"])
                    }
                }
            }

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "date": date,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                message=str(e),
                timestamp=datetime.now().isoformat()
            ).dict()
        )

# Алиасы в соответствии с ТЗ
@app.get(
    "/api/alpha_bank_data",
    response_model=BankResponse,
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Некорректные параметры", "model": ErrorResponse},
        502: {"description": "Ошибка сервиса Альфа-Банка", "model": ErrorResponse},
        504: {"description": "Таймаут сервиса Альфа-Банка", "model": ErrorResponse}
    }
)
async def get_alpha_bank_data(
    organization: Optional[str] = Query(None, description="Организация"),
    limit: int = Query(default=100, le=1000, description="Ограничение количества записей")
):
    """
    Получение данных из Альфа-Банка (алиас для /api/transactions)

    - **organization**: Фильтр по организации
    - **limit**: Ограничение количества возвращаемых записей
    """
    return await get_transactions(organization, limit=limit)

@app.get(
    "/api/1c_data",
    response_model=ProductResponse,
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Некорректные параметры", "model": ErrorResponse},
        502: {"description": "Ошибка сервиса 1С", "model": ErrorResponse},
        504: {"description": "Таймаут сервиса 1С", "model": ErrorResponse}
    }
)
async def get_1c_data(
    organization: Optional[str] = Query(None, description="Организация"),
    limit: int = Query(default=100, le=1000, description="Ограничение количества записей")
):
    """
    Получение данных из 1С (алиас для /api/products)

    - **organization**: Фильтр по организации
    - **limit**: Ограничение количества возвращаемых записей
    """
    return await get_products(organization, limit=limit)

@app.post(
    "/api/sync",
    response_model=SyncResponse,
    responses={
        200: {"description": "Успешный ответ"},
        500: {"description": "Внутренняя ошибка сервера", "model": ErrorResponse},
        502: {"description": "Ошибка внешнего сервиса", "model": ErrorResponse},
        504: {"description": "Таймаут внешнего сервиса", "model": ErrorResponse}
    }
)
async def sync_all():
    """
    Синхронизация данных из всех источников.
    Запускает параллельную синхронизацию данных из Альфа-Банка и 1С.
    """
    try:
        bank_sync_task = proxy_request(
            settings.ALFA_BANK_SERVICE_URL,
            "sync",
            method="POST"
        )
        products_sync_task = proxy_request(
            settings.ONEC_SERVICE_URL,
            "sync",
            method="POST"
        )

        bank_result, products_result = await asyncio.gather(
            bank_sync_task,
            products_sync_task
        )

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "sync_results": {
                "bank": bank_result,
                "products": products_result
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                message=str(e),
                timestamp=datetime.now().isoformat()
            ).dict()
        )

@app.get(
    "/health",
    responses={
        200: {"description": "Сервис работает нормально"},
        500: {"description": "Сервис недоступен"}
    }
)
async def health_check():
    """
    Проверка работоспособности сервиса
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    } 
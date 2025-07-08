from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from config import settings

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
            raise HTTPException(status_code=504, detail=f"Timeout при запросе к {path}")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Ошибка сервиса при запросе к {path}: {str(e)}")

# Эндпоинты 1C Integration
@app.get("/api/products")
async def get_products(
    organization: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
):
    """
    Получение списка товарных операций из 1С
    """
    params = {
        "organization": organization,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }
    return await proxy_request(settings.ONEC_SERVICE_URL, "products", params)

@app.get("/api/products/summary")
async def get_products_summary(date: Optional[str] = None):
    """
    Получение сводки по товарным операциям из 1С
    """
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

# Эндпоинты Alfa Bank Integration
@app.get("/api/transactions")
async def get_transactions(
    organization: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
):
    """
    Получение банковских транзакций
    """
    return await proxy_request(
        settings.ALFA_BANK_SERVICE_URL,
        "transactions",
        {"organization": organization, "limit": limit}
    )

@app.get("/api/transactions/summary")
async def get_transactions_summary(
    organization: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
):
    """
    Получение сводки по банковским транзакциям
    """
    params = {
        "organization": organization,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }
    return await proxy_request(
        settings.ALFA_BANK_SERVICE_URL,
        "transactions/summary",
        params
    )

@app.get("/api/monthly_balance")
async def get_monthly_balance(organization: Optional[str] = None):
    """
    Получение месячного баланса по организации
    """
    return await proxy_request(
        settings.ALFA_BANK_SERVICE_URL,
        "api/monthly_balance",
        {"organization": organization}
    )

@app.get("/api/incoming_raw")
async def get_incoming_raw():
    """
    Получение сырых данных из банка
    """
    return await proxy_request(
        settings.ALFA_BANK_SERVICE_URL,
        "api/incoming_raw"
    )

@app.get("/api/daily_report")
async def get_daily_report(date: Optional[str] = None):
    """
    Получение агрегированного дневного отчета
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    async with httpx.AsyncClient(timeout=10.0) as client:
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
                result[org] = {
                    "finance": {
                        "in": sum(tx["amount"] for tx in bank_data.get("data", [])
                                if tx["organization"] == org and tx["operation"] == "Поступление"),
                        "out": sum(tx["amount"] for tx in bank_data.get("data", [])
                                 if tx["organization"] == org and tx["operation"] == "Списание")
                    },
                    "products": {
                        "in": len([tx for tx in product_data.get("data", [])
                                 if tx["organization"] == org and tx["operation"] == "Поступление"]),
                        "out": len([tx for tx in product_data.get("data", [])
                                  if tx["organization"] == org and tx["operation"] == "Расход"])
                    }
                }

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "date": date,
                "data": result
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Алиасы в соответствии с ТЗ
@app.get("/api/alpha_bank_data")
async def get_alpha_bank_data(
    organization: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
):
    """
    Получение данных из Альфа-Банка (алиас для /api/transactions)
    """
    return await get_transactions(organization, limit)

@app.get("/api/1c_data")
async def get_1c_data(
    organization: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
):
    """
    Получение данных из 1С (алиас для /api/products)
    """
    return await get_products(organization, limit=limit)

@app.post("/api/sync")
async def sync_all():
    """
    Синхронизация данных из всех источников
    """
    try:
        # Запускаем синхронизацию параллельно
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

        # Ждем завершения обеих синхронизаций
        bank_result, products_result = await asyncio.gather(
            bank_sync_task,
            products_sync_task
        )

        # Получаем обновленный дневной отчет
        daily_report = await get_daily_report()

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "sync_results": {
                "bank": bank_result,
                "products": products_result
            },
            "daily_report": daily_report
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health")
async def health_check():
    """
    Проверка работоспособности сервиса
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        services_health = {
            "api_gateway": "healthy",
            "alfa_bank": "unknown",
            "1c": "unknown"
        }

        try:
            alfa_response = await client.get(f"{settings.ALFA_BANK_SERVICE_URL}/health")
            services_health["alfa_bank"] = "healthy" if alfa_response.status_code == 200 else "unhealthy"
        except Exception:
            services_health["alfa_bank"] = "unhealthy"

        try:
            onec_response = await client.get(f"{settings.ONEC_SERVICE_URL}/health")
            services_health["1c"] = "healthy" if onec_response.status_code == 200 else "unhealthy"
        except Exception:
            services_health["1c"] = "unhealthy"

        overall_status = "healthy" if all(status == "healthy" for status in services_health.values()) else "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": services_health
        } 
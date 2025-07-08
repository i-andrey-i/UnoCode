from fastapi import FastAPI, HTTPException
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

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def fetch_service_data(client: httpx.AsyncClient, url: str) -> Dict:
    """Получение данных от сервиса с обработкой ошибок"""
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Timeout при запросе к {url}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка сервиса при запросе к {url}: {str(e)}")

@app.get("/api/daily_report")
async def get_daily_report(date: Optional[str] = None):
    """
    Получение агрегированного дневного отчета
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Получаем данные параллельно
        bank_data_task = fetch_service_data(
            client,
            f"{settings.ALFA_BANK_SERVICE_URL}/transactions/summary?date={date}"
        )
        product_data_task = fetch_service_data(
            client,
            f"{settings.ONEC_SERVICE_URL}/products/summary?date={date}"
        )

        try:
            bank_data, product_data = await asyncio.gather(
                bank_data_task,
                product_data_task
            )
        except HTTPException as e:
            return {
                "status": "error",
                "error": str(e.detail),
                "timestamp": datetime.now().isoformat()
            }

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

@app.get("/api/incoming_raw")
async def get_raw_data():
    """
    Получение необработанных данных из обоих сервисов
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            bank_data_task = fetch_service_data(
                client,
                f"{settings.ALFA_BANK_SERVICE_URL}/transactions"
            )
            product_data_task = fetch_service_data(
                client,
                f"{settings.ONEC_SERVICE_URL}/products"
            )

            bank_data, product_data = await asyncio.gather(
                bank_data_task,
                product_data_task
            )

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "bank_operations": bank_data,
                    "product_operations": product_data
                }
            }
        except HTTPException as e:
            return {
                "status": "error",
                "error": str(e.detail),
                "timestamp": datetime.now().isoformat()
            }

@app.post("/api/sync")
async def sync_all():
    """
    Синхронизация данных из всех источников
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Запускаем синхронизацию параллельно
            bank_sync_task = client.post(f"{settings.ALFA_BANK_SERVICE_URL}/sync")
            product_sync_task = client.post(f"{settings.ONEC_SERVICE_URL}/sync")

            bank_result, product_result = await asyncio.gather(
                bank_sync_task,
                product_sync_task
            )

            # Получаем обновленные данные
            daily_report = await get_daily_report()

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "sync_results": {
                    "bank": bank_result.json(),
                    "products": product_result.json()
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
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/monthly_balance")
async def get_monthly_balance(organization: Optional[str] = None):
    """
    Получение месячного баланса
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await fetch_service_data(
                client,
                f"{settings.ALFA_BANK_SERVICE_URL}/api/monthly_balance"
                + (f"?organization={organization}" if organization else "")
            )
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "data": response
            }
        except HTTPException as e:
            return {
                "status": "error",
                "error": str(e.detail),
                "timestamp": datetime.now().isoformat()
            } 
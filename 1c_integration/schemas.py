from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class OperationType(str, Enum):
    INCOME = "Поступление"
    EXPENSE = "Расход"

class MethodType(str, Enum):
    PURCHASE = "Закупка"
    MOVEMENT = "Перемещение"
    REALIZATION = "Реализация"
    WRITEOFF = "Списание"

class Organization(str, Enum):
    IP1 = "ИП1"
    IP2 = "ИП2"
    IP3 = "ИП3"
    OOO = "ООО"

class ProductOperation(BaseModel):
    id: Optional[int] = Field(None, description="Уникальный ID операции")
    organization: Organization = Field(..., description="Организация")
    operation: OperationType = Field(..., description="Тип операции")
    method: MethodType = Field(..., description="Метод операции")
    item: str = Field(..., description="Наименование товара")
    date: datetime = Field(..., description="Дата операции")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания записи")
    external_id: int = Field(..., description="ID операции в 1С")

class ProductsResponse(BaseModel):
    status: Literal["success", "error"]
    data: List[ProductOperation]
    total: Optional[int] = None

class DailySummaryItem(BaseModel):
    organization: Organization
    income_count: int = Field(..., description="Количество поступлений")
    expense_count: int = Field(..., description="Количество расходов")
    total_operations: int = Field(..., description="Общее количество операций")
    date: datetime = Field(..., description="Дата отчета")

class DailySummaryResponse(BaseModel):
    status: Literal["success", "error"]
    date: str
    data: List[DailySummaryItem]

class SyncResponse(BaseModel):
    status: Literal["success", "error"]
    total: Optional[int] = None
    success: Optional[int] = None
    errors: Optional[int] = None
    message: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    timestamp: datetime 
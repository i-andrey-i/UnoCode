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

class ProductOperation(BaseModel):
    id: Optional[int] = Field(None, description="Уникальный ID операции")
    organization: str = Field(..., description="Организация", min_length=1, max_length=100)
    operation: OperationType = Field(..., description="Тип операции")
    method: MethodType = Field(..., description="Метод операции")
    item: str = Field(..., description="Наименование товара")
    date: str = Field(..., description="Дата операции в формате YYYY-MM-DD")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания записи")
    external_id: int = Field(..., description="ID операции в 1С")

    @validator('organization')
    def validate_organization(cls, v):
        if not v.strip():
            raise ValueError('Organization name cannot be empty or whitespace')
        return v.strip()
        
    @validator('date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class ProductsResponse(BaseModel):
    status: Literal["success", "error"]
    data: List[ProductOperation]
    total: Optional[int] = None

class DailySummaryItem(BaseModel):
    organization: str = Field(..., description="Организация", min_length=1, max_length=100)
    income_count: int = Field(..., description="Количество поступлений", ge=0)
    expense_count: int = Field(..., description="Количество расходов", ge=0)
    total_operations: int = Field(..., description="Общее количество операций", ge=0)
    date: str = Field(..., description="Дата отчета в формате YYYY-MM-DD")

    @validator('organization')
    def validate_organization(cls, v):
        if not v.strip():
            raise ValueError('Organization name cannot be empty or whitespace')
        return v.strip()

    @validator('date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    @validator('total_operations')
    def validate_total_operations(cls, v, values):
        if 'income_count' in values and 'expense_count' in values:
            if v != values['income_count'] + values['expense_count']:
                raise ValueError('Total operations must equal sum of income and expense counts')
        return v

class DailySummaryResponse(BaseModel):
    status: Literal["success", "error"]
    date: str
    data: List[DailySummaryItem]

class MonthlySummaryItem(BaseModel):
    organization: str = Field(..., description="Организация", min_length=1, max_length=100)
    date: str = Field(..., description="Дата в формате YYYY-MM-DD")
    income_count: int = Field(..., description="Количество поступлений", ge=0)
    expense_count: int = Field(..., description="Количество расходов", ge=0)
    total_operations: int = Field(..., description="Общее количество операций", ge=0)

    @validator('organization')
    def validate_organization(cls, v):
        if not v.strip():
            raise ValueError('Organization name cannot be empty or whitespace')
        return v.strip()

    @validator('date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    @validator('total_operations')
    def validate_total_operations(cls, v, values):
        if 'income_count' in values and 'expense_count' in values:
            if v != values['income_count'] + values['expense_count']:
                raise ValueError('Total operations must equal sum of income and expense counts')
        return v

class MonthlySummaryResponse(BaseModel):
    status: Literal["success", "error"]
    month: str  # YYYY-MM
    data: List[MonthlySummaryItem]

class SyncResponse(BaseModel):
    status: Literal["success", "error"]
    total: Optional[int] = None
    success: Optional[int] = None
    errors: Optional[int] = None
    message: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    timestamp: datetime 
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class OperationType(str, Enum):
    INCOME = "Поступление"
    EXPENSE = "Списание"

class MethodType(str, Enum):
    ACCOUNT = "Счет"
    CARD = "Карта"
    CASH = "Наличка"
    QR = "QR"

class BankTransaction(BaseModel):
    organization: str = Field(..., description="Организация", min_length=1, max_length=100)
    operation: OperationType = Field(..., description="Тип операции")
    method: MethodType = Field(..., description="Метод операции")
    amount: float = Field(..., description="Сумма операции", gt=0)
    date: str = Field(..., description="Дата операции")
    external_id: int = Field(..., description="Внешний ID транзакции")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания записи")
    counterparty: Optional[str] = Field(None, description="Контрагент")
    purpose: Optional[str] = Field(None, description="Назначение платежа")

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

class TransactionSummary(BaseModel):
    date: str = Field(..., description="Дата операции")
    operation: OperationType = Field(..., description="Тип операции")
    method: MethodType = Field(..., description="Метод операции")
    amount: float = Field(..., description="Сумма операции", gt=0)
    organization: str = Field(..., description="Организация", min_length=1, max_length=100)
    counterparty: str = Field(..., description="Контрагент")
    purpose: str = Field(..., description="Назначение платежа")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания записи")

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

class DailyReport(BaseModel):
    date: str = Field(..., description="Дата отчета")
    organization: str = Field(..., description="Организация", min_length=1, max_length=100)
    total_income: float = Field(..., description="Общая сумма поступлений", ge=0)
    total_expense: float = Field(..., description="Общая сумма списаний", ge=0)

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

class MonthlyBalance(BaseModel):
    organization: str = Field(..., description="Организация", min_length=1, max_length=100)
    date: str = Field(..., description="Дата")
    balance: float = Field(..., description="Баланс")

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

class SyncResponse(BaseModel):
    status: Literal["success", "error"]
    raw_count: Optional[int] = Field(None, description="Количество сырых транзакций")
    validated_count: Optional[int] = Field(None, description="Количество валидированных транзакций")
    saved_count: Optional[int] = Field(None, description="Количество сохраненных транзакций")
    organizations: Optional[List[str]] = Field(None, description="Список организаций")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")

# Response models
class TransactionsResponse(BaseModel):
    data: List[BankTransaction]

class TransactionSummaryResponse(BaseModel):
    data: List[TransactionSummary]

class DailyReportResponse(BaseModel):
    data: List[DailyReport]

class MonthlyBalanceResponse(BaseModel):
    data: List[MonthlyBalance] 
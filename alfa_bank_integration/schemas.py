from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class OperationType(str, Enum):
    INCOME = "Поступление"
    EXPENSE = "Списание"

class Organization(str, Enum):
    IP1 = "ИП1"
    IP2 = "ИП2"
    IP3 = "ИП3"
    OOO = "ООО"

class BankTransaction(BaseModel):
    organization: Organization = Field(..., description="Организация")
    operation: OperationType = Field(..., description="Тип операции")
    method: str = Field(..., description="Метод операции")
    amount: float = Field(..., description="Сумма операции")
    date: str = Field(..., description="Дата операции")
    external_id: str = Field(..., description="Внешний ID транзакции")

class TransactionSummary(BaseModel):
    date: str = Field(..., description="Дата операции")
    operation: OperationType = Field(..., description="Тип операции")
    method: str = Field(..., description="Метод операции")
    amount: float = Field(..., description="Сумма операции")
    organization: Organization = Field(..., description="Организация")
    counterparty: str = Field(..., description="Контрагент")
    purpose: str = Field(..., description="Назначение платежа")

class DailyReport(BaseModel):
    date: str = Field(..., description="Дата отчета")
    organization: Organization = Field(..., description="Организация")
    total_income: float = Field(..., description="Общая сумма поступлений")
    total_expense: float = Field(..., description="Общая сумма списаний")

class MonthlyBalance(BaseModel):
    organization: Organization = Field(..., description="Организация")
    date: str = Field(..., description="Дата")
    balance: float = Field(..., description="Баланс")

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
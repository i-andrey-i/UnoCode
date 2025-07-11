from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, condecimal

class BankTransaction(BaseModel):
    """Модель банковской операции"""
    organization: str = Field(..., description="Организация (например: ИП1, ИП2, ИП3, ООО)")
    operation: str = Field(..., description="Тип операции (Поступление/Списание)")
    method: str = Field(..., description="Способ операции (Счет/Карта/Наличка/QR)")
    amount: condecimal(decimal_places=2) = Field(..., description="Сумма операции")
    date: date = Field(..., description="Дата операции")
    external_id: str = Field(..., description="Внешний идентификатор из Альфа-Банка")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Дата создания записи")

class BankResponse(BaseModel):
    """Модель ответа со списком банковских операций"""
    status: str = Field("success", description="Статус ответа")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время формирования ответа")
    data: List[BankTransaction] = Field(default_factory=list, description="Список банковских операций")

class BankSummaryItem(BaseModel):
    """Модель элемента сводки по банковским операциям"""
    organization: str = Field(..., description="Организация")
    operation: str = Field(..., description="Тип операции")
    method: str = Field(..., description="Способ операции")
    total_amount: condecimal(decimal_places=2) = Field(..., description="Общая сумма")

class BankSummaryResponse(BaseModel):
    """Модель ответа со сводкой по банковским операциям"""
    status: str = Field("success", description="Статус ответа")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время формирования ответа")
    data: List[BankSummaryItem] = Field(default_factory=list, description="Сводка по операциям")

class MonthlyBalance(BaseModel):
    """Модель месячного баланса"""
    organization: str = Field(..., description="Организация")
    date: date = Field(..., description="Дата")
    balance: condecimal(decimal_places=2) = Field(..., description="Текущий баланс")

class MonthlyBalanceResponse(BaseModel):
    """Модель ответа с месячными балансами"""
    status: str = Field("success", description="Статус ответа")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время формирования ответа")
    data: List[MonthlyBalance] = Field(default_factory=list, description="Список балансов")

class SyncResponse(BaseModel):
    """Модель ответа о результатах синхронизации"""
    status: str = Field(..., description="Статус синхронизации")
    total: int = Field(..., description="Всего обработано записей")
    success: int = Field(..., description="Успешно обработано")
    errors: int = Field(..., description="Количество ошибок")

class ErrorResponse(BaseModel):
    """Модель ответа с ошибкой"""
    status: str = Field("error", description="Статус ответа")
    message: str = Field(..., description="Описание ошибки")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время возникновения ошибки") 
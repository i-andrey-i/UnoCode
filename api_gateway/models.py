from typing import List, Dict, Optional
from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from decimal import Decimal

class ProductTransaction(BaseModel):
    organization: str = Field(..., description="Организация (ИП1/ИП2/ИП3/ООО)")
    operation: str = Field(..., description="Тип операции: Поступление/Расход")
    method: str = Field(..., description="Метод: Закупка/Перемещение/Реализация/Списание")
    item: str = Field(..., description="Наименование товара")
    date: datetime = Field(..., description="Дата операции")
    external_id: str = Field(..., description="Уникальный идентификатор из 1С")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания записи")

class ProductSummary(BaseModel):
    organization: str = Field(..., description="Организация (ИП1/ИП2/ИП3/ООО)")
    operation: str = Field(..., description="Тип операции: Поступление/Расход")
    count: int = Field(..., description="Количество операций")
    items: List[str] = Field(..., description="Список товаров")

class ProductResponse(BaseModel):
    status: str = Field(..., description="Статус ответа: success/error")
    date: Optional[datetime] = Field(None, description="Дата операции")
    data: List[ProductTransaction] = Field(..., description="Список товарных операций")

class ProductSummaryResponse(BaseModel):
    status: str = Field(..., description="Статус ответа: success/error")
    date: datetime = Field(..., description="Дата операции")
    data: List[ProductSummary] = Field(..., description="Список сводок по операциям")

class SyncResponse(BaseModel):
    status: str = Field(..., description="Статус ответа: success/error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Временная метка синхронизации")
    sync_results: Dict[str, Dict] = Field(..., description="Результаты синхронизации по сервисам")

class ErrorResponse(BaseModel):
    status: str = Field("error", description="Статус ответа: error")
    message: str = Field(..., description="Описание ошибки")
    timestamp: datetime = Field(default_factory=datetime.now, description="Временная метка ошибки")

# Модели для банковских операций
class BankTransaction(BaseModel):
    organization: str = Field(..., description="Организация (ИП1/ИП2/ИП3/ООО)")
    operation: str = Field(..., description="Тип операции: Поступление/Списание")
    method: str = Field(..., description="Метод: Счет/Карта/Наличка/QR")
    amount: condecimal(decimal_places=2) = Field(..., description="Сумма операции")
    date: datetime = Field(..., description="Дата операции")
    external_id: str = Field(..., description="Уникальный идентификатор из банка")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания записи")

class BankResponse(BaseModel):
    status: str = Field(..., description="Статус ответа: success/error")
    date: Optional[datetime] = Field(None, description="Дата операции")
    data: List[BankTransaction] = Field(..., description="Список банковских операций")

class DailyReportFinance(BaseModel):
    in_amount: condecimal(decimal_places=2) = Field(..., description="Сумма входящих операций")
    out_amount: condecimal(decimal_places=2) = Field(..., description="Сумма исходящих операций")
    details: Dict[str, condecimal(decimal_places=2)] = Field(..., description="Детализация по методам оплаты")

class DailyReportProducts(BaseModel):
    in_count: int = Field(..., description="Количество входящих операций")
    out_count: int = Field(..., description="Количество исходящих операций")
    details: Dict[str, int] = Field(..., description="Детализация по методам")

class DailyReportOrg(BaseModel):
    finance: DailyReportFinance
    products: DailyReportProducts

class DailyReport(BaseModel):
    status: str = Field(..., description="Статус ответа: success/error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Временная метка отчета")
    date: datetime = Field(..., description="Дата отчета")
    data: Dict[str, DailyReportOrg] = Field(..., description="Данные по организациям") 
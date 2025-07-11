from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field

class ProductTransaction(BaseModel):
    """Модель товарной операции"""
    organization: str = Field(..., description="Организация (например: ИП1, ИП2, ИП3, ООО)")
    operation: str = Field(..., description="Тип операции (Поступление/Расход)")
    method: str = Field(..., description="Способ операции (Закупка/Перемещение/Реализация/Списание)")
    item: str = Field(..., description="Наименование товара")
    date: date = Field(..., description="Дата операции")
    external_id: str = Field(..., description="Внешний идентификатор из 1С")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Дата создания записи")

class ProductResponse(BaseModel):
    """Модель ответа со списком товарных операций"""
    status: str = Field("success", description="Статус ответа")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время формирования ответа")
    data: List[ProductTransaction] = Field(default_factory=list, description="Список товарных операций")

class ProductSummaryItem(BaseModel):
    """Модель элемента сводки по товарным операциям"""
    organization: str = Field(..., description="Организация")
    operation: str = Field(..., description="Тип операции")
    method: str = Field(..., description="Способ операции")
    count: int = Field(..., description="Количество операций")

class ProductSummaryResponse(BaseModel):
    """Модель ответа со сводкой по товарным операциям"""
    status: str = Field("success", description="Статус ответа")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время формирования ответа")
    data: List[ProductSummaryItem] = Field(default_factory=list, description="Сводка по операциям")

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
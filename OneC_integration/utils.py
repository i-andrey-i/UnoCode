from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

def parse_1c_date(date_str: str) -> datetime:
    """
    Преобразование даты из формата 1С в datetime
    
    Args:
        date_str: Дата в формате строки из 1С
    """
    if not date_str:
        raise ValueError("Пустая строка даты")
        
    # Обработка различных форматов даты из 1С
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%d.%m.%Y %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    raise ValueError(f"Неподдерживаемый формат даты: {date_str}")

def format_1c_guid(guid: str) -> str:
    """
    Форматирование GUID для запросов к 1С
    
    Args:
        guid: GUID в любом формате
    """
    # Убираем все не-алфавитные и не-цифровые символы
    clean_guid = ''.join(c for c in guid if c.isalnum())
    return clean_guid.lower()

def parse_1c_number(number_str: str) -> Decimal:
    """
    Преобразование числа из формата 1С в Decimal
    
    Args:
        number_str: Число в формате строки из 1С
    """
    if not number_str:
        raise ValueError("Пустая строка числа")
        
    # Заменяем разделители
    clean_number = number_str.replace(',', '.').replace(' ', '')
    try:
        return Decimal(clean_number)
    except:
        raise ValueError(f"Неверный формат числа: {number_str}")

def build_odata_query(entity: str, filters: Dict[str, Any] = None, select: list = None, 
                     expand: list = None, orderby: list = None, top: int = None) -> str:
    """
    Построение OData запроса
    
    Args:
        entity: Имя сущности
        filters: Словарь с фильтрами
        select: Список полей для выборки
        expand: Список связанных сущностей для развертывания
        orderby: Список полей для сортировки
        top: Ограничение количества записей
    """
    query_parts = []
    
    # Фильтры
    if filters:
        filter_parts = []
        for key, value in filters.items():
            if isinstance(value, str):
                filter_parts.append(f"{key} eq '{value}'")
            elif isinstance(value, (int, float)):
                filter_parts.append(f"{key} eq {value}")
            elif isinstance(value, datetime):
                filter_parts.append(f"{key} eq {value.strftime('%Y-%m-%dT%H:%M:%S')}")
        if filter_parts:
            query_parts.append(f"$filter={' and '.join(filter_parts)}")
    
    # Выборка полей
    if select:
        query_parts.append(f"$select={','.join(select)}")
    
    # Развертывание связанных сущностей
    if expand:
        query_parts.append(f"$expand={','.join(expand)}")
    
    # Сортировка
    if orderby:
        query_parts.append(f"$orderby={','.join(orderby)}")
    
    # Ограничение количества
    if top:
        query_parts.append(f"$top={top}")
    
    return f"{entity}{'?' if query_parts else ''}&".join(query_parts) 
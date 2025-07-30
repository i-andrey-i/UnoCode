FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Добавляем пути к базам данных
ENV ONEC_DATABASE_PATH=/app/data/products.db
ENV ALFA_DATABASE_PATH=/app/data/transactions.db

WORKDIR /app

# Создаем директории для баз данных
RUN mkdir -p /app/data

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY app.py .
COPY OneC_integration/ OneC_integration/
COPY alfa_bank_integration/ alfa_bank_integration/

# Создаем непривилегированного пользователя
RUN adduser --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000 8001

CMD ["python", "app.py"]
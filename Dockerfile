FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY app.py .
COPY OneC_integration/ OneC_integration/
COPY alfa_bank_integration/ alfa_bank_integration/

EXPOSE 8000 8001

CMD ["python", "app.py"]
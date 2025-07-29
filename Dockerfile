FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1C Integration Service
FROM base as 1c_service
WORKDIR /app
COPY 1c_integration/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY 1c_integration/ .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Alfa Bank Integration Service
FROM base as alfa_service
WORKDIR /app
COPY alfa_bank_integration/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY alfa_bank_integration/ .
EXPOSE 8001
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
FROM python:3.10-slim

# Установить рабочую директорию
WORKDIR /app

# Установить переменные окружения для PYTHONPATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Установить зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копировать весь код
COPY . .

# Запустить бота
CMD ["python", "src/bot/main.py"] 
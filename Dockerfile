# Базовый образ с Python
FROM python:3.11-slim

# Рабочая папка внутри контейнера
WORKDIR /app

# Копируем зависимости (если есть requirements.txt)
COPY requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt || true

# Копируем всё остальное
COPY . /app

# Команда для запуска бота
CMD ["python", "main.py"]

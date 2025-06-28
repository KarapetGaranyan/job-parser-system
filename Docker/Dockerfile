# Job Parser System - Dockerfile
FROM python:3.11-slim

# Информация о образе
LABEL maintainer="Job Parser System"
LABEL description="Автоматическая система поиска и парсинга вакансий"
LABEL version="1.0"

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для безопасности
RUN groupadd -r jobparser && useradd -r -g jobparser jobparser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt для кеширования слоев
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Создаем директории для данных
RUN mkdir -p /app/data /app/logs && \
    chown -R jobparser:jobparser /app

# Переключаемся на непривилегированного пользователя
USER jobparser

# Открываем порт
EXPOSE 5000

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Переменные окружения по умолчанию
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///data/vacancies.db

# Команда запуска
CMD ["python", "app.py"]
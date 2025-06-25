# Job Parser System

Система автоматического парсинга вакансий с популярных сайтов с возможностью поиска и фильтрации данных.

## 🚀 Быстрый старт

### Использование Docker (рекомендуется)
```bash
# Клонировать репозиторий
git clone https://github.com/KarapetGaranyan/job-parser-system.git
cd job-parser-system

# Настроить переменные окружения
cp .env.example .env

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps
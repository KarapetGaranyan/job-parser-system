# 🔍 Job Parser System

Система автоматического поиска и парсинга вакансий с популярных job-сайтов России. Поддерживает HH.ru и SuperJob с возможностью автоматического планирования поисков.

## ✨ Возможности

- 🔍 **Поиск вакансий** на HH.ru и SuperJob
- 📍 **Фильтрация по городам** 
- 🕐 **Автоматический планировщик** для регулярного поиска
- 📊 **Статистика и аналитика** по собранным данным
- 💾 **База данных SQLite** для хранения вакансий
- 📤 **Экспорт данных** в CSV и текстовый формат
- 🌐 **Web интерфейс** с Bootstrap
- 🔌 **REST API** для интеграции
- 🧪 **Полное покрытие тестами**

## 🚀 Быстрый старт

### Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd job-parser-system

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### Настройка

Создайте файл `.env` в корневой папке:

```env
# Секретный ключ Flask
SECRET_KEY=your-secret-key-here

# База данных (опционально)
DATABASE_URL=sqlite:///vacancies.db

# API ключ SuperJob (опционально - есть дефолтный)
SUPERJOB_SECRET=your-superjob-api-key
```

### Запуск

```bash
python app.py
```

Приложение будет доступно по адресу: http://localhost:5000

## 📁 Структура проекта

```
job-parser-system/
├── app.py                 # Главный файл приложения
├── requirements.txt       # Зависимости Python
├── README.md             # Документация
├── .env                  # Конфигурация (создать самостоятельно)
│
├── parsers/              # Модули парсинга
│   ├── base_parser.py    # Базовый класс для всех парсеров
│   ├── hh_parser.py      # Парсер HH.ru
│   └── superjob_parser.py # Парсер SuperJob API
│
├── database/             # Модели базы данных
│   └── models.py         # SQLAlchemy модели
│
├── routes/               # Маршруты Flask
│   ├── __init__.py       # Регистрация blueprint'ов
│   ├── main_routes.py    # Основные страницы
│   ├── api_routes.py     # REST API
│   ├── export_routes.py  # Экспорт данных
│   └── scheduler_routes.py # Управление планировщиком
│
├── services/             # Бизнес-логика
│   ├── search_service.py    # Сервис поиска
│   ├── scheduler_service.py # Сервис планировщика
│   └── export_service.py    # Сервис экспорта
│
├── scheduler/            # Планировщик задач
│   └── simple_scheduler.py # Простой планировщик
│
├── utils/                # Утилиты
│   ├── search.py         # Утилиты поиска
│   └── export.py         # Утилиты экспорта
│
├── templates/            # HTML шаблоны
│   └── base.html         # Базовый шаблон
│
├── tests/                # Тесты
│   ├── test_parsers_documented.py # Unit тесты с описаниями
│   └── run_explained_tests.py     # Запуск тестов с объяснениями
│
└── static/               # Статические файлы (CSS, JS)
```

## 🔌 API Endpoints

### Основные маршруты

- `GET /` - Главная страница с формой поиска
- `GET /vacancies` - Страница всех вакансий
- `GET /stats` - Статистика
- `GET /scheduler` - Управление планировщиком

### REST API

- `GET /api/health` - Проверка работоспособности
- `POST /api/search` - Поиск вакансий
- `GET /api/vacancies` - Получение всех вакансий
- `GET /api/stats` - Статистика
- `DELETE /api/clear-db` - Очистка базы данных

### Планировщик API

- `GET /api/scheduler/status` - Статус планировщика
- `POST /api/scheduler/start` - Запуск планировщика
- `POST /api/scheduler/stop` - Остановка планировщика
- `POST /api/scheduler/add-search-job` - Добавить автоматический поиск
- `DELETE /api/scheduler/remove-job/<job_id>` - Удалить задачу

### Экспорт

- `GET /export/csv` - Экспорт в CSV
- `GET /export/text` - Экспорт в текст

## 💻 Использование

### Поиск вакансий через API

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"vacancy": "Python Developer", "city": "Москва"}'
```

### Настройка автоматического поиска

```bash
curl -X POST http://localhost:5000/api/scheduler/add-search-job \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "Python Developer\nДжанго разработчик\nBackend Python",
    "city": "Москва", 
    "interval_minutes": 60,
    "limit": 20,
    "run_immediately": true
  }'
```

## 🧪 Тестирование

Система включает подробные Unit тесты с человекопонятными объяснениями:

```bash
# Запуск всех тестов
python tests/run_explained_tests.py

# Интерактивное меню тестов
python tests/run_explained_tests.py --interactive

# Быстрые тесты
python tests/run_explained_tests.py --quick

# Тесты с покрытием кода
python tests/run_explained_tests.py --coverage
```

### Категории тестов

- 🏗️ **Базовый парсер** - тесты абстрактного класса
- 🔍 **HH.ru парсер** - тесты парсинга HH.ru
- 🔧 **SuperJob парсер** - тесты API SuperJob
- 🔗 **Интеграция** - тесты совместной работы
- 📁 **Структура** - тесты организации файлов

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `SECRET_KEY` | Секретный ключ Flask | `dev-secret-key` |
| `DATABASE_URL` | URL базы данных | `sqlite:///vacancies.db` |
| `SUPERJOB_SECRET` | API ключ SuperJob | Встроенный тестовый ключ |

### Настройка парсеров

**HH.ru парсер:**
- Использует веб-скрапинг
- Автоматическая обработка пагинации
- Задержки между запросами (0.3 сек)

**SuperJob парсер:**
- Использует официальный API
- Лимит запросов согласно API
- Задержки между запросами (0.5 сек)

## 🔒 Безопасность

- Защита от SQL инъекций через SQLAlchemy ORM
- Валидация входных данных
- Ограничение лимитов запросов
- Graceful обработка ошибок
- Санитизация пользовательского ввода

## 📊 Мониторинг

Система предоставляет:

- Логирование всех операций
- Статистику по источникам данных
- Мониторинг статуса планировщика
- Отчеты об ошибках парсинга

## 🚨 Ограничения

- **HH.ru**: Возможна блокировка при частых запросах
- **SuperJob**: Лимиты API (до 500 запросов/час для бесплатного ключа)
- **База данных**: SQLite подходит для разработки, для продакшена рекомендуется PostgreSQL

## 🤝 Разработка

### Добавление нового парсера

1. Создайте класс, наследующий от `BaseParser`
2. Реализуйте метод `search()`
3. Добавьте парсер в `SearchService`
4. Напишите тесты

```python
from parsers.base_parser import BaseParser

class NewSiteParser(BaseParser):
    def __init__(self):
        super().__init__('newsite')
    
    def search(self, query: str, limit: int = 20, city: str = ''):
        # Ваша логика парсинга
        return []
```

### Стиль кода

- Используйте docstring для всех методов
- Следуйте PEP 8
- Добавляйте логирование для важных операций
- Покрывайте новый код тестами

## 📝 Лицензия

MIT License - смотрите файл LICENSE для деталей.

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Запустите тесты: `python tests/run_explained_tests.py`
3. Проверьте статус планировщика: `/api/scheduler/status`
4. Убедитесь в корректности `.env` файла

## 🎯 Планы развития

- [ ] Добавление новых job-сайтов
- [ ] Telegram бот для уведомлений
- [ ] Машинное обучение для фильтрации релевантных вакансий  
- [ ] Docker контейнеризация
- [ ] Продвинутая аналитика и дашборды
- [ ] Интеграция с внешними HR системами
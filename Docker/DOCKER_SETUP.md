# 🐳 Docker установка Job Parser System

Полная инструкция по развертыванию системы парсинга вакансий в Docker.

## 🚀 Быстрый старт (для разработки)

### 1. **Клонирование и подготовка**

```bash
# Клонируем репозиторий
git clone <your-repository-url>
cd job-parser-system

# Копируем файл окружения
cp .env.docker .env

# Редактируем настройки (обязательно!)
nano .env
```

### 2. **Запуск простой конфигурации**

```bash
# Собираем и запускаем только основное приложение
docker-compose up -d jobparser

# Проверяем статус
docker-compose ps

# Смотрим логи
docker-compose logs -f jobparser
```

### 3. **Доступ к приложению**

Откройте браузер: **http://localhost:5000**

**Тестовые аккаунты:**
- `admin` / `admin123` (администратор)
- `user1` / `pass123` (пользователь) 
- `guest` / `guest789` (гость)

## 🏗️ Полная конфигурация (для продакшена)

### 1. **Настройка переменных окружения**

Отредактируйте файл `.env`:

```bash
# Обязательно смените!
SECRET_KEY=your-unique-secret-key-here
POSTGRES_PASSWORD=secure_database_password
GRAFANA_PASSWORD=secure_grafana_password

# API ключ SuperJob (опционально)
SUPERJOB_SECRET=your-superjob-api-key

# Для продакшена
FLASK_ENV=production
DEBUG=false
```

### 2. **Запуск всех сервисов**

```bash
# Запускаем полный стек
docker-compose up -d

# Проверяем все сервисы
docker-compose ps
```

### 3. **Доступные сервисы**

| Сервис | URL | Описание |
|--------|-----|-----------|
| **Job Parser** | http://localhost:5000 | Основное приложение |
| **PostgreSQL** | localhost:5432 | База данных |
| **Redis** | localhost:6379 | Кеширование |
| **Nginx** | http://localhost:80 | Веб-сервер |
| **Prometheus** | http://localhost:9090 | Мониторинг |
| **Grafana** | http://localhost:3000 | Дашборды |

## 📊 Мониторинг и логи

### **Просмотр логов:**

```bash
# Логи основного приложения
docker-compose logs -f jobparser

# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f postgres
```

### **Мониторинг ресурсов:**

```bash
# Статистика контейнеров
docker stats

# Использование томов
docker system df

# Состояние сервисов
docker-compose ps
```

## 🔧 Управление системой

### **Основные команды:**

```bash
# Запуск системы
docker-compose up -d

# Остановка системы
docker-compose down

# Перезапуск сервиса
docker-compose restart jobparser

# Обновление образов
docker-compose pull
docker-compose up -d --force-recreate

# Масштабирование (несколько экземпляров)
docker-compose up -d --scale jobparser=3
```

### **Управление данными:**

```bash
# Создание резервной копии БД
docker-compose exec postgres pg_dump -U jobparser jobparser > backup.sql

# Восстановление БД
docker-compose exec -T postgres psql -U jobparser jobparser < backup.sql

# Очистка логов
docker-compose exec jobparser truncate -s 0 /app/logs/*.log
```

## 🛠️ Настройка дополнительных сервисов

### **Nginx (для продакшена)**

Создайте файл `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream jobparser {
        server jobparser:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://jobparser;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Статические файлы
        location /static/ {
            alias /app/static/;
            expires 1y;
        }
    }
}
```

### **Prometheus мониторинг**

Создайте файл `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'jobparser'
    static_configs:
      - targets: ['jobparser:5000']
```

## 🔐 Безопасность

### **Настройки для продакшена:**

1. **Смените все пароли по умолчанию**
2. **Используйте HTTPS сертификаты**
3. **Настройте файрвол**
4. **Ограничьте доступ к портам БД**

```bash
# Создание SSL сертификатов
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/jobparser.key \
  -out nginx/ssl/jobparser.crt
```

## 🧪 Тестирование в Docker

### **Запуск тестов:**

```bash
# Запуск тестов в контейнере
docker-compose exec jobparser python run_explained_tests.py

# Или создание отдельного контейнера для тестов
docker build -t jobparser-test .
docker run --rm jobparser-test python run_explained_tests.py
```

## 🚨 Устранение неполадок

### **Частые проблемы:**

1. **Контейнер не запускается:**
```bash
# Проверяем логи
docker-compose logs jobparser

# Проверяем конфигурацию
docker-compose config
```

2. **База данных недоступна:**
```bash
# Проверяем PostgreSQL
docker-compose exec postgres psql -U jobparser -d jobparser -c "\l"

# Пересоздаем том БД
docker-compose down -v
docker-compose up -d
```

3. **Нет доступа к API:**
```bash
# Проверяем health check
curl http://localhost:5000/api/health

# Проверяем сеть
docker network ls
docker network inspect jobparser-network
```

4. **Медленная работа:**
```bash
# Увеличиваем ресурсы в docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
```

### **Очистка системы:**

```bash
# Полная очистка (ВНИМАНИЕ: удаляет все данные!)
docker-compose down -v --rmi all --remove-orphans

# Очистка только образов
docker-compose down --rmi all

# Очистка неиспользуемых ресурсов
docker system prune -a
```

## 📋 Checklist для продакшена

- [ ] Изменены все пароли по умолчанию
- [ ] Настроен HTTPS
- [ ] Настроен файрвол
- [ ] Настроено резервное копирование
- [ ] Настроен мониторинг
- [ ] Проведено нагрузочное тестирование
- [ ] Настроены логи и алерты
- [ ] Проверена безопасность

## 🎯 Готовые сценарии

### **Разработка:**
```bash
docker-compose up -d jobparser redis
```

### **Тестирование:**
```bash
docker-compose up -d jobparser postgres
```

### **Продакшен:**
```bash
docker-compose up -d
```

---

**🐳 Job Parser System готов к работе в Docker!**

Для получения помощи обращайтесь к основному README.md или изучайте логи системы.

📦 Созданные файлы:
1. Dockerfile

Многоступенчатый образ с оптимизацией
Безопасность (непривилегированный пользователь)
Health check для мониторинга
Все необходимые системные зависимости

2. docker-compose.yml

🚀 Основное приложение (jobparser)
🗄️ PostgreSQL для продакшена
🔄 Redis для кеширования
🌐 Nginx для проксирования
📊 Prometheus + Grafana для мониторинга
🔒 Настройки безопасности и ресурсов

3. .env.docker

Шаблон переменных окружения
Настройки для разработки и продакшена
Комментарии для каждой настройки

4. DOCKER_SETUP.md

📚 Полная документация по установке
🚀 Быстрый старт для разработчиков
🏗️ Конфигурация для продакшена
🛠️ Команды управления
🚨 Устранение неполадок

5. .dockerignore

Исключение ненужных файлов из образа
Оптимизация размера образа
Безопасность (исключение секретов)

🚀 Быстрый запуск:
bash# 1. Копируем переменные окружения
cp .env.docker .env

# 2. Редактируем настройки
nano .env

# 3. Запускаем систему
docker-compose up -d

# 4. Проверяем
curl http://localhost:5000/api/health
🎯 Варианты развертывания:
Для разработки:
bashdocker-compose up -d jobparser
Для тестирования:
bashdocker-compose up -d jobparser postgres
Для продакшена:
bashdocker-compose up -d




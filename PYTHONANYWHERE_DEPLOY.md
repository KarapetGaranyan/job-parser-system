# 🚀 Пошаговая инструкция деплоя на PythonAnywhere

## 📋 Предварительные требования

### 1. Аккаунт на PythonAnywhere
- Зарегистрируйтесь на [www.pythonanywhere.com](https://www.pythonanywhere.com)
- Выберите подходящий план (Beginner бесплатный)
- Подтвердите email

### 2. Git репозиторий
- Убедитесь, что ваш код находится в публичном Git репозитории
- Запомните URL репозитория (например: `https://github.com/username/job-parser-system`)

## 🔧 Шаг 1: Создание веб-приложения

### 1.1 Вход в PythonAnywhere
1. Войдите в свой аккаунт на PythonAnywhere
2. Перейдите в раздел **Web** в верхнем меню
3. Нажмите **Add a new web app**

### 1.2 Настройка домена
1. Выберите домен: `yourusername.pythonanywhere.com`
2. Нажмите **Next**

### 1.3 Выбор фреймворка
1. Выберите **Flask**
2. Выберите версию Python: **Python 3.11**
3. Нажмите **Next**

### 1.4 Настройка пути
1. Оставьте путь по умолчанию: `/home/yourusername/mysite/flask_app.py`
2. Нажмите **Next**

## 📥 Шаг 2: Загрузка кода

### 2.1 Открытие консоли
1. Перейдите в раздел **Consoles** в верхнем меню
2. Нажмите **Bash** для открытия терминала

### 2.2 Клонирование репозитория
```bash
# Переходим в домашнюю директорию
cd ~

# Клонируем репозиторий
git clone https://github.com/yourusername/job-parser-system.git

# Переходим в папку проекта
cd job-parser-system

# Проверяем содержимое
ls -la
```

### 2.3 Проверка файлов
Убедитесь, что все файлы загрузились:
```bash
# Должны быть файлы:
# - app.py
# - requirements.txt
# - Dockerfile
# - README.md
# и другие
```

## 🐍 Шаг 3: Настройка Python окружения

### 3.1 Создание виртуального окружения
```bash
# Создаем виртуальное окружение
python3.11 -m venv venv

# Активируем его
source venv/bin/activate

# Проверяем активацию (должен появиться (venv) в начале строки)
which python
```

### 3.2 Установка зависимостей
```bash
# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt

# Проверяем установку
pip list
```

## ⚙️ Шаг 4: Настройка WSGI файла

### 4.1 Открытие WSGI файла
1. Вернитесь в раздел **Web**
2. Нажмите на ссылку вашего веб-приложения
3. Найдите секцию **Code** и нажмите на файл `wsgi.py`

### 4.2 Замена содержимого
Замените содержимое файла на:

```python
#!/usr/bin/env python3
import sys
import os

# Добавляем путь к проекту
path = '/home/yourusername/job-parser-system'
if path not in sys.path:
    sys.path.append(path)

# Активируем виртуальное окружение
activate_this = '/home/yourusername/job-parser-system/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Импортируем приложение
from app import app as application

# Настройки для продакшена
if __name__ == "__main__":
    application.run()
```

### 4.3 Сохранение файла
1. Нажмите **Save** в редакторе
2. Закройте редактор

## 🔧 Шаг 5: Настройка переменных окружения

### 5.1 Создание .env файла
В консоли выполните:
```bash
# Переходим в папку проекта
cd ~/job-parser-system

# Создаем .env файл
nano .env
```

### 5.2 Добавление переменных
Вставьте в файл:
```env
# Основные настройки
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-12345
DEBUG=False

# База данных
DATABASE_URL=sqlite:///home/yourusername/job-parser-system/vacancies.db

# SuperJob API (опционально)
SUPERJOB_SECRET=your-superjob-api-key

# Настройки приложения
HOST=0.0.0.0
PORT=5000
```

### 5.3 Сохранение файла
1. Нажмите `Ctrl+X` для выхода
2. Нажмите `Y` для сохранения
3. Нажмите `Enter` для подтверждения имени файла

## 📁 Шаг 6: Настройка статических файлов

### 6.1 Создание папок
```bash
# Переходим в папку проекта
cd ~/job-parser-system

# Создаем папки для статических файлов
mkdir -p static/css static/js

# Проверяем структуру
ls -la static/
```

### 6.2 Копирование файлов
Убедитесь, что все статические файлы на месте:
```bash
# Проверяем CSS файлы
ls -la static/css/

# Проверяем JS файлы  
ls -la static/js/

# Проверяем шаблоны
ls -la templates/
```

## 🗄️ Шаг 7: Настройка базы данных

### 7.1 Инициализация базы
```bash
# Переходим в папку проекта
cd ~/job-parser-system

# Запускаем Python для инициализации БД
python3.11 -c "
from database.models import db, User
from app import app

with app.app_context():
    db.create_all()
    print('База данных создана успешно!')
"
```

### 7.2 Создание тестовых пользователей
```bash
# Создаем тестовых пользователей
python3.11 -c "
from database.models import db, User
from app import app
import json

with app.app_context():
    # Создаем тестовых пользователей
    users_data = {
        'admin': {'password': 'admin123', 'role': 'admin', 'expires': None},
        'user1': {'password': 'pass123', 'role': 'user', 'expires': '2025-12-31'},
        'guest': {'password': 'guest789', 'role': 'guest', 'expires': '2024-12-31'}
    }
    
    for username, data in users_data.items():
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role=data['role'], expires=data['expires'])
            user.set_password(data['password'])
            db.session.add(user)
    
    db.session.commit()
    print('Тестовые пользователи созданы!')
"
```

## 🔄 Шаг 8: Перезапуск приложения

### 8.1 Перезапуск через веб-интерфейс
1. Вернитесь в раздел **Web**
2. Нажмите на ссылку вашего веб-приложения
3. Нажмите кнопку **Reload yourusername.pythonanywhere.com**

### 8.2 Проверка логов
1. В разделе **Web** найдите секцию **Log files**
2. Нажмите на **Error log** для просмотра ошибок
3. Нажмите на **Server log** для просмотра серверных логов

## 🧪 Шаг 9: Тестирование

### 9.1 Проверка доступности
1. Откройте браузер
2. Перейдите по адресу: `https://yourusername.pythonanywhere.com`
3. Должна загрузиться главная страница приложения

### 9.2 Тестирование функций
1. **Поиск вакансий**: введите "Python" и нажмите "Найти"
2. **Авторизация**: попробуйте войти как `admin` / `admin123`
3. **Статистика**: перейдите в раздел "Статистика"
4. **Темная тема**: нажмите кнопку "Темная тема" в хедере

### 9.3 Проверка API
```bash
# Тестируем API поиска
curl "https://yourusername.pythonanywhere.com/api/search?q=Python&limit=5"
```

## 🔧 Шаг 10: Настройка домена (опционально)

### 10.1 Покупка домена
1. Купите домен у регистратора (например, Namecheap, GoDaddy)
2. Получите доступ к DNS настройкам

### 10.2 Настройка DNS
1. Добавьте CNAME запись:
   - **Name**: `www` или `@`
   - **Value**: `yourusername.pythonanywhere.com`
   - **TTL**: `3600`

### 10.3 Настройка в PythonAnywhere
1. В разделе **Web** нажмите **Add a new web app**
2. Выберите ваш домен
3. Настройте как описано выше

## 🚨 Устранение проблем

### Проблема: "ModuleNotFoundError"
```bash
# Решение: проверьте виртуальное окружение
cd ~/job-parser-system
source venv/bin/activate
pip list

# Переустановите зависимости
pip install -r requirements.txt
```

### Проблема: "Permission denied"
```bash
# Решение: проверьте права доступа
chmod +x ~/job-parser-system/app.py
chmod 755 ~/job-parser-system/static/
```

### Проблема: "Database locked"
```bash
# Решение: перезапустите приложение
# В разделе Web нажмите Reload
```

### Проблема: "Static files not found"
```bash
# Решение: проверьте структуру папок
ls -la ~/job-parser-system/static/
ls -la ~/job-parser-system/templates/
```

## 📊 Мониторинг

### Просмотр логов
1. **Error log**: ошибки приложения
2. **Server log**: серверные логи
3. **Access log**: запросы пользователей

### Проверка производительности
```bash
# Проверка использования памяти
free -h

# Проверка дискового пространства
df -h

# Проверка процессов
ps aux | grep python
```

## 🔄 Обновление приложения

### Обновление кода
```bash
# Переходим в папку проекта
cd ~/job-parser-system

# Получаем обновления
git pull origin main

# Обновляем зависимости
source venv/bin/activate
pip install -r requirements.txt

# Перезапускаем приложение
# В разделе Web нажмите Reload
```

### Резервное копирование
```bash
# Создаем резервную копию базы данных
cp ~/job-parser-system/vacancies.db ~/vacancies_backup.db

# Создаем резервную копию кода
cp -r ~/job-parser-system ~/job-parser-system-backup
```

## 🎯 Финальная проверка

### Чек-лист готовности
- [ ] Приложение доступно по адресу
- [ ] Поиск вакансий работает
- [ ] Авторизация работает
- [ ] Статистика отображается
- [ ] Темная тема переключается
- [ ] API отвечает корректно
- [ ] Логи не содержат ошибок

### Тестовые аккаунты
- **admin** / **admin123** - полный доступ
- **user1** / **pass123** - пользователь
- **guest** / **guest789** - гость

## 📞 Поддержка

### Полезные ссылки
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GitHub Issues](https://github.com/yourusername/job-parser-system/issues)

### Контакты
- Создайте Issue в GitHub репозитории
- Опишите проблему с деталями
- Приложите логи ошибок

---

**🎉 Поздравляем! Ваше приложение успешно развернуто на PythonAnywhere!**

**URL**: `https://yourusername.pythonanywhere.com`  
**Статус**: ✅ Работает  
**Версия**: 3.0  
**Последнее обновление**: Декабрь 2024 
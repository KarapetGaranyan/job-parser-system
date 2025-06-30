# ⚡ Быстрый деплой на PythonAnywhere

## 🚀 Экспресс-инструкция (5 минут)

### 1. Создание веб-приложения
```
Web → Add a new web app → yourusername.pythonanywhere.com → Flask → Python 3.11
```

### 2. Загрузка кода
```bash
cd ~
git clone https://github.com/yourusername/job-parser-system.git
cd job-parser-system
```

### 3. Настройка окружения
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Настройка WSGI
Замените содержимое `wsgi.py`:
```python
#!/usr/bin/env python3
import sys
path = '/home/yourusername/job-parser-system'
if path not in sys.path:
    sys.path.append(path)

activate_this = '/home/yourusername/job-parser-system/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application
```

### 5. Создание .env
```bash
nano .env
```
Содержимое:
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-12345
DEBUG=False
DATABASE_URL=sqlite:///home/yourusername/job-parser-system/vacancies.db
```

### 6. Инициализация БД
```bash
python3.11 -c "
from database.models import db, User
from app import app
with app.app_context():
    db.create_all()
    print('OK!')
"
```

### 7. Перезапуск
```
Web → Reload yourusername.pythonanywhere.com
```

### 8. Тест
Откройте: `https://yourusername.pythonanywhere.com`

## 🔑 Тестовые аккаунты
- `admin` / `admin123`
- `user1` / `pass123`
- `guest` / `guest789`

## 🚨 Частые проблемы

### "ModuleNotFoundError"
```bash
cd ~/job-parser-system
source venv/bin/activate
pip install -r requirements.txt
```

### "Permission denied"
```bash
chmod +x ~/job-parser-system/app.py
```

### "Database locked"
```
Web → Reload
```

## 📞 Логи
- **Error log**: ошибки приложения
- **Server log**: серверные логи
- **Access log**: запросы

## 🔄 Обновление
```bash
cd ~/job-parser-system
git pull
source venv/bin/activate
pip install -r requirements.txt
# Web → Reload
```

---
**✅ Готово! Приложение работает на PythonAnywhere!** 
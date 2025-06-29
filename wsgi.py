#!/usr/bin/env python3
"""
WSGI файл для развертывания на PythonAnywhere
"""

import sys
import os

# Добавляем путь к проекту
path = '/home/yourusername/job-parser-system'
if path not in sys.path:
    sys.path.append(path)

# Устанавливаем переменные окружения
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_URL'] = 'sqlite:///vacancies.db'

# Импортируем приложение
from app import app as application

# Для отладки
if __name__ == "__main__":
    application.run() 
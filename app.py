from flask import Flask
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
from database.models import init_db
from routes import register_routes

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    # Инициализация базы данных
    init_db()

    # Регистрация всех маршрутов
    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    print("🌐 Главная: http://localhost:5000")
    print("🕐 Планировщик: http://localhost:5000/scheduler")
    app.run(host='0.0.0.0', port=5000, debug=True)
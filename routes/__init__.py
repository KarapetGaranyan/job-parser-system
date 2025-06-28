from .main_routes import main_bp
from .api_routes import api_bp
from .export_routes import export_bp
from .scheduler_routes import scheduler_bp  # ДОБАВИТЬ ЭТУ СТРОКУ


def register_routes(app):
    """Регистрация всех blueprint'ов"""
    from .main_routes import main_bp
    from .api_routes import api_bp
    from .export_routes import export_bp
    from .scheduler_routes import scheduler_bp
    from auth.routes import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/export')
    app.register_blueprint(scheduler_bp, url_prefix='/api/scheduler')
    app.register_blueprint(auth_bp)  # ДОБАВИТЬ

    print("✅ Все маршруты зарегистрированы, включая планировщик")

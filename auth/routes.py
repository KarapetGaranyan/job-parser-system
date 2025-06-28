from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
import hashlib
import json
import os
import shutil

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Файл для хранения пользователей
USERS_FILE = 'users.json'


def load_users():
    """Загрузка пользователей из файла"""
    default_users = {
        'admin': {
            'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
            'expires': None,
            'role': 'admin'
        },
        'user1': {
            'password_hash': hashlib.sha256('pass123'.encode()).hexdigest(),
            'expires': datetime.now() + timedelta(days=30),
            'role': 'user'
        },
        'guest': {
            'password_hash': hashlib.sha256('guest789'.encode()).hexdigest(),
            'expires': datetime.now() + timedelta(hours=24),
            'role': 'guest'
        }
    }

    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)

                # Конвертируем строки дат обратно в datetime
                for username, user_data in users.items():
                    if user_data.get('expires'):
                        try:
                            if isinstance(user_data['expires'], str):
                                user_data['expires'] = datetime.fromisoformat(user_data['expires'])
                        except (ValueError, TypeError):
                            user_data['expires'] = None
                    else:
                        user_data['expires'] = None

                return users
        else:
            save_users(default_users)
            return default_users

    except Exception as e:
        print(f"Ошибка загрузки пользователей: {e}")
        return default_users


def save_users(users):
    """Сохранение пользователей в файл"""
    try:
        # Конвертируем datetime в строки для JSON
        users_to_save = {}
        for username, user_data in users.items():
            expires_str = None
            if user_data.get('expires'):
                if isinstance(user_data['expires'], datetime):
                    expires_str = user_data['expires'].isoformat()
                elif isinstance(user_data['expires'], str):
                    expires_str = user_data['expires']

            users_to_save[username] = {
                'password_hash': user_data['password_hash'],
                'expires': expires_str,
                'role': user_data['role']
            }

        # Создаем резервную копию безопасным способом
        if os.path.exists(USERS_FILE):
            backup_file = f"{USERS_FILE}.backup"
            if os.path.exists(backup_file):
                os.remove(backup_file)
            shutil.copy2(USERS_FILE, backup_file)

        # Сохраняем новые данные
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_to_save, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Ошибка сохранения пользователей: {e}")
        return False


def hash_password(password):
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_auth():
    """Проверка авторизации"""
    if 'user' not in session:
        return False

    username = session['user']
    users = load_users()

    if username not in users:
        session.clear()
        return False

    user = users[username]
    if user.get('expires'):
        expires_dt = user['expires']
        if isinstance(expires_dt, str):
            try:
                expires_dt = datetime.fromisoformat(expires_dt)
            except:
                expires_dt = None

        if expires_dt and datetime.now() > expires_dt:
            session.clear()
            return False

    return True


def get_expires_datetime(expires_value):
    """Безопасное получение datetime из различных форматов"""
    if not expires_value:
        return None

    if isinstance(expires_value, datetime):
        return expires_value

    if isinstance(expires_value, str):
        try:
            return datetime.fromisoformat(expires_value)
        except:
            return None

    return None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """Страница входа"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Введите логин и пароль', 'warning')
            return render_template('auth/login.html')

        users = load_users()

        if username in users:
            user = users[username]
            password_hash = hash_password(password)

            if user['password_hash'] == password_hash:
                # Проверка срока действия
                expires_dt = get_expires_datetime(user.get('expires'))
                if expires_dt and datetime.now() > expires_dt:
                    flash('Срок действия аккаунта истек', 'error')
                    return render_template('auth/login.html')

                # Успешная авторизация
                session['user'] = username
                session['role'] = user['role']
                session['expires'] = expires_dt.isoformat() if expires_dt else None

                flash(f'Добро пожаловать, {username}!', 'success')
                next_page = request.args.get('next', '/')
                return redirect(next_page)
            else:
                flash('Неверный пароль', 'error')
        else:
            flash('Пользователь не найден', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Выход из системы"""
    username = session.get('user', 'Пользователь')
    session.clear()
    flash(f'До свидания, {username}!', 'info')
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/profile')
def profile():
    """Профиль пользователя"""
    if not check_auth():
        flash('Необходима авторизация', 'warning')
        return redirect(url_for('auth.login_page'))

    return render_template('auth/profile.html')


@auth_bp.route('/admin')
def admin_panel():
    """Панель администратора"""
    if not check_auth():
        flash('Необходима авторизация', 'warning')
        return redirect(url_for('auth.login_page'))

    if session.get('role') != 'admin':
        flash('Доступ запрещен. Необходимы права администратора.', 'error')
        return redirect(url_for('main.index'))

    return render_template('auth/admin.html')


@auth_bp.route('/api/users')
def api_users():
    """API для получения списка пользователей"""
    if not check_auth() or session.get('role') != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403

    users = load_users()
    users_list = []

    for username, user_data in users.items():
        days_left = None
        is_expired = False
        expires_str = None

        expires_dt = get_expires_datetime(user_data.get('expires'))
        if expires_dt:
            expires_str = expires_dt.strftime('%Y-%m-%d')
            time_diff = expires_dt - datetime.now()
            days_left = time_diff.days
            is_expired = time_diff.total_seconds() <= 0

        user_info = {
            'username': username,
            'role': user_data['role'],
            'expires': expires_str,
            'days_left': days_left,
            'is_expired': is_expired
        }
        users_list.append(user_info)

    return jsonify(users_list)


@auth_bp.route('/admin/add_user', methods=['POST'])
def add_user():
    """Добавить пользователя"""
    if not check_auth() or session.get('role') != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('auth.login_page'))

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    try:
        days = int(request.form.get('days', 30))
    except (ValueError, TypeError):
        days = 30

    role = request.form.get('role', 'user')

    if not username or not password:
        flash('Заполните все поля', 'warning')
        return redirect(url_for('auth.admin_panel'))

    if len(username) < 3:
        flash('Логин должен содержать минимум 3 символа', 'warning')
        return redirect(url_for('auth.admin_panel'))

    if len(password) < 4:
        flash('Пароль должен содержать минимум 4 символа', 'warning')
        return redirect(url_for('auth.admin_panel'))

    users = load_users()

    if username in users:
        flash('Пользователь уже существует', 'error')
        return redirect(url_for('auth.admin_panel'))

    # Устанавливаем срок действия
    expires = None
    if days > 0:
        expires = datetime.now() + timedelta(days=days)

    users[username] = {
        'password_hash': hash_password(password),
        'expires': expires,
        'role': role
    }

    if save_users(users):
        expires_text = f"на {days} дней" if days > 0 else "бессрочно"
        flash(f'Пользователь {username} успешно добавлен ({expires_text})', 'success')
    else:
        flash('Ошибка при сохранении пользователя', 'error')

    return redirect(url_for('auth.admin_panel'))


@auth_bp.route('/admin/extend/<username>', methods=['POST'])
def extend_user_access(username):
    """Продлить доступ пользователю"""
    if not check_auth() or session.get('role') != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('auth.login_page'))

    users = load_users()

    if username not in users:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('auth.admin_panel'))

    try:
        days = int(request.form.get('days', 30))
    except (ValueError, TypeError):
        days = 30

    if days > 0:
        # Продлеваем доступ
        current_expires = get_expires_datetime(users[username].get('expires'))
        if current_expires:
            # Если у пользователя уже есть срок, продлеваем от текущего срока
            users[username]['expires'] = current_expires + timedelta(days=days)
        else:
            # Если доступ был бессрочным, устанавливаем новый срок от сегодня
            users[username]['expires'] = datetime.now() + timedelta(days=days)

        message = f'Доступ для {username} продлен на {days} дней'
    else:
        # Бессрочный доступ
        users[username]['expires'] = None
        message = f'Пользователю {username} предоставлен бессрочный доступ'

    if save_users(users):
        flash(message, 'success')
    else:
        flash('Ошибка при сохранении изменений', 'error')

    return redirect(url_for('auth.admin_panel'))


@auth_bp.route('/admin/delete/<username>', methods=['POST'])
def delete_user(username):
    """Удалить пользователя"""
    if not check_auth() or session.get('role') != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('auth.login_page'))

    current_user = session.get('user')

    if username == current_user:
        flash('Нельзя удалить самого себя', 'error')
        return redirect(url_for('auth.admin_panel'))

    users = load_users()

    if username in users:
        user_role = users[username]['role']
        del users[username]

        if save_users(users):
            flash(f'Пользователь {username} ({user_role}) удален', 'success')
        else:
            flash('Ошибка при удалении пользователя', 'error')
    else:
        flash('Пользователь не найден', 'error')

    return redirect(url_for('auth.admin_panel'))


@auth_bp.route('/debug/users')
def debug_users():
    """Отладочная информация о пользователях"""
    if not check_auth() or session.get('role') != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403

    users = load_users()

    debug_info = {
        'file_exists': os.path.exists(USERS_FILE),
        'file_size': os.path.getsize(USERS_FILE) if os.path.exists(USERS_FILE) else 0,
        'users_count': len(users),
        'users_list': list(users.keys()),
        'current_directory': os.getcwd(),
        'file_path': os.path.abspath(USERS_FILE)
    }

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            debug_info['file_content'] = f.read()

    return jsonify(debug_info)


@auth_bp.route('/api/user_info')
def api_user_info():
    """API для получения информации о текущем пользователе"""
    if not check_auth():
        return jsonify({'error': 'Не авторизован'}), 401

    username = session['user']
    users = load_users()

    if username not in users:
        return jsonify({'error': 'Пользователь не найден'}), 404

    user_data = users[username]
    expires_dt = get_expires_datetime(user_data.get('expires'))

    user_info = {
        'username': username,
        'role': user_data['role'],
        'expires': expires_dt.isoformat() if expires_dt else None,
        'days_left': (expires_dt - datetime.now()).days if expires_dt else None,
        'is_expired': expires_dt and datetime.now() > expires_dt if expires_dt else False
    }

    return jsonify(user_info)


@auth_bp.route('/check_session')
def check_session():
    """Проверка валидности сессии"""
    if check_auth():
        return jsonify({
            'valid': True,
            'user': session['user'],
            'role': session['role']
        })
    else:
        return jsonify({'valid': False}), 401
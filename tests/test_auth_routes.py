import sys
import os
import types
import json
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Мокаем open, os.path.exists, os.remove, shutil.copy2 для тестов
class DummyFile:
    def __init__(self):
        self.content = ''
        self.lines = []
    def write(self, data):
        self.content += data
    def read(self):
        return self.content
    def readline(self):
        if self.lines:
            return self.lines.pop(0)
        return ''
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def test_save_users():
    import builtins
    import auth.routes as ar
    orig_open = builtins.open
    orig_exists = os.path.exists
    orig_remove = os.remove
    import shutil
    orig_copy2 = shutil.copy2
    dummy_file = DummyFile()
    builtins.open = lambda file, mode='r', encoding=None: dummy_file
    os.path.exists = lambda path: False
    os.remove = lambda path: None
    shutil.copy2 = lambda src, dst: None
    try:
        users = {
            'user1': {
                'password_hash': 'hash',
                'expires': datetime(2024, 1, 1),
                'role': 'admin'
            }
        }
        ar.USERS_FILE = 'users.json'
        result = ar.save_users(users)
        assert result is True
        assert 'user1' in dummy_file.content
        print('test_save_users: OK')
    finally:
        builtins.open = orig_open
        os.path.exists = orig_exists
        os.remove = orig_remove
        shutil.copy2 = orig_copy2

def test_load_users():
    import builtins
    import auth.routes as ar
    orig_open = builtins.open
    dummy_file = DummyFile()
    users_data = {
        'user1': {
            'password_hash': 'hash',
            'expires': '2024-01-01T00:00:00',
            'role': 'admin'
        }
    }
    dummy_file.content = json.dumps(users_data)
    builtins.open = lambda file, mode='r', encoding=None: dummy_file
    try:
        ar.USERS_FILE = 'users.json'
        users = ar.load_users()
        assert 'user1' in users
        assert users['user1']['role'] == 'admin'
        print('test_load_users: OK')
    finally:
        builtins.open = orig_open

if __name__ == "__main__":
    test_save_users()
    test_load_users() 
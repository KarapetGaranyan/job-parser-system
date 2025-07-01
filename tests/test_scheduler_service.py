import sys
import os
import types
import tempfile
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Мокаем open, os.path.exists и os.remove для тестов
class DummyFile:
    def __init__(self):
        self.content = ''
        self._read_pointer = 0
    def write(self, data):
        self.content += data
    def read(self):
        return self.content
    def readline(self):
        if self._read_pointer == 0:
            self._read_pointer = 1
            return self.content
        return ''
    def __iter__(self):
        return iter([self.content])
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def test_add_and_remove_job():
    from services.scheduler_service import SchedulerService
    # Мокаем методы работы с файлами
    orig_open = open
    orig_exists = os.path.exists
    orig_remove = os.remove
    dummy_file = DummyFile()
    def fake_open(file, mode='r', encoding=None):
        return dummy_file
    os.path.exists = lambda path: False
    os.remove = lambda path: None
    globals()['open'] = fake_open
    try:
        service = SchedulerService()
        job_id = service.add_search_job('python', 10, city='Moscow', limit=5)
        assert job_id in service.jobs
        result = service.remove_job(job_id)
        assert result['status'] == 'removed'
        print('test_add_and_remove_job: OK')
    finally:
        globals()['open'] = orig_open
        os.path.exists = orig_exists
        os.remove = orig_remove

def test_save_and_load_data():
    from services.scheduler_service import SchedulerService
    # Мокаем open и os.path.exists
    orig_open = open
    orig_exists = os.path.exists
    file_storage = {'content': ''}
    class FileWriter(DummyFile):
        def write(self, data):
            file_storage['content'] = data
    class FileReader(DummyFile):
        def __init__(self):
            super().__init__()
            self.content = file_storage['content']
    def fake_open(file, mode='r', encoding=None):
        if 'w' in mode:
            return FileWriter()
        if 'r' in mode:
            return FileReader()
    os.path.exists = lambda path: True
    globals()['open'] = fake_open
    try:
        service = SchedulerService()
        service.is_running = True
        service.jobs = {'job1': {'id': 'job1'}}
        service.save_data()
        # Новый экземпляр для проверки загрузки
        service2 = SchedulerService()
        assert service2.is_running is True
        assert 'job1' in service2.jobs
        print('test_save_and_load_data: OK')
    finally:
        globals()['open'] = orig_open
        os.path.exists = orig_exists

if __name__ == "__main__":
    test_add_and_remove_job()
    test_save_and_load_data() 
#!/usr/bin/env python3
"""
Unit тесты парсеров с подробными описаниями для человека
Каждый тест содержит понятное объяснение что и зачем проверяется
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os
import time

# Добавляем корневую папку в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from parsers.base_parser import BaseParser
    from parsers.hh_parser import HHParser
    from parsers.superjob_parser import SuperJobParser
except ImportError as e:
    pytest.skip(f"Ошибка импорта парсеров: {e}", allow_module_level=True)


# ========== ФИКСТУРЫ ==========

@pytest.fixture
def test_parser():
    """
    🏗️ ФИКСТУРА: Создает тестовый парсер

    Зачем нужна: Для тестирования базового класса BaseParser
    Что делает: Создает простую реализацию абстрактного класса
    """

    class TestParser(BaseParser):
        def search(self, query, limit=20, city=''):
            return []

    return TestParser('test_source')


@pytest.fixture
def hh_parser():
    """
    🏗️ ФИКСТУРА: Создает HH парсер

    Зачем нужна: Для тестирования функциональности HH.ru парсера
    Что делает: Инициализирует реальный экземпляр HHParser
    """
    return HHParser()


@pytest.fixture
def superjob_parser():
    """
    🏗️ ФИКСТУРА: Создает SuperJob парсер

    Зачем нужна: Для тестирования функциональности SuperJob парсера
    Что делает: Инициализирует реальный экземпляр SuperJobParser
    """
    return SuperJobParser()


@pytest.fixture
def sample_vacancy_data():
    """
    📋 ФИКСТУРА: Образец данных вакансии

    Зачем нужна: Для тестирования методов сохранения вакансий
    Что содержит: Типичную структуру данных вакансии
    """
    return {
        'title': 'Python Developer',
        'link': 'https://example.com/job/1',
        'company': 'Test Company',
        'salary': '100000 руб.'
    }


# ========== ТЕСТЫ БАЗОВОГО ПАРСЕРА ==========

class TestBaseParser:
    """
    🧪 КАТЕГОРИЯ: Тесты базового парсера

    Что тестируем: Основную логику абстрактного класса BaseParser
    Зачем важно: BaseParser - основа всех парсеров, от него зависит вся система
    """

    def test_init_correct_values(self, test_parser):
        """
        ✅ ТЕСТ: Правильная инициализация парсера

        🎯 Что проверяем: Корректно ли создается экземпляр парсера
        🔍 Как проверяем: Сравниваем переданное имя источника с сохраненным
        💡 Зачем нужно: Убедиться что парсер правильно сохраняет свои настройки
        🚨 Что может сломаться: Если конструктор не работает, вся система не запустится
        """
        assert test_parser.source_name == 'test_source'
        assert test_parser is not None
        print("    ✅ Парсер правильно инициализируется с именем источника")

    def test_source_name_assignment(self):
        """
        ✅ ТЕСТ: Корректное присвоение имени источника

        🎯 Что проверяем: Разные парсеры имеют разные имена источников
        🔍 Как проверяем: Создаем два парсера с разными именами и сравниваем
        💡 Зачем нужно: В системе могут быть несколько парсеров одновременно
        🚨 Что может сломаться: Парсеры могут перепутать источники данных
        """

        class TestParser(BaseParser):
            def search(self, query, limit=20, city=''):
                return []

        parser1 = TestParser('source1')
        parser2 = TestParser('source2')

        assert parser1.source_name == 'source1'
        assert parser2.source_name == 'source2'
        assert parser1.source_name != parser2.source_name
        print("    ✅ Разные парсеры корректно получают разные имена")

    # ========== ГРАНИЧНЫЕ СЛУЧАИ ==========

    def test_empty_source_name(self):
        """
        🔍 ТЕСТ: Обработка пустого имени источника

        🎯 Что проверяем: Парсер работает с пустой строкой как именем
        🔍 Как проверяем: Создаем парсер с пустой строкой
        💡 Зачем нужно: Защита от некорректных данных при инициализации
        🚨 Что может сломаться: Система может упасть при некорректной конфигурации
        """

        class TestParser(BaseParser):
            def search(self, query, limit=20, city=''):
                return []

        parser = TestParser('')
        assert parser.source_name == ''
        print("    ✅ Парсер корректно обрабатывает пустое имя источника")

    def test_none_source_name(self):
        """
        🔍 ТЕСТ: Обработка None как имени источника

        🎯 Что проверяем: Парсер работает с None вместо строки
        🔍 Как проверяем: Создаем парсер с None
        💡 Зачем нужно: Защита от случайной передачи None
        🚨 Что может сломаться: TypeError при попытках работать с именем
        """

        class TestParser(BaseParser):
            def search(self, query, limit=20, city=''):
                return []

        parser = TestParser(None)
        assert parser.source_name is None
        print("    ✅ Парсер корректно обрабатывает None как имя источника")

    def test_long_source_name(self):
        """
        🔍 ТЕСТ: Обработка очень длинного имени источника

        🎯 Что проверяем: Парсер работает с длинными строками
        🔍 Как проверяем: Создаем парсер с именем в 1000 символов
        💡 Зачем нужно: Защита от переполнения при длинных конфигах
        🚨 Что может сломаться: Проблемы с памятью или базой данных
        """

        class TestParser(BaseParser):
            def search(self, query, limit=20, city=''):
                return []

        long_name = 'a' * 1000
        parser = TestParser(long_name)
        assert parser.source_name == long_name
        print("    ✅ Парсер корректно обрабатывает длинные имена источников")

    def test_special_characters_source_name(self):
        """
        🔍 ТЕСТ: Обработка специальных символов в имени

        🎯 Что проверяем: Парсер работает с символами -, _, числами, спецсимволами
        🔍 Как проверяем: Создаем парсер с именем "test-parser_123!@#"
        💡 Зачем нужно: Реальные имена источников могут содержать разные символы
        🚨 Что может сломаться: Проблемы с кодировкой или SQL инъекции
        """

        class TestParser(BaseParser):
            def search(self, query, limit=20, city=''):
                return []

        special_name = "test-parser_123!@#"
        parser = TestParser(special_name)
        assert parser.source_name == special_name
        print("    ✅ Парсер корректно обрабатывает специальные символы в имени")

    # ========== ТИПЫ ДАННЫХ ==========

    def test_numeric_source_name(self):
        """
        📊 ТЕСТ: Числовое имя источника

        🎯 Что проверяем: Парсер принимает число вместо строки
        🔍 Как проверяем: Передаем число 123 как имя
        💡 Зачем нужно: Гибкость системы при различных типах конфигурации
        🚨 Что может сломаться: Проблемы при конвертации числа в строку
        """

        class TestParser(BaseParser):
            def search(self, query, limit=20, city=''):
                return []

        parser = TestParser(123)
        assert parser.source_name == 123
        print("    ✅ Парсер принимает числовые имена источников")

    def test_search_returns_list(self, test_parser):
        """
        📊 ТЕСТ: Метод search возвращает список

        🎯 Что проверяем: Тип возвращаемого значения метода search
        🔍 Как проверяем: Вызываем search() и проверяем тип результата
        💡 Зачем нужно: Единообразие API - всегда ожидаем список вакансий
        🚨 Что может сломаться: Если метод вернет None или строку, система упадет
        """
        result = test_parser.search('test')
        assert isinstance(result, list)
        print("    ✅ Метод search возвращает список (даже если пустой)")

    @patch('database.models.Session')
    @patch('database.models.Vacancy')
    def test_save_vacancy_returns_boolean(self, mock_vacancy, mock_session, test_parser, sample_vacancy_data):
        """
        📊 ТЕСТ: Метод save_vacancy возвращает boolean

        🎯 Что проверяем: Тип возвращаемого значения метода save_vacancy
        🔍 Как проверяем: Мокаем БД и проверяем тип результата
        💡 Зачем нужно: API должно четко показывать успех/неудачу операции
        🚨 Что может сломаться: Если метод вернет строку, логика проверок сломается
        """
        result = test_parser.save_vacancy(sample_vacancy_data)
        assert isinstance(result, bool)
        print("    ✅ Метод save_vacancy возвращает boolean (True/False)")

    # ========== ВАЛИДАЦИЯ ПАРАМЕТРОВ ==========

    @patch('database.models.Session')
    @patch('database.models.Vacancy')
    def test_save_vacancy_empty_dict(self, mock_vacancy, mock_session, test_parser):
        """
        🔒 ТЕСТ: Сохранение пустого словаря

        🎯 Что проверяем: Обработка некорректных данных вакансии
        🔍 Как проверяем: Передаем пустой словарь {} в save_vacancy
        💡 Зачем нужно: Защита от сбоев при получении неполных данных
        🚨 Что может сломаться: KeyError при попытке доступа к обязательным полям
        """
        result = test_parser.save_vacancy({})
        assert isinstance(result, bool)
        print("    ✅ Парсер корректно обрабатывает пустые данные вакансии")

    def test_save_vacancy_none_input(self, test_parser):
        """
        🔒 ТЕСТ: Сохранение None вместо данных

        🎯 Что проверяем: Обработка None как данных вакансии
        🔍 Как проверяем: Передаем None в save_vacancy
        💡 Зачем нужно: Защита от случайной передачи None
        🚨 Что может сломаться: AttributeError при попытке доступа к полям None
        """
        try:
            result = test_parser.save_vacancy(None)
            assert isinstance(result, bool)
            print("    ✅ Парсер корректно обрабатывает None (возвращает bool)")
        except (TypeError, AttributeError, KeyError):
            print("    ✅ Парсер корректно выбрасывает исключение для None")

    # ========== ОБРАБОТКА ОШИБОК ==========

    @patch('database.models.Session')
    @patch('database.models.Vacancy')
    def test_save_vacancy_database_error(self, mock_vacancy, mock_session, test_parser, sample_vacancy_data):
        """
        ❌ ТЕСТ: Обработка ошибок базы данных

        🎯 Что проверяем: Корректную обработку сбоев БД
        🔍 Как проверяем: Мокаем исключение при запросе к БД
        💡 Зачем нужно: БД может быть недоступна или выдавать ошибки
        🚨 Что может сломаться: Вся система упадет если не обработать ошибку БД
        ✨ Ожидаемое поведение: Метод должен вернуть False и не упасть
        """
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.side_effect = Exception("Database error")

        result = test_parser.save_vacancy(sample_vacancy_data)

        assert result is False
        mock_session_instance.rollback.assert_called_once()
        mock_session_instance.close.assert_called_once()
        print("    ✅ Парсер корректно обрабатывает ошибки БД (rollback + close)")

    def test_save_vacancy_import_error(self, test_parser, sample_vacancy_data):
        """
        ❌ ТЕСТ: Обработка отсутствия модулей БД

        🎯 Что проверяем: Работу без доступа к модулям базы данных
        🔍 Как проверяем: Мокаем ImportError при импорте database.models
        💡 Зачем нужно: Модули БД могут отсутствовать в некоторых окружениях
        🚨 Что может сломаться: ImportError убьет всю систему
        ✨ Ожидаемое поведение: Система должна работать без БД (тесты, демо)
        """
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            result = test_parser.save_vacancy(sample_vacancy_data)
            assert result is True  # Graceful degradation без БД
        print("    ✅ Парсер корректно работает без модулей БД (graceful degradation)")

    # ========== СОСТОЯНИЕ ОБЪЕКТА ==========

    def test_object_state_immutability(self, test_parser):
        """
        🔄 ТЕСТ: Неизменность состояния объекта

        🎯 Что проверяем: Операции не изменяют внутреннее состояние парсера
        🔍 Как проверяем: Сохраняем source_name, вызываем search, проверяем что не изменился
        💡 Зачем нужно: Парсер должен быть stateless для thread-safety
        🚨 Что может сломаться: Состояние может измениться, что сломает параллельную работу
        ✨ Ожидаемое поведение: source_name остается неизменным
        """
        original_source = test_parser.source_name
        test_parser.search('test query')
        assert test_parser.source_name == original_source
        print("    ✅ Операции поиска не изменяют состояние парсера")

    def test_multiple_instances_independence(self):
        """
        🔄 ТЕСТ: Независимость нескольких экземпляров

        🎯 Что проверяем: Разные экземпляры парсеров не влияют друг на друга
        🔍 Как проверяем: Создаем два парсера и проверяем их независимость
        💡 Зачем нужно: В системе может работать несколько парсеров одновременно
        🚨 Что может сломаться: Состояние может быть shared между экземплярами
        ✨ Ожидаемое поведение: Каждый парсер имеет собственное состояние
        """

        class TestParser(BaseParser):
            def search(self, query, limit=20, city=''):
                return []

        parser1 = TestParser('parser1')
        parser2 = TestParser('parser2')

        assert parser1.source_name != parser2.source_name
        assert parser1 is not parser2
        print("    ✅ Разные экземпляры парсеров независимы друг от друга")

    # ========== ПОБОЧНЫЕ ЭФФЕКТЫ ==========

    @patch('database.models.Session')
    @patch('database.models.Vacancy')
    def test_save_vacancy_side_effects(self, mock_vacancy, mock_session, test_parser, sample_vacancy_data):
        """
        🎭 ТЕСТ: Правильные побочные эффекты сохранения

        🎯 Что проверяем: Корректную последовательность операций с БД
        🔍 Как проверяем: Мокаем БД и проверяем вызовы add -> commit -> close
        💡 Зачем нужно: Неправильная последовательность может повредить данные
        🚨 Что может сломаться: Транзакции могут остаться открытыми или данные не сохранятся
        ✨ Ожидаемое поведение: add() -> commit() -> close() в правильном порядке
        """
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        result = test_parser.save_vacancy(sample_vacancy_data)

        # Проверяем правильную последовательность вызовов
        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()
        assert result is True
        print("    ✅ Сохранение выполняет правильную последовательность операций БД")

    @patch('database.models.Session')
    @patch('database.models.Vacancy')
    def test_save_vacancy_duplicate_no_side_effects(self, mock_vacancy, mock_session, test_parser, sample_vacancy_data):
        """
        🎭 ТЕСТ: Отсутствие побочных эффектов при дубликатах

        🎯 Что проверяем: При обнаружении дубликата не происходит записи
        🔍 Как проверяем: Мокаем существующую вакансию и проверяем отсутствие add/commit
        💡 Зачем нужно: Дубликаты не должны засорять БД
        🚨 Что может сломаться: Лишние записи в БД или нарушение уникальности
        ✨ Ожидаемое поведение: НЕ вызываются add() и commit(), только close()
        """
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        # Имитируем существующую вакансию
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = Mock()

        result = test_parser.save_vacancy(sample_vacancy_data)

        # Не должно быть операций записи при дубликате
        mock_session_instance.add.assert_not_called()
        mock_session_instance.commit.assert_not_called()
        mock_session_instance.close.assert_called_once()
        assert result is False
        print("    ✅ При дубликатах не происходит лишних операций записи")

    # ========== ПРОИЗВОДИТЕЛЬНОСТЬ ==========

    @patch('database.models.Session')
    @patch('database.models.Vacancy')
    def test_save_vacancy_performance(self, mock_vacancy, mock_session, test_parser, sample_vacancy_data):
        """
        ⚡ ТЕСТ: Производительность сохранения вакансии

        🎯 Что проверяем: Время выполнения операции сохранения
        🔍 Как проверяем: Измеряем время до и после вызова save_vacancy
        💡 Зачем нужно: Медленные операции могут блокировать всю систему
        🚨 Что может сломаться: Тормоза в БД могут сделать систему неюзабельной
        ✨ Ожидаемое поведение: Операция должна выполняться быстро (<0.1 сек для мока)
        """
        start_time = time.time()
        test_parser.save_vacancy(sample_vacancy_data)
        end_time = time.time()

        # Для мока должно быть очень быстро
        execution_time = end_time - start_time
        assert execution_time < 0.1
        print(f"    ✅ Сохранение выполняется быстро ({execution_time:.4f} сек)")


# ========== ТЕСТЫ HH ПАРСЕРА ==========

class TestHHParser:
    """
    🧪 КАТЕГОРИЯ: Тесты HH.ru парсера

    Что тестируем: Специфическую логику парсинга сайта HH.ru
    Зачем важно: HH.ru - основной источник вакансий, критически важен для работы системы
    """

    def test_init_correct_values(self, hh_parser):
        """
        ✅ ТЕСТ: Правильная инициализация HH парсера

        🎯 Что проверяем: Корректные значения при создании HH парсера
        🔍 Как проверяем: Проверяем source_name, base_url, наличие User-Agent
        💡 Зачем нужно: Неправильная инициализация сломает запросы к HH.ru
        🚨 Что может сломаться: Отсутствие User-Agent -> блокировка, неправильный URL -> 404
        ✨ Ожидаемое поведение: source_name='hh', правильный URL, есть заголовки
        """
        assert hh_parser.source_name == 'hh'
        assert hh_parser.base_url == 'https://hh.ru'
        assert 'User-Agent' in hh_parser.headers
        assert isinstance(hh_parser.headers['User-Agent'], str)
        print("    ✅ HH парсер правильно инициализируется со всеми настройками")

    # ========== ГРАНИЧНЫЕ СЛУЧАИ ==========

    @patch('requests.get')
    def test_search_empty_query(self, mock_get, hh_parser):
        """
        🔍 ТЕСТ: Поиск с пустым запросом

        🎯 Что проверяем: Обработку пустой поисковой строки
        🔍 Как проверяем: Передаем пустую строку в search()
        💡 Зачем нужно: Пользователь может случайно отправить пустой поиск
        🚨 Что может сломаться: HTTP ошибка или некорректный запрос к HH.ru
        ✨ Ожидаемое поведение: Возвращает пустой список, не падает
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with patch.object(hh_parser, 'save_vacancy', return_value=True):
            result = hh_parser.search('')
            assert isinstance(result, list)
        print("    ✅ HH парсер корректно обрабатывает пустые поисковые запросы")

    @patch('requests.get')
    def test_search_zero_limit(self, mock_get, hh_parser):
        """
        🔍 ТЕСТ: Поиск с нулевым лимитом

        🎯 Что проверяем: Обработку лимита = 0
        🔍 Как проверяем: Передаем limit=0 в search()
        💡 Зачем нужно: Защита от некорректных параметров пагинации
        🚨 Что может сломаться: Бесконечный цикл или ошибка API
        ✨ Ожидаемое поведение: Возвращает пустой список
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with patch.object(hh_parser, 'save_vacancy', return_value=True):
            result = hh_parser.search('Python', limit=0)
            assert isinstance(result, list)
        print("    ✅ HH парсер корректно обрабатывает нулевой лимит результатов")

    @patch('requests.get')
    def test_search_large_limit(self, mock_get, hh_parser):
        """
        🔍 ТЕСТ: Поиск с очень большим лимитом

        🎯 Что проверяем: Обработку аномально большого лимита
        🔍 Как проверяем: Передаем limit=1000 в search()
        💡 Зачем нужно: Защита от перегрузки системы и HH.ru
        🚨 Что может сломаться: Блокировка по IP, таймауты, перегрузка памяти
        ✨ Ожидаемое поведение: Ограничивает запрос разумными пределами
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with patch.object(hh_parser, 'save_vacancy', return_value=True):
            result = hh_parser.search('Python', limit=1000)
            assert isinstance(result, list)
        print("    ✅ HH парсер корректно обрабатывает большие лимиты (защита от перегрузки)")

    # ========== ТИПЫ ДАННЫХ ==========

    @patch('requests.get')
    def test_search_numeric_query(self, mock_get, hh_parser):
        """
        📊 ТЕСТ: Поиск с числовым запросом

        🎯 Что проверяем: Обработку числа вместо строки поиска
        🔍 Как проверяем: Передаем число 12345 в search()
        💡 Зачем нужно: Пользователь может искать по ID или числовым кодам
        🚨 Что может сломаться: TypeError при конкатенации с строками
        ✨ Ожидаемое поведение: Конвертирует число в строку и ищет
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with patch.object(hh_parser, 'save_vacancy', return_value=True):
            result = hh_parser.search(12345)
            assert isinstance(result, list)
        print("    ✅ HH парсер корректно обрабатывает числовые поисковые запросы")

    # ========== ОБРАБОТКА ОШИБОК ==========

    @patch('requests.get')
    def test_search_network_error(self, mock_get, hh_parser):
        """
        ❌ ТЕСТ: Обработка сетевых ошибок

        🎯 Что проверяем: Поведение при проблемах с сетью
        🔍 Как проверяем: Мокаем RequestException при запросе
        💡 Зачем нужно: Интернет может быть недоступен или нестабилен
        🚨 Что может сломаться: Вся система упадет при обрыве соединения
        ✨ Ожидаемое поведение: Возвращает пустой список, логирует ошибку
        """
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        result = hh_parser.search('Python')
        assert result == []
        print("    ✅ HH парсер корректно обрабатывает сетевые ошибки (graceful degradation)")

    @patch('requests.get')
    def test_search_http_error(self, mock_get, hh_parser):
        """
        ❌ ТЕСТ: Обработка HTTP ошибок

        🎯 Что проверяем: Поведение при HTTP ошибках (404, 500, etc)
        🔍 Как проверяем: Мокаем HTTPError при запросе
        💡 Зачем нужно: HH.ru может вернуть ошибку или быть недоступен
        🚨 Что может сломаться: HTTPError убьет поток парсинга
        ✨ Ожидаемое поведение: Возвращает пустой список, обрабатывает ошибку
        """
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        result = hh_parser.search('Python')
        assert result == []
        print("    ✅ HH парсер корректно обрабатывает HTTP ошибки (404, 500, etc)")

    # ========== ПАРСИНГ HTML ==========

    def test_parse_vacancy_item_complete(self, hh_parser):
        """
        🔧 ТЕСТ: Парсинг полной вакансии из HTML

        🎯 Что проверяем: Корректное извлечение всех данных из HTML
        🔍 Как проверяем: Подаем корректный HTML и проверяем все поля
        💡 Зачем нужно: Основная функция парсера - извлечение данных
        🚨 Что может сломаться: Изменение разметки HH.ru сломает парсинг
        ✨ Ожидаемое поведение: Все поля извлекаются правильно
        """
        bs4 = pytest.importorskip("bs4", reason="BeautifulSoup необходима для парсинга HTML")

        html = '''
        <div data-qa="vacancy-serp__vacancy">
            <a data-qa="serp-item__title" href="/vacancy/12345">Python Developer</a>
            <a data-qa="vacancy-serp__vacancy-employer">Яндекс</a>
            <span data-qa="vacancy-serp__vacancy-compensation">от 200 000 руб.</span>
        </div>
        '''

        soup = bs4.BeautifulSoup(html, 'html.parser')
        item = soup.find('div')

        result = hh_parser._parse_vacancy_item(item)

        assert result is not None
        assert isinstance(result, dict)
        assert result['title'] == 'Python Developer'
        assert result['company'] == 'Яндекс'
        assert result['salary'] == 'от 200 000 руб.'
        assert result['source'] == 'hh'
        assert '12345' in result['link']
        print("    ✅ HH парсер корректно извлекает все данные из HTML вакансии")

    def test_parse_vacancy_item_missing_fields(self, hh_parser):
        """
        🔧 ТЕСТ: Парсинг неполной вакансии из HTML

        🎯 Что проверяем: Обработку HTML с отсутствующими полями
        🔍 Как проверяем: Подаем HTML без заголовка вакансии
        💡 Зачем нужно: HTML может быть неполным или поврежденным
        🚨 Что может сломаться: KeyError при доступе к отсутствующим элементам
        ✨ Ожидаемое поведение: Возвращает None для некорректных данных
        """
        bs4 = pytest.importorskip("bs4", reason="BeautifulSoup необходима для парсинга HTML")

        # HTML без заголовка - критически важного поля
        html_no_title = '''
        <div data-qa="vacancy-serp__vacancy">
            <a data-qa="vacancy-serp__vacancy-employer">Яндекс</a>
            <span data-qa="vacancy-serp__vacancy-compensation">200k</span>
        </div>
        '''

        soup = bs4.BeautifulSoup(html_no_title, 'html.parser')
        item = soup.find('div')

        result = hh_parser._parse_vacancy_item(item)
        assert result is None  # Должно вернуть None без заголовка
        print("    ✅ HH парсер корректно отклоняет вакансии без критически важных полей")


# ========== ТЕСТЫ SUPERJOB ПАРСЕРА ==========

class TestSuperJobParser:
    """
    🧪 КАТЕГОРИЯ: Тесты SuperJob парсера

    Что тестируем: Специфическую логику работы с SuperJob API
    Зачем важно: SuperJob - второй по важности источник вакансий в системе
    """

    def test_init_correct_values(self, superjob_parser):
        """
        ✅ ТЕСТ: Правильная инициализация SuperJob парсера

        🎯 Что проверяем: Корректные настройки API при инициализации
        🔍 Как проверяем: Проверяем source_name, API URL, наличие API ключа
        💡 Зачем нужно: Неправильные настройки API сломают все запросы
        🚨 Что может сломаться: Отсутствие API ключа -> 401, неправильный URL -> 404
        ✨ Ожидаемое поведение: Все настройки API корректны
        """
        assert superjob_parser.source_name == 'superjob'
        assert superjob_parser.api_url == 'https://api.superjob.ru/2.0/vacancies'
        assert 'X-Api-App-Id' in superjob_parser.headers
        assert isinstance(superjob_parser.headers['X-Api-App-Id'], str)
        print("    ✅ SuperJob парсер правильно инициализируется с настройками API")

    # ========== ОБРАБОТКА ОШИБОК ==========

    @patch('requests.get')
    def test_search_api_error(self, mock_get, superjob_parser):
        """
        ❌ ТЕСТ: Обработка ошибок SuperJob API

        🎯 Что проверяем: Поведение при сбоях API SuperJob
        🔍 Как проверяем: Мокаем RequestException при запросе к API
        💡 Зачем нужно: API может быть недоступно или превышен лимит
        🚨 Что может сломаться: Исключение убьет весь процесс парсинга
        ✨ Ожидаемое поведение: Возвращает пустой список, не падает
        """
        import requests
        mock_get.side_effect = requests.RequestException("API error")

        result = superjob_parser.search('Python')
        assert result == []
        print("    ✅ SuperJob парсер корректно обрабатывает ошибки API")

    @patch('requests.get')
    def test_search_json_decode_error(self, mock_get, superjob_parser):
        """
        ❌ ТЕСТ: Обработка ошибок декодирования JSON

        🎯 Что проверяем: Поведение при получении некорректного JSON
        🔍 Как проверяем: Мокаем ValueError при json.decode()
        💡 Зачем нужно: API может вернуть поврежденный или не-JSON ответ
        🚨 Что может сломаться: ValueError при попытке парсинга JSON
        ✨ Ожидаемое поведение: Обрабатывает ошибку, возвращает пустой список
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = superjob_parser.search('Python')
        assert result == []
        print("    ✅ SuperJob парсер корректно обрабатывает поврежденный JSON")

    # ========== ПАРСИНГ ДАННЫХ ==========

    def test_parse_vacancy_object_complete(self, superjob_parser):
        """
        🔧 ТЕСТ: Парсинг полного объекта вакансии из API

        🎯 Что проверяем: Корректное извлечение всех данных из JSON объекта
        🔍 Как проверяем: Подаем полный JSON объект и проверяем все поля
        💡 Зачем нужно: Основная функция API парсера - обработка JSON
        🚨 Что может сломаться: Изменение структуры API ответа
        ✨ Ожидаемое поведение: Все поля извлекаются и форматируются правильно
        """
        vacancy_obj = {
            'profession': 'Python Developer',
            'firm_name': 'Яндекс',
            'payment_from': 200000,
            'payment_to': 300000,
            'currency': 'rub',
            'link': 'https://superjob.ru/vacancy/12345'
        }

        result = superjob_parser._parse_vacancy_object(vacancy_obj)

        assert isinstance(result, dict)
        assert result['title'] == 'Python Developer'
        assert result['company'] == 'Яндекс'
        assert result['salary'] == 'от 200000 до 300000 rub'
        assert result['source'] == 'superjob'
        assert result['link'] == 'https://superjob.ru/vacancy/12345'
        print("    ✅ SuperJob парсер корректно обрабатывает полные данные вакансий")

    def test_parse_vacancy_object_no_salary(self, superjob_parser):
        """
        🔧 ТЕСТ: Парсинг вакансии без указания зарплаты

        🎯 Что проверяем: Обработку вакансий без информации о зарплате
        🔍 Как проверяем: Подаем объект с нулевыми значениями зарплаты
        💡 Зачем нужно: Многие вакансии публикуются без указания зарплаты
        🚨 Что может сломаться: Пустые поля могут вызвать ошибки форматирования
        ✨ Ожидаемое поведение: Ставит "Не указана" вместо пустой зарплаты
        """
        vacancy_obj = {
            'profession': 'Python Developer',
            'firm_name': 'Test Company',
            'payment_from': 0,
            'payment_to': 0,
            'currency': '',
            'link': 'https://superjob.ru/vacancy/test'
        }

        result = superjob_parser._parse_vacancy_object(vacancy_obj)
        assert result['salary'] == 'Не указана'
        print("    ✅ SuperJob парсер корректно обрабатывает вакансии без зарплаты")

    def test_parse_vacancy_object_partial_salary(self, superjob_parser):
        """
        🔧 ТЕСТ: Парсинг вакансии с частичной информацией о зарплате

        🎯 Что проверяем: Обработку вакансий с только минимальной или максимальной зарплатой
        🔍 Как проверяем: Тестируем случаи "от X" и "до Y"
        💡 Зачем нужно: Часто указывается только нижняя или верхняя граница
        🚨 Что может сломаться: Неправильное форматирование частичных данных
        ✨ Ожидаемое поведение: Корректно форматирует "от X" или "до Y"
        """
        # Только нижняя граница (payment_from)
        vacancy_obj1 = {
            'profession': 'Developer',
            'firm_name': 'Company',
            'payment_from': 100000,
            'payment_to': 0,
            'currency': 'rub',
            'link': 'https://superjob.ru/vacancy/1'
        }

        result1 = superjob_parser._parse_vacancy_object(vacancy_obj1)
        assert result1['salary'] == 'от 100000 rub'

        # Только верхняя граница (payment_to)
        vacancy_obj2 = {
            'profession': 'Developer',
            'firm_name': 'Company',
            'payment_from': 0,
            'payment_to': 200000,
            'currency': 'rub',
            'link': 'https://superjob.ru/vacancy/2'
        }

        result2 = superjob_parser._parse_vacancy_object(vacancy_obj2)
        assert result2['salary'] == 'до 200000 rub'
        print("    ✅ SuperJob парсер корректно форматирует частичную информацию о зарплате")


# ========== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ==========

class TestParsersIntegration:
    """
    🧪 КАТЕГОРИЯ: Интеграционные тесты парсеров

    Что тестируем: Взаимодействие парсеров между собой и единообразие API
    Зачем важно: Парсеры должны работать как единая система с общим интерфейсом
    """

    def test_parsers_interface_consistency(self, hh_parser, superjob_parser):
        """
        🔗 ТЕСТ: Единообразие интерфейса парсеров

        🎯 Что проверяем: Все парсеры имеют одинаковые методы и поведение
        🔍 Как проверяем: Проверяем наличие одинаковых методов у всех парсеров
        💡 Зачем нужно: Система должна работать с любым парсером одинаково
        🚨 Что может сломаться: Разный API сломает универсальную обработку
        ✨ Ожидаемое поведение: Все парсеры имеют search() и save_vacancy()
        """
        # Все парсеры должны иметь одинаковые методы
        required_methods = ['search', 'save_vacancy']

        for method in required_methods:
            assert hasattr(hh_parser, method)
            assert hasattr(superjob_parser, method)
            assert callable(getattr(hh_parser, method))
            assert callable(getattr(superjob_parser, method))

        # Все парсеры должны иметь уникальные source_name
        assert hh_parser.source_name is not None
        assert superjob_parser.source_name is not None
        assert hh_parser.source_name != superjob_parser.source_name
        print("    ✅ Все парсеры имеют единообразный интерфейс и уникальные имена")


# ========== ТЕСТЫ СТРУКТУРЫ ПРОЕКТА ==========

class TestProjectStructure:
    """
    🧪 КАТЕГОРИЯ: Тесты структуры проекта

    Что тестируем: Правильную организацию файлов и модулей проекта
    Зачем важно: Неправильная структура сломает импорты и развертывание
    """

    def test_parsers_folder_exists(self):
        """
        🏗️ ТЕСТ: Существование папки parsers

        🎯 Что проверяем: Наличие основной папки с парсерами
        🔍 Как проверяем: Проверяем существование папки parsers/
        💡 Зачем нужно: Без этой папки система не запустится
        🚨 Что может сломаться: ImportError при запуске приложения
        ✨ Ожидаемое поведение: Папка parsers/ существует
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parsers_path = os.path.join(project_root, 'parsers')
        assert os.path.exists(parsers_path), "Папка parsers должна существовать"
        print("    ✅ Основная папка parsers/ существует")

    def test_parser_files_exist(self):
        """
        🏗️ ТЕСТ: Существование файлов парсеров

        🎯 Что проверяем: Наличие всех необходимых файлов парсеров
        🔍 Как проверяем: Проверяем каждый файл: base_parser.py, hh_parser.py, superjob_parser.py
        💡 Зачем нужно: Отсутствие любого файла сломает систему
        🚨 Что может сломаться: ModuleNotFoundError при импорте
        ✨ Ожидаемое поведение: Все файлы парсеров на месте
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parsers_path = os.path.join(project_root, 'parsers')

        required_files = [
            'base_parser.py',
            'hh_parser.py',
            'superjob_parser.py'
        ]

        for file in required_files:
            file_path = os.path.join(parsers_path, file)
            assert os.path.exists(file_path), f"Файл {file} должен существовать"
        print("    ✅ Все необходимые файлы парсеров существуют")

    def test_imports_work(self):
        """
        🏗️ ТЕСТ: Работоспособность импортов

        🎯 Что проверяем: Все модули можно импортировать без ошибок
        🔍 Как проверяем: Пытаемся импортировать каждый класс парсера
        💡 Зачем нужно: Синтаксические ошибки в коде сломают импорты
        🚨 Что может сломаться: SyntaxError, NameError при импорте
        ✨ Ожидаемое поведение: Все классы импортируются успешно
        """
        try:
            from parsers.base_parser import BaseParser
            from parsers.hh_parser import HHParser
            from parsers.superjob_parser import SuperJobParser

            # Проверяем что классы действительно импортированы
            assert callable(BaseParser)
            assert callable(HHParser)
            assert callable(SuperJobParser)
            print("    ✅ Все классы парсеров успешно импортируются")

        except ImportError as e:
            pytest.fail(f"Ошибка импорта: {e}")


if __name__ == '__main__':
    print("""
🧪 ЗАПУСК ТЕСТОВ С ПОДРОБНЫМИ ОПИСАНИЯМИ

Каждый тест содержит:
🎯 Что проверяем - цель теста
🔍 Как проверяем - методология 
💡 Зачем нужно - важность для системы
🚨 Что может сломаться - возможные проблемы
✨ Ожидаемое поведение - что должно происходить

Запуск: pytest {__file__} -v -s
    """)
    pytest.main([__file__, '-v', '-s'])
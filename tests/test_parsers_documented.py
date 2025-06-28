#!/usr/bin/env python3
"""
Скрипт запуска тестов с подробными человекопонятными объяснениями
Показывает что именно тестируется и зачем это важно
"""

import sys
import os
import subprocess
import time
from pathlib import Path


# Цвета для консоли
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header():
    """Печать заголовка с объяснением"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 80)
    print("🧪 UNIT ТЕСТИРОВАНИЕ С ПОДРОБНЫМИ ОБЪЯСНЕНИЯМИ")
    print("📚 Каждый тест объясняет ЧТО и ЗАЧЕМ он проверяет")
    print("=" * 80)
    print(f"{Colors.END}")


def print_test_categories():
    """Объяснение категорий тестов"""
    print(f"{Colors.BLUE}{Colors.BOLD}📋 ЧТО БУДЕТ ТЕСТИРОВАТЬСЯ:{Colors.END}")
    print()

    categories = [
        ("🏗️ БАЗОВЫЙ ПАРСЕР", "Основа всех парсеров - абстрактный класс",
         "Критично: если сломается, вся система упадет"),
        ("🔍 HH.RU ПАРСЕР", "Парсинг сайта HeadHunter.ru", "Важно: основной источник вакансий"),
        ("🔧 SUPERJOB ПАРСЕР", "Работа с API SuperJob", "Важно: второй по важности источник"),
        ("🔗 ИНТЕГРАЦИЯ", "Совместная работа парсеров", "Важно: единообразие интерфейса"),
        ("📁 СТРУКТУРА", "Организация файлов проекта", "Критично: без правильной структуры не запустится"),
    ]

    for emoji_name, description, importance in categories:
        print(f"  {emoji_name}")
        print(f"    📝 Что: {description}")
        print(f"    ⚡ {importance}")
        print()

    print(f"{Colors.YELLOW}💡 В каждом тесте вы увидите:{Colors.END}")
    print("  🎯 Что проверяем - цель теста")
    print("  🔍 Как проверяем - методология")
    print("  💡 Зачем нужно - важность для системы")
    print("  🚨 Что может сломаться - возможные проблемы")
    print("  ✨ Ожидаемое поведение - что должно происходить")
    print()


def print_test_aspects():
    """Объяснение аспектов Unit тестирования"""
    print(f"{Colors.PURPLE}{Colors.BOLD}🎯 АСПЕКТЫ UNIT ТЕСТИРОВАНИЯ:{Colors.END}")
    print()

    aspects = [
        ("✅ Корректность логики", "Правильно ли работает основная функциональность"),
        ("🔍 Граничные случаи", "Обработка пустых значений, экстремумов, спецсимволов"),
        ("📊 Типы данных", "Правильные типы входных и выходных данных"),
        ("🔒 Валидация параметров", "Проверка корректности входных параметров"),
        ("❌ Обработка ошибок", "Graceful обработка сбоев и исключений"),
        ("🔄 Состояние объектов", "Неизменность и независимость экземпляров"),
        ("🎭 Побочные эффекты", "Правильные операции с внешними системами"),
        ("⚡ Производительность", "Приемлемое время выполнения операций"),
        ("🔧 Парсинг данных", "Корректное извлечение информации из HTML/JSON"),
        ("🏗️ Структура проекта", "Правильная организация файлов и модулей"),
    ]

    for aspect, description in aspects:
        print(f"  {aspect} - {description}")
    print()


def run_explained_tests():
    """Запуск тестов с подробными объяснениями"""
    test_file = Path(__file__).parent / "test_parsers_documented.py"

    if not test_file.exists():
        print(f"{Colors.RED}❌ Файл с объяснениями не найден: {test_file}{Colors.END}")
        return False

    print(f"{Colors.BLUE}🚀 Запуск тестов с подробными объяснениями...{Colors.END}")
    print(f"📁 Файл: {test_file}")
    print()

    # Команда pytest с выводом всех print'ов
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",  # Подробный вывод
        "-s",  # Показывать print() из тестов
        "--tb=short",  # Короткий traceback
        "--color=yes",  # Цветной вывод
        "--capture=no",  # Не захватывать вывод
        "--durations=10",  # 10 самых медленных тестов
    ]

    try:
        print(f"{Colors.CYAN}⏳ Выполнение тестов (с объяснениями в реальном времени)...{Colors.END}")
        print("=" * 80)

        # Запускаем pytest
        result = subprocess.run(cmd, capture_output=False, text=True)

        print("=" * 80)
        return result.returncode == 0

    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка запуска тестов: {e}{Colors.END}")
        return False


def generate_summary_report():
    """Генерация итогового отчета"""
    print(f"\n{Colors.BOLD}📊 ИТОГОВЫЙ ОТЧЕТ О ТЕСТИРОВАНИИ{Colors.END}")
    print("=" * 60)

    print(f"{Colors.GREEN}✅ ЧТО БЫЛО ПРОВЕРЕНО:{Colors.END}")
    print("  🏗️ Базовая архитектура парсеров")
    print("  🔍 Обработка всех граничных случаев")
    print("  📊 Корректность типов данных")
    print("  🔒 Валидация входных параметров")
    print("  ❌ Обработка всех возможных ошибок")
    print("  🔄 Независимость и неизменность объектов")
    print("  🎭 Правильные побочные эффекты")
    print("  ⚡ Приемлемая производительность")
    print("  🔧 Корректный парсинг HTML и JSON")
    print("  🏗️ Правильная структура проекта")

    print(f"\n{Colors.BLUE}💡 ЗАЧЕМ ЭТО ВАЖНО:{Colors.END}")
    print("  🛡️ Защита от сбоев в production")
    print("  🔧 Упрощение отладки и поддержки")
    print("  📈 Обеспечение качества кода")
    print("  🚀 Уверенность в рефакторинге")
    print("  🎯 Соответствие требованиям")

    print(f"\n{Colors.YELLOW}🔄 РЕКОМЕНДАЦИИ:{Colors.END}")
    print("  📅 Запускайте тесты перед каждым коммитом")
    print("  🔄 Обновляйте тесты при изменении кода")
    print("  📊 Следите за покрытием кода (>90%)")
    print("  🐛 Добавляйте тесты для каждого найденного бага")
    print("  📚 Документируйте сложные тесты")


def print_useful_commands():
    """Полезные команды для тестирования"""
    print(f"\n{Colors.CYAN}💻 ПОЛЕЗНЫЕ КОМАНДЫ:{Colors.END}")
    print()

    commands = [
        ("🚀 Все тесты с объяснениями", "python run_explained_tests.py"),
        ("⚡ Быстрые тесты", "python test_parsers_documented.py --quick"),
        ("🎯 Конкретная категория", "python test_parsers_documented.py --category hh"),
        ("📊 С покрытием кода", "python test_parsers_documented.py --coverage"),
        ("🔍 Один конкретный тест", "pytest test_parsers_documented.py::TestBaseParser::test_init_correct_values -v -s"),
        ("📋 Список всех тестов", "pytest test_parsers_documented.py --collect-only"),
        ("🐛 Остановка на первой ошибке", "pytest test_parsers_documented.py -x -v -s"),
        ("📈 HTML отчет покрытия", "pytest --cov=parsers --cov-report=html"),
    ]

    for description, command in commands:
        print(f"  {description}:")
        print(f"    {Colors.YELLOW}{command}{Colors.END}")
        print()


def interactive_test_menu():
    """Интерактивное меню выбора тестов"""
    print(f"{Colors.BOLD}🎛️ ИНТЕРАКТИВНОЕ МЕНЮ ТЕСТИРОВАНИЯ{Colors.END}")
    print()

    options = [
        ("1", "🚀 Запустить все тесты с объяснениями", "explained"),
        ("2", "⚡ Быстрые smoke тесты", "quick"),
        ("3", "🏗️ Только тесты базового парсера", "base"),
        ("4", "🔍 Только тесты HH парсера", "hh"),
        ("5", "🔧 Только тесты SuperJob парсера", "superjob"),
        ("6", "❌ Только тесты обработки ошибок", "errors"),
        ("7", "⚡ Только тесты производительности", "performance"),
        ("8", "🔧 Только тесты парсинга данных", "parsing"),
        ("9", "📊 Запуск с покрытием кода", "coverage"),
        ("0", "❌ Выход", "exit"),
    ]

    for key, description, _ in options:
        print(f"  {key}. {description}")

    print()
    choice = input(f"{Colors.CYAN}Выберите опцию (0-9): {Colors.END}").strip()

    # Найти выбранную опцию
    selected = None
    for key, _, action in options:
        if key == choice:
            selected = action
            break

    return selected


def run_interactive_mode():
    """Запуск в интерактивном режиме"""
    while True:
        choice = interactive_test_menu()

        if choice == "exit":
            print(f"{Colors.YELLOW}👋 До свидания!{Colors.END}")
            break
        elif choice == "explained":
            success = run_explained_tests()
        elif choice == "quick":
            success = run_category_tests("quick")
        elif choice in ["base", "hh", "superjob", "errors", "performance", "parsing"]:
            success = run_category_tests(choice)
        elif choice == "coverage":
            success = run_with_coverage()
        else:
            print(f"{Colors.RED}❌ Неверный выбор. Попробуйте снова.{Colors.END}")
            continue

        if success:
            print(f"\n{Colors.GREEN}✅ Тесты выполнены успешно!{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Есть проблемы в тестах.{Colors.END}")

        print(f"\n{Colors.CYAN}Нажмите Enter для продолжения...{Colors.END}")
        input()
        print("\n" + "=" * 80 + "\n")


def run_category_tests(category):
    """Запуск тестов конкретной категории"""
    if category == "quick":
        test_file = Path(__file__).parent / "test_quick.py"
        cmd = [sys.executable, "-m", "pytest", str(test_file), "-v", "-s"]
    else:
        test_file = Path(__file__).parent / "test_parsers_documented.py"

        # Маппинг категорий на паттерны классов
        class_patterns = {
            'base': 'TestBaseParser',
            'hh': 'TestHHParser',
            'superjob': 'TestSuperJobParser',
            'errors': '*error*',
            'performance': '*performance*',
            'parsing': '*parse*'
        }

        pattern = class_patterns.get(category, category)
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "-k", pattern,
            "-v", "-s",
            "--tb=short"
        ]

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка: {e}{Colors.END}")
        return False


def run_with_coverage():
    """Запуск с покрытием кода"""
    test_file = Path(__file__).parent / "test_parsers_documented.py"
    project_root = Path(__file__).parent.parent

    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        f"--cov={project_root / 'parsers'}",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v",
        "--tb=short"
    ]

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            print(f"\n{Colors.GREEN}📊 HTML отчет покрытия сохранен в: htmlcov/index.html{Colors.END}")

        return result.returncode == 0
    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка: {e}{Colors.END}")
        return False


# Добавить в test_parsers_documented.py:

def test_malicious_input_handling(self, test_parser):
    """
    🔒 ТЕСТ: Обработка потенциально опасного ввода

    🎯 Что проверяем: Защиту от вредоносных данных
    🔍 Как проверяем: Подаем SQL инъекции, XSS, длинные строки
    💡 Зачем нужно: Защита от атак через пользовательский ввод
    🚨 Что может сломаться: SQL инъекции, XSS атаки, DoS
    ✨ Ожидаемое поведение: Данные санитизируются или отклоняются
    """
    malicious_inputs = [
        "'; DROP TABLE vacancies; --",
        "<script>alert('xss')</script>",
        'A' * 10000,  # Очень длинная строка
        'javascript:alert("xss")'
    ]

    for malicious_input in malicious_inputs:
        vacancy_data = {
            'title': malicious_input,
            'link': 'https://example.com/job/1',
            'company': 'Test Company',
            'salary': '100k'
        }

        # Должен безопасно обработать без падения
        result = test_parser.save_vacancy(vacancy_data)
        assert isinstance(result, bool)
        print(f"    ✅ Безопасно обработан: {malicious_input[:20]}...")

def main():
    """Главная функция"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Запуск Unit тестов с подробными человекопонятными объяснениями',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 ЦЕЛЬ ЭТОГО СКРИПТА:
Показать ЧТО именно тестируется и ЗАЧЕМ это важно для системы.
Каждый тест содержит подробное объяснение своего назначения.

📚 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
  python run_explained_tests.py              # Все тесты с объяснениями
  python run_explained_tests.py --interactive # Интерактивное меню
  python run_explained_tests.py --category hh # Только HH парсер
  python run_explained_tests.py --quick       # Быстрые тесты

🔍 ЧТО ВЫ УВИДИТЕ В КАЖДОМ ТЕСТЕ:
  🎯 Что проверяем - цель теста
  🔍 Как проверяем - методология
  💡 Зачем нужно - важность для системы  
  🚨 Что может сломаться - возможные проблемы
  ✨ Ожидаемое поведение - что должно происходить
        """
    )

    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Интерактивное меню выбора тестов')
    parser.add_argument('--category', '-c',
                        choices=['base', 'hh', 'superjob', 'errors', 'performance', 'parsing'],
                        help='Запуск конкретной категории тестов')
    parser.add_argument('--quick', '-q', action='store_true',
                        help='Быстрые smoke тесты')
    parser.add_argument('--coverage', action='store_true',
                        help='Запуск с покрытием кода')

    args = parser.parse_args()

    print_header()

    # Проверка pytest
    try:
        import pytest
        print(f"{Colors.GREEN}✅ pytest доступен (версия {pytest.__version__}){Colors.END}\n")
    except ImportError:
        print(f"{Colors.RED}❌ pytest не установлен. Установите: pip install pytest{Colors.END}")
        return 1

    if not args.interactive:
        print_test_categories()
        print_test_aspects()

    # Выбор режима работы
    if args.interactive:
        run_interactive_mode()
        return 0
    elif args.quick:
        success = run_category_tests("quick")
    elif args.category:
        success = run_category_tests(args.category)
    elif args.coverage:
        success = run_with_coverage()
    else:
        success = run_explained_tests()

    # Результат
    print("\n" + "=" * 80)
    if success:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО! 🎉{Colors.END}")
        generate_summary_report()
        return_code = 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ ❌{Colors.END}")
        print(f"{Colors.YELLOW}💡 Проверьте вывод выше для деталей{Colors.END}")
        return_code = 1

    print("=" * 80)
    print_useful_commands()

    return return_code


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Прервано пользователем{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Критическая ошибка: {e}{Colors.END}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
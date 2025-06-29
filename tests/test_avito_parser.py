import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.avito_parser import AvitoParser
import unittest
from unittest.mock import patch, MagicMock


class TestAvitoParser(unittest.TestCase):
    """Тесты для парсера Avito"""

    def setUp(self):
        self.parser = AvitoParser()

    def test_init(self):
        """Тест инициализации парсера"""
        self.assertEqual(self.parser.source_name, 'avito')
        self.assertEqual(self.parser.base_url, 'https://www.avito.ru')
        self.assertIn('User-Agent', self.parser.headers)

    @patch('requests.get')
    def test_search_success(self, mock_get):
        """Тест успешного поиска"""
        # Мокаем ответ от сервера
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <body>
                <div data-marker="item">
                    <a data-marker="item-title" href="/test/vacancy1">Тестовая вакансия 1</a>
                    <div data-marker="item-specific-params">ООО Тест Компания</div>
                    <span data-marker="item-price">50000 руб</span>
                    <div data-marker="item-address">Москва</div>
                </div>
                <div data-marker="item">
                    <a data-marker="item-title" href="/test/vacancy2">Тестовая вакансия 2</a>
                    <div data-marker="item-specific-params">ИП Тест</div>
                    <span data-marker="item-price">60000 руб</span>
                    <div data-marker="item-address">Санкт-Петербург</div>
                </div>
            </body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Выполняем поиск
        result = self.parser.search('python developer', limit=2)

        # Проверяем результаты
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Тестовая вакансия 1')
        self.assertEqual(result[0]['company'], 'ООО Тест Компания')
        self.assertEqual(result[0]['salary'], '50000 руб')
        self.assertEqual(result[0]['location'], 'Москва')
        self.assertEqual(result[0]['source'], 'avito')

    @patch('requests.get')
    def test_search_with_city(self, mock_get):
        """Тест поиска с указанием города"""
        mock_response = MagicMock()
        mock_response.text = '<html><body></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Выполняем поиск с городом
        self.parser.search('python developer', city='Москва', limit=1)

        # Проверяем, что город был добавлен в запрос
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('python developer Москва', call_args[1]['params']['q'])

    @patch('requests.get')
    def test_search_error_handling(self, mock_get):
        """Тест обработки ошибок"""
        mock_get.side_effect = Exception('Connection error')

        # Выполняем поиск
        result = self.parser.search('python developer', limit=1)

        # Проверяем, что возвращается пустой список при ошибке
        self.assertEqual(result, [])

    def test_parse_vacancy_item(self):
        """Тест парсинга отдельной вакансии"""
        from bs4 import BeautifulSoup

        html = '''
        <div data-marker="item">
            <a data-marker="item-title" href="/test/vacancy">Python Developer</a>
            <div data-marker="item-specific-params">ООО Тест</div>
            <span data-marker="item-price">80000 руб</span>
            <div data-marker="item-address">Москва, центр</div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find('div', {'data-marker': 'item'})

        result = self.parser._parse_vacancy_item(item)

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Python Developer')
        self.assertEqual(result['company'], 'ООО Тест')
        self.assertEqual(result['salary'], '80000 руб')
        self.assertEqual(result['location'], 'Москва, центр')
        self.assertEqual(result['source'], 'avito')

    def test_parse_vacancy_item_missing_data(self):
        """Тест парсинга вакансии с отсутствующими данными"""
        from bs4 import BeautifulSoup

        html = '''
        <div data-marker="item">
            <a data-marker="item-title" href="/test/vacancy">Python Developer</a>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find('div', {'data-marker': 'item'})

        result = self.parser._parse_vacancy_item(item)

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Python Developer')
        self.assertEqual(result['company'], 'Не указана')
        self.assertEqual(result['salary'], 'Не указана')
        self.assertEqual(result['location'], '')


if __name__ == '__main__':
    unittest.main() 
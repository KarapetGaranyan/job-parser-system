import unittest
from unittest.mock import patch, MagicMock
from parsers.hh_parser import HHParser
from parsers.superjob_parser import SuperJobParser


class TestParsers(unittest.TestCase):
    """Тесты для парсеров"""

    def setUp(self):
        """Подготовка к тестам"""
        self.hh_parser = HHParser()
        self.sj_parser = SuperJobParser()

    @patch('parsers.hh_parser.requests.get')
    def test_hh_parser_search(self, mock_get):
        """Тест поиска на HH.ru"""
        # Мокаем ответ от HH.ru
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <div data-qa="vacancy-serp__vacancy">
            <a data-qa="serp-item__title" href="/vacancy/123">Python разработчик</a>
            <a data-qa="vacancy-serp__vacancy-employer">ООО Компания</a>
            <span data-qa="vacancy-serp__vacancy-compensation">100 000 руб.</span>
        </div>
        '''
        mock_get.return_value = mock_response

        results = self.hh_parser.search('python', limit=1)

        self.assertTrue(len(results) > 0)
        self.assertIn('title', results[0])
        self.assertIn('company', results[0])
        self.assertIn('salary', results[0])

    @patch('parsers.superjob_parser.requests.get')
    def test_superjob_parser_search(self, mock_get):
        """Тест поиска в SuperJob"""
        # Мокаем ответ от SuperJob API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'objects': [{
                'profession': 'Python разработчик',
                'link': 'https://superjob.ru/vacancy/123',
                'firm_name': 'ООО Компания',
                'payment_from': 100000,
                'payment_to': 150000,
                'currency': 'rub'
            }],
            'more': False
        }
        mock_get.return_value = mock_response

        results = self.sj_parser.search('python', limit=1)

        self.assertTrue(len(results) > 0)
        self.assertIn('title', results[0])
        self.assertIn('company', results[0])
        self.assertIn('salary', results[0])


if __name__ == '__main__':
    unittest.main()

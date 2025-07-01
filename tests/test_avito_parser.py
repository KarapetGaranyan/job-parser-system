import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parsers.avito_parser import AvitoParser

def test_avito_parser_search():
    parser = AvitoParser()
    result = parser.search('python')
    assert result == []
    print('test_avito_parser_search: OK')

if __name__ == "__main__":
    test_avito_parser_search() 
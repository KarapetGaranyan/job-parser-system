from .base_parser import BaseParser
from typing import List, Dict


class AvitoParser(BaseParser):
    """Заглушка для Avito парсера - не работает через requests"""

    def __init__(self):
        super().__init__('avito')

    def search(self, query: str, limit: int = 20, city: str = '') -> List[Dict]:
        """Avito не работает через requests из-за блокировок"""
        print(f"🚫 Avito: Парсинг отключен")
        print(f"   Причина: Avito блокирует автоматические запросы (QRATOR)")
        print(f"   Решение: Используйте Selenium или откажитесь от Avito")
        print(f"   Альтернативы: HH.ru и SuperJob работают отлично через API")
        
        return [] 
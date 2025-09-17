# src/domain/repositories/patent_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.patent import Patent


class PatentRepository(ABC):
    """Абстрактный интерфейс для работы с патентами"""
    
    @abstractmethod
    async def search_by_query(self, query: str, limit: int = 10) -> List[Patent]:
        """Поиск патентов по запросу"""
        pass

    @abstractmethod
    async def search_similar(self, text: str, limit: int = 10) -> List[Patent]:
        """Семантический поиск похожих патентов"""
        pass

    @abstractmethod
    async def get_by_id(self, patent_id: str) -> Optional[Patent]:
        """Получение патента по ID"""
        pass
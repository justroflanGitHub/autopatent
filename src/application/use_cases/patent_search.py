# src/application/use_cases/patent_search.py

from dataclasses import dataclass
from typing import List, Optional

from src.domain.entities.patent import Patent
from src.domain.entities.search_filter import SearchFilter
from src.domain.repositories.patent_repository import PatentRepository


@dataclass
class PatentSearchResult:
    """Результат поиска патентов"""
    patents: List[Patent]
    total_count: int
    query: str


class PatentSearchUseCase:
    """Use case для поиска патентов"""

    def __init__(self, patent_repository: PatentRepository):
        self.patent_repository = patent_repository

    async def search_by_query(
        self, 
        query: str, 
        limit: int = 10,
        search_filter: Optional[SearchFilter] = None
    ) -> PatentSearchResult:
        """Поиск патентов по запросу"""
        patents = await self.patent_repository.search_by_query(
            query, 
            limit,
            search_filter
        )
        return PatentSearchResult(
            patents=patents,
            total_count=len(patents),
            query=query
        )

    async def search_similar(self, text: str, limit: int = 10) -> PatentSearchResult:
        """Семантический поиск патентов"""
        patents = await self.patent_repository.search_similar(text, limit)
        return PatentSearchResult(
            patents=patents,
            total_count=len(patents),
            query=text
        )

    async def get_patent_details(self, patent_id: str) -> Patent:
        """Получение детальной информации о патенте"""
        patent = await self.patent_repository.get_by_id(patent_id)
        if not patent:
            raise ValueError(f"Patent with id {patent_id} not found")
        return patent

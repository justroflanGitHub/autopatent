# src/domain/entities/patent.py

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class Patent:
    """Доменная модель патента"""
    id: str
    title: str
    publication_date: Optional[date]
    application_date: Optional[date]
    authors: List[str]
    patent_holders: List[str]
    ipc_codes: List[str]
    abstract: str
    claims: str
    description: str

    @classmethod
    def create(
        cls,
        id: str,
        title: str,
        publication_date: Optional[date] = None,
        application_date: Optional[date] = None,
        authors: Optional[List[str]] = None,
        patent_holders: Optional[List[str]] = None,
        ipc_codes: Optional[List[str]] = None,
        abstract: str = "",
        claims: str = "",
        description: str = ""
    ) -> "Patent":
        """Фабричный метод для создания объекта патента"""
        return cls(
            id=id,
            title=title,
            publication_date=publication_date,
            application_date=application_date,
            authors=authors,
            patent_holders=patent_holders,
            ipc_codes=ipc_codes,
            abstract=abstract,
            claims=claims,
            description=description
        )

    def get_full_text(self) -> str:
        """Возвращает полный текст патента для анализа"""
        parts = []
        
        if self.title:
            parts.append(f"Название: {self.title}")
            
        if self.abstract:
            parts.append(f"Реферат: {self.abstract}")
            
        if self.description:
            parts.append(f"Описание: {self.description}")
            
        if self.claims:
            parts.append(f"Формула изобретения: {self.claims}")
            
        return "\n\n".join(parts)

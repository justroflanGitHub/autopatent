from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class SearchFilter:
    """Фильтры для поиска патентов"""
    countries: Optional[List[str]] = None  # Коды стран (например, ["RU", "US"])
    ipc_codes: Optional[List[str]] = None  # Коды МПК
    cpc_codes: Optional[List[str]] = None  # Коды СПК
    date_from: Optional[date] = None  # Дата начала поиска
    date_to: Optional[date] = None    # Дата окончания поиска

    def to_api_format(self) -> dict:
        """Преобразование фильтров в формат API Роспатента"""
        filters = {}

        if self.countries:
            filters["country"] = {"values": self.countries}

        if self.ipc_codes:
            filters["classification.ipc"] = {"values": self.ipc_codes}

        if self.cpc_codes:
            filters["classification.cpc"] = {"values": self.cpc_codes}

        # Добавляем фильтр по дате, если указана хотя бы одна дата
        if self.date_from or self.date_to:
            date_range = {}
            if self.date_from:
                date_range["gte"] = self.date_from.strftime("%Y%m%d")
            if self.date_to:
                date_range["lte"] = self.date_to.strftime("%Y%m%d")
            filters["date_published"] = {"range": date_range}

        return filters 
# src/infrastructure/rospatent/config.py

from dataclasses import dataclass


@dataclass
class RospatentConfig:
    """Конфигурация для работы с API Роспатента"""
    jwt_token: str
    base_url: str = "https://searchplatform.rospatent.gov.ru/patsearch/v0.2"
    timeout: int = 30

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
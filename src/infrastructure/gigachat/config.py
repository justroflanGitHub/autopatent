# src/infrastructure/gigachat/config.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class GigaChatConfig:
    """Конфигурация для работы с GigaChat API"""
    client_id: str
    client_secret: str
    scope: str = "GIGACHAT_API_PERS"
    base_url: str = "https://gigachat.devices.sberbank.ru/api/v1"
    auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    timeout: int = 30
    _access_token: Optional[str] = None

    @property
    def headers(self) -> dict:
        """Заголовки для запросов к API"""
        if not self._access_token:
            raise ValueError("Access token not set")
            
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
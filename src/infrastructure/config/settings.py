# src/infrastructure/config/settings.py

import logging
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


@dataclass
class Settings:
    """Основные настройки приложения"""
    # Обязательные параметры (без значений по умолчанию)
    rospatent_jwt: str
    gigachat_client_id: str
    gigachat_client_secret: str

    # Опциональные параметры
    bot_token: Optional[str] = None

    # Необязательные параметры (со значениями по умолчанию)
    log_level: str = "INFO"
    cache_ttl_hours: int = 24

    # Web service settings
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    debug: bool = False

    # API URLs
    rospatent_base_url: str = "https://searchplatform.rospatent.gov.ru"
    gigachat_base_url: str = "https://gigachat.devices.sberbank.ru/api/v1"

    # GigaChat API key (for direct API access)
    gigachat_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Создание настроек из переменных окружения"""
        rospatent_jwt = os.getenv("ROSPATENT_JWT")
        if not rospatent_jwt:
            raise ValueError("ROSPATENT_JWT is not set in environment variables")

        gigachat_client_id = os.getenv("GIGACHAT_CLIENT_ID")
        if not gigachat_client_id:
            raise ValueError("GIGACHAT_CLIENT_ID is not set")

        gigachat_client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
        if not gigachat_client_secret:
            raise ValueError("GIGACHAT_CLIENT_SECRET is not set")

        # Optional parameters
        bot_token = os.getenv("BOT_TOKEN")

        log_level = os.getenv("LOG_LEVEL", "INFO")

        cache_ttl = int(os.getenv("CACHE_TTL_HOURS", "24"))

        # Web service settings
        web_host = os.getenv("WEB_HOST", "0.0.0.0")
        web_port = int(os.getenv("WEB_PORT", "8000"))
        debug = os.getenv("DEBUG", "false").lower() == "true"

        # API URLs
        rospatent_base_url = os.getenv("ROSPATENT_BASE_URL", "https://searchplatform.rospatent.gov.ru")
        gigachat_base_url = os.getenv("GIGACHAT_BASE_URL", "https://gigachat.devices.sberbank.ru/api/v1")

        # GigaChat API key
        gigachat_api_key = os.getenv("GIGACHAT_API_KEY")

        return cls(
            rospatent_jwt=rospatent_jwt,
            gigachat_client_id=gigachat_client_id,
            gigachat_client_secret=gigachat_client_secret,
            bot_token=bot_token,
            log_level=log_level,
            cache_ttl_hours=cache_ttl,
            web_host=web_host,
            web_port=web_port,
            debug=debug,
            rospatent_base_url=rospatent_base_url,
            gigachat_base_url=gigachat_base_url,
            gigachat_api_key=gigachat_api_key
        )


# Создаем глобальный экземпляр настроек
settings = Settings.from_env()

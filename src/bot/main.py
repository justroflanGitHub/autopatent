# src/bot/main.py

import asyncio
import logging
import os

from src.application.services.patent_summarizer import PatentSummarizer
from src.application.use_cases.patent_search import PatentSearchUseCase
from src.infrastructure.cache.patent_cache import PatentCache
from src.infrastructure.config.settings import Settings
from src.infrastructure.gigachat.client import GigaChatClient
from src.infrastructure.gigachat.config import GigaChatConfig
from src.infrastructure.rospatent.config import RospatentConfig
from src.infrastructure.rospatent.repository import RospatentRepository
from src.interfaces.telegram.bot import PatentBot


async def main():
    # Загружаем настройки
    try:
        settings = Settings.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required environment variables are set.")
        return

    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Проверяем наличие токена бота
    if not settings.bot_token:
        print("BOT_TOKEN is not set. Please add it to your .env file.")
        return

    # Инициализация зависимостей
    rospatent_config = RospatentConfig(jwt_token=settings.rospatent_jwt)
    patent_repository = RospatentRepository(rospatent_config)
    search_use_case = PatentSearchUseCase(patent_repository)

    # Инициализация GigaChat
    gigachat_config = GigaChatConfig(
        client_id=settings.gigachat_client_id,
        client_secret=settings.gigachat_client_secret
    )
    gigachat_client = GigaChatClient(gigachat_config)

    # Инициализация сервисов
    patent_summarizer = PatentSummarizer(gigachat_client)
    patent_cache = PatentCache(ttl_hours=settings.cache_ttl_hours)

    # Создание и запуск бота
    bot = PatentBot(
        token=settings.bot_token,
        search_use_case=search_use_case,
        patent_summarizer=patent_summarizer,
        patent_cache=patent_cache
    )

    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())

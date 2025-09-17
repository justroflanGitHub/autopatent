# src/interfaces/telegram/bot.py

import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.application.services.patent_summarizer import PatentSummarizer
from src.application.use_cases.patent_search import PatentSearchUseCase
from src.infrastructure.cache.patent_cache import PatentCache
from src.interfaces.telegram.handlers.filters import router as filters_router
from src.interfaces.telegram.handlers.search import SearchHandler
from src.interfaces.telegram.handlers.search import router as search_router


class PatentBot:
    """Основной класс телеграм-бота"""

    def __init__(
        self,
        token: str,
        search_use_case: PatentSearchUseCase,
        patent_summarizer: PatentSummarizer,
        patent_cache: PatentCache,
        log_level: Optional[int] = None
    ):
        # Настройка логирования
        if log_level:
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        # Инициализация бота и хранилища состояний
        self.bot = Bot(token=token, parse_mode="HTML")
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)

        # Инициализация обработчиков
        self.search_handler = SearchHandler(
            search_use_case=search_use_case,
            patent_summarizer=patent_summarizer,
            patent_cache=patent_cache
        )
        
        # Подключаем все роутеры
        self.dp.include_router(search_router)
        self.dp.include_router(filters_router)

    async def start(self) -> None:
        """Запуск бота"""
        logging.info("Starting bot...")
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.close()
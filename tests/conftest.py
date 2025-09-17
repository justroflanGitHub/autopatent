from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Dispatcher
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.application.use_cases.patent_search import PatentSearchUseCase
from src.interfaces.telegram.bot import PatentBot
from src.interfaces.telegram.handlers.search import SearchHandler


@pytest.fixture
def mock_dispatcher():
    """
    Фикстура для замокирования класса Dispatcher внутри bot.py.
    """
    with patch('src.interfaces.telegram.bot.Dispatcher') as mock_dispatcher_cls:
        mock_dispatcher_instance = AsyncMock(spec=Dispatcher)
        # Замокируем метод include_router, чтобы избежать реальных вызовов
        mock_dispatcher_instance.include_router = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher_instance
        yield mock_dispatcher_instance


@pytest.fixture
def mock_search_use_case():
    """
    Фикстура для создания замокированного объекта PatentSearchUseCase.
    """
    return AsyncMock(spec=PatentSearchUseCase)


@pytest.fixture
def mock_patent_summarizer():
    """
    Фикстура для создания замокированного объекта PatentSummarizer
    """
    return AsyncMock()


@pytest.fixture
def mock_patent_cache():
    """
    Фикстура для создания замокированного объекта PatentCache
    """
    return AsyncMock()


@pytest.fixture
def handler(mock_search_use_case, mock_patent_summarizer, mock_patent_cache):
    """
    Фикстура для создания объекта SearchHandler с замокированными зависимостями
    """
    return SearchHandler(
        search_use_case=mock_search_use_case,
        patent_summarizer=mock_patent_summarizer,
        patent_cache=mock_patent_cache
    )


@pytest.fixture
def patent_bot(mock_search_use_case, mock_patent_summarizer, mock_patent_cache):
    """
    Фикстура для создания объекта PatentBot с замокированными зависимостями
    """
    with patch('src.interfaces.telegram.bot.Dispatcher') as mock_dispatcher_cls:
        mock_dispatcher_instance = AsyncMock(spec=Dispatcher)
        mock_dispatcher_instance.include_router = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher_instance

        return PatentBot(
            token="123456:ABCDEF",
            search_use_case=mock_search_use_case,
            patent_summarizer=mock_patent_summarizer,
            patent_cache=mock_patent_cache,
            log_level=None
        )

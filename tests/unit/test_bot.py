from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramUnauthorizedError

from src.interfaces.telegram.bot import PatentBot


@pytest.mark.asyncio
async def test_start_and_close(patent_bot):
    """
    Тест проверяет корректное закрытие бота в методе start() 
    после завершения работы
    """
    # Arrange
    patent_bot.bot = AsyncMock(spec=Bot)
    
    # Act
    await patent_bot.start()

    # Assert
    patent_bot.dp.start_polling.assert_awaited_once_with(patent_bot.bot)
    patent_bot.bot.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_bot_initialization(mock_search_use_case, mock_patent_summarizer, mock_patent_cache):
    # Arrange
    token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

    with patch('src.interfaces.telegram.bot.Bot') as mock_bot:
        mock_bot_instance = AsyncMock(spec=Bot)
        mock_bot.return_value = mock_bot_instance

        # Act
        bot = PatentBot(
            token=token, 
            search_use_case=mock_search_use_case,
            patent_summarizer=mock_patent_summarizer,
            patent_cache=mock_patent_cache
        )

        # Assert
        assert isinstance(bot.bot, Bot)
        assert bot.search_handler.search_use_case == mock_search_use_case
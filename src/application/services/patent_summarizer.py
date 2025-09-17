# src/application/services/patent_summarizer.py

import asyncio
import logging
from typing import Optional

from src.domain.entities.patent import Patent
from src.infrastructure.gigachat.client import GigaChatClient
from src.infrastructure.utils.text import clean_text, format_patent_analysis

logger = logging.getLogger(__name__)

MAX_CHARS = 25000  # Примерно 31744 токена, с запасом
MAX_RETRIES = 3    # Максимальное количество попыток
RETRY_DELAY = 1    # Задержка между попытками в секундах

class PatentSummarizer:
    """Сервис для анализа патентов с помощью GigaChat"""

    def __init__(self, gigachat_client: GigaChatClient):
        self.gigachat_client = gigachat_client

    def _validate_and_fix_response(self, response: dict) -> dict:
        """Проверяет и исправляет ответ от GigaChat"""
        if not response or response.get("status") != "success":
            logger.warning(f"Получен некорректный ответ: {response}")
            return {
                "status": "error",
                "summary": "Не удалось выполнить анализ патента"
            }

        summary = response.get("summary")
        if not summary:
            return {
                "status": "error",
                "summary": "Пустой ответ от сервиса анализа"
            }

        logger.info(f"Получен ответ от GigaChat:\n{summary}\n{'-' * 80}")
        
        return {
            "status": "success",
            "summary": summary
        }

    async def summarize(self, patent: Patent) -> Optional[dict]:
        """Суммаризация информации о патенте"""
        # Формируем сокращенный текст для анализа
        title = f"Название: {patent.title}\n" if patent.title else ""
        abstract = f"Реферат: {patent.abstract}\n" if patent.abstract else ""
        claims = f"Формула изобретения: {self._truncate_text(patent.claims, MAX_CHARS // 4)}\n" if patent.claims else ""
        description = f"Описание: {self._truncate_text(patent.description, MAX_CHARS // 2)}\n" if patent.description else ""

        patent_text = self._truncate_text(
            title + abstract + claims + description
        )

        try:
            logger.info(f"Попытка анализа патента {patent.id}")
            result = await self.gigachat_client.summarize_patent(patent_text)
            return self._validate_and_fix_response(result)
            
        except Exception as e:
            logger.error(f"Ошибка при анализе патента {patent.id}: {e}")
            return {
                "status": "error",
                "summary": "Произошла ошибка при анализе патента"
            }

    def _truncate_text(self, text: str, max_chars: int = MAX_CHARS) -> str:
        """Обрезает текст до указанного количества символов, сохраняя целостность предложений"""
        if len(text) <= max_chars:
            return text
            
        # Находим последнюю точку перед лимитом
        truncated = text[:max_chars]
        last_period = truncated.rfind('.')
        
        if last_period > 0:
            return truncated[:last_period + 1]
        return truncated

    async def analyze_patent(self, patent_id: str, patent_text: str) -> str:
        """Анализирует текст патента и возвращает отформатированный результат"""
        try:
            logger.info(f"Попытка анализа патента {patent_id}")

            # Очищаем текст патента
            cleaned_text = clean_text(patent_text)

            # Получаем анализ от GigaChat
            analysis_result = await self.gigachat_client.summarize_patent(cleaned_text)

            # Форматируем результат с помощью утилиты из text.py
            return format_patent_analysis(analysis_result)

        except Exception as e:
            logger.error(f"Ошибка при анализе патента {patent_id}: {str(e)}")
            return format_patent_analysis({
                "status": "error",
                "summary": "Произошла ошибка при анализе патента",
                "error": str(e)
            })

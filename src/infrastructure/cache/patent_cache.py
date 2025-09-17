import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class PatentCache:
    """Простой in-memory кэш для результатов суммаризации патентов"""

    def __init__(self, ttl_hours: int = 24, cleanup_interval: int = 1):
        self._cache: Dict[str, Tuple[dict, datetime]] = {}
        self._ttl = timedelta(hours=ttl_hours)
        self._last_cleanup = datetime.now()
        self._cleanup_interval = timedelta(hours=cleanup_interval)

    def _cleanup_expired(self) -> None:
        """Очистка просроченных записей"""
        now = datetime.now()
        # Проверяем, нужно ли запускать очистку
        if now - self._last_cleanup < self._cleanup_interval:
            return

        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self._ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
            
        if expired_keys:
            logger.info(f"Очищено {len(expired_keys)} просроченных записей из кэша")
            
        self._last_cleanup = now

    def get(self, patent_id: str) -> Optional[dict]:
        """Получение результата суммаризации из кэша"""
        self._cleanup_expired()  # Проверяем и чистим при каждом обращении
        
        if patent_id not in self._cache:
            return None

        result, timestamp = self._cache[patent_id]
        if datetime.now() - timestamp > self._ttl:
            del self._cache[patent_id]
            return None

        logger.info(f"Получен результат анализа из кэша для патента {patent_id}")
        return result

    def set(self, patent_id: str, summary: dict) -> None:
        """Сохранение результата суммаризации в кэш"""
        self._cleanup_expired()  # Проверяем и чистим при каждом обращении
        self._cache[patent_id] = (summary, datetime.now())

    def clear(self) -> None:
        """Полная очистка кэша"""
        self._cache.clear()
        logger.info("Кэш полностью очищен")

    @property
    def size(self) -> int:
        """Текущий размер кэша"""
        self._cleanup_expired()
        return len(self._cache)
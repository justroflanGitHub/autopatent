import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.domain.entities.patent import Patent
from src.infrastructure.gigachat.client import GigaChatClient
from src.infrastructure.utils.text import clean_text

logger = logging.getLogger(__name__)

MAX_CHARS = 20000  # Максимальная длина текста для анализа
MAX_RETRIES = 2    # Максимальное количество попыток
RETRY_DELAY = 1    # Задержка между попытками в секундах

class PatentEnricher:
    """Сервис для обогащения данных патентов с помощью GigaChat"""

    def __init__(self, gigachat_client: GigaChatClient):
        self.gigachat_client = gigachat_client

    async def enrich_patent(self, patent: Patent) -> Patent:
        """Обогащение данных патента с помощью ИИ"""
        try:
            logger.info(f"Начало обогащения данных патента {patent.id}")
            logger.info(f"Исходные данные патента: title='{patent.title}', authors={patent.authors}, abstract='{patent.abstract[:100] if patent.abstract else None}'")

            # Формируем текст патента для анализа
            patent_text = self._prepare_patent_text(patent)
            logger.info(f"Текст для анализа GigaChat: {len(patent_text)} символов")

            # Получаем обогащенные данные от GigaChat
            enrichment_result = await self.gigachat_client.enrich_patent_data(patent_text)

            if enrichment_result and enrichment_result.get("status") == "success":
                enriched_data = enrichment_result["enriched_data"]
                logger.info(f"Успешно получены обогащенные данные для патента {patent.id}: {enriched_data}")

                # Создаем обновленный объект патента
                merged_patent = self._merge_enriched_data(patent, enriched_data)
                logger.info(f"Результат слияния: title='{merged_patent.title}', authors={merged_patent.authors}")
                return merged_patent
            else:
                logger.warning(f"Не удалось обогатить данные патента {patent.id}: {enrichment_result}")
                return patent

        except Exception as e:
            logger.error(f"Ошибка при обогащении патента {patent.id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return patent

    def _prepare_patent_text(self, patent: Patent) -> str:
        """Подготовка текста патента для анализа"""
        parts = []

        if patent.title:
            parts.append(f"Название: {patent.title}")

        if patent.abstract:
            parts.append(f"Реферат: {patent.abstract}")

        if patent.description:
            parts.append(f"Описание: {patent.description}")

        if patent.claims:
            parts.append(f"Формула изобретения: {patent.claims}")

        if patent.authors:
            parts.append(f"Авторы: {', '.join(patent.authors)}")

        if patent.patent_holders:
            parts.append(f"Правообладатели: {', '.join(patent.patent_holders)}")

        if patent.ipc_codes:
            parts.append(f"МПК: {', '.join(patent.ipc_codes)}")

        if patent.publication_date:
            parts.append(f"Дата публикации: {patent.publication_date.strftime('%Y-%m-%d')}")

        if patent.application_date:
            parts.append(f"Дата подачи: {patent.application_date.strftime('%Y-%m-%d')}")

        text = "\n\n".join(parts)

        # Ограничиваем длину текста
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + "..."

        return text

    def _merge_enriched_data(self, original_patent: Patent, enriched_data: Dict[str, Any]) -> Patent:
        """Слияние обогащенных данных с оригинальными"""
        try:
            # Создаем копию оригинального патента
            merged_data = {
                "id": original_patent.id,
                "title": original_patent.title,
                "publication_date": original_patent.publication_date,
                "application_date": original_patent.application_date,
                "authors": original_patent.authors.copy() if original_patent.authors else [],
                "patent_holders": original_patent.patent_holders.copy() if original_patent.patent_holders else [],
                "ipc_codes": original_patent.ipc_codes.copy() if original_patent.ipc_codes else [],
                "abstract": original_patent.abstract,
                "claims": original_patent.claims,
                "description": original_patent.description
            }

            # Функция для проверки, является ли значение placeholder'ом
            def is_placeholder(value):
                if not value:
                    return True
                placeholder_texts = [
                    "название не указано", "не указано", "не указаны",
                    "отсутствует", "нет данных", "пусто"
                ]
                return str(value).lower().strip() in placeholder_texts

            # Обновляем данные из обогащенных данных, если они отсутствуют или являются placeholder'ами
            if enriched_data.get("title") and is_placeholder(merged_data["title"]):
                merged_data["title"] = clean_text(enriched_data["title"])

            if enriched_data.get("abstract") and is_placeholder(merged_data["abstract"]):
                merged_data["abstract"] = clean_text(enriched_data["abstract"])

            if enriched_data.get("description") and is_placeholder(merged_data["description"]):
                merged_data["description"] = clean_text(enriched_data["description"])

            if enriched_data.get("claims") and is_placeholder(merged_data["claims"]):
                merged_data["claims"] = clean_text(enriched_data["claims"])

            # Обновляем авторов, если они отсутствуют или являются placeholder'ами
            if enriched_data.get("authors") and (not merged_data["authors"] or all(is_placeholder(author) for author in merged_data["authors"])):
                authors = [clean_text(author) for author in enriched_data["authors"] if author and not is_placeholder(author)]
                if authors:
                    merged_data["authors"] = authors

            # Обновляем правообладателей, если они отсутствуют или являются placeholder'ами
            if enriched_data.get("patent_holders") and (not merged_data["patent_holders"] or all(is_placeholder(holder) for holder in merged_data["patent_holders"])):
                holders = [clean_text(holder) for holder in enriched_data["patent_holders"] if holder and not is_placeholder(holder)]
                if holders:
                    merged_data["patent_holders"] = holders

            # Обновляем IPC коды, если они отсутствуют или являются placeholder'ами
            if enriched_data.get("ipc_codes") and (not merged_data["ipc_codes"] or all(is_placeholder(code) for code in merged_data["ipc_codes"])):
                codes = [clean_text(code) for code in enriched_data["ipc_codes"] if code and not is_placeholder(code)]
                if codes:
                    merged_data["ipc_codes"] = codes

            # Пытаемся обновить даты, если они отсутствуют
            if enriched_data.get("publication_date") and not merged_data["publication_date"]:
                try:
                    merged_data["publication_date"] = datetime.strptime(
                        enriched_data["publication_date"], "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError):
                    pass

            if enriched_data.get("application_date") and not merged_data["application_date"]:
                try:
                    merged_data["application_date"] = datetime.strptime(
                        enriched_data["application_date"], "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError):
                    pass

            # Создаем новый объект патента
            return Patent.create(**merged_data)

        except Exception as e:
            logger.error(f"Ошибка при слиянии данных патента {original_patent.id}: {e}")
            return original_patent

    async def get_enrichment_summary(self, patent: Patent) -> Dict[str, Any]:
        """Получение сводки обогащения для отображения в интерфейсе"""
        try:
            enriched_patent = await self.enrich_patent(patent)

            # Определяем, какие поля были обогащены
            enriched_fields = []

            if enriched_patent.title != patent.title:
                enriched_fields.append("название")

            if enriched_patent.abstract != patent.abstract:
                enriched_fields.append("реферат")

            if enriched_patent.description != patent.description:
                enriched_fields.append("описание")

            if enriched_patent.claims != patent.claims:
                enriched_fields.append("формула изобретения")

            if enriched_patent.authors != patent.authors:
                enriched_fields.append("авторы")

            if enriched_patent.patent_holders != patent.patent_holders:
                enriched_fields.append("правообладатели")

            if enriched_patent.ipc_codes != patent.ipc_codes:
                enriched_fields.append("IPC коды")

            if enriched_patent.publication_date != patent.publication_date:
                enriched_fields.append("дата публикации")

            if enriched_patent.application_date != patent.application_date:
                enriched_fields.append("дата подачи")

            return {
                "enriched_patent": {
                    "id": enriched_patent.id,
                    "title": enriched_patent.title,
                    "publication_date": enriched_patent.publication_date.isoformat() if enriched_patent.publication_date else None,
                    "application_date": enriched_patent.application_date.isoformat() if enriched_patent.application_date else None,
                    "authors": enriched_patent.authors,
                    "patent_holders": enriched_patent.patent_holders,
                    "ipc_codes": enriched_patent.ipc_codes,
                    "abstract": enriched_patent.abstract,
                    "claims": enriched_patent.claims,
                    "description": enriched_patent.description
                },
                "enrichment_info": {
                    "fields_enriched": enriched_fields,
                    "enrichment_status": "success" if enriched_fields else "no_changes"
                }
            }

        except Exception as e:
            logger.error(f"Ошибка при получении сводки обогащения для патента {patent.id}: {e}")
            return {
                "enriched_patent": {
                    "id": patent.id,
                    "title": patent.title,
                    "publication_date": patent.publication_date.isoformat() if patent.publication_date else None,
                    "application_date": patent.application_date.isoformat() if patent.application_date else None,
                    "authors": patent.authors,
                    "patent_holders": patent.patent_holders,
                    "ipc_codes": patent.ipc_codes,
                    "abstract": patent.abstract,
                    "claims": patent.claims,
                    "description": patent.description
                },
                "enrichment_info": {
                    "fields_enriched": [],
                    "enrichment_status": "error",
                    "error_message": str(e)
                }
            }

# src/infrastructure/rospatent/repository.py

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import List, Optional

import aiohttp
from aiohttp import ClientResponseError, ClientTimeout

from src.domain.entities.patent import Patent
from src.domain.entities.search_filter import SearchFilter
from src.domain.repositories.patent_repository import PatentRepository
from src.infrastructure.rospatent.config import RospatentConfig
from src.infrastructure.config.settings import Settings
from src.infrastructure.utils.text import clean_text, count_words

logger = logging.getLogger(__name__)


class RospatentRepository(PatentRepository):
    """Реализация репозитория для работы с API Роспатента"""

    def __init__(self, config: RospatentConfig):
        self.config = config
        self.timeout = ClientTimeout(total=config.timeout)
        self.max_retries = 3  # Максимальное количество повторных попыток
        self.retry_delay = 2  # Начальная задержка перед повторной попыткой (в секундах)

    @asynccontextmanager
    async def _get_session(self):
        """Контекстный менеджер для создания и закрытия сессии"""
        # TODO: убрать verify_ssl=False, когда rospatent вернет валидный сертификат
        connector = aiohttp.TCPConnector(verify_ssl=False)
        
        # Настройка параметров сессии для более стабильной работы
        timeout = ClientTimeout(total=self.config.timeout, 
                               connect=10,  # Увеличиваем таймаут соединения
                               sock_connect=10,  # Увеличиваем таймаут подключения сокета
                               sock_read=self.config.timeout)  # Таймаут чтения сокета
        
        session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            # Отключаем автоматический редирект, будем обрабатывать вручную
            auto_decompress=True,
            trust_env=True
        )
        try:
            yield session
        finally:
            await session.close()

    async def search_by_query(self, query: str, limit: int = 10, search_filter: Optional[SearchFilter] = None) -> List[Patent]:
        """Поиск патентов по запросу"""
        logger.info(f"Starting patent search for query: '{query}', limit: {limit}")
        retries = 0
        while retries <= self.max_retries:
            try:
                # Логируем информацию о попытке и окружении
                env_info = {
                    "http_proxy": os.environ.get("http_proxy", "не установлен"),
                    "https_proxy": os.environ.get("https_proxy", "не установлен"),
                    "no_proxy": os.environ.get("no_proxy", "не установлен"),
                }
                logger.debug(f"Попытка выполнения search_by_query (attempt: {retries+1}). Env: {env_info}")

                async with self._get_session() as session:
                    url = f"{self.config.base_url}/search"
                    payload = {"qn": query, "limit": limit}

                    if search_filter:
                        payload["filter"] = search_filter.to_api_format()

                    # Логируем полный URL и заголовки (без токена)
                    safe_headers = {k: v for k, v in self.config.headers.items() if k != "Authorization"}
                    safe_headers["Authorization"] = "Bearer ***"
                    logger.debug(f"Запрос к: {url}, headers: {safe_headers}, payload size: {len(str(payload))}")

                    async with session.post(url, json=payload, headers=self.config.headers) as response:
                        status = response.status
                        logger.debug(f"Получен статус: {status}")

                        if status == 301 or status == 302:
                            # Обрабатываем редирект вручную
                            redirect_url = response.headers.get('Location')
                            logger.debug(f"Перенаправление на: {redirect_url}")

                            if not redirect_url:
                                logger.error("Получен редирект без URL перенаправления")
                                return []
                                # Проверяем, что URL доступен извне
                            if "prod:" in redirect_url or "10.2.40" in redirect_url:
                                logger.error(f"Недопустимый URL перенаправления (внутренний): {redirect_url}")
                                return []

                            # Выполняем запрос к новому URL
                            async with session.post(redirect_url, json=payload, headers=self.config.headers) as redirect_response:
                                redirect_response.raise_for_status()
                                data = await redirect_response.json()
                        else:
                            # Проверяем статус и продолжаем как обычно
                            response.raise_for_status()
                            data = await response.json()

                        # Проверяем ответ на наличие ошибок
                        if isinstance(data, str) and "Failed to establish a connection" in data:
                            logger.error(f"API вернуло ошибку строкой: {data}")
                            if retries < self.max_retries:
                                retry_after = self.retry_delay * (2 ** retries)
                                logger.warning(f"Ошибка соединения к внутреннему сервису, повторная попытка через {retry_after}s")
                                await asyncio.sleep(retry_after)
                                retries += 1
                                continue
                            return []

                        # Проверяем наличие hits в ответе
                        if not data.get("hits"):
                            logger.debug(f"Нет результатов поиска (пустой hits): {data}")
                            return []

                        patents = []
                        for hit in data.get("hits", []):
                            patent_id = hit.get("id")
                            if patent_id:
                                patent_url = f"{self.config.base_url}/docs/{patent_id}"
                                try:
                                    async with session.get(patent_url, headers=self.config.headers) as patent_response:
                                        patent_response.raise_for_status()
                                        patent_data = await patent_response.json()
                                        if patent := self._parse_patent_data(patent_data, patent_id):
                                            patents.append(patent)
                                except aiohttp.ClientError as e:
                                    import traceback
                                    logger.error(f"Error fetching patent {patent_id}: {repr(e)}\n{traceback.format_exc()}")
                                    # If we can't fetch patent details, try to enrich hit data with GigaChat
                                    try:
                                        patent = await self._create_enriched_patent_from_hit(hit, patent_id)
                                        if patent:
                                            patents.append(patent)
                                    except Exception as enrich_error:
                                        logger.error(f"Failed to create enriched patent from hit: {enrich_error}")
                                    continue

                        # If we got some patents, return them; otherwise return demo data
                        if patents:
                            logger.info(f"Successfully fetched {len(patents)} patents from API")
                            for i, patent in enumerate(patents[:5]):  # Log first 5 patents
                                title_display = patent.title[:50] + "..." if len(patent.title) > 50 else patent.title
                                logger.info(f"Patent {i+1}: ID={patent.id}, Title='{title_display}'")
                            return patents
                        else:
                            logger.info("No patents could be fetched, returning demo data")
                            return self._get_demo_patents(query, limit)

            except aiohttp.ClientResponseError as e:
                if e.status == 503 and retries < self.max_retries:
                    # Сервис временно недоступен, повторяем запрос
                    retry_after = self.retry_delay * (2 ** retries)  # Экспоненциальная задержка
                    logger.warning(f"Service unavailable (503), retrying in {retry_after}s (attempt {retries+1}/{self.max_retries})")
                    await asyncio.sleep(retry_after)
                    retries += 1
                    continue
                else:
                    import traceback
                    logger.error(f"Client response error during patent search: {repr(e)}\n{traceback.format_exc()}")
                    # Если все попытки исчерпаны, возвращаем демо-данные
                    if retries >= self.max_retries:
                        logger.info("All retries exhausted, returning demo data")
                        return self._get_demo_patents(query, limit)
                    return []
            except aiohttp.ClientError as e:
                import traceback
                logger.error(f"Error during patent search: {repr(e)}\n{traceback.format_exc()}")
                # При ошибке соединения возвращаем демо-данные
                return self._get_demo_patents(query, limit)
            except Exception as e:
                import traceback
                logger.error(f"Unexpected error during patent search: {repr(e)}\n{traceback.format_exc()}")
                # При любой ошибке возвращаем демо-данные
                return self._get_demo_patents(query, limit)

        logger.error(f"Max retries ({self.max_retries}) exceeded for search_by_query")
        # Возвращаем демо-данные при исчерпании всех попыток
        return self._get_demo_patents(query, limit)

    async def search_similar(self, text: str, limit: int = 10) -> List[Patent]:
        """Семантический поиск похожих патентов"""
        retries = 0
        while retries <= self.max_retries:
            try:
                # Логируем информацию о попытке и окружении
                env_info = {
                    "http_proxy": os.environ.get("http_proxy", "не установлен"),
                    "https_proxy": os.environ.get("https_proxy", "не установлен"),
                    "no_proxy": os.environ.get("no_proxy", "не установлен"),
                }
                logger.debug(f"Попытка выполнения search_similar (attempt: {retries+1}). Env: {env_info}")
                
                async with self._get_session() as session:
                    url = f"{self.config.base_url}/similar_search"
                    payload = {
                        "type_search": "text_search",
                        "pat_text": text,
                        "count": limit
                    }

                    # Добавляем проверку длины текста
                    if count_words(text) < 50:
                        logger.warning(f"Текст запроса содержит менее 50 слов ({count_words(text)}), что может привести к ошибке API")

                    # Логируем полный URL и заголовки (без токена)
                    safe_headers = {k: v for k, v in self.config.headers.items() if k != "Authorization"}
                    safe_headers["Authorization"] = "Bearer ***" 
                    logger.debug(f"Запрос к: {url}, headers: {safe_headers}, payload size: {len(str(payload))}")
                    
                    async with session.post(url, json=payload, headers=self.config.headers) as response:
                        status = response.status
                        logger.debug(f"Получен статус: {status}")
                        
                        if status == 301 or status == 302:
                            # Обрабатываем редирект вручную
                            redirect_url = response.headers.get('Location')
                            logger.debug(f"Перенаправление на: {redirect_url}")
                            
                            if not redirect_url:
                                logger.error("Получен редирект без URL перенаправления")
                                return []
                                
                            # Проверяем, что URL доступен извне
                            if "prod:" in redirect_url or "10.2.40" in redirect_url:
                                logger.error(f"Недопустимый URL перенаправления (внутренний): {redirect_url}")
                                return []
                                
                            # Выполняем запрос к новому URL
                            async with session.post(redirect_url, json=payload, headers=self.config.headers) as redirect_response:
                                redirect_response.raise_for_status()
                                data = await redirect_response.json()
                        else:
                            # Проверяем статус и продолжаем как обычно
                            response.raise_for_status()
                            data = await response.json()
                        
                        # Проверяем ответ на наличие ошибок
                        if isinstance(data, str) and "Failed to establish a connection" in data:
                            logger.error(f"API вернуло ошибку строкой: {data}")
                            if retries < self.max_retries:
                                retry_after = self.retry_delay * (2 ** retries)
                                logger.warning(f"Ошибка соединения к внутреннему сервису, повторная попытка через {retry_after}s")
                                await asyncio.sleep(retry_after)
                                retries += 1
                                continue
                            return []
                            
                        # Ожидаем наличие 'data' в ответе
                        if not data.get("data"):
                            logger.warning(f"Пустой ответ от API, нет ключа 'data': {data}")
                            return []
                        
                        patents = []
                        for item in data.get("data", []):
                            patent_id = item.get("id")
                            if patent_id:
                                patent_url = f"{self.config.base_url}/docs/{patent_id}"
                                try:
                                    async with session.get(patent_url, headers=self.config.headers) as patent_response:
                                        patent_response.raise_for_status()
                                        patent_data = await patent_response.json()
                                        if patent := self._parse_patent_data(patent_data, patent_id):
                                            patents.append(patent)
                                except aiohttp.ClientError as e:
                                    import traceback
                                    logger.error(f"Error fetching patent {patent_id}: {repr(e)}\n{traceback.format_exc()}")
                                    continue
                        
                        return patents

            except aiohttp.ClientResponseError as e:
                if e.status == 503 and retries < self.max_retries:
                    # Сервис временно недоступен, повторяем запрос
                    retry_after = self.retry_delay * (2 ** retries)  # Экспоненциальная задержка
                    logger.warning(f"Service unavailable (503), retrying in {retry_after}s (attempt {retries+1}/{self.max_retries})")
                    await asyncio.sleep(retry_after)
                    retries += 1
                    continue
                else:
                    import traceback
                    logger.error(f"Client response error during similar patent search: {repr(e)}\n{traceback.format_exc()}")
                    return []
            except aiohttp.ClientError as e:
                import traceback
                logger.error(f"Error during similar patent search: {repr(e)}\n{traceback.format_exc()}")
                return []
            except Exception as e:
                import traceback
                logger.error(f"Unexpected error during similar patent search: {repr(e)}\n{traceback.format_exc()}")
                return []

        logger.error(f"Max retries ({self.max_retries}) exceeded for search_similar")
        return []

    async def get_by_id(self, patent_id: str) -> Optional[Patent]:
        """Получение патента по ID"""
        retries = 0
        while retries <= self.max_retries:
            try:
                # Логируем информацию о попытке и окружении
                env_info = {
                    "http_proxy": os.environ.get("http_proxy", "не установлен"),
                    "https_proxy": os.environ.get("https_proxy", "не установлен"),
                    "no_proxy": os.environ.get("no_proxy", "не установлен"),
                }
                logger.debug(f"Попытка выполнения get_by_id (attempt: {retries+1}). Env: {env_info}")
                
                async with self._get_session() as session:
                    url = f"{self.config.base_url}/docs/{patent_id}"

                    # Логируем полный URL и заголовки (без токена)
                    safe_headers = {k: v for k, v in self.config.headers.items() if k != "Authorization"}
                    safe_headers["Authorization"] = "Bearer ***" 
                    logger.debug(f"Запрос к: {url}, headers: {safe_headers}")
                    
                    async with session.get(url, headers=self.config.headers) as response:
                        status = response.status
                        logger.debug(f"Получен статус: {status}")
                        
                        if status == 301 or status == 302:
                            # Обрабатываем редирект вручную
                            redirect_url = response.headers.get('Location')
                            logger.debug(f"Перенаправление на: {redirect_url}")
                            
                            if not redirect_url:
                                logger.error("Получен редирект без URL перенаправления")
                                return await self._create_basic_patent_from_hit({"id": patent_id}, patent_id)

                            # Проверяем, что URL доступен извне
                            if "prod:" in redirect_url or "10.2.40" in redirect_url:
                                logger.error(f"Недопустимый URL перенаправления (внутренний): {redirect_url}")
                                return await self._create_basic_patent_from_hit({"id": patent_id}, patent_id)
                                
                            # Выполняем запрос к новому URL
                            async with session.get(redirect_url, headers=self.config.headers) as redirect_response:
                                redirect_response.raise_for_status()
                                data = await redirect_response.json()
                        else:
                            # Проверяем статус и продолжаем как обычно
                            response.raise_for_status()
                            data = await response.json()
                        
                        # Проверяем ответ на наличие ошибок
                        if isinstance(data, str) and "Failed to establish a connection" in data:
                            logger.error(f"API вернуло ошибку строкой: {data}")
                            if retries < self.max_retries:
                                retry_after = self.retry_delay * (2 ** retries)
                                logger.warning(f"Ошибка соединения к внутреннему сервису, повторная попытка через {retry_after}s")
                                await asyncio.sleep(retry_after)
                                retries += 1
                                continue
                            return await self._create_basic_patent_from_hit({"id": patent_id}, patent_id)

                        return self._parse_patent_data(data, patent_id)

            except aiohttp.ClientResponseError as e:
                if e.status == 503 and retries < self.max_retries:
                    # Сервис временно недоступен, повторяем запрос
                    retry_after = self.retry_delay * (2 ** retries)  # Экспоненциальная задержка
                    logger.warning(f"Service unavailable (503), retrying in {retry_after}s (attempt {retries+1}/{self.max_retries})")
                    await asyncio.sleep(retry_after)
                    retries += 1
                    continue
                else:
                    import traceback
                    logger.error(f"Client response error while fetching patent {patent_id}: {repr(e)}\n{traceback.format_exc()}")
                    return await self._create_basic_patent_from_hit({"id": patent_id}, patent_id)
            except aiohttp.ClientError as e:
                import traceback
                logger.error(f"Error fetching patent {patent_id}: {repr(e)}\n{traceback.format_exc()}")
                return await self._create_basic_patent_from_hit({"id": patent_id}, patent_id)
            except Exception as e:
                import traceback
                logger.error(f"Unexpected error fetching patent {patent_id}: {repr(e)}\n{traceback.format_exc()}")
                return await self._create_basic_patent_from_hit({"id": patent_id}, patent_id)

        logger.error(f"Max retries ({self.max_retries}) exceeded for get_by_id")
        return await self._create_basic_patent_from_hit({"id": patent_id}, patent_id)

    def _parse_patent_data(self, data: dict, patent_id: str) -> Patent:
        """Парсинг данных патента из ответа API"""
        logger.error(f"STARTING PARSING for {patent_id}")
        logger.error(f"Raw data keys: {list(data.keys())}")

        # Логируем полный raw ответ до abstract
        import json
        raw_data_str = json.dumps(data, ensure_ascii=False, indent=2)
        lines = raw_data_str.split('\n')
        abstract_index = -1
        for i, line in enumerate(lines):
            if 'abstract' in line.lower():
                abstract_index = i
                break

        if abstract_index > 0:
            # Показываем только до abstract
            relevant_lines = lines[:abstract_index]
            logger.error(f"Raw API response (before abstract):\n{chr(10).join(relevant_lines)}")
        else:
            logger.error(f"Raw API response:\n{raw_data_str}")

        common = data.get("common", {})
        biblio = data.get("biblio", {})

        logger.error(f"Biblio keys: {list(biblio.keys())}")

        biblio_ru = biblio.get("ru", {})
        biblio_en = biblio.get("en", {})

        logger.error(f"Biblio_ru keys: {list(biblio_ru.keys())}, biblio_en keys: {list(biblio_en.keys())}")
        logger.error(f"Biblio_ru title: '{biblio_ru.get('title', 'NOT FOUND')}'")
        logger.error(f"Biblio_en title: '{biblio_en.get('title', 'NOT FOUND')}'")

        def parse_date(date_str: str) -> Optional[date]:
            if not date_str:
                logger.debug(f"Empty date string for patent {patent_id}")
                return None

            # Очищаем строку от лишних символов
            date_str = date_str.strip()

            date_formats = [
                "%Y-%m-%d",  # формат YYYY-MM-DD
                "%Y%m%d",    # формат YYYYMMDD
                "%Y.%m.%d",  # формат YYYY.MM.DD
                "%d.%m.%Y",  # формат DD.MM.YYYY
                "%m/%d/%Y",  # формат MM/DD/YYYY
                "%Y/%m/%d"   # формат YYYY/MM/DD
            ]

            for date_format in date_formats:
                try:
                    return datetime.strptime(date_str, date_format).date()
                except ValueError:
                    continue

            # Попробуем распарсить вручную для формата YYYY.MM.DD с переменным количеством цифр
            try:
                parts = date_str.split('.')
                if len(parts) == 3:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    return date(year, month, day)
            except (ValueError, IndexError):
                pass

            logger.error(f"Failed to parse date '{date_str}' for patent {patent_id}")
            return None

        pub_date = parse_date(common.get("publication_date", ""))
        app_date = parse_date(
            common.get("application", {}).get("filing_date", "")
        )

        if not pub_date or not app_date:
            logger.warning(
                f"Missing dates for patent {patent_id}. "
                f"Publication date: {pub_date}, Application date: {app_date}"
            )

        # Извлекаем название патента из biblio.ru.title
        title = biblio.get("ru", {}).get("title", "").strip()
        logger.error(f"Patent {patent_id} - biblio.ru.title: '{title}'")

        if not title:
            # Если русское название отсутствует, пробуем английское
            title = biblio.get("en", {}).get("title", "").strip()
            logger.error(f"Patent {patent_id} - biblio.en.title: '{title}'")

        logger.error(f"Patent {patent_id} - final extracted title: '{title}'")

        if not title:
            title = f"Патент {patent_id}"
            logger.error(f"Patent {patent_id} - using fallback title: '{title}'")

        # Обрабатываем авторов
        authors = [
            clean_text(author.get("name", ""))
            for author in biblio_ru.get("inventor", [])
        ]
        authors = [author for author in authors if author]  # Убираем пустые строки

        # Обрабатываем правообладателей
        patent_holders = [
            clean_text(holder.get("name", ""))
            for holder in biblio_ru.get("patentee", [])
        ]
        patent_holders = [holder for holder in patent_holders if holder]  # Убираем пустые строки

        # Обрабатываем IPC коды
        ipc_codes = [
            clean_text(ipc.get("fullname", ""))
            for ipc in common.get("classification", {}).get("ipc", [])
        ]
        ipc_codes = [code for code in ipc_codes if code]  # Убираем пустые строки

        # Обрабатываем текстовые поля
        abstract = clean_text(data.get("abstract", {}).get("ru", ""))
        claims = clean_text(data.get("claims", {}).get("ru", ""))
        description = clean_text(data.get("description", {}).get("ru", ""))

        return Patent.create(
            id=patent_id,
            title=title,
            publication_date=pub_date,
            application_date=app_date,
            authors=authors,
            patent_holders=patent_holders,
            ipc_codes=ipc_codes,
            abstract=abstract,
            claims=claims,
            description=description
        )

    def _get_demo_patents(self, query: str, limit: int) -> List[Patent]:
        """Возвращает демо-данные патентов для демонстрации интерфейса"""
        logger.info(f"Returning demo patents for query: '{query}', limit: {limit}")

        # Создаем демо-данные на основе запроса
        demo_patents = [
            Patent.create(
                id="RU2023123456",
                title=f"Изобретение в области {query}",
                publication_date=date(2023, 6, 15),
                application_date=date(2022, 12, 1),
                authors=["Иванов И.И.", "Петров П.П."],
                patent_holders=["ООО Инновационные Технологии"],
                ipc_codes=["G06F", "H04L"],
                abstract=f"Предложено техническое решение в области {query}. Изобретение позволяет улучшить эффективность работы системы за счет применения современных технологий обработки данных."
            ),
            Patent.create(
                id="RU2023789012",
                title=f"Способ оптимизации {query}",
                publication_date=date(2023, 8, 20),
                application_date=date(2023, 2, 10),
                authors=["Сидоров С.С.", "Кузнецова А.А."],
                patent_holders=["ЗАО ТехноСервис"],
                ipc_codes=["G06N", "H04M"],
                abstract=f"Разработан новый способ оптимизации процессов {query}. Метод обеспечивает повышение производительности на 30% и снижение энергопотребления."
            ),
            Patent.create(
                id="RU2023567890",
                title=f"Система управления {query}",
                publication_date=date(2023, 9, 5),
                application_date=date(2023, 3, 15),
                authors=["Васильев В.В."],
                patent_holders=["ИП Инновации"],
                ipc_codes=["G05B", "H04W"],
                abstract=f"Предложена система управления для {query}. Система включает модули мониторинга, анализа и автоматической корректировки параметров работы."
            ),
            Patent.create(
                id="RU2023456789",
                title=f"Устройство для {query}",
                publication_date=date(2023, 10, 12),
                application_date=date(2023, 4, 20),
                authors=["Михайлова Е.Н.", "Андреев Д.М."],
                patent_holders=["Корпорация ТехИнвест"],
                ipc_codes=["H04B", "G01S"],
                abstract=f"Разработано устройство для реализации функций {query}. Устройство отличается компактностью, высокой надежностью и простотой эксплуатации."
            ),
            Patent.create(
                id="RU2023345678",
                title=f"Метод анализа {query}",
                publication_date=date(2023, 11, 8),
                application_date=date(2023, 5, 25),
                authors=["Николаев Н.Н."],
                patent_holders=["Научно-исследовательский институт"],
                ipc_codes=["G06K", "H04N"],
                abstract=f"Предложен метод анализа данных в области {query}. Метод позволяет выявлять скрытые закономерности и прогнозировать развитие процессов."
            )
        ]

        # Возвращаем ограниченное количество патентов
        return demo_patents[:min(limit, len(demo_patents))]

    async def _create_enriched_patent_from_hit(self, hit: dict, patent_id: str) -> Optional[Patent]:
        """Создает обогащенный объект патента из данных hit с помощью GigaChat"""
        try:
            logger.info(f"Creating enriched patent from hit data for {patent_id}")
            logger.info(f"Hit data keys: {list(hit.keys())}")
            logger.info(f"Hit data: {hit}")

            # Извлекаем доступную информацию из hit
            # Название может быть в разных местах
            title = ""

            # Проверяем biblio.ru.title (основной источник)
            biblio_title = hit.get('biblio', {}).get('ru', {}).get('title', '').strip()
            if biblio_title:
                title = biblio_title
                logger.info(f"Found title in biblio.ru.title: '{title}'")

            # Проверяем biblio.en.title (запасной вариант)
            if not title:
                biblio_en_title = hit.get('biblio', {}).get('en', {}).get('title', '').strip()
                if biblio_en_title:
                    title = biblio_en_title
                    logger.info(f"Found title in biblio.en.title: '{title}'")

            # Проверяем snippet.title (еще один вариант)
            if not title:
                snippet_title = hit.get('snippet', {}).get('title', '').strip()
                if snippet_title:
                    # Убираем HTML теги из snippet
                    import re
                    title = re.sub(r'<[^>]+>', '', snippet_title)
                    logger.info(f"Found title in snippet.title: '{title}'")

            # Проверяем прямое поле title
            if not title:
                direct_title = hit.get("title", "").strip()
                if direct_title:
                    title = direct_title
                    logger.info(f"Found title in direct field: '{title}'")

            # Извлекаем abstract из разных мест
            abstract = ""
            snippet_abstract = hit.get('snippet', {}).get('description', '').strip()
            if snippet_abstract:
                # Убираем HTML теги
                import re
                abstract = re.sub(r'<[^>]+>', '', snippet_abstract)
                logger.info(f"Found abstract in snippet.description: '{abstract[:100]}...'")

            logger.info(f"Final title from hit: '{title}'")
            logger.info(f"Final abstract from hit: '{abstract[:100]}...'")

            # Если title пустое или совпадает с ID, используем fallback
            if not title or title == patent_id:
                title = f"Патент {patent_id}"
                logger.info(f"Using fallback title: '{title}'")

            # Обрабатываем списки из правильных мест
            authors = []
            biblio_authors = hit.get('biblio', {}).get('ru', {}).get('inventor', [])
            if biblio_authors:
                authors = [clean_text(author.get('name', '')) for author in biblio_authors if author.get('name')]
                logger.info(f"Found authors in biblio.ru.inventor: {authors}")

            patent_holders = []
            biblio_holders = hit.get('biblio', {}).get('ru', {}).get('patentee', [])
            if biblio_holders:
                patent_holders = [clean_text(holder.get('name', '')) for holder in biblio_holders if holder.get('name')]
                logger.info(f"Found patent holders in biblio.ru.patentee: {patent_holders}")

            ipc_codes = []
            common_classification = hit.get('common', {}).get('classification', {}).get('ipc', [])
            if common_classification:
                ipc_codes = [clean_text(ipc.get('fullname', '')) for ipc in common_classification if ipc.get('fullname')]
                logger.info(f"Found IPC codes in common.classification.ipc: {ipc_codes}")

            logger.info(f"Authors from hit: {authors}")
            logger.info(f"Patent holders from hit: {patent_holders}")

            # Пытаемся распарсить даты
            publication_date = None
            application_date = None

            # Используем тот же парсер дат, что и в _parse_patent_data
            def parse_date(date_str: str) -> Optional[date]:
                if not date_str:
                    return None

                # Очищаем строку от лишних символов
                date_str = date_str.strip()

                date_formats = [
                    "%Y-%m-%d",  # формат YYYY-MM-DD
                    "%Y%m%d",    # формат YYYYMMDD
                    "%Y.%m.%d",  # формат YYYY.MM.DD
                    "%d.%m.%Y",  # формат DD.MM.YYYY
                    "%m/%d/%Y",  # формат MM/DD/YYYY
                    "%Y/%m/%d"   # формат YYYY/MM/DD
                ]

                for date_format in date_formats:
                    try:
                        return datetime.strptime(date_str, date_format).date()
                    except ValueError:
                        continue

                # Попробуем распарсить вручную для формата YYYY.MM.DD с переменным количеством цифр
                try:
                    parts = date_str.split('.')
                    if len(parts) == 3:
                        year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])
                        return date(year, month, day)
                except (ValueError, IndexError):
                    pass

                logger.error(f"Failed to parse date '{date_str}' for patent {patent_id}")
                return None

            # Парсим даты из hit данных
            if hit.get("common", {}).get("publication_date"):
                publication_date = parse_date(hit["common"]["publication_date"])
                logger.info(f"Publication date from hit: {publication_date}")

            if hit.get("common", {}).get("application", {}).get("filing_date"):
                application_date = parse_date(hit["common"]["application"]["filing_date"])
                logger.info(f"Application date from hit: {application_date}")

            # Создаем базовый патент
            patent = Patent.create(
                id=patent_id,
                title=title,
                publication_date=publication_date,
                application_date=application_date,
                authors=authors or [],
                patent_holders=patent_holders or [],
                ipc_codes=ipc_codes or [],
                abstract=abstract
            )

            # Всегда пытаемся обогатить через GigaChat, даже если есть базовые данные
            text_to_analyze = ""
            if abstract and len(abstract.strip()) > 20:
                text_to_analyze = abstract
                logger.info(f"Using abstract for GigaChat analysis ({len(abstract)} chars)")
            elif title and title != f"Патент {patent_id}" and len(title.strip()) > 5:
                text_to_analyze = title
                logger.info(f"Using title for GigaChat analysis ({len(title)} chars)")
            else:
                # Если нет текста, создаем на основе ID патента
                text_to_analyze = f"Патент {patent_id}"
                logger.info(f"Using patent ID for GigaChat analysis")

            if text_to_analyze:
                try:
                    from src.infrastructure.gigachat.client import GigaChatClient
                    from src.infrastructure.gigachat.config import GigaChatConfig

                    # Создаем клиент GigaChat для обогащения
                    settings_instance = Settings.from_env()
                    gigachat_config = GigaChatConfig(
                        client_id=settings_instance.gigachat_client_id,
                        client_secret=settings_instance.gigachat_client_secret,
                        base_url=settings_instance.gigachat_base_url
                    )
                    gigachat_client = GigaChatClient(gigachat_config)

                    logger.info(f"Enriching patent {patent_id} with GigaChat using text: '{text_to_analyze[:100]}...'")
                    try:
                        enriched_data = await gigachat_client.enrich_patent_data(text_to_analyze)

                        if enriched_data:
                            logger.info(f"GigaChat returned enriched data: {enriched_data}")

                            # Обновляем данные патента
                            if enriched_data.get("title") and enriched_data["title"] != title:
                                old_title = patent.title
                                patent.title = enriched_data["title"]
                                logger.info(f"Updated title for {patent_id}: '{old_title}' -> '{patent.title}'")

                            if enriched_data.get("authors") and not patent.authors:
                                patent.authors = enriched_data["authors"]
                                logger.info(f"Updated authors for {patent_id}: {patent.authors}")

                            if enriched_data.get("patent_holders") and not patent.patent_holders:
                                patent.patent_holders = enriched_data["patent_holders"]
                                logger.info(f"Updated patent_holders for {patent_id}: {patent.patent_holders}")
                        else:
                            logger.warning(f"GigaChat returned no enriched data for {patent_id}")
                    except Exception as enrich_error:
                        logger.warning(f"Failed to enrich patent {patent_id} with GigaChat: {enrich_error}")
                        # Продолжаем без обогащения

                except Exception as e:
                    logger.error(f"Error enriching patent {patent_id} with GigaChat: {e}")
                    import traceback
                    logger.error(f"GigaChat error traceback: {traceback.format_exc()}")

            logger.info(f"Final enriched patent for {patent_id}: title='{patent.title}', authors={len(patent.authors)}")
            return patent

        except Exception as e:
            logger.error(f"Error creating enriched patent from hit data for {patent_id}: {e}")
            import traceback
            logger.error(f"Enriched patent creation traceback: {traceback.format_exc()}")
            return None

    async def _create_basic_patent_from_hit(self, hit: dict, patent_id: str) -> Optional[Patent]:
        """Создает базовый объект патента из данных hit (когда детальная информация недоступна)"""
        try:
            logger.debug(f"Creating basic patent from hit data for {patent_id}, hit keys: {list(hit.keys())}")

            # Извлекаем доступную информацию из hit
            title = hit.get("title", "").strip()
            logger.debug(f"Hit title for {patent_id}: '{hit.get('title')}' -> stripped: '{title}'")

            # Если title пустое или совпадает с ID, используем fallback
            if not title or title == patent_id:
                title = f"Патент {patent_id}"

            abstract = clean_text(hit.get("abstract", ""))

            # Обрабатываем списки, убирая пустые значения
            authors = [clean_text(author) for author in hit.get("inventors", []) if author]
            patent_holders = [clean_text(holder) for holder in hit.get("patentees", []) if holder]
            ipc_codes = [clean_text(code) for code in hit.get("ipc_codes", []) if code]

            # Пытаемся распарсить даты
            publication_date = None
            application_date = None

            if hit.get("publication_date"):
                try:
                    publication_date = datetime.strptime(hit["publication_date"], "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    pass

            if hit.get("application_date"):
                try:
                    application_date = datetime.strptime(hit["application_date"], "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    pass

            logger.debug(f"Created basic patent for {patent_id}: title='{title}', authors={len(authors)}")

            return Patent.create(
                id=patent_id,
                title=title,
                publication_date=publication_date,
                application_date=application_date,
                authors=authors or [],
                patent_holders=patent_holders or [],
                ipc_codes=ipc_codes or [],
                abstract=abstract
            )
        except Exception as e:
            logger.error(f"Error creating basic patent from hit data for {patent_id}: {e}")
            return None

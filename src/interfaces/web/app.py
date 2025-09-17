from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from datetime import date
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

from src.infrastructure.config.settings import Settings
from src.infrastructure.rospatent.repository import RospatentRepository
from src.infrastructure.rospatent.config import RospatentConfig
from src.infrastructure.cache.patent_cache import PatentCache
from src.infrastructure.gigachat.client import GigaChatClient
from src.infrastructure.gigachat.config import GigaChatConfig
from src.application.services.patent_summarizer import PatentSummarizer
from src.application.services.patent_enricher import PatentEnricher
from src.application.services.patent_clustering import PatentClusteringService
from src.application.services.patent_analytics import PatentAnalyticsService
from src.application.use_cases.patent_search import PatentSearchUseCase
from src.domain.entities.search_filter import SearchFilter
from src.domain.entities.patent import Patent

app = FastAPI(
    title="Patent Search API",
    description="API for patent search, analysis and clustering",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Serve the main HTML page
@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return {"message": "Welcome to Patent Search API. Visit /static/index.html for the web interface."}

async def initialize_services():
    """Инициализация всех сервисов приложения"""
    global api_instance
    try:
        # Загружаем настройки
        settings = Settings.from_env()

        # Настраиваем логирование
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        logger = logging.getLogger(__name__)
        logger.info("Initializing patent search web service...")

        # Инициализируем инфраструктуру
        patent_cache = PatentCache()
        gigachat_config = GigaChatConfig(
            client_id=settings.gigachat_client_id,
            client_secret=settings.gigachat_client_secret,
            base_url=settings.gigachat_base_url
        )
        gigachat_client = GigaChatClient(config=gigachat_config)

        # Инициализируем репозиторий
        rospatent_config = RospatentConfig(
            jwt_token=settings.rospatent_jwt,
            base_url=settings.rospatent_base_url
        )
        patent_repository = RospatentRepository(config=rospatent_config)

        # Инициализируем сервисы
        patent_summarizer = PatentSummarizer(gigachat_client)
        patent_enricher = PatentEnricher(gigachat_client)
        clustering_service = PatentClusteringService(gigachat_client)
        analytics_service = PatentAnalyticsService(gigachat_client)

        # Инициализируем use case
        search_use_case = PatentSearchUseCase(patent_repository)

        # Инициализируем API
        api_instance = PatentSearchAPI(
            search_use_case=search_use_case,
            patent_summarizer=patent_summarizer,
            patent_enricher=patent_enricher,
            clustering_service=clustering_service,
            analytics_service=analytics_service
        )

        logger.info("All services initialized successfully")

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    await initialize_services()

class PatentSearchAPI:
    """REST API для поиска и анализа патентов"""

    def __init__(
        self,
        search_use_case: PatentSearchUseCase,
        patent_summarizer: PatentSummarizer,
        patent_enricher: PatentEnricher,
        clustering_service: PatentClusteringService,
        analytics_service: PatentAnalyticsService
    ):
        self.search_use_case = search_use_case
        self.patent_summarizer = patent_summarizer
        self.patent_enricher = patent_enricher
        self.clustering_service = clustering_service
        self.analytics_service = analytics_service
        self.logger = logging.getLogger(__name__)

    async def search_patents(
        self,
        query: str,
        limit: int = 10,
        author: Optional[str] = None,
        countries: Optional[List[str]] = None,
        ipc_codes: Optional[List[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ):
        """Поиск патентов с фильтрами"""
        try:
            # Создаем фильтр поиска
            search_filter = SearchFilter(
                countries=countries,
                ipc_codes=ipc_codes,
                date_from=date_from,
                date_to=date_to
            )

            # Выполняем поиск
            result = await self.search_use_case.search_by_query(
                query=query,
                limit=limit,
                search_filter=search_filter
            )

            # Фильтруем по автору если указан
            if author:
                filtered_patents = [
                    patent for patent in result.patents
                    if any(author.lower() in a.lower() for a in patent.authors)
                ]
                result = result.__class__(
                    patents=filtered_patents,
                    total_count=len(filtered_patents),
                    query=result.query
                )

            return {
                "query": result.query,
                "total_count": result.total_count,
                "patents": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "publication_date": p.publication_date.isoformat() if p.publication_date else None,
                        "application_date": p.application_date.isoformat() if p.application_date else None,
                        "authors": p.authors,
                        "patent_holders": p.patent_holders,
                        "ipc_codes": p.ipc_codes,
                        "abstract": p.abstract
                    }
                    for p in result.patents
                ]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    async def get_patent_details(self, patent_id: str):
        """Получение детальной информации о патенте с обогащением данных"""
        try:
            self.logger.info(f"Получение деталей патента {patent_id}")

            # Получаем базовую информацию о патенте
            patent = await self.search_use_case.get_patent_details(patent_id)
            self.logger.info(f"Получены базовые данные патента: title='{patent.title}', authors={patent.authors}")

            # Обогащаем данные патента с помощью GigaChat (с обработкой ошибок)
            try:
                self.logger.info(f"Запуск обогащения данных для патента {patent_id}")
                enrichment_result = await self.patent_enricher.get_enrichment_summary(patent)
                enriched_patent_data = enrichment_result["enriched_patent"]
                enrichment_info = enrichment_result["enrichment_info"]
            except Exception as enrichment_error:
                self.logger.warning(f"Failed to enrich patent data for {patent_id}: {enrichment_error}")
                # Fallback to original patent data
                enriched_patent_data = {
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
                }
                enrichment_info = {
                    "fields_enriched": [],
                    "enrichment_status": "error"
                }

            self.logger.info(f"Результат обогащения: fields_enriched={enrichment_info['fields_enriched']}, status={enrichment_info['enrichment_status']}")
            self.logger.info(f"Обогащенные данные: title='{enriched_patent_data['title']}', authors={enriched_patent_data['authors']}")

            # Получаем анализ патента (с обработкой ошибок)
            try:
                analysis = await self.patent_summarizer.summarize(patent)
            except Exception as analysis_error:
                self.logger.warning(f"Failed to get patent analysis for {patent_id}: {analysis_error}")
                analysis = {
                    "status": "error",
                    "summary": "Анализ патента временно недоступен"
                }

            return {
                "patent": enriched_patent_data,
                "enrichment_info": enrichment_info,
                "analysis": analysis
            }

        except ValueError as e:
            self.logger.error(f"Патент {patent_id} не найден: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            self.logger.error(f"Ошибка при получении деталей патента {patent_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to get patent details: {str(e)}")

    async def cluster_patents(self, query: str, limit: int = 20, num_clusters: Optional[int] = None):
        """Кластеризация патентов по темам"""
        try:
            # Получаем патенты для кластеризации
            result = await self.search_use_case.search_by_query(query=query, limit=limit)
            patents = result.patents

            if len(patents) < 2:
                return {"error": "Недостаточно патентов для кластеризации (минимум 2)"}

            # Выполняем кластеризацию
            clustering_result = await self.clustering_service.cluster_patents_by_theme(
                patents=patents,
                num_clusters=num_clusters
            )

            return clustering_result

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")

    async def get_similar_patents(self, patent_id: str, limit: int = 5):
        """Поиск похожих патентов"""
        try:
            # Получаем целевой патент
            target_patent = await self.search_use_case.get_patent_details(patent_id)

            # Получаем все патенты для сравнения (в реальности нужно оптимизировать)
            all_patents_result = await self.search_use_case.search_by_query(
                query="", limit=100  # Ограничение для производительности
            )
            all_patents = all_patents_result.patents

            # Находим похожие патенты
            similar_patents = await self.clustering_service.find_similar_patents(
                target_patent=target_patent,
                all_patents=all_patents,
                top_k=limit
            )

            return {
                "target_patent": {
                    "id": target_patent.id,
                    "title": target_patent.title
                },
                "similar_patents": similar_patents
            }

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to find similar patents: {str(e)}")

    async def analyze_innovations(self, patent_id: str):
        """Анализ ключевых инноваций патента"""
        try:
            patent = await self.search_use_case.get_patent_details(patent_id)
            analysis = await self.analytics_service.extract_key_innovations(patent)
            return analysis

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    async def get_trends(self, query: str = "", period_years: int = 5, limit: int = 500):
        """Анализ трендов патентования на основе Hit data"""
        try:
            # Получаем Hit data из поиска (без детальной информации о патентах)
            async with self.search_use_case.patent_repository._get_session() as session:
                url = f"{self.search_use_case.patent_repository.config.base_url}/search"
                payload = {"qn": query, "limit": limit}

                async with session.post(url, json=payload, headers=self.search_use_case.patent_repository.config.headers) as response:
                    response.raise_for_status()
                    search_data = await response.json()

                    # Извлекаем hits из ответа
                    hits = search_data.get("hits", [])
                    logger.info(f"Retrieved {len(hits)} hits for trend analysis")

            # Анализируем тренды по упрощенной логике на основе Hit data
            trends = self.analytics_service.analyze_simple_trends(
                hits=hits,
                period_years=period_years,
                limit=limit
            )

            return trends

        except Exception as e:
            logger.error(f"Trends analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Trends analysis failed: {str(e)}")

    async def get_visualization_data(self, query: str = "", period_years: int = 5, limit: int = 500):
        """Получение данных для визуализации трендов"""
        try:
            # Получаем патенты для анализа
            result = await self.search_use_case.search_by_query(
                query=query,
                limit=limit  # Настраиваемое количество патентов для анализа трендов
            )
            patents = result.patents

            # Генерируем данные для графиков
            viz_data = self.analytics_service.generate_trend_visualization_data(
                patents=patents,
                period_years=period_years
            )

            return viz_data

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Visualization data generation failed: {str(e)}")

    async def get_ipc_trends(self, ipc_code: str, query: str = "", limit: int = 500):
        """Получение трендов по конкретному IPC коду"""
        try:
            # Получаем патенты для анализа
            result = await self.search_use_case.search_by_query(
                query=query,
                limit=limit
            )
            patents = result.patents

            # Анализируем тренды по конкретному IPC коду
            ipc_trends = self.analytics_service.analyze_ipc_trends(
                patents=patents,
                ipc_code=ipc_code
            )

            return ipc_trends

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"IPC trends analysis failed: {str(e)}")

# Global API instance (will be initialized in main)
api_instance: Optional["PatentSearchAPI"] = None

@app.get("/api/search")
async def search_patents(
    query: str = Query("", description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
    author: Optional[str] = Query(None, description="Filter by author"),
    countries: Optional[List[str]] = Query(None, description="Filter by countries"),
    ipc_codes: Optional[List[str]] = Query(None, description="Filter by IPC codes"),
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date")
):
    """Поиск патентов с фильтрами"""
    if not api_instance:
        raise HTTPException(status_code=500, detail="API not initialized")
    return await api_instance.search_patents(
        query=query, limit=limit, author=author, countries=countries,
        ipc_codes=ipc_codes, date_from=date_from, date_to=date_to
    )

@app.get("/api/patents/{patent_id}")
async def get_patent_details(patent_id: str):
    """Получение детальной информации о патенте"""
    if not api_instance:
        raise HTTPException(status_code=500, detail="API not initialized")
    return await api_instance.get_patent_details(patent_id)

@app.post("/api/cluster")
async def cluster_patents(
    query: str = Query("", description="Search query for patents to cluster"),
    limit: int = Query(20, description="Maximum number of patents to cluster"),
    num_clusters: Optional[int] = Query(None, description="Number of clusters (auto if not specified)")
):
    """Кластеризация патентов по тематической близости"""
    if not api_instance:
        raise HTTPException(status_code=500, detail="API not initialized")
    return await api_instance.cluster_patents(query=query, limit=limit, num_clusters=num_clusters)

@app.get("/api/patents/{patent_id}/similar")
async def get_similar_patents(
    patent_id: str,
    limit: int = Query(5, description="Number of similar patents to return")
):
    """Поиск патентов, похожих на заданный"""
    if not api_instance:
        raise HTTPException(status_code=500, detail="API not initialized")
    return await api_instance.get_similar_patents(patent_id=patent_id, limit=limit)

@app.get("/api/patents/{patent_id}/innovations")
async def analyze_innovations(patent_id: str):
    """Анализ ключевых инноваций патента"""
    if not api_instance:
        raise HTTPException(status_code=500, detail="API not initialized")
    return await api_instance.analyze_innovations(patent_id=patent_id)

@app.get("/api/trends")
async def get_trends(
    query: str = Query("", description="Search query (empty for all patents)"),
    period_years: int = Query(5, description="Analysis period in years"),
    limit: int = Query(500, description="Maximum number of patents to analyze")
):
    """Анализ трендов патентования"""
    if not api_instance:
        raise HTTPException(status_code=500, detail="API not initialized")
    return await api_instance.get_trends(query=query, period_years=period_years, limit=limit)

@app.get("/api/visualization")
async def get_visualization_data(
    query: str = Query("", description="Search query (empty for all patents)"),
    period_years: int = Query(5, description="Analysis period in years"),
    limit: int = Query(500, description="Maximum number of patents to analyze")
):
    """Получение данных для построения графиков трендов"""
    if not api_instance:
        raise HTTPException(status_code=500, detail="API not initialized")
    return await api_instance.get_visualization_data(query=query, period_years=period_years, limit=limit)

@app.get("/api/ipc-trends/{ipc_code}")
async def get_ipc_trends(
    ipc_code: str,
    query: str = Query("", description="Search query (empty for all patents)"),
    limit: int = Query(500, description="Maximum number of patents to analyze")
):
    """Получение трендов по конкретному IPC коду"""
    if not api_instance:
        raise HTTPException(status_code=500, detail="API not initialized")
    return await api_instance.get_ipc_trends(ipc_code=ipc_code, query=query, limit=limit)

@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "healthy"}

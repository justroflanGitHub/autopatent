import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from collections import defaultdict, Counter
import json

from src.domain.entities.patent import Patent
from src.infrastructure.gigachat.client import GigaChatClient

logger = logging.getLogger(__name__)

class PatentAnalyticsService:
    """Сервис для анализа патентов и трендов"""

    def __init__(self, gigachat_client: GigaChatClient):
        self.gigachat_client = gigachat_client

    async def extract_key_innovations(self, patent: Patent) -> Dict[str, Any]:
        """Извлекает ключевые инновации из патента"""
        try:
            # Формируем текст для анализа
            patent_text = patent.get_full_text()

            prompt = f"""Проанализируй следующий патент и выдели ключевые инновации.

            {patent_text}

            Пожалуйста, предоставь анализ в следующем формате JSON:
            {{
                "technical_solution": "краткое описание нового технического решения",
                "advantages": ["преимущество 1", "преимущество 2", "преимущество 3"],
                "novelty": "что именно нового в этом решении",
                "application_field": "область применения",
                "key_features": ["особенность 1", "особенность 2"]
            }}

            Ответ должен быть только в формате JSON, без дополнительного текста."""

            # Используем summarize_patent с кастомным промптом для анализа инноваций
            analysis_result = await self.gigachat_client.summarize_patent(patent_text)

            if analysis_result.get("status") == "success":
                # Пытаемся распарсить ответ как JSON
                try:
                    analysis = json.loads(analysis_result.get("summary", "{}"))
                except json.JSONDecodeError:
                    # Fallback анализ
                    analysis = await self._fallback_innovation_analysis(patent)
            else:
                # Fallback анализ при ошибке
                analysis = await self._fallback_innovation_analysis(patent)

            return {
                "patent_id": patent.id,
                "analysis": analysis,
                "method": "AI-powered analysis"
            }

        except Exception as e:
            logger.error(f"Error extracting innovations from patent {patent.id}: {e}")
            return {
                "patent_id": patent.id,
                "analysis": {
                    "technical_solution": "Не удалось проанализировать",
                    "advantages": [],
                    "novelty": "Ошибка анализа",
                    "application_field": "Не определено",
                    "key_features": []
                },
                "error": str(e)
            }

    async def _fallback_innovation_analysis(self, patent: Patent) -> Dict[str, Any]:
        """Резервный анализ инноваций без JSON парсинга"""
        try:
            prompt = f"""Проанализируй патент и выдели ключевые инновации:

            Название: {patent.title}
            Реферат: {patent.abstract}

            Опиши:
            1. Новое техническое решение
            2. Преимущества перед аналогами
            3. Область применения"""

            # Используем summarize_patent для fallback анализа
            fallback_result = await self.gigachat_client.summarize_patent(patent_text)

            return {
                "technical_solution": patent.title,
                "advantages": ["Анализ требует уточнения"],
                "novelty": "Требуется дополнительный анализ",
                "application_field": "Определяется по IPC кодам",
                "key_features": patent.ipc_codes
            }

        except Exception:
            return {
                "technical_solution": patent.title,
                "advantages": [],
                "novelty": "Не проанализировано",
                "application_field": "Не определено",
                "key_features": []
            }

    def analyze_patent_trends(
        self,
        patents: List[Patent],
        period_years: int = 5
    ) -> Dict[str, Any]:
        """Анализирует тренды патентования"""
        try:
            if not patents:
                return {"error": "No patents to analyze"}

            logger.info(f"Starting trend analysis for {len(patents)} patents, period: {period_years} years")

            # Группируем патенты по годам
            yearly_stats = defaultdict(int)
            ipc_trends = defaultdict(lambda: defaultdict(int))
            author_trends = defaultdict(lambda: defaultdict(int))

            current_year = datetime.now().year
            start_year = current_year - period_years

            patents_with_dates = 0
            patents_without_dates = 0

            for patent in patents:
                logger.debug(f"Analyzing patent {patent.id}: pub_date={patent.publication_date}, app_date={patent.application_date}")

                # Пробуем использовать publication_date, если нет - application_date
                patent_date = patent.publication_date or patent.application_date

                if patent_date:
                    year = patent_date.year
                    # Расширяем период анализа - включаем все патенты с датами
                    if 2000 <= year <= current_year + 5:  # От 2000 до 2030
                        yearly_stats[year] += 1
                        patents_with_dates += 1

                        # Анализ по IPC кодам
                        for ipc_code in patent.ipc_codes:
                            ipc_trends[ipc_code][year] += 1

                        # Анализ по авторам
                        for author in patent.authors:
                            author_trends[author][year] += 1
                    else:
                        logger.debug(f"Patent {patent.id} date {year} is outside extended analysis period 2000-{current_year + 5}")
                        patents_without_dates += 1
                else:
                    # Fallback: распределяем патенты без дат равномерно по периоду анализа
                    patents_without_dates += 1
                    logger.debug(f"Patent {patent.id} has no dates, distributing across analysis period")

                    # Распределяем патент равномерно по всем годам периода анализа
                    years_in_period = list(range(start_year, current_year + 1))
                    patents_per_year = 1.0 / len(years_in_period) if years_in_period else 1.0

                    for year in years_in_period:
                        yearly_stats[year] += patents_per_year

                        # Анализ по IPC кодам для патентов без дат
                        for ipc_code in patent.ipc_codes:
                            ipc_trends[ipc_code][year] += patents_per_year

                        # Анализ по авторам для патентов без дат
                        for author in patent.authors:
                            author_trends[author][year] += patents_per_year

            logger.info(f"Analysis complete: {patents_with_dates} patents with dates, {patents_without_dates} without dates")
            logger.info(f"Yearly stats: {dict(yearly_stats)}")
            logger.info(f"IPC trends keys: {list(ipc_trends.keys())[:5]}")  # Показываем первые 5 IPC кодов
            logger.info(f"Author trends keys: {list(author_trends.keys())[:5]}")  # Показываем первых 5 авторов

            # Вычисляем рост/падение
            growth_rates = self._calculate_growth_rates(yearly_stats)

            # Находим наиболее активные области
            top_ipc_codes = self._get_top_trending_ipc(ipc_trends, period_years)

            # Находим наиболее активных авторов
            top_authors = self._get_top_authors(author_trends, period_years)

            return {
                "period": {
                    "start_year": start_year,
                    "end_year": current_year,
                    "years_analyzed": period_years
                },
                "yearly_statistics": dict(yearly_stats),
                "growth_rates": growth_rates,
                "top_ipc_codes": top_ipc_codes,
                "top_authors": top_authors,
                "total_patents": len(patents),
                "analyzed_patents": sum(yearly_stats.values())
            }

        except Exception as e:
            logger.error(f"Error analyzing patent trends: {e}")
            return {"error": str(e)}

    def _calculate_growth_rates(self, yearly_stats: Dict[int, int]) -> Dict[str, Any]:
        """Вычисляет темпы роста патентования"""
        if len(yearly_stats) < 2:
            return {"insufficient_data": True}

        sorted_years = sorted(yearly_stats.keys())
        growth_rates = {}

        for i in range(1, len(sorted_years)):
            current_year = sorted_years[i]
            previous_year = sorted_years[i-1]

            current_count = yearly_stats[current_year]
            previous_count = yearly_stats[previous_year]

            if previous_count > 0:
                growth_rate = ((current_count - previous_count) / previous_count) * 100
                growth_rates[f"{previous_year}-{current_year}"] = round(growth_rate, 2)

        # Общий тренд
        first_year = sorted_years[0]
        last_year = sorted_years[-1]

        if yearly_stats[first_year] > 0:
            total_growth = ((yearly_stats[last_year] - yearly_stats[first_year]) / yearly_stats[first_year]) * 100
            growth_rates["total"] = round(total_growth, 2)

        return growth_rates

    def _get_top_trending_ipc(
        self,
        ipc_trends: Dict[str, Dict[int, int]],
        period_years: int
    ) -> List[Dict[str, Any]]:
        """Определяет наиболее трендовые IPC коды"""
        current_year = datetime.now().year
        recent_years = [current_year - i for i in range(period_years)]

        ipc_scores = []

        for ipc_code, yearly_data in ipc_trends.items():
            total_patents = sum(yearly_data.values())
            recent_patents = sum(yearly_data.get(year, 0) for year in recent_years)

            # Вычисляем трендовость (рост в последние годы)
            if total_patents > 0:
                recency_score = recent_patents / period_years
                ipc_scores.append({
                    "ipc_code": ipc_code,
                    "total_patents": total_patents,
                    "recent_patents": recent_patents,
                    "recency_score": round(recency_score, 2)
                })

        # Сортируем по трендовости
        ipc_scores.sort(key=lambda x: x["recency_score"], reverse=True)

        return ipc_scores[:10]  # Топ-10

    def _get_top_authors(
        self,
        author_trends: Dict[str, Dict[int, int]],
        period_years: int
    ) -> List[Dict[str, Any]]:
        """Определяет наиболее активных авторов"""
        current_year = datetime.now().year
        recent_years = [current_year - i for i in range(period_years)]

        author_scores = []

        for author, yearly_data in author_trends.items():
            total_patents = sum(yearly_data.values())
            recent_patents = sum(yearly_data.get(year, 0) for year in recent_years)

            if total_patents > 0:
                author_scores.append({
                    "author": author,
                    "total_patents": total_patents,
                    "recent_patents": recent_patents,
                    "avg_per_year": round(total_patents / period_years, 2)
                })

        # Сортируем по общему количеству патентов
        author_scores.sort(key=lambda x: x["total_patents"], reverse=True)

        return author_scores[:10]  # Топ-10

    def generate_trend_visualization_data(
        self,
        patents: List[Patent],
        period_years: int = 5
    ) -> Dict[str, Any]:
        """Генерирует данные для визуализации трендов"""
        trends = self.analyze_patent_trends(patents, period_years)

        if "error" in trends:
            return trends

        # Данные для линейного графика по годам
        yearly_data = trends["yearly_statistics"]
        chart_data = {
            "years": sorted(yearly_data.keys()),
            "patents_count": [yearly_data[year] for year in sorted(yearly_data.keys())]
        }

        # Данные для круговой диаграммы по IPC кодам
        ipc_data = []
        for ipc_item in trends["top_ipc_codes"][:8]:  # Топ-8 для читаемости
            ipc_data.append({
                "ipc_code": ipc_item["ipc_code"],
                "count": ipc_item["total_patents"]
            })

        return {
            "line_chart": chart_data,
            "pie_chart": ipc_data,
            "trends_summary": {
                "total_growth_rate": trends["growth_rates"].get("total", 0),
                "top_ipc_code": trends["top_ipc_codes"][0]["ipc_code"] if trends["top_ipc_codes"] else None,
                "most_active_author": trends["top_authors"][0]["author"] if trends["top_authors"] else None
            }
        }

    async def compare_patents(self, patent1: Patent, patent2: Patent) -> Dict[str, Any]:
        """Сравнивает два патента"""
        try:
            text1 = patent1.get_full_text()
            text2 = patent2.get_full_text()

            prompt = f"""Сравни следующие два патента:

            ПАТЕНТ 1:
            Название: {patent1.title}
            Реферат: {patent1.abstract}

            ПАТЕНТ 2:
            Название: {patent2.title}
            Реферат: {patent2.abstract}

            Проанализируй:
            1. Общие темы/области
            2. Ключевые различия в технических решениях
            3. Возможные преимущества каждого решения
            4. Потенциал для комбинирования идей

            Дай краткий анализ в 200-300 слов."""

            # Используем summarize_patent для сравнения патентов
            comparison_result = await self.gigachat_client.summarize_patent(text1 + "\n\n--- Сравнение с ---\n\n" + text2)

            return {
                "patent1_id": patent1.id,
                "patent2_id": patent2.id,
                "comparison": comparison_result.get("summary", "Не удалось выполнить сравнение") if comparison_result.get("status") == "success" else "Не удалось выполнить сравнение",
                "similarity_score": self._calculate_similarity_score(text1, text2)
            }

        except Exception as e:
            logger.error(f"Error comparing patents: {e}")
            return {
                "patent1_id": patent1.id,
                "patent2_id": patent2.id,
                "comparison": "Ошибка при сравнении патентов",
                "error": str(e)
            }

    def analyze_ipc_trends(self, patents: List[Patent], ipc_code: str) -> Dict[str, Any]:
        """Анализ трендов по конкретному IPC коду"""
        try:
            logger.info(f"Analyzing trends for IPC code: {ipc_code}")

            # Группируем патенты по годам для этого IPC кода
            yearly_stats = defaultdict(int)
            current_year = datetime.now().year
            start_year = current_year - 5  # Анализируем последние 5 лет

            patents_with_ipc = []
            recent_patents = []

            for patent in patents:
                # Проверяем, содержит ли патент нужный IPC код
                if ipc_code in patent.ipc_codes:
                    patents_with_ipc.append(patent)

                    # Определяем год для патента
                    patent_date = patent.publication_date or patent.application_date
                    if patent_date:
                        year = patent_date.year
                        if start_year <= year <= current_year:
                            yearly_stats[year] += 1

                            # Собираем недавние патенты (последние 3 года)
                            if year >= current_year - 3:
                                recent_patents.append({
                                    "id": patent.id,
                                    "title": patent.title,
                                    "publication_date": patent.publication_date.isoformat() if patent.publication_date else None
                                })

            # Вычисляем статистику
            total_patents = len(patents_with_ipc)
            avg_per_year = total_patents / 5 if total_patents > 0 else 0

            # Вычисляем рост тренда
            sorted_years = sorted(yearly_stats.keys())
            growth_rate = None
            if len(sorted_years) >= 2:
                first_year = sorted_years[0]
                last_year = sorted_years[-1]
                if yearly_stats[first_year] > 0:
                    growth_rate = round(
                        ((yearly_stats[last_year] - yearly_stats[first_year]) / yearly_stats[first_year]) * 100,
                        2
                    )

            logger.info(f"IPC {ipc_code} analysis: {total_patents} patents, avg {avg_per_year} per year")

            return {
                "ipc_code": ipc_code,
                "total_patents": total_patents,
                "period": {
                    "start_year": start_year,
                    "end_year": current_year
                },
                "yearly_data": dict(yearly_stats),
                "avg_per_year": round(avg_per_year, 2),
                "growth_rate": growth_rate,
                "recent_patents": recent_patents[:10]  # Ограничиваем до 10 недавних патентов
            }

        except Exception as e:
            logger.error(f"Error analyzing IPC trends for {ipc_code}: {e}")
            return {"error": str(e)}

    def _calculate_similarity_score(self, text1: str, text2: str) -> float:
        """Простой расчет схожести текстов по пересечению слов"""
        try:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            intersection = words1.intersection(words2)
            union = words1.union(words2)

            if not union:
                return 0.0

            return len(intersection) / len(union)

        except Exception:
            return 0.0

    def analyze_simple_trends(
        self,
        hits: List[Dict[str, Any]],
        period_years: int = 5,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Анализирует тренды патентования по упрощенной логике на основе Hit data"""
        try:
            if not hits:
                return {"error": "No hits to analyze"}

            logger.info(f"Starting simple trend analysis for {len(hits)} hits, period: {period_years} years, limit: {limit}")

            # Ограничиваем количество hits для анализа
            hits_to_analyze = hits[:limit] if limit > 0 else hits

            # Группируем патенты по годам на основе publication_date из Hit data
            yearly_stats = defaultdict(int)
            ipc_trends = defaultdict(lambda: defaultdict(int))

            current_year = datetime.now().year
            start_year = current_year - period_years + 1  # Включаем текущий год

            # Расширяем период для анализа, чтобы захватить все патенты
            extended_start_year = max(2000, start_year - 2)  # Начинаем с 2000 или на 2 года раньше
            extended_end_year = current_year + 2  # Заканчиваем на 2 года позже

            hits_with_dates = 0

            for hit in hits_to_analyze:
                logger.debug(f"Analyzing hit: {hit.get('id', 'unknown')}")

                # Извлекаем дату публикации из Hit data
                publication_date_str = hit.get('common', {}).get('publication_date', '')
                logger.debug(f"Publication date string: '{publication_date_str}'")

                if publication_date_str:
                    # Парсим дату публикации
                    patent_date = self._parse_hit_date(publication_date_str)
                    logger.debug(f"Parsed publication date: {patent_date}")

                    if patent_date:
                        year = patent_date.year
                        # Проверяем, что год входит в расширенный период анализа
                        if extended_start_year <= year <= extended_end_year:
                            yearly_stats[year] += 1
                            hits_with_dates += 1

                            # Анализ по IPC кодам из Hit data
                            ipc_codes = hit.get('common', {}).get('classification', {}).get('ipc', [])
                            for ipc_item in ipc_codes:
                                ipc_code = ipc_item.get('fullname', '').strip()
                                if ipc_code:
                                    ipc_trends[ipc_code][year] += 1
                                    logger.debug(f"Added IPC code: {ipc_code} for year {year}")
                        else:
                            logger.debug(f"Hit {hit.get('id', 'unknown')} date {year} is outside extended analysis period {extended_start_year}-{extended_end_year}")
                    else:
                        logger.debug(f"Could not parse publication date: '{publication_date_str}'")
                else:
                    logger.debug(f"Hit has no publication_date")

            logger.info(f"Analysis complete: {hits_with_dates} hits with dates")
            logger.info(f"Yearly stats: {dict(yearly_stats)}")

            # Находим наиболее активные области
            top_ipc_codes = self._get_top_trending_ipc(ipc_trends, period_years)

            return {
                "period": {
                    "start_year": start_year,
                    "end_year": current_year,
                    "years_analyzed": period_years
                },
                "yearly_statistics": dict(yearly_stats),
                "top_ipc_codes": top_ipc_codes,
                "total_patents": len(hits_to_analyze),
                "analyzed_patents": hits_with_dates
            }

        except Exception as e:
            logger.error(f"Error analyzing simple patent trends: {e}")
            return {"error": str(e)}

    def _parse_hit_date(self, date_str: str) -> Optional[date]:
        """Парсит дату из Hit data"""
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

        logger.error(f"Failed to parse hit date '{date_str}'")
        return None

    def _get_top_trending_ipc_monthly(
        self,
        ipc_trends: Dict[str, Dict[str, int]],
        period_years: int
    ) -> List[Dict[str, Any]]:
        """Определяет наиболее трендовые IPC коды по месячным данным"""
        current_date = datetime.now()
        # Берем последние period_years лет
        recent_months = []
        for i in range(period_years * 12):
            date = current_date - timedelta(days=i * 30)
            month_key = f"{date.year}-{date.month:02d}"
            if month_key not in recent_months:
                recent_months.append(month_key)

        ipc_scores = []

        for ipc_code, monthly_data in ipc_trends.items():
            total_patents = sum(monthly_data.values())
            recent_patents = sum(monthly_data.get(month, 0) for month in recent_months)

            # Вычисляем трендовость (рост в последние месяцы)
            if total_patents > 0:
                recency_score = recent_patents / (period_years * 12) if period_years * 12 > 0 else 0
                ipc_scores.append({
                    "ipc_code": ipc_code,
                    "total_patents": total_patents,
                    "recent_patents": recent_patents,
                    "recency_score": round(recency_score, 2)
                })

        # Сортируем по трендовости
        ipc_scores.sort(key=lambda x: x["recency_score"], reverse=True)

        return ipc_scores[:10]  # Топ-10

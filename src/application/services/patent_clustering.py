import asyncio
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.domain.entities.patent import Patent
from src.infrastructure.gigachat.client import GigaChatClient

logger = logging.getLogger(__name__)

class PatentClusteringService:
    """Сервис для кластеризации патентов с помощью AI"""

    def __init__(self, gigachat_client: GigaChatClient):
        self.gigachat_client = gigachat_client

    async def cluster_patents_by_theme(
        self,
        patents: List[Patent],
        num_clusters: Optional[int] = None
    ) -> Dict[str, Any]:
        """Кластеризация патентов по тематической близости"""
        if len(patents) < 2:
            return {
                "clusters": [{"patents": patents, "theme": "Single patent", "count": len(patents)}],
                "total_clusters": 1
            }

        try:
            # Извлекаем тексты патентов для анализа
            patent_texts = []
            patent_ids = []

            for patent in patents:
                text = patent.get_full_text()
                if text.strip():
                    patent_texts.append(text)
                    patent_ids.append(patent.id)

            if len(patent_texts) < 2:
                return {
                    "clusters": [{"patents": patents, "theme": "Insufficient data", "count": len(patents)}],
                    "total_clusters": 1
                }

            # Определяем оптимальное количество кластеров
            if num_clusters is None:
                num_clusters = min(len(patent_texts), max(2, len(patent_texts) // 3))

            # Создаем TF-IDF векторы
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=self._get_russian_stop_words(),
                ngram_range=(1, 2)
            )

            tfidf_matrix = vectorizer.fit_transform(patent_texts)

            # Выполняем кластеризацию
            kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)

            # Группируем патенты по кластерам
            cluster_groups = defaultdict(list)
            for idx, cluster_id in enumerate(clusters):
                patent_id = patent_ids[idx]
                original_patent = next(p for p in patents if p.id == patent_id)
                cluster_groups[cluster_id].append(original_patent)

            # Определяем темы для каждого кластера
            cluster_themes = await self._extract_cluster_themes(cluster_groups, vectorizer, kmeans)

            # Формируем результат
            result_clusters = []
            for cluster_id, patents_in_cluster in cluster_groups.items():
                theme = cluster_themes.get(cluster_id, f"Cluster {cluster_id}")
                result_clusters.append({
                    "theme": theme,
                    "patents": [
                        {
                            "id": p.id,
                            "title": p.title,
                            "authors": p.authors,
                            "ipc_codes": p.ipc_codes,
                            "abstract": p.abstract[:200] + "..." if len(p.abstract) > 200 else p.abstract
                        }
                        for p in patents_in_cluster
                    ],
                    "count": len(patents_in_cluster)
                })

            return {
                "clusters": result_clusters,
                "total_clusters": len(result_clusters),
                "method": "TF-IDF + K-means clustering"
            }

        except Exception as e:
            logger.error(f"Error during patent clustering: {e}")
            return {
                "clusters": [{"patents": patents, "theme": "Clustering failed", "count": len(patents)}],
                "total_clusters": 1,
                "error": str(e)
            }

    async def _extract_cluster_themes(
        self,
        cluster_groups: Dict[int, List[Patent]],
        vectorizer: TfidfVectorizer,
        kmeans: KMeans
    ) -> Dict[int, str]:
        """Извлекает темы для каждого кластера с помощью AI"""
        themes = {}

        for cluster_id, patents in cluster_groups.items():
            try:
                # Собираем тексты патентов в кластере
                cluster_texts = []
                for patent in patents[:5]:  # Ограничиваем для эффективности
                    text = f"Название: {patent.title}\nРеферат: {patent.abstract}"
                    cluster_texts.append(text)

                combined_text = "\n\n".join(cluster_texts)

                # Запрашиваем тему у GigaChat
                prompt = f"""Проанализируй следующие патенты и определи общую тему/область, к которой они относятся.
                Дай краткое название темы (3-7 слов).

                Патенты:
                {combined_text}

                Тема:"""

                response = await self.gigachat_client.generate_response(prompt)
                theme = response.get("response", "").strip()

                if not theme or len(theme) > 50:
                    # Fallback: используем наиболее частые слова из кластера
                    theme = self._extract_theme_from_tfidf(cluster_id, vectorizer, kmeans)

                themes[cluster_id] = theme

            except Exception as e:
                logger.warning(f"Failed to extract theme for cluster {cluster_id}: {e}")
                themes[cluster_id] = f"Тема кластера {cluster_id}"

        return themes

    def _extract_theme_from_tfidf(self, cluster_id: int, vectorizer: TfidfVectorizer, kmeans: KMeans) -> str:
        """Извлекает тему из TF-IDF векторов кластера"""
        try:
            # Получаем центроид кластера
            centroid = kmeans.cluster_centers_[cluster_id]

            # Находим наиболее важные признаки
            feature_names = vectorizer.get_feature_names_out()
            top_indices = centroid.argsort()[-5:][::-1]  # Топ-5 слов

            top_words = [feature_names[i] for i in top_indices if i < len(feature_names)]
            theme = " ".join(top_words[:3])  # Первые 3 слова

            return theme.capitalize() if theme else f"Кластер {cluster_id}"

        except Exception:
            return f"Кластер {cluster_id}"

    def _get_russian_stop_words(self) -> List[str]:
        """Возвращает список стоп-слов для русского языка"""
        return [
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она',
            'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее',
            'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда',
            'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до',
            'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей',
            'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем',
            'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет',
            'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь',
            'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем',
            'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после',
            'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много',
            'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда',
            'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю',
            'между', 'патент', 'изобретение', 'способ', 'устройство', 'метод', 'система'
        ]

    async def find_similar_patents(
        self,
        target_patent: Patent,
        all_patents: List[Patent],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Находит наиболее похожие патенты на заданный"""
        try:
            target_text = target_patent.get_full_text()

            similarities = []
            for patent in all_patents:
                if patent.id == target_patent.id:
                    continue

                patent_text = patent.get_full_text()

                # Вычисляем косинусное сходство
                similarity = self._calculate_text_similarity(target_text, patent_text)
                similarities.append({
                    "patent": patent,
                    "similarity": similarity
                })

            # Сортируем по сходству
            similarities.sort(key=lambda x: x["similarity"], reverse=True)

            # Возвращаем топ-K похожих патентов
            result = []
            for item in similarities[:top_k]:
                patent = item["patent"]
                result.append({
                    "id": patent.id,
                    "title": patent.title,
                    "authors": patent.authors,
                    "similarity": round(item["similarity"], 3),
                    "abstract": patent.abstract[:150] + "..." if len(patent.abstract) > 150 else patent.abstract
                })

            return result

        except Exception as e:
            logger.error(f"Error finding similar patents: {e}")
            return []

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Вычисляет сходство между двумя текстами"""
        try:
            vectorizer = TfidfVectorizer(max_features=500, stop_words=self._get_russian_stop_words())
            tfidf_matrix = vectorizer.fit_transform([text1, text2])

            if tfidf_matrix.shape[0] < 2:
                return 0.0

            similarity_matrix = cosine_similarity(tfidf_matrix)
            return similarity_matrix[0, 1]

        except Exception:
            return 0.0

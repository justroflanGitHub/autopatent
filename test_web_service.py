#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работоспособности веб-сервиса патентного поиска
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_web_service():
    """Тестирование основных функций веб-сервиса"""
    try:
        print("🚀 Testing Patent Search Web Service...")

        # Импортируем необходимые модули
        from src.infrastructure.config.settings import Settings
        from src.infrastructure.rospatent.repository import RospatentRepository
        from src.infrastructure.rospatent.config import RospatentConfig
        from src.infrastructure.cache.patent_cache import PatentCache
        from src.infrastructure.gigachat.client import GigaChatClient
        from src.infrastructure.gigachat.config import GigaChatConfig
        from src.application.services.patent_summarizer import PatentSummarizer
        from src.application.services.patent_clustering import PatentClusteringService
        from src.application.services.patent_analytics import PatentAnalyticsService
        from src.application.use_cases.patent_search import PatentSearchUseCase
        from src.interfaces.web.app import PatentSearchAPI

        print("✅ Imports successful")

        # Проверяем настройки
        try:
            settings = Settings.from_env()
            print("✅ Settings loaded successfully")
            print(f"   Web service will run on {settings.web_host}:{settings.web_port}")
        except Exception as e:
            print(f"❌ Settings error: {e}")
            return False

        # Инициализируем сервисы
        try:
            patent_cache = PatentCache()
            gigachat_config = GigaChatConfig(
                client_id=settings.gigachat_client_id,
                client_secret=settings.gigachat_client_secret,
                base_url=settings.gigachat_base_url
            )
            gigachat_client = GigaChatClient(gigachat_config)
            rospatent_config = RospatentConfig(
                jwt_token=settings.rospatent_jwt,
                base_url=settings.rospatent_base_url
            )
            patent_repository = RospatentRepository(rospatent_config)
            patent_summarizer = PatentSummarizer(gigachat_client)
            clustering_service = PatentClusteringService(gigachat_client)
            analytics_service = PatentAnalyticsService(gigachat_client)
            search_use_case = PatentSearchUseCase(patent_repository)

            print("✅ All services initialized successfully")
        except Exception as e:
            print(f"❌ Service initialization error: {e}")
            return False

        # Тестируем создание API экземпляра
        try:
            api = PatentSearchAPI(
                search_use_case=search_use_case,
                patent_summarizer=patent_summarizer,
                clustering_service=clustering_service,
                analytics_service=analytics_service
            )
            print("✅ API instance created successfully")

            # Имитируем глобальную переменную для тестирования
            from src.interfaces.web.app import api_instance
            # Note: In real app, this would be set by the startup event
            print("✅ API instance would be set globally by startup event")

        except Exception as e:
            print(f"❌ API creation error: {e}")
            return False

        print("\n🎉 All tests passed! Web service is ready to run.")
        print("\nTo start the web service, run:")
        print("python -m src.interfaces.web.main")
        print("\nOr use uvicorn directly:")
        print("uvicorn src.interfaces.web.app:app --host 0.0.0.0 --port 8000 --reload")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Главная функция"""
    print("Patent Search Web Service Test")
    print("=" * 40)

    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found. Using default settings.")
        print("   Make sure to create .env file based on .env.example")

    # Запускаем тест
    success = asyncio.run(test_web_service())

    if success:
        print("\n✅ Web service test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Web service test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

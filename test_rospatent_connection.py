# test_rospatent_connection.py

import asyncio
import logging
import os
import socket
import ssl
import sys

import aiohttp
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
ROSPATENT_JWT = os.getenv("ROSPATENT_JWT")
if not ROSPATENT_JWT:
    logger.error("ROSPATENT_JWT is not set in environment variables")
    sys.exit(1)

BASE_URL = "https://searchplatform.rospatent.gov.ru/patsearch/v0.2"
HEADERS = {
    "Authorization": f"Bearer {ROSPATENT_JWT}",
    "Content-Type": "application/json"
}

def test_dns_lookup():
    """Проверка DNS-разрешения имени хоста Роспатента"""
    logger.info("Выполняется DNS-проверка...")
    try:
        host = "searchplatform.rospatent.gov.ru"
        ip_address = socket.gethostbyname(host)
        logger.info(f"DNS-разрешение для {host}: {ip_address}")
        return True
    except socket.gaierror as e:
        logger.error(f"Ошибка DNS-разрешения: {e}")
        return False

def test_connection_via_requests():
    """Проверка соединения с API Роспатента через библиотеку requests"""
    logger.info("Тестирование соединения через requests...")
    
    try:
        # Тест 1: Запрос HEAD для проверки базового соединения
        response = requests.head(BASE_URL, headers=HEADERS, timeout=10)
        logger.info(f"HEAD запрос: Статус код {response.status_code}")
        
        # Тест 2: Запрос OPTIONS для проверки доступных методов
        response = requests.options(BASE_URL, headers=HEADERS, timeout=10)
        logger.info(f"OPTIONS запрос: Статус код {response.status_code}")
        
        # Тест 3: Получение заголовков сервера 
        logger.info(f"Заголовки сервера: {dict(response.headers)}")
        
        # Тест 4: Проверка SSL информации
        logger.info("SSL сертификат действителен")
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка соединения через requests: {repr(e)}")
        return False

async def test_connection_via_aiohttp():
    """Проверка соединения с API Роспатента через aiohttp (как в приложении)"""
    logger.info("Тестирование соединения через aiohttp...")
    
    try:
        # Тест 1: Создание сессии и запрос
        connector = aiohttp.TCPConnector(verify_ssl=False)  # Так в приложении
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.head(BASE_URL, headers=HEADERS, timeout=10) as response:
                logger.info(f"aiohttp HEAD запрос: Статус код {response.status}")
        
        # Тест 2: Создание сессии и запрос с проверкой SSL
        connector = aiohttp.TCPConnector(verify_ssl=True)  # С проверкой SSL
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.head(BASE_URL, headers=HEADERS, timeout=10) as response:
                logger.info(f"aiohttp HEAD запрос (с SSL проверкой): Статус код {response.status}")
        
        return True
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Ошибка соединения через aiohttp: {repr(e)}")
        return False

async def test_search_similar_request():
    """Тестирование запроса поиска похожих патентов"""
    logger.info("Тестирование запроса поиска похожих патентов...")
    url = f"{BASE_URL}/similar_search"
    payload = {
        "type_search": "id_search",
        "pat_id": "RU2358138C1_20090610",
        "count": 5  # Уменьшаем количество для быстроты
    }
    
    # Проверяем переменные окружения прокси
    env_info = {
        "http_proxy": os.environ.get("http_proxy", "не установлен"),
        "https_proxy": os.environ.get("https_proxy", "не установлен"),
        "no_proxy": os.environ.get("no_proxy", "не установлен"),
        "HTTP_PROXY": os.environ.get("HTTP_PROXY", "не установлен"),
        "HTTPS_PROXY": os.environ.get("HTTPS_PROXY", "не установлен"),
        "NO_PROXY": os.environ.get("NO_PROXY", "не установлен"),
    }
    logger.info(f"Переменные окружения прокси: {env_info}")
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)  # Используем ssl=False вместо устаревшего verify_ssl
        async with aiohttp.ClientSession(connector=connector) as session:
            # Устанавливаем allow_redirects=False для ручной обработки редиректов
            async with session.post(url, json=payload, headers=HEADERS, timeout=30, allow_redirects=False) as response:
                status = response.status
                logger.info(f"Статус запроса /similar_search: {status}")
                
                # Проверяем редирект
                if status in (301, 302, 303, 307, 308):
                    redirect_url = response.headers.get('Location')
                    logger.info(f"Получен редирект на: {redirect_url}")
                    
                    # Проверяем, что URL доступен извне
                    if "prod:" in redirect_url or "10.2.40" in redirect_url:
                        logger.error(f"Недопустимый URL перенаправления (внутренний): {redirect_url}")
                    else:
                        # Проверяем доступность URL перенаправления
                        try:
                            async with session.post(redirect_url, json=payload, headers=HEADERS, timeout=30) as redirect_response:
                                redirect_status = redirect_response.status
                                logger.info(f"Статус запроса после редиректа: {redirect_status}")
                                
                                if redirect_status == 200:
                                    data = await redirect_response.json()
                                    if isinstance(data, dict) and "data" in data:
                                        logger.info(f"Успешный ответ после редиректа, получено элементов: {len(data.get('data', []))}")
                                    else:
                                        logger.warning(f"Неожиданный формат ответа после редиректа: {data}")
                                else:
                                    text = await redirect_response.text()
                                    logger.error(f"Ошибка запроса после редиректа: {redirect_status}, тело ответа: {text}")
                        except Exception as e:
                            logger.error(f"Ошибка при обращении к URL перенаправления: {repr(e)}")
                            import traceback
                            logger.error(traceback.format_exc())
                    
                    return False
                
                elif status == 200:
                    data = await response.json()
                    logger.info(f"Успешный ответ, получено элементов: {len(data.get('data', []))}")
                    return True
                else:
                    text = await response.text()
                    logger.error(f"Ошибка запроса: {status}, тело ответа: {text}")
                    return False
    
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса поиска: {repr(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def test_connections_with_known_working_services():
    """Тестирование соединения с заведомо рабочими сервисами для проверки сети"""
    logger.info("Проверка соединения с заведомо рабочими сервисами...")
    test_urls = [
        "https://www.google.com",
        "https://api.ipify.org?format=json",  # Вернет ваш IP
        "https://httpbin.org/ip"
    ]
    
    results = {}
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        for url in test_urls:
            try:
                async with session.get(url, timeout=10) as response:
                    status = response.status
                    if status == 200:
                        content = await response.text()
                        results[url] = f"OK (status: {status}, length: {len(content)})"
                    else:
                        results[url] = f"ERROR (status: {status})"
            except Exception as e:
                results[url] = f"FAILED: {repr(e)}"
    
    for url, result in results.items():
        logger.info(f"Тест {url}: {result}")
    
    return all(result.startswith("OK") for result in results.values())

async def main():
    """Основная функция для запуска тестов"""
    logger.info("=== Начало тестирования соединения с API Роспатента ===")
    
    # Первый тест: проверка соединения с известными сервисами
    logger.info("1. Проверка общей доступности интернета из контейнера...")
    if not await test_connections_with_known_working_services():
        logger.error("Проверка доступности интернета не пройдена. Есть проблемы с сетью.")
    
    # Второй тест: Проверка DNS
    logger.info("2. Проверка DNS разрешения...")
    if not test_dns_lookup():
        logger.error("DNS-проверка не пройдена. Невозможно разрешить имя хоста.")
        return
    
    # Третий тест: Проверка через requests
    logger.info("3. Проверка через библиотеку requests...")
    if not test_connection_via_requests():
        logger.warning("Тест с requests не пройден.")
    
    # Четвертый тест: Проверка через aiohttp
    logger.info("4. Проверка через библиотеку aiohttp...")
    if not await test_connection_via_aiohttp():
        logger.warning("Тест с aiohttp не пройден.")
    
    # Пятый тест: Проверка запроса поиска
    logger.info("5. Проверка запроса похожих патентов...")
    if not await test_search_similar_request():
        logger.warning("Тест запроса похожих патентов не пройден.")
    
    logger.info("=== Тестирование соединения завершено ===")

if __name__ == "__main__":
    asyncio.run(main()) 
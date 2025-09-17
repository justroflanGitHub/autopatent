import uvicorn
from src.infrastructure.config.settings import Settings

def main():
    """Главная функция для запуска веб-сервиса"""
    # Настройки сервера
    settings = Settings.from_env()

    # Запускаем сервер
    uvicorn.run(
        "src.interfaces.web.app:app",
        host=settings.web_host,
        port=settings.web_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()

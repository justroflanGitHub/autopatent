# 🚀 Autopatent

**Система автоматизированного патентного исследования с AI-анализом**

## ✨ Возможности

- 🔍 **Поиск патентов** по различным критериям
- 🤖 **AI-кластеризация** патентов
- 📊 **Анализ трендов** патентования
- 💡 **Извлечение инноваций** из патентов
- 🌐 **Веб-интерфейс** для удобной работы
- 🔗 **REST API** для интеграции

## 🛠 Установка

### 📋 Системные требования
- **Python**: 3.10 или выше
- **Оперативная память**: минимум 2GB (рекомендуется 4GB+)
- **Дисковое пространство**: минимум 1GB свободного места
- **Интернет-соединение**: обязательно (для API запросов)
- **Git**: для клонирования репозитория

### 📦 Python зависимости
Проект использует следующие основные пакеты:
- **FastAPI** - веб-фреймворк
- **Uvicorn** - ASGI сервер
- **Scikit-learn** - машинное обучение
- **NumPy** - числовые вычисления
- **Requests** - HTTP запросы
- **Pydantic** - валидация данных

### 🚀 Быстрая установка

```bash
# Клонируем репозиторий
git clone https://github.com/yourusername/autopatent.git
cd autopatent

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 🐳 С Docker

```bash
# Запуск с Docker Compose
docker-compose up --build
```

## ⚙️ Настройка

1. Скопируйте `.env.example` в `.env`
2. Заполните необходимые API ключи:
   - `ROSPATENT_JWT` - токен Роспатента
   - `GIGACHAT_CLIENT_ID` - ID GigaChat
   - `GIGACHAT_CLIENT_SECRET` - секрет GigaChat
   - `GIGACHAT_API_KEY` - API ключ GigaChat

## 🚀 Запуск

```bash
python -m src.interfaces.web.main
```

Сервис будет доступен на `http://localhost:8000/static/index.html`

## 📖 Использование

### Веб-интерфейс
1. Откройте `http://localhost:8000/static/index.html`
2. Введите поисковый запрос
3. Просматривайте результаты и анализируйте тренды

### API
Основные endpoints:
- `GET /api/search` - поиск патентов
- `GET /api/trends` - анализ трендов
- `GET /api/patents/{id}` - детальная информация

Полная документация: `http://localhost:8000/docs`

## 📄 Лицензия

MIT License

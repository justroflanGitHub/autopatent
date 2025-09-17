# Настройка GitHub Actions для CI/CD

## Обзор

Проект использует GitHub Actions для автоматического тестирования, сборки и развертывания приложения.

## Рабочие процессы

### 1. CI/CD Pipeline (`.github/workflows/tests.yml`)

Автоматически запускается при:
- Push в ветки `main` или `master`
- Pull Request в ветки `main` или `master`

#### Что делает:
- ✅ Сборка Docker образов
- ✅ Запуск тестов
- ✅ Отправка покрытия кода в Codecov
- ✅ Автоматическое развертывание при push в main

### 2. Production Deployment (`.github/workflows/deploy.yml`)

Запускается:
- Вручную через GitHub UI
- При push в ветку `production`
- При создании тега версии (`v*`)

#### Что делает:
- ✅ Сборка и публикация Docker образа в Docker Hub
- ✅ Развертывание на VPS (опционально)
- ✅ Health check после развертывания


## Необходимые секреты

### Обязательные секреты:

```bash
# Для Telegram бота
BOT_TOKEN=your_bot_token_here

# Для API Роспатента
ROSPATENT_JWT=your_jwt_token_here

# Для GigaChat API
GIGACHAT_CLIENT_ID=your_client_id
GIGACHAT_CLIENT_SECRET=your_client_secret

# Для Codecov (опционально)
CODECOV_TOKEN=your_codecov_token
```

### Для развертывания (опционально):

```bash
# Docker Hub
DOCKERHUB_USERNAME=your_dockerhub_username
DOCKERHUB_TOKEN=your_dockerhub_access_token

# VPS развертывание
VPS_HOST=your_server_ip
VPS_USERNAME=your_server_username
VPS_SSH_KEY=your_private_ssh_key
VPS_PORT=22

# Slack уведомления
SLACK_WEBHOOK=your_slack_webhook_url
```

## Настройка секретов

1. Перейдите в **Settings** → **Secrets and variables** → **Actions**
2. Нажмите **New repository secret**
3. Добавьте все необходимые секреты

## Запуск рабочих процессов

### Ручной запуск развертывания:

1. Перейдите во вкладку **Actions**
2. Выберите **Deploy to Production**
3. Нажмите **Run workflow**
4. Выберите окружение (staging/production)

### Автоматический запуск:

- **Тесты**: запускаются автоматически при push/PR
- **Развертывание**: запускается при push в main (через CI/CD pipeline)

## Мониторинг

### Просмотр логов:

1. Перейдите во вкладку **Actions**
2. Выберите нужный workflow
3. Кликните на конкретный запуск
4. Просмотрите логи каждого шага

### Уведомления:

- Slack уведомления настраиваются через `SLACK_WEBHOOK`
- Email уведомления приходят автоматически от GitHub

## Troubleshooting

### Проблема: Docker build fails
```bash
# Проверьте логи сборки
docker-compose build --no-cache
```

### Проблема: Тесты не проходят
```bash
# Запустите локально
docker-compose run tests
```

### Проблема: Развертывание не работает
```bash
# Проверьте секреты
# Проверьте подключение к VPS
ssh -i ~/.ssh/id_rsa user@host
```

## Структура файлов

```
.github/
├── workflows/
│   ├── tests.yml      # CI/CD pipeline
│   └── deploy.yml     # Production deployment
```

## Полезные команды

```bash
# Локальная проверка
docker-compose build
docker-compose run tests

# Просмотр логов GitHub Actions
gh run list
gh run view <run-id>

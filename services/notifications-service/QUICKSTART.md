# Notifications Service - Quick Start Guide

Быстрый старт для микросервиса "Уведомления"

## Быстрый запуск с Docker Compose

1. **Запустите все сервисы** (включая базу данных):
   ```bash
   docker-compose up -d
   ```

2. **Или запустите только notifications-service**:
   ```bash
   docker-compose up notifications-service
   ```

3. **Проверьте статус сервиса**:
   ```bash
   curl http://localhost:8005/health
   ```

## API Endpoints

### Базовые эндпоинты

- **Health Check**: `GET http://localhost:8005/health`
- **Root**: `GET http://localhost:8005/`
- **API Docs**: `GET http://localhost:8005/docs`

### Уведомления пользователя

#### Получить список своих уведомлений
```bash
curl -X GET "http://localhost:8005/api/notifications/me?status=all" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

С фильтрами:
```bash
# Только непрочитанные
curl -X GET "http://localhost:8005/api/notifications/me?status=unread" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# По типу
curl -X GET "http://localhost:8005/api/notifications/me?type=homework" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Отметить уведомление как прочитанное
```bash
curl -X POST "http://localhost:8005/api/notifications/{notification_id}/read" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Отметить все уведомления как прочитанные
```bash
curl -X POST "http://localhost:8005/api/notifications:mark-all-read" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

С фильтром по типу:
```bash
curl -X POST "http://localhost:8005/api/notifications:mark-all-read?type=homework" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Получить количество непрочитанных уведомлений
```bash
curl -X GET "http://localhost:8005/api/notifications/me/unread-count" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Создание уведомления (для внутренних сервисов)

```bash
curl -X POST "http://localhost:8005/api/notifications" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "12345678-1234-5678-1234-567812345678",
    "type": "homework",
    "title": "Новое домашнее задание",
    "body": "По курсу \"Алгебра\" выдано новое ДЗ. Дедлайн: 01.03.2025 18:00.",
    "data": {
      "course_id": "uuid",
      "homework_id": "uuid",
      "due_at": "2025-03-01T18:00:00Z"
    },
    "send_email": true,
    "send_push": true
  }'
```

## Локальная разработка

### Без Docker

1. **Создайте виртуальное окружение**:
   ```bash
   cd services/notifications-service
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения**:
   ```bash
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_USER=notifications_service
   export DB_PASSWORD=notifications_service_pass123
   export DB_NAME=notifications_service_db
   export JWT_SECRET=your-secret-key
   ```

4. **Запустите сервис**:
   ```bash
   uvicorn app.main:app --reload --port 8005
   ```

## Запуск тестов

```bash
pytest
```

Или с отчетом о покрытии:
```bash
pytest --cov=app --cov-report=html
```

## Проверка логов

```bash
docker logs notifications-service
```

Или следить за логами в реальном времени:
```bash
docker logs -f notifications-service
```

## Остановка сервиса

```bash
docker-compose stop notifications-service
```

Или остановить все сервисы:
```bash
docker-compose down
```

## Переменные окружения

Основные переменные окружения для конфигурации:

```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=notifications_service
DB_PASSWORD=notifications_service_pass123
DB_NAME=notifications_service_db

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256

# App
ENV=local  # local, dev, prod
LOG_LEVEL=INFO
```

## Интеграция с другими сервисами

### Пример создания уведомления из homework-service

```python
import httpx
from datetime import datetime

async def notify_new_homework(user_id: str, homework_id: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://notifications-service:8000/api/notifications",
            json={
                "user_id": user_id,
                "type": "homework",
                "title": "Новое домашнее задание",
                "body": "По курсу \"Алгебра\" выдано новое ДЗ.",
                "data": {
                    "homework_id": homework_id,
                    "due_at": "2025-03-01T18:00:00Z"
                },
                "send_email": True,
                "send_push": False
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### Пример уведомления о достижении

```python
async def notify_achievement(user_id: str, achievement_code: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://notifications-service:8000/api/notifications",
            json={
                "user_id": user_id,
                "type": "achievement",
                "title": "Новое достижение!",
                "body": f"Вы получили достижение: {achievement_code}",
                "data": {"achievement_code": achievement_code},
                "send_email": False,
                "send_push": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## Типы уведомлений

Стандартные типы:
- `homework` - домашние задания
- `test` - тесты
- `schedule` - изменения в расписании
- `achievement` - достижения
- `system` - системные уведомления
- Любые другие типы, определяемые вызывающими сервисами

## Troubleshooting

### Проблема: База данных недоступна
```bash
# Проверьте, что PostgreSQL запущен
docker-compose ps postgres

# Проверьте логи PostgreSQL
docker logs online-teaching-postgres
```

### Проблема: Ошибка аутентификации
- Убедитесь, что JWT_SECRET совпадает с user-service
- Проверьте формат токена в заголовке Authorization

### Проблема: Порт уже используется
```bash
# Измените порт в docker-compose.yml или остановите процесс на порту 8005
lsof -i :8005  # Linux/Mac
netstat -ano | findstr :8005  # Windows
```

### Проблема: Уведомления не создаются
- Проверьте логи сервиса: `docker logs notifications-service`
- Убедитесь, что user_id существует
- Проверьте формат данных в запросе


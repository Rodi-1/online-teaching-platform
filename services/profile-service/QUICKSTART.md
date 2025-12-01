# Profile Service - Quick Start Guide

Быстрый старт для микросервиса "Профиль и достижения"

## Быстрый запуск с Docker Compose

1. **Запустите все сервисы** (включая базу данных):
   ```bash
   docker-compose up -d
   ```

2. **Или запустите только profile-service**:
   ```bash
   docker-compose up profile-service
   ```

3. **Проверьте статус сервиса**:
   ```bash
   curl http://localhost:8004/health
   ```

## API Endpoints

### Базовые эндпоинты

- **Health Check**: `GET http://localhost:8004/health`
- **Root**: `GET http://localhost:8004/`
- **API Docs**: `GET http://localhost:8004/docs`

### Профиль пользователя

#### Получить свой профиль
```bash
curl -X GET http://localhost:8004/api/profile/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Обновить свой профиль
```bash
curl -X PATCH http://localhost:8004/api/profile/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "avatar_url": "https://example.com/avatar.png",
    "about": "Студент, люблю программирование",
    "social_links": ["https://github.com/username"]
  }'
```

### Достижения

#### Получить достижения пользователя
```bash
curl -X GET http://localhost:8004/api/profile/users/{user_id}/achievements \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Выдать достижение пользователю
```bash
curl -X POST http://localhost:8004/api/profile/users/{user_id}/achievements \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "first_homework",
    "title": "Первое домашнее задание",
    "description": "Выполнено первое ДЗ",
    "icon_url": "https://example.com/icon.png",
    "received_at": "2025-02-01T10:00:00Z"
  }'
```

### Обновление статистики (для внутренних сервисов)

```bash
curl -X POST http://localhost:8004/api/profile/users/{user_id}/stats:update \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "homeworks_completed_delta": 1,
    "tests_passed_delta": 0,
    "average_grade": 4.7
  }'
```

## Локальная разработка

### Без Docker

1. **Создайте виртуальное окружение**:
   ```bash
   cd services/profile-service
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
   export DB_USER=profile_service
   export DB_PASSWORD=profile_service_pass123
   export DB_NAME=profile_service_db
   export JWT_SECRET=your-secret-key
   ```

4. **Запустите сервис**:
   ```bash
   uvicorn app.main:app --reload --port 8004
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
docker logs profile-service
```

Или следить за логами в реальном времени:
```bash
docker logs -f profile-service
```

## Остановка сервиса

```bash
docker-compose stop profile-service
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
DB_USER=profile_service
DB_PASSWORD=profile_service_pass123
DB_NAME=profile_service_db

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256

# App
ENV=local  # local, dev, prod
LOG_LEVEL=INFO
```

## Интеграция с другими сервисами

### Обновление статистики из homework-service

```python
import httpx

async def update_profile_stats(user_id: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://profile-service:8000/api/profile/users/{user_id}/stats:update",
            json={"homeworks_completed_delta": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### Выдача достижения

```python
async def grant_achievement(user_id: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://profile-service:8000/api/profile/users/{user_id}/achievements",
            json={
                "code": "first_homework",
                "title": "Первое домашнее задание",
                "description": "Выполнено первое ДЗ",
                "received_at": datetime.utcnow().isoformat()
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

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
# Измените порт в docker-compose.yml или остановите процесс на порту 8004
lsof -i :8004  # Linux/Mac
netstat -ano | findstr :8004  # Windows
```


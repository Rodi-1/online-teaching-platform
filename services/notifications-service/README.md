# Notifications Service

Микросервис "Уведомления" для платформы онлайн-обучения.

## Описание

Этот микросервис отвечает за:

- Хранение уведомлений для пользователей (внутренний «колокольчик» в интерфейсе)
- Получение списка уведомлений пользователем
- Пометку уведомлений как прочитанных (по одному и массово)
- Подсчёт количества непрочитанных уведомлений
- Приём запросов от других микросервисов на создание уведомлений

## Технологический стек

- **Python 3.11**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных
- **Alembic** - миграции базы данных

## Структура проекта

```
notifications-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # точка входа FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # зависимости для аутентификации
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── notifications.py   # эндпоинты уведомлений
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # конфигурация
│   │   └── security.py            # JWT валидация
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py             # engine + SessionLocal
│   │   └── migrations/            # alembic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py           # ORM-модель Notification
│   │   └── schemas.py             # Pydantic-схемы
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── notifications_repo.py  # доступ к БД
│   └── services/
│       ├── __init__.py
│       └── notifications_service.py
├── tests/
│   ├── __init__.py
│   └── test_api_notifications.py
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md
```

## API Endpoints

### Уведомления пользователя

- `GET /api/notifications/me` - Получить список уведомлений текущего пользователя
- `POST /api/notifications/{notification_id}/read` - Отметить уведомление как прочитанное
- `POST /api/notifications:mark-all-read` - Отметить все уведомления как прочитанные
- `GET /api/notifications/me/unread-count` - Получить количество непрочитанных уведомлений

### Создание уведомлений (для внутренних сервисов)

- `POST /api/notifications` - Создать новое уведомление

## Модель данных

### Notification

- `id` - UUID, PK
- `user_id` - UUID, ID пользователя
- `type` - строка (homework, test, schedule, achievement, system и т.п.)
- `title` - строка, заголовок уведомления
- `body` - строка, основной текст уведомления
- `data` - JSON, произвольные дополнительные данные
- `is_read` - boolean, прочитано/не прочитано
- `created_at` - datetime, когда уведомление создано
- `read_at` - datetime, nullable, когда помечено как прочитанное
- `send_email` - boolean, было ли отправлено по email
- `send_push` - boolean, было ли отправлено push-уведомление

Индексы:
- по `user_id`
- по `(user_id, is_read)`
- по `created_at`

## Переменные окружения

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=notifications_service_db

JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

ENV=local  # local, dev, prod
LOG_LEVEL=INFO
```

## Локальный запуск

### С Docker Compose

```bash
docker-compose up notifications-service
```

### Без Docker

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить сервис
uvicorn app.main:app --reload --port 8000
```

## Тестирование

```bash
pytest
```

## Интеграция с другими сервисами

### Создание уведомления из другого сервиса

```python
import httpx

async def create_notification(user_id: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://notifications-service:8000/api/notifications",
            json={
                "user_id": user_id,
                "type": "homework",
                "title": "Новое домашнее задание",
                "body": "По курсу \"Алгебра\" выдано новое ДЗ.",
                "data": {
                    "course_id": "...",
                    "homework_id": "...",
                    "due_at": "2025-03-01T18:00:00Z"
                },
                "send_email": True,
                "send_push": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## Авторизация

Все эндпоинты требуют JWT токен в заголовке:

```
Authorization: Bearer <token>
```

Токен должен содержать `user_id` в поле `sub`.

## Типы уведомлений

Поддерживаемые типы:
- `homework` - домашние задания
- `test` - тесты
- `schedule` - изменения в расписании
- `achievement` - достижения
- `system` - системные уведомления
- и другие (определяются вызывающими сервисами)

## Фильтрация уведомлений

Поддерживается фильтрация по:
- `status` - статус прочтения (unread, read, all)
- `type` - тип уведомления
- `from` / `to` - временной интервал

## Пагинация

Все списковые эндпоинты поддерживают:
- `offset` - сколько пропустить
- `count` - сколько вернуть (макс 100)


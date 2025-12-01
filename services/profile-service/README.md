# Profile Service

Микросервис "Профиль и достижения" для платформы онлайн-обучения.

## Описание

Этот микросервис отвечает за:

- Хранение и выдачу **профиля пользователя** (аватар, описание, ссылки, агрегированная статистика)
- Хранение и выдачу **достижений (ачивок)** пользователя
- Обновление базовой статистики прогресса по запросу других микросервисов

## Технологический стек

- **Python 3.11**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных
- **Alembic** - миграции базы данных

## Структура проекта

```
profile-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # точка входа FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py     # зависимости для аутентификации
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── profile.py      # эндпоинты профиля и достижений
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # конфигурация
│   │   └── security.py         # JWT валидация
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py          # engine + SessionLocal
│   │   └── migrations/         # alembic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py        # ORM-модели
│   │   └── schemas.py          # Pydantic-схемы
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── profile_repo.py     # работа с БД
│   └── services/
│       ├── __init__.py
│       └── profile_service.py  # бизнес-логика
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_api_profile.py
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md
```

## API Endpoints

### Профиль

- `GET /api/profile/me` - Получить профиль текущего пользователя
- `PATCH /api/profile/me` - Обновить профиль текущего пользователя

### Достижения

- `GET /api/profile/users/{user_id}/achievements` - Получить достижения пользователя
- `POST /api/profile/users/{user_id}/achievements` - Выдать достижение пользователю

### Статистика

- `POST /api/profile/users/{user_id}/stats:update` - Обновить статистику пользователя (для внутренних сервисов)

## Модели данных

### UserProfile

- `id` - UUID, PK
- `user_id` - UUID, уникальный FK на пользователя
- `avatar_url` - строка, ссылка на аватар
- `about` - строка, описание о себе
- `social_links` - JSON, список ссылок на соцсети
- Статистика: `total_courses`, `completed_courses`, `active_courses`, `average_grade`, `homeworks_completed`, `tests_passed`
- `created_at`, `updated_at` - datetime

### Achievement

- `id` - UUID, PK
- `user_id` - UUID, FK на пользователя
- `code` - строка-код достижения
- `title` - строка, заголовок
- `description` - строка, описание
- `icon_url` - строка, ссылка на иконку
- `received_at` - datetime, когда выдано
- `created_at` - datetime

## Переменные окружения

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=profile_service_db

JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

ENV=local  # local, dev, prod
LOG_LEVEL=INFO
```

## Локальный запуск

### С Docker Compose

```bash
docker-compose up profile-service
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

### Обновление статистики

Другие сервисы могут обновлять статистику пользователя через endpoint:

```bash
POST /api/profile/users/{user_id}/stats:update
```

Примеры:

- **homework-service**: увеличивает `homeworks_completed_delta`
- **tests-service**: увеличивает `tests_passed_delta`
- **gradebook-service**: обновляет `average_grade` и счётчики курсов

### Выдача достижений

Сервисы могут выдавать достижения через endpoint:

```bash
POST /api/profile/users/{user_id}/achievements
```

## Авторизация

Все эндпоинты требуют JWT токен в заголовке:

```
Authorization: Bearer <token>
```

Токен должен содержать `user_id` в поле `sub`.


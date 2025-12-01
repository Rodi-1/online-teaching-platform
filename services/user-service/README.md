# User Service

Микросервис управления пользователями для платформы онлайн-обучения.

## Описание

User Service отвечает за:
- Регистрацию пользователей (учеников, преподавателей, администраторов)
- Аутентификацию (логин/логаут, выдача JWT токенов)
- Управление профилем пользователя
- Подтверждение email и телефона
- Восстановление пароля
- Административные функции (просмотр списка пользователей)

## Технологии

- **Python 3.11+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с PostgreSQL
- **Pydantic** - валидация данных
- **JWT** - авторизация
- **bcrypt** - хеширование паролей
- **PostgreSQL** - база данных

## Структура проекта

```
user-service/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py          # Endpoints аутентификации
│   │   │   └── users.py         # Endpoints пользователей
│   │   └── dependencies.py      # Зависимости для API
│   ├── core/
│   │   ├── config.py            # Конфигурация
│   │   └── security.py          # JWT и хеширование
│   ├── db/
│   │   └── session.py           # Сессии БД
│   ├── models/
│   │   ├── db_models.py         # ORM модели
│   │   └── schemas.py           # Pydantic схемы
│   ├── repositories/
│   │   └── users_repo.py        # Репозиторий для БД операций
│   ├── services/
│   │   └── users_service.py     # Бизнес-логика
│   └── main.py                  # Точка входа FastAPI
├── tests/                       # Тесты
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

### Аутентификация

- `POST /api/auth/login` - Вход в систему
- `POST /api/auth/logout` - Выход из системы

### Пользователи

- `POST /api/users` - Регистрация нового пользователя
- `GET /api/users/me` - Получить текущего пользователя
- `PATCH /api/users/me` - Обновить профиль
- `POST /api/users/confirm-email` - Подтвердить email
- `POST /api/users/confirm-phone` - Подтвердить телефон
- `POST /api/users:request-password-reset` - Запросить сброс пароля
- `POST /api/users:reset-password` - Сбросить пароль
- `GET /api/users` - Список пользователей (только для админов)

## Переменные окружения

Скопируйте `.env.example` в `.env` и настройте:

```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=user_service
DB_PASSWORD=your_password
DB_NAME=user_service_db

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MIN=60

# Environment
ENV=local  # local, dev, prod
LOG_LEVEL=INFO
```

## Запуск

### Локально (разработка)

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения в `.env`

3. Запустите сервис:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. API документация будет доступна по адресу: http://localhost:8000/docs

### Docker

1. Соберите образ:
```bash
docker build -t user-service .
```

2. Запустите контейнер:
```bash
docker run -p 8000:8000 --env-file .env user-service
```

### Docker Compose

```bash
docker-compose up -d
```

## Тестирование

Запуск тестов:
```bash
pytest
```

С покрытием:
```bash
pytest --cov=app tests/
```

## Разработка

### Миграции базы данных (Alembic)

Создать миграцию:
```bash
alembic revision --autogenerate -m "описание изменений"
```

Применить миграции:
```bash
alembic upgrade head
```

## Лицензия

MIT


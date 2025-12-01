# Быстрый старт - Платформа онлайн-обучения

Это руководство поможет вам быстро запустить проект локально.

## Шаг 1: Проверка требований

Убедитесь, что установлены:
- Docker Desktop (для Windows/Mac) или Docker Engine + Docker Compose (для Linux)
- Git

Проверить установку:
```bash
docker --version
docker-compose --version
git --version
```

## Шаг 2: Клонирование проекта

Если проект еще не клонирован:
```bash
git clone <your-repository-url>
cd online-teaching-platform
```

## Шаг 3: Проверка конфигурации

Файл `.env` уже создан с базовыми настройками. Если хотите изменить пароли или другие параметры, отредактируйте его:

```bash
# Пример содержимого .env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=online_teaching

USER_SERVICE_DB_USER=user_service
USER_SERVICE_DB_PASSWORD=user_service_pass123
USER_SERVICE_DB_NAME=user_service_db

JWT_SECRET=your-super-secret-jwt-key-change-in-production-123456789
```

## Шаг 4: Запуск сервисов

Запустите все сервисы с помощью Docker Compose:

```bash
docker-compose up -d
```

Это запустит:
- PostgreSQL базу данных (порт 5432)
- User Service (порт 8001)

## Шаг 5: Проверка статуса

Проверьте, что все контейнеры запущены:

```bash
docker-compose ps
```

Вы должны увидеть:
- `online-teaching-postgres` (healthy)
- `user-service` (running)

## Шаг 6: Тестирование API

### Через браузер (Swagger UI)

Откройте в браузере:
```
http://localhost:8001/docs
```

Вы увидите интерактивную документацию API (Swagger UI).

### Через curl или Postman

#### 1. Регистрация пользователя

```bash
curl -X POST "http://localhost:8001/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "phone": "+79990001122",
    "password": "password123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "role": "student"
  }'
```

#### 2. Вход в систему

```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

Сохраните `access_token` из ответа для следующих запросов.

#### 3. Получение профиля

```bash
curl -X GET "http://localhost:8001/api/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Шаг 7: Просмотр логов

Просмотр логов всех сервисов:
```bash
docker-compose logs -f
```

Просмотр логов конкретного сервиса:
```bash
docker-compose logs -f user-service
```

## Шаг 8: Остановка сервисов

Остановка без удаления данных:
```bash
docker-compose stop
```

Остановка с удалением контейнеров (данные в volumes сохранятся):
```bash
docker-compose down
```

Полная очистка (включая volumes с данными БД):
```bash
docker-compose down -v
```

## Troubleshooting

### Порт уже занят

Если порт 8001 или 5432 уже используется, измените в `docker-compose.yml`:

```yaml
services:
  user-service:
    ports:
      - "8002:8000"  # Измените 8001 на 8002
  
  postgres:
    ports:
      - "5433:5432"  # Измените 5432 на 5433
```

### Контейнер не запускается

1. Проверьте логи:
```bash
docker-compose logs user-service
```

2. Проверьте, что PostgreSQL запущен и здоров:
```bash
docker-compose ps postgres
```

### База данных не инициализировалась

1. Остановите все:
```bash
docker-compose down -v
```

2. Запустите заново:
```bash
docker-compose up -d
```

## Разработка

### Локальный запуск без Docker

Если хотите разрабатывать без Docker:

1. Установите PostgreSQL локально
2. Создайте виртуальное окружение:

```bash
cd services/user-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Настройте `.env` файл в `services/user-service/.env`
4. Запустите сервис:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Запуск тестов

```bash
cd services/user-service
pytest
```

## Дополнительные ресурсы

- [Основной README](README.md) - Полная документация проекта
- [User Service README](services/user-service/README.md) - Документация микросервиса пользователей
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Документация FastAPI
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/) - Документация SQLAlchemy

## Следующие шаги

1. Ознакомьтесь с API через Swagger UI (http://localhost:8001/docs)
2. Попробуйте создать пользователей разных ролей (student, teacher, admin)
3. Протестируйте все эндпоинты
4. Изучите код в `services/user-service/`
5. Начните разработку следующего микросервиса!

Удачи! 🚀


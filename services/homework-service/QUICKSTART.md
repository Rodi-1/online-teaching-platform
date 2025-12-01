# Быстрый старт - Homework Service

## Запуск через Docker Compose (рекомендуется)

Из корня проекта:

```bash
# Запустить все сервисы (включая homework-service)
docker-compose up -d

# Или запустить только homework-service
docker-compose up -d homework-service

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f homework-service
```

## Доступ к API

- **API**: http://localhost:8002
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **Health check**: http://localhost:8002/health

## Локальный запуск (разработка)

```bash
cd services/homework-service

# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Активировать (Linux/Mac)
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Настроить .env (создать из .env.example)
# Указать подключение к БД

# Запустить сервис
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Тестирование API

### 1. Получить JWT токен

Сначала нужно получить токен от User Service:

```bash
# Зарегистрировать пользователя (если еще нет)
curl -X POST http://localhost:8001/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "password123",
    "first_name": "Teacher",
    "last_name": "Test",
    "role": "teacher"
  }'

# Получить токен
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "password": "password123"
  }'

# Сохранить access_token из ответа
export TOKEN="your_access_token_here"
```

### 2. Создать домашнее задание (преподаватель)

```bash
curl -X POST http://localhost:8002/api/courses/123e4567-e89b-12d3-a456-426614174000/homeworks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Домашнее задание по теме \"Функции\"",
    "description": "Решить задачи 1–10 из файла",
    "lesson_id": null,
    "due_at": "2025-03-01T18:00:00Z",
    "max_score": 10,
    "attachments": ["https://files.example.com/hw1.pdf"]
  }'
```

### 3. Просмотреть список ДЗ курса

```bash
curl -X GET "http://localhost:8002/api/courses/123e4567-e89b-12d3-a456-426614174000/homeworks" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Отправить решение (студент)

```bash
# Получить токен студента
export STUDENT_TOKEN="student_token_here"

# Отправить решение
curl -X POST http://localhost:8002/api/homeworks/{homework_id}/submissions \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "answer_text": "Решения задач приведены в файле",
    "attachments": ["https://files.example.com/answer.pdf"]
  }'
```

### 5. Выставить оценку (преподаватель)

```bash
curl -X POST http://localhost:8002/api/homeworks/{homework_id}/submissions/{submission_id}:grade \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "score": 9,
    "teacher_comment": "Хорошая работа!",
    "status": "checked"
  }'
```

## Запуск тестов

```bash
cd services/homework-service

# Установить зависимости (если еще не установлены)
pip install -r requirements.txt

# Запустить тесты
pytest

# С подробным выводом
pytest -v

# С покрытием
pytest --cov=app
```

## Переменные окружения

Основные переменные (настраиваются в `.env` корня проекта):

```env
# Database
HOMEWORK_SERVICE_DB_USER=homework_service
HOMEWORK_SERVICE_DB_PASSWORD=your_password
HOMEWORK_SERVICE_DB_NAME=homework_service_db

# JWT (должен совпадать с User Service)
JWT_SECRET=your-secret-key

# Integration
GRADEBOOK_SERVICE_URL=http://gradebook-service:8000
USER_SERVICE_URL=http://user-service:8000

# Environment
ENV=local
LOG_LEVEL=INFO
```

## Troubleshooting

### Порт занят

Измените порт в `docker-compose.yml`:
```yaml
ports:
  - "8003:8000"  # Вместо 8002
```

### База данных не инициализировалась

```bash
# Пересоздать контейнеры
docker-compose down -v
docker-compose up -d
```

### Ошибка авторизации

Убедитесь, что:
1. JWT_SECRET совпадает между User Service и Homework Service
2. Токен не истек (по умолчанию 60 минут)
3. Роль пользователя соответствует требуемой

## Следующие шаги

1. Изучите API через Swagger UI: http://localhost:8002/docs
2. Протестируйте все endpoints
3. Посмотрите примеры в тестах: `tests/test_api_homeworks.py`
4. Изучите код в `app/` директории

## Полезные ссылки

- [README.md](README.md) - Полная документация
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Детальный отчет
- [Основной README](../../README.md) - Документация проекта

Удачи! 🚀


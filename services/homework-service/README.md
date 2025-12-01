# Homework Service

Микросервис управления домашними заданиями для платформы онлайн-обучения.

## Описание

Homework Service отвечает за:
- Создание домашних заданий преподавателями
- Получение списка ДЗ по курсу
- Получение списка ДЗ для конкретного ученика
- Отправку решений учениками
- Просмотр конкретного решения
- Проверку и выставление оценки за ДЗ (с интеграцией в Электронный журнал)

## Технологии

- **Python 3.11+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с PostgreSQL
- **Pydantic** - валидация данных
- **httpx** - HTTP клиент для интеграции с другими сервисами
- **PostgreSQL** - база данных

## Структура проекта

```
homework-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── homeworks.py     # Все HTTP endpoints
│   ├── core/
│   │   └── config.py            # Конфигурация
│   ├── db/
│   │   └── session.py           # Сессии БД
│   ├── models/
│   │   ├── db_models.py         # ORM модели
│   │   └── schemas.py           # Pydantic схемы
│   ├── repositories/
│   │   └── homeworks_repo.py    # Репозиторий для БД операций
│   ├── services/
│   │   └── homeworks_service.py # Бизнес-логика
│   └── main.py                  # Точка входа FastAPI
├── tests/                       # Тесты
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

### Создание и управление ДЗ (Преподаватель)

- `POST /api/courses/{course_id}/homeworks` - Создать домашнее задание
- `GET /api/courses/{course_id}/homeworks` - Получить список ДЗ по курсу

### Работа с ДЗ (Студент)

- `GET /api/students/me/homeworks` - Получить список своих ДЗ
- `POST /api/homeworks/{homework_id}/submissions` - Отправить решение ДЗ

### Просмотр и оценка решений

- `GET /api/homeworks/{homework_id}/submissions/{submission_id}` - Просмотр решения
- `POST /api/homeworks/{homework_id}/submissions/{submission_id}:grade` - Выставить оценку (преподаватель)

## Модели данных

### Homework (Домашнее задание)
- `id` - UUID
- `course_id` - UUID курса
- `lesson_id` - UUID урока (опционально)
- `title` - название
- `description` - описание/условие
- `due_at` - дедлайн сдачи
- `max_score` - максимальный балл
- `status` - статус (draft/assigned/closed)
- `attachments` - вложения (JSON)

### HomeworkSubmission (Решение ДЗ)
- `id` - UUID
- `homework_id` - UUID задания
- `student_id` - UUID студента
- `answer_text` - текст ответа
- `attachments` - вложения (JSON)
- `status` - статус (submitted/checked/needs_fix)
- `score` - оценка
- `teacher_comment` - комментарий преподавателя
- `checked_at` - время проверки

## Переменные окружения

Настройте в `.env`:

```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=homework_service
DB_PASSWORD=your_password
DB_NAME=homework_service_db

# Integration
GRADEBOOK_SERVICE_URL=http://gradebook-service:8000
USER_SERVICE_URL=http://user-service:8000

# Environment
ENV=local  # local, dev, prod
LOG_LEVEL=INFO
```

## Запуск

### Docker

```bash
docker build -t homework-service .
docker run -p 8000:8000 --env-file .env homework-service
```

### Локально (разработка)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
# Из корня проекта
docker-compose up -d homework-service
```

API документация: http://localhost:8002/docs

## Интеграция с другими сервисами

### User Service
- Аутентификация через JWT токены
- Проверка ролей (teacher/student)

### Gradebook Service (опционально)
- При выставлении оценки автоматически отправляется запрос в Gradebook Service
- Если сервис недоступен, оценка все равно сохраняется

## Тестирование

```bash
pytest
```

## Безопасность

- JWT токены для авторизации
- Role-based access control (RBAC)
- Валидация всех входных данных
- Проверка прав доступа на уровне API

## Разработка

### Миграции (Alembic)

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Лицензия

MIT


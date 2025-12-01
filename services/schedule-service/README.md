# Schedule Service

Микросервис управления расписанием занятий для платформы онлайн-обучения.

## Описание

Schedule Service отвечает за:
- Хранение и управление занятиями (уроками) в рамках курсов
- Выдачу расписания для конкретного пользователя (ученика/преподавателя)
- Выдачу расписания по курсу
- Фиксацию и просмотр посещаемости по занятию

## Технологии

- **Python 3.11+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с PostgreSQL
- **Pydantic** - валидация данных
- **PostgreSQL** - база данных

## Структура проекта

```
schedule-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── schedule.py          # Все HTTP endpoints
│   ├── core/
│   │   ├── config.py                # Конфигурация
│   │   └── security.py              # Утилиты безопасности
│   ├── db/
│   │   ├── session.py               # Сессии БД
│   │   └── migrations/              # Alembic миграции
│   ├── models/
│   │   ├── db_models.py             # ORM модели
│   │   └── schemas.py               # Pydantic схемы
│   ├── repositories/
│   │   └── schedule_repo.py         # Репозиторий для БД операций
│   ├── services/
│   │   └── schedule_service.py      # Бизнес-логика
│   └── main.py                      # Точка входа FastAPI
├── tests/                           # Тесты
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

### Управление занятиями (Преподаватель/Администратор)

- `POST /api/courses/{course_id}/lessons` - Создать занятие в курсе
- `PATCH /api/lessons/{lesson_id}` - Изменить занятие (перенос/изменение параметров)
- `GET /api/lessons/{lesson_id}` - Получить информацию о занятии

### Расписание

- `GET /api/schedule/me` - Получить расписание текущего пользователя
- `GET /api/courses/{course_id}/schedule` - Получить расписание по курсу

### Посещаемость

- `POST /api/lessons/{lesson_id}/attendance` - Отметить посещаемость (преподаватель)
- `GET /api/lessons/{lesson_id}/attendance` - Получить посещаемость по занятию

## Модели данных

### Lesson (Занятие)
- `id` - UUID
- `course_id` - UUID курса
- `title` - тема занятия
- `description` - описание (опционально)
- `start_at` - дата и время начала (UTC)
- `end_at` - дата и время окончания (UTC)
- `location_type` - тип локации (online/offline)
- `room` - аудитория (для offline)
- `online_link` - ссылка на онлайн-конференцию (для online)
- `status` - статус (scheduled/cancelled/finished)
- `created_at` - дата создания
- `updated_at` - дата обновления

### LessonAttendance (Посещаемость)
- `id` - UUID
- `lesson_id` - UUID занятия
- `student_id` - UUID ученика
- `status` - статус посещаемости (present/absent/late)
- `comment` - комментарий преподавателя
- `marked_at` - время отметки

## Переменные окружения

Настройте в `.env`:

```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=schedule_service
DB_PASSWORD=your_password
DB_NAME=schedule_service_db

# Environment
ENV=local  # local, dev, prod
LOG_LEVEL=INFO
```

## Запуск

### Docker

```bash
docker build -t schedule-service .
docker run -p 8000:8000 --env-file .env schedule-service
```

### Локально (разработка)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
# Из корня проекта
docker-compose up -d schedule-service
```

API документация: http://localhost:8007/docs

## Интеграция с другими сервисами

### User Service
- Аутентификация через заголовки `x-user-id` и `x-user-role`
- Проверка ролей (teacher/admin/student)

### Course Service (будущая интеграция)
- Получение информации о курсах
- Проверка участников курса

## Бизнес-правила

### Создание и редактирование занятий
- Только преподаватели и администраторы могут создавать/редактировать занятия
- `end_at` должно быть больше `start_at`
- Нельзя изменять занятия со статусом `finished`

### Посещаемость
- Только преподаватели и администраторы могут отмечать посещаемость
- Одна запись посещаемости на пару (ученик, занятие)
- Преподаватели видят всю посещаемость, студенты - только свою

### Расписание
- Студенты видят занятия курсов, в которых они записаны
- Преподаватели видят занятия курсов, которые они ведут
- Сортировка по `start_at`

## Тестирование

```bash
pytest
```

Тесты включают:
- Создание занятий
- Обновление занятий
- Получение расписания
- Управление посещаемостью
- Проверку прав доступа

## Безопасность

- Header-based аутентификация (`x-user-id`, `x-user-role`)
- Role-based access control (RBAC)
- Валидация всех входных данных
- Проверка прав доступа на уровне API

## Разработка

### Миграции (Alembic)

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Индексы базы данных

Для оптимизации производительности созданы индексы:
- `course_id` - для быстрого поиска занятий курса
- `start_at` - для сортировки по времени
- `(course_id, start_at)` - композитный индекс для расписания курса
- `(lesson_id, student_id)` - уникальный индекс для посещаемости

## Лицензия

MIT


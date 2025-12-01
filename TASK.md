````markdown
# Микросервис «Расписание» – техническое задание

Этот документ описывает, **что нужно реализовать** в микросервисе «Расписание» для онлайн-платформы обучения.

Микросервис отвечает за:

- хранение и управление **занятиями (уроками)** в рамках курсов;
- выдачу **расписания** для конкретного пользователя (ученика/преподавателя);
- выдачу **расписания по курсу**;
- фиксацию и просмотр **посещаемости** по занятию.

**Не отвечает** за:

- создание курсов и управление составом групп (это отдельный сервис «Курс» или «Каталог курсов»);
- оценивание (это «Электронный журнал» и сервисы «Домашнее задание» / «Тест»);
- уведомления об изменении расписания (это сервис «Уведомления»).

---

## 1. Общие требования и стек

**Язык:** Python  
**Фреймворк:** FastAPI (для единообразия с остальными сервисами)

Рекомендуемые библиотеки:

- `fastapi` – HTTP API;
- `uvicorn` – ASGI-сервер;
- `pydantic` – схемы запросов/ответов;
- `sqlalchemy` – ORM для PostgreSQL;
- `alembic` – миграции (желательно);
- стандартный `logging` – логирование.

---

## 2. Структура директорий микросервиса

Папка: `services/schedule-service`

```text
schedule-service/
├── app/
│   ├── __init__.py
│   ├── main.py                   # точка входа FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── schedule.py       # все HTTP-эндпоинты сервиса «Расписание»
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py             # конфиг (DB_HOST и пр.)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py            # engine + SessionLocal
│   │   └── migrations/           # alembic (миграции схемы)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py          # ORM-модели (Lesson, LessonAttendance)
│   │   └── schemas.py            # Pydantic-схемы (LessonCreate, LessonOut и т.д.)
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── schedule_repo.py      # доступ к данным расписания и посещаемости
│   └── services/
│       ├── __init__.py
│       └── schedule_service.py   # бизнес-логика
│
├── tests/
│   ├── __init__.py
│   └── test_api_schedule.py
│
├── Dockerfile
├── requirements.txt
└── README.md
````

---

## 3. Конфигурация и переменные окружения

Через `core/config.py` прочитать:

Обязательные:

* `DB_HOST` – хост PostgreSQL;
* `DB_PORT` – порт PostgreSQL;
* `DB_USER` – пользователь БД;
* `DB_PASSWORD` – пароль пользователя БД;
* `DB_NAME` – имя базы;
* `ENV` – окружение (`local` / `dev` / `prod`).

Желательно:

* `LOG_LEVEL` – уровень логов.

`db/session.py` должен:

* создавать `SQLAlchemy` engine на основе этих переменных;
* предоставлять `SessionLocal` (sessionmaker), который используется в репозиториях.

---

## 4. Модель данных (БД)

### 4.1. Таблица `lessons` (занятия)

Хранит информацию о каждом занятии курса.

Поля:

* `id` – UUID, PK;
* `course_id` – UUID, идентификатор курса;
* `title` – строка, тема занятия;
* `description` – строка, краткое описание (nullable);
* `start_at` – datetime, дата и время начала (UTC);
* `end_at` – datetime, дата и время окончания (UTC);
* `location_type` – строка: `"online"` или `"offline"`;
* `room` – строка, аудитория (для офлайн-занятий, nullable);
* `online_link` – строка, ссылка на онлайн-конференцию (для онлайн-занятий, nullable);
* `status` – строка: `scheduled`, `cancelled`, `finished`;
* `created_at` – datetime;
* `updated_at` – datetime.

Индексы:

* по `course_id`;
* по `start_at`;
* по `(course_id, start_at)`.

### 4.2. Таблица `lesson_attendance` (посещаемость)

Хранит отметки посещаемости учеников по каждому занятию.

Поля:

* `id` – UUID, PK;
* `lesson_id` – FK → lessons.id;
* `student_id` – UUID, идентификатор ученика (из сервиса «Пользователь»);
* `status` – строка: `present` (присутствовал), `absent` (отсутствовал), `late` (опоздал);
* `comment` – строка, комментарий преподавателя (nullable);
* `marked_at` – datetime, когда была поставлена отметка.

Индексы:

* по `(lesson_id, student_id)` – уникальный (одна строка на ученика и занятие);
* по `lesson_id`.

---

## 5. Pydantic-схемы

В `models/schemas.py` описать схемы запросов/ответов.

### 5.1. Занятия (расписание)

`LessonCreate` – создание занятия:

```json
{
  "title": "Функции. Введение",
  "description": "Обсуждаем базовые определения и примеры функций.",
  "start_at": "2025-02-21T16:00:00Z",
  "end_at": "2025-02-21T16:45:00Z",
  "location_type": "online",
  "room": null,
  "online_link": "https://meet.example.com/course123_lesson1"
}
```

`LessonUpdate` – частичное обновление (все поля опциональны):

```json
{
  "start_at": "2025-02-21T17:00:00Z",
  "end_at": "2025-02-21T17:45:00Z",
  "location_type": "offline",
  "room": "Кабинет 302",
  "online_link": null,
  "status": "scheduled"
}
```

`LessonOut` – выдача занятия наружу:

```json
{
  "id": "UUID",
  "course_id": "UUID",
  "title": "Функции. Введение",
  "description": "Обсуждаем базовые определения и примеры функций.",
  "start_at": "2025-02-21T17:00:00Z",
  "end_at": "2025-02-21T17:45:00Z",
  "location_type": "offline",
  "room": "Кабинет 302",
  "online_link": null,
  "status": "scheduled",
  "created_at": "2025-02-18T12:00:00Z",
  "updated_at": "2025-02-19T09:30:00Z"
}
```

`ScheduleItemMe` – элемент расписания текущего пользователя:

```json
{
  "lesson_id": "UUID",
  "course_id": "UUID",
  "course_title": "Алгебра, 10 класс",
  "title": "Функции. Введение",
  "start_at": "2025-02-21T17:00:00Z",
  "end_at": "2025-02-21T17:45:00Z",
  "location_type": "offline",
  "room": "Кабинет 302",
  "online_link": null,
  "role": "student",
  "status": "scheduled"
}
```

`ScheduleResponse`:

```json
{
  "items": [ /* массив ScheduleItemMe */ ],
  "total": 2,
  "offset": 0,
  "count": 50
}
```

### 5.2. Посещаемость

`AttendanceItemUpdate` – элемент при отметке посещаемости:

```json
{
  "student_id": "UUID",
  "status": "present",
  "comment": null
}
```

`AttendanceSetRequest`:

```json
{
  "items": [ /* массив AttendanceItemUpdate */ ]
}
```

`AttendanceItemOut`:

```json
{
  "student_id": "UUID",
  "student_name": "Иванов Иван",
  "status": "present",
  "comment": null
}
```

`AttendanceResponse`:

```json
{
  "lesson_id": "UUID",
  "course_id": "UUID",
  "lesson_title": "Функции. Введение",
  "items": [ /* массив AttendanceItemOut */ ]
}
```

---

## 6. Репозиторий и сервис

### 6.1. `schedule_repo.py`

Примерный набор функций:

* `create_lesson(course_id, data: LessonCreate) -> Lesson`;
* `get_lesson(lesson_id) -> Lesson | None`;
* `update_lesson(lesson_id, data: LessonUpdate) -> Lesson`;
* `list_lessons_for_user(user_id, role, date_from, date_to, offset, count)`
  (объединяет занятия по всем курсам пользователя, связь курс–пользователь можно пока считать внешней или сделать заглушкой);
* `list_lessons_for_course(course_id, date_from, date_to) -> list[Lesson]`;
* `set_attendance(lesson_id, items: list[AttendanceItemUpdate]) -> list[LessonAttendance]`;
* `get_attendance(lesson_id) -> list[LessonAttendance]`.

### 6.2. `schedule_service.py`

Основная логика:

* проверка прав по ролям:

  * создавать/редактировать занятия может только `teacher` / `admin`;
  * отмечать посещаемость – только преподаватель курса;
* валидация дат:

  * `end_at` > `start_at`;
* при `list_lessons_for_user`:

  * фильтрация по интервалу `from` / `to`;
  * сортировка по `start_at`;
* при отметке посещаемости:

  * обновлять существующие строки или создавать новые;
  * ставить `marked_at = now()`.

---

## 7. REST API эндпоинты

Все пути ниже — относительно префикса `/api`.

### 7.1. Добавление занятия в расписание курса

**Path:** `POST /api/courses/{course_id}/lessons`
**Авторизация:** требуется (`teacher` / `admin`)

**Параметры пути:**

* `course_id` – UUID, идентификатор курса.

**Тело запроса:** `LessonCreate`.

Логика:

* проверить, что вызывающий пользователь является преподавателем этого курса (минимум – роль `teacher`);
* создать запись в `lessons`.

**Ответ 201:** `LessonOut`.

---

### 7.2. Изменение занятия (перенос / изменение параметров)

**Path:** `PATCH /api/lessons/{lesson_id}`
**Авторизация:** `teacher` / `admin`

**Параметры пути:**

* `lesson_id` – UUID.

**Тело запроса:** `LessonUpdate` (все поля опциональны).

Логика:

* получить занятие;
* обновить только переданные поля;
* не разрешать изменение уже `finished` (по желанию).

**Ответ 200:** `LessonOut`.

---

### 7.3. Получение расписания текущего пользователя

**Path:** `GET /api/schedule/me`
**Авторизация:** требуется (любой авторизованный пользователь)

**Query-параметры:**

* `from` – datetime, начало интервала (опционально);
* `to` – datetime, конец интервала (опционально);
* `offset` – int, по умолчанию 0;
* `count` – int, по умолчанию 50.

Логика:

* получить `user_id` и `role` из JWT;
* выбрать занятия:

  * если `student` – по курсам, в которых он записан;
  * если `teacher` – по курсам, которые он ведёт;
* вернуть массив `ScheduleItemMe`.

**Ответ 200:** `ScheduleResponse`.

---

### 7.4. Получение расписания по курсу

**Path:** `GET /api/courses/{course_id}/schedule`
**Авторизация:** `teacher` / `admin` (можно разрешить student, если курс публичный – на усмотрение)

**Параметры пути:**

* `course_id` – UUID.

**Query-параметры:**

* `from`, `to` – интервал (опционально).

Логика:

* выбрать все занятия курса в интервале;
* вернуть список `LessonOut` или упрощённых объектов.

**Ответ 200:**

```json
{
  "course_id": "UUID",
  "course_title": "Алгебра, 10 класс",
  "items": [ /* массив LessonOut или сокращённых объектов */ ]
}
```

---

### 7.5. Отметка посещаемости по занятию

**Path:** `POST /api/lessons/{lesson_id}/attendance`
**Авторизация:** `teacher` / `admin`

**Параметры пути:**

* `lesson_id` – UUID.

**Тело запроса:** `AttendanceSetRequest`.

Логика:

* убедиться, что вызывающий – преподаватель курса (или админ);
* для каждого `student_id`:

  * создать или обновить запись в `lesson_attendance`;
  * проставить `marked_at = now()`.

**Ответ 200:** объект с `lesson_id`, списком итоговых записей и временем обновления:

```json
{
  "lesson_id": "UUID",
  "items": [
    {
      "student_id": "UUID",
      "status": "present",
      "comment": null,
      "marked_at": "2025-02-21T17:50:00Z"
    }
  ],
  "updated_at": "2025-02-21T17:50:00Z"
}
```

---

### 7.6. Получение посещаемости по занятию

**Path:** `GET /api/lessons/{lesson_id}/attendance`
**Авторизация:**

* `teacher` / `admin` – видит всех;
* `student` – может видеть только свою строку (либо всех по политике платформы).

**Параметры пути:**

* `lesson_id` – UUID.

**Ответ 200:** `AttendanceResponse` (см. выше).

---

## 8. Обработка ошибок

Формат ошибок общий:

```json
{
  "detail": "Сообщение об ошибке"
}
```

Основные коды:

* 400 – некорректные данные (например, `end_at` ≤ `start_at`);
* 401 – пользователь не авторизован (нет/невалидный токен);
* 403 – нет прав (например, студент пытается изменить занятие);
* 404 – занятие или посещаемость не найдены;
* 409 – конфликт (например, попытка создать занятие с пересечением по времени, если такое правило вводится);
* 500 – внутренняя ошибка сервера.

---

## 9. Dockerfile

Использовать такой же подход, как в остальных микросервисах:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

В `docker-compose.yml`:

```yaml
  schedule-service:
    build:
      context: ./services/schedule-service
    container_name: schedule-service
    env_file:
      - .env
    environment:
      SERVICE_NAME: schedule-service
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: otp_user
      DB_PASSWORD: otp_password
      DB_NAME: otp_main
    depends_on:
      - postgres
    ports:
      - "8007:8000"
```

---

## 10. Минимальные тесты

Рекомендуется:

### Юнит-тесты `schedule_service`

* создание занятия:

  * успешный кейс;
  * проверка, что `end_at > start_at`;
* обновление занятия (меняются только переданные поля);
* получение расписания для пользователя:

  * фильтрация по интервалу дат;
* отметка посещаемости:

  * корректное обновление/создание записей.

### Интеграционные тесты HTTP

* `POST /api/courses/{id}/lessons` – создаёт занятие (роль teacher);
* `PATCH /api/lessons/{id}` – изменяет занятие;
* `GET /api/schedule/me` – возвращает расписание текущего пользователя;
* `POST /api/lessons/{id}/attendance` – выставляет посещаемость;
* `GET /api/lessons/{id}/attendance` – возвращает посещаемость.

Этого достаточно, чтобы разработчик, не участвовавший в проектировании, смог корректно реализовать микросервис «Расписание» и встроить его в общую микросервисную архитектуру проекта.

```
```

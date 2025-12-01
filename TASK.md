````markdown
# Микросервис «Домашнее задание» – техническое задание

Этот документ описывает, **что нужно реализовать** в микросервисе «Домашнее задание» в рамках проекта онлайн-платформы обучения.

Микросервис отвечает за:

- создание домашних заданий преподавателем;
- получение списка ДЗ по курсу;
- получение списка ДЗ для конкретного ученика;
- отправку решений учениками;
- просмотр конкретного решения;
- проверку и выставление оценки за ДЗ (c последующей записью в «Электронный журнал»).

---

## 1. Общие требования и стек

**Язык:** Python  
**Фреймворк:** FastAPI (желательно)  
Дополнительно:

- Pydantic – схемы запросов/ответов;
- SQLAlchemy – работа с PostgreSQL;
- Alembic – миграции (желательно);
- HTTP-клиент (например, `httpx`) для синхронного вызова «Электронного журнала» при выставлении оценки (опционально, можно заглушкой).

Все настройки — через переменные окружения (аналогично микросервису «Пользователь»).

---

## 2. Структура директорий микросервиса

Папка: `services/homework-service`

```text
homework-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI-приложение
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── homeworks.py # все HTTP-эндпоинты ДЗ
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # конфиг (DB_HOST и т.п.)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py       # engine + сессии
│   │   └── migrations/      # alembic (если делаешь)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py     # ORM-модели HomeWork, Submission
│   │   └── schemas.py       # Pydantic-схемы
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── homeworks_repo.py
│   └── services/
│       ├── __init__.py
│       └── homeworks_service.py
│
├── tests/
│   ├── __init__.py
│   └── test_api_homeworks.py
│
├── Dockerfile
├── requirements.txt
└── README.md
````

---

## 3. Конфигурация и окружение

Через `core/config.py` прочитать:

* `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`;
* `ENV` – окружение (`local/dev/prod`);
* при интеграции с журналом:

  * `GRADEBOOK_SERVICE_URL` – базовый URL сервиса «Электронный журнал» (например, `http://gradebook-service:8000`).

---

## 4. Модель данных

### 4.1. Таблица `homeworks`

Хранит сами задания.

Поля:

* `id` – UUID, PK;
* `course_id` – UUID (идентификатор курса);
* `lesson_id` – UUID, nullable (если ДЗ не привязано к конкретному занятию);
* `title` – строка, название задания;
* `description` – строка, текст условия;
* `due_at` – datetime, дедлайн сдачи;
* `max_score` – число (int/float);
* `status` – строка (`draft`, `assigned`, `closed`);
* `attachments` – JSON/текст (список URL к материалам);
* `created_at` – datetime;
* `updated_at` – datetime.

### 4.2. Таблица `homework_submissions`

Хранит решения учеников.

Поля:

* `id` – UUID, PK;
* `homework_id` – FK → homeworks.id;
* `student_id` – UUID (из сервиса «Пользователь»);
* `answer_text` – текстовый ответ (nullable);
* `attachments` – JSON/текст (массив ссылок на файлы);
* `status` – строка (`submitted`, `checked`, `needs_fix`);
* `score` – число, nullable;
* `teacher_comment` – строка, nullable;
* `created_at` – datetime (когда ученик отправил);
* `checked_at` – datetime, nullable.

---

## 5. Pydantic-схемы (примерный набор)

В `models/schemas.py`:

* `HomeworkCreate` – тело запроса для создания ДЗ;

* `HomeworkOut` – объект ДЗ для отдачи наружу (краткая/полная версия);

* `HomeworkListItem` + `HomeworkListResponse`;

* `StudentHomeworkItem` – строка для списка ДЗ ученика;

* `SubmissionCreate` – отправка решения;

* `SubmissionOut` – выдача решения;

* `GradeSubmissionRequest` – запрос на выставление оценки (teacher);

* `GradeSubmissionResponse` – результат проверки.

---

## 6. Репозиторий и сервис

### 6.1. `homeworks_repo.py`

Примерный функционал:

* `create_homework(data: HomeworkCreate)` → `Homework`;
* `get_homework(homework_id)` → `Homework | None`;
* `list_homeworks_for_course(course_id, filters, offset, count)` → список + total;
* `create_submission(homework_id, student_id, data: SubmissionCreate)` → `Submission`;
* `get_submission(submission_id)` → `Submission | None`;
* `list_student_homeworks(student_id, status, offset, count)` → сводный список;
* `grade_submission(submission_id, score, status, comment)` → обновлённый `Submission`.

### 6.2. `homeworks_service.py`

Бизнес-логика:

* проверка прав (учитель/ученик — можно делать в HTTP-слое по ролям из JWT);
* валидация статусов:

  * нельзя создавать submission, если ДЗ `closed`;
* при выставлении оценки:

  * обновить `Submission`;
  * (опционально) дернуть сервис «Электронный журнал»:

    * `POST /api/gradebook/homework` с `student_id`, `course_id`, `homework_id`, `score`, `max_score`, `graded_at`.

---

## 7. REST API эндпоинты

Все пути ниже предполагают префикс `/api`.

### 7.1. Создание домашнего задания

**Path:** `POST /api/courses/{course_id}/homeworks`
**Авторизация:** `teacher`

Тело запроса (схема `HomeworkCreate`):

```json
{
  "title": "Домашнее задание по теме \"Функции\"",
  "description": "Решить задачи 1–10 из файла и загрузить ответы в формате PDF.",
  "lesson_id": "UUID (или null)",
  "due_at": "2025-03-01T18:00:00Z",
  "max_score": 10,
  "attachments": [
    "https://files.example.com/homeworks/hw1_tasks.pdf"
  ]
}
```

Ответ 201: созданный `HomeworkOut`.

---

### 7.2. Получение списка ДЗ по курсу (для преподавателя)

**Path:** `GET /api/courses/{course_id}/homeworks`
**Авторизация:** `teacher`

Query-параметры:

* `lesson_id` – фильтр по уроку (опционально);
* `status` – `draft/assigned/closed` (опционально);
* `offset`, `count` – пагинация.

Ответ 200:

```json
{
  "items": [ /* массив HomeworkListItem */ ],
  "total": 123,
  "offset": 0,
  "count": 20
}
```

---

### 7.3. Получение списка ДЗ ученика

**Path:** `GET /api/students/me/homeworks`
**Авторизация:** `student`

Query-параметры:

* `status` – `active/submitted/checked` (опционально);
* `offset`, `count`.

Для каждого элемента желательно отдать:

* `homework_id`, `course_id`, `title`, `due_at`, `status`;
* `submission_id`, `score`, `max_score` (если есть).

---

### 7.4. Отправка решения ДЗ

**Path:** `POST /api/homeworks/{homework_id}/submissions`
**Авторизация:** `student`

Тело запроса (схема `SubmissionCreate`):

```json
{
  "answer_text": "Решения задач приведены в приложенном файле.",
  "attachments": [
    "https://files.example.com/submissions/hw1_ivanov.pdf"
  ]
}
```

Логика:

* проверить существование ДЗ;
* проверить, что текущий пользователь — ученик;
* запретить вторую попытку/разрешить перезапись — на твой выбор (можно сохранять только одну активную или хранить несколько).

Ответ 201: объект `SubmissionOut`.

---

### 7.5. Просмотр решения ДЗ

**Path:** `GET /api/homeworks/{homework_id}/submissions/{submission_id}`
**Авторизация:**

* `student` – только свою submission;
* `teacher` – решения своих учеников по своим курсам.

Ответ 200: `SubmissionOut` со всеми полями (answer_text, attachments, score, comment, status и т.д.).

---

### 7.6. Проверка ДЗ и выставление оценки

**Path:**
`POST /api/homeworks/{homework_id}/submissions/{submission_id}:grade`
**Авторизация:** `teacher`

Тело запроса (схема `GradeSubmissionRequest`):

```json
{
  "score": 9,
  "teacher_comment": "Хорошая работа, одна ошибка в задаче 7.",
  "status": "checked"
}
```

Логика:

* убедиться, что submission существует;
* проверить, что score ≤ max_score ДЗ;
* обновить `Submission`:

  * `score`, `teacher_comment`, `status`, `checked_at`;
* (опционально) вызвать REST-метод «Электронного журнала» для записи оценки.

Ответ 200: обновлённый `SubmissionOut`.

---

## 8. Ошибки и статусы

Рекомендуемый формат ошибки:

```json
{
  "detail": "Сообщение"
}
```

Типичные ошибки:

* 400 – неправильные данные (дедлайн в прошлом, неверный статус и т.д.);
* 401 – нет токена;
* 403 – нет прав (например, ученик пытается создавать ДЗ);
* 404 – ДЗ или submission не найдены;
* 409 – конфликт (например, повторная отправка, если запрещено).

---

## 9. Dockerfile

Минимальный `Dockerfile`, такой же как у остальных сервисов:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

В `docker-compose.yml` этот сервис мапится, например, на порт `8002`:

```yaml
  homework-service:
    build:
      context: ./services/homework-service
    container_name: homework-service
    env_file:
      - .env
    environment:
      SERVICE_NAME: homework-service
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: otp_user
      DB_PASSWORD: otp_password
      DB_NAME: otp_main
    depends_on:
      - postgres
    ports:
      - "8002:8000"
```

---

## 10. Минимальные тесты

* юнит-тесты сервиса:

  * создание ДЗ;
  * отправка решения;
  * проверка/оценка;
* интеграционные (через HTTP):

  * `POST /api/courses/{id}/homeworks` – создаёт задание;
  * `GET /api/courses/{id}/homeworks` – возвращает список;
  * `POST /api/homeworks/{id}/submissions` – создаёт решение;
  * `POST /api/homeworks/{id}/submissions/{sub_id}:grade` – выставляет оценку.

Этого объёма достаточно, чтобы другой разработчик корректно реализовал микросервис и вписал его в общую архитектуру.

```
```

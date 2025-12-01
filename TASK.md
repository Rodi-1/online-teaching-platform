````markdown
# Микросервис «Отчёт» – техническое задание

Этот документ описывает, **что нужно реализовать** в микросервисе «Отчёт» в рамках онлайн-платформы обучения.

Микросервис отвечает за:

- запуск **длительных операций генерации отчётов**;
- хранение метаданных операций (статус, прогресс, ошибки);
- хранение **готовых отчётов** (метаданные + ссылка на файл);
- выдачу **списка отчётов**, информации по одному отчёту;
- получение **ссылки для скачивания**;
- **перегенерацию** отчёта с теми же параметрами.

**Не отвечает** за:

- непосредственный рендер PDF/XLSX (может делаться заглушкой или отдельной библиотекой внутри сервиса);
- визуализацию отчётов в интерфейсе (это фронтенд);
- расчёт бизнес-логики оценок (это делает «Электронный журнал» и другие сервисы, отчёт их только агрегирует).

---

## 1. Общие требования и стек

**Язык:** Python  
**Фреймворк:** FastAPI (как и у остальных микросервисов)

Рекомендуемые библиотеки:

- `fastapi` – HTTP API;
- `uvicorn` – ASGI-сервер;
- `pydantic` – схемы запросов/ответов;
- `sqlalchemy` – ORM (PostgreSQL);
- `alembic` – миграции (желательно);
- стандартный `logging`.

Форматы отчётов (минимум):

- `type`:  
  - `course_performance` – успеваемость по курсу;  
  - `student_progress` – прогресс конкретного ученика;  
  - `attendance` – посещаемость.
- `format`: `pdf`, `xlsx` (минимум один можно реализовать как заглушку).

---

## 2. Структура директорий микросервиса

Папка: `services/reports-service`

```text
reports-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # точка входа FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── reports.py         # HTTP-эндпоинты сервиса «Отчёт»
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # конфиг (DB_HOST, и т.п.)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py             # engine + SessionLocal
│   │   └── migrations/            # alembic-миграции
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py           # ORM-модели (Report, ReportOperation)
│   │   └── schemas.py             # Pydantic-схемы
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── reports_repo.py        # работа с БД
│   └── services/
│       ├── __init__.py
│       └── reports_service.py     # бизнес-логика (операции + генерация)
│
├── tests/
│   ├── __init__.py
│   └── test_api_reports.py
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
* `DB_PASSWORD` – пароль БД;
* `DB_NAME` – имя базы/схемы для отчётов;
* `ENV` – `local` / `dev` / `prod`.

Желательно:

* `LOG_LEVEL`;
* `REPORT_STORAGE_BASE_URL` – базовый URL, по которому фронтенд будет скачивать файлы (например, `https://files.example.com/reports/`);
* `REPORT_STORAGE_PATH` – локальный путь в контейнере для сохранения отчётных файлов (например, `/data/reports`).

`db/session.py`:

* создаёт `SQLAlchemy` engine;
* предоставляет `SessionLocal` (sessionmaker).

---

## 4. Модель данных (БД)

### 4.1. Таблица `report_operations` (операции генерации)

Описывает **длительную операцию** генерации отчёта.

Поля:

* `id` – UUID, PK (`operation_id`);
* `status` – строка:

  * `pending` – ожидает выполнения;
  * `in_progress` – идёт генерация;
  * `completed` – завершена успешно;
  * `failed` – завершилась с ошибкой.
* `type` – тип отчёта (`course_performance`, `student_progress`, `attendance`, …);
* `format` – формат (`pdf`, `xlsx`, …);
* `requested_by` – строка/UUID (id пользователя или сервиса, запросившего отчёт);
* `requested_at` – datetime;
* `started_at` – datetime, nullable;
* `finished_at` – datetime, nullable;
* `progress_percent` – int (0–100, nullable);
* `report_id` – FK → `reports.id`, nullable (заполняется после успешной генерации);
* `error_message` – строка, nullable (описание ошибки при `failed`);
* `filters_json` – JSON / text (сырые фильтры, чтобы не дублировать поля).

Индексы:

* по `requested_by`;
* по `status`.

### 4.2. Таблица `reports` (готовые отчёты)

Хранит метаданные уже сгенерированных отчётов.

Поля:

* `id` – UUID, PK (`report_id`);
* `type` – строка (как выше);
* `format` – строка (`pdf`, `xlsx`);
* `status` – строка: `completed`, `failed`, `expired` (минимум – `completed`, `failed`);
* `created_by` – строка/UUID (кто запросил отчёт);
* `created_at` – datetime;
* `ready_at` – datetime, nullable;
* `filters_json` – JSON / text (структура фильтров: course_id, student_id, from/to и т.д.);
* `file_path` – строка, путь к файлу в файловой системе (например, `/data/reports/rep-xxx.xlsx`);
* `download_url` – строка, публичная ссылка (может формироваться на основе `REPORT_STORAGE_BASE_URL`);
* `size_bytes` – int, nullable (размер файла в байтах).

Индексы:

* по `created_by`;
* по `type`;
* по `created_at`.

---

## 5. Pydantic-схемы

В `models/schemas.py` описать основные модели.

### 5.1. Запуск генерации отчёта

`ReportGenerateFilters` – вложенный объект фильтров:

```json
{
  "course_id": "UUID (опционально)",
  "student_id": "UUID (опционально)",
  "from": "2025-02-01T00:00:00Z",
  "to": "2025-02-28T23:59:59Z"
}
```

`ReportGenerateRequest`:

```json
{
  "type": "course_performance",
  "format": "xlsx",
  "filters": {
    "course_id": "UUID",
    "from": "2025-02-01T00:00:00Z",
    "to": "2025-02-28T23:59:59Z"
  }
}
```

`ReportOperationOut` (для ответа при запуске и при запросе статуса):

```json
{
  "operation_id": "UUID",
  "status": "pending",
  "type": "course_performance",
  "format": "xlsx",
  "requested_by": "user-123",
  "requested_at": "2025-03-01T09:00:00Z",
  "started_at": null,
  "finished_at": null,
  "progress_percent": 0,
  "report_id": null,
  "error_message": null
}
```

### 5.2. Описание отчёта

`ReportOut`:

```json
{
  "id": "UUID",
  "type": "course_performance",
  "format": "xlsx",
  "status": "completed",
  "created_by": "user-123",
  "created_at": "2025-03-01T09:00:05Z",
  "ready_at": "2025-03-01T09:01:20Z",
  "filters": {
    "course_id": "UUID",
    "from": "2025-02-01T00:00:00Z",
    "to": "2025-02-28T23:59:59Z"
  },
  "download_url": "https://files.example.com/reports/rep-81c2f4b9.xlsx",
  "size_bytes": 24576
}
```

`ReportsListResponse`:

```json
{
  "items": [ /* массив ReportOut (без лишних полей, по желанию) */ ],
  "total": 10,
  "offset": 0,
  "count": 20
}
```

`ReportDownloadLink`:

```json
{
  "report_id": "UUID",
  "download_url": "https://files.example.com/reports/rep-81c2f4b9.xlsx?token=abc123",
  "expires_at": "2025-03-01T12:00:00Z"
}
```

---

## 6. Репозиторий и сервис

### 6.1. `reports_repo.py`

Примерный набор функций:

* операции:

  * `create_operation(type, format, filters_json, requested_by) -> ReportOperation`;
  * `set_operation_started(operation_id) -> ReportOperation`;
  * `set_operation_progress(operation_id, progress_percent) -> ReportOperation`;
  * `set_operation_completed(operation_id, report_id) -> ReportOperation`;
  * `set_operation_failed(operation_id, error_message) -> ReportOperation`;
  * `get_operation(operation_id) -> ReportOperation | None`;

* отчёты:

  * `create_report(type, format, filters_json, created_by, file_path, download_url, size_bytes) -> Report`;
  * `get_report(report_id) -> Report | None`;
  * `list_reports(filters, offset, count) -> (list[Report], total)`
    (фильтры: type, format, status, created_by, from, to).

### 6.2. `reports_service.py`

Основная логика:

* `start_generation(request: ReportGenerateRequest, requested_by)`:

  * создать запись в `report_operations` со статусом `pending`;

  * **минимальный вариант:** сразу в том же процессе:

    * пометить `in_progress`;
    * сгенерировать отчёт (заглушкой – создать файл с минимальным содержимым);
    * создать запись в таблице `reports`;
    * пометить операцию как `completed` с привязкой к `report_id`;

  * вернуть `operation_id`.

  > Важно: даже если генерация выполняется синхронно, API остаётся «длительным» — клиент всегда работает через `operation_id` и статус.

* `get_operation_status(operation_id)` – возвращает `ReportOperationOut`.

* `regenerate_report(report_id, requested_by)`:

  * загрузить старый отчёт;
  * взять `type`, `format`, `filters_json`;
  * создать новую операцию с этими параметрами (как в `start_generation`);
  * запустить генерацию (так же, как выше);
  * вернуть `operation_id`.

* вспомогательные:

  * генерация физического файла отчёта;
  * построение `download_url` из `file_path` и `REPORT_STORAGE_BASE_URL`.

---

## 7. REST API эндпоинты

Все пути далее указаны относительно префикса `/api`.

### 7.1. Запуск генерации отчёта (длительная операция)

**Path:** `POST /api/reports:generate`
**Авторизация:** требуется (роль `teacher` или `admin`, можно добавить `manager`)

**Тело запроса:** `ReportGenerateRequest`.

Пример:

```json
{
  "type": "course_performance",
  "format": "xlsx",
  "filters": {
    "course_id": "UUID",
    "from": "2025-02-01T00:00:00Z",
    "to": "2025-02-28T23:59:59Z"
  }
}
```

**Ответ 200/202:** `ReportOperationOut` (минимальный набор полей):

```json
{
  "operation_id": "UUID",
  "status": "pending",
  "type": "course_performance",
  "format": "xlsx",
  "requested_by": "teacher-42",
  "requested_at": "2025-03-01T09:00:00Z"
}
```

---

### 7.2. Получение статуса операции генерации

**Path:** `GET /api/reports/operations/{operation_id}`
**Авторизация:** требуется (владелец операции или админ)

**Параметры пути:**

* `operation_id` – UUID.

**Ответ 200:** `ReportOperationOut`.

---

### 7.3. Получение списка сгенерированных отчётов

**Path:** `GET /api/reports`
**Авторизация:** требуется (роль `teacher` / `admin`; можно фильтровать по `created_by`)

**Query-параметры (фильтры):**

* `type` – тип отчёта (опционально);
* `format` – формат (опционально);
* `status` – `completed` / `failed` / `all` (по умолчанию `completed`);
* `from` – дата-время начала периода по `created_at`;
* `to` – дата-время конца периода;
* `offset` – int, по умолчанию 0;
* `count` – int, по умолчанию 20.

**Ответ 200:** `ReportsListResponse`.

---

### 7.4. Получение информации о конкретном отчёте

**Path:** `GET /api/reports/{report_id}`
**Авторизация:** требуется (создатель или админ)

**Параметры пути:**

* `report_id` – UUID.

**Ответ 200:** `ReportOut`.

---

### 7.5. Получение ссылки для скачивания отчёта

> В учебном варианте можно не отдавать сам бинарный файл, а вернуть JSON с URL и временем истечения.

**Path:** `GET /api/reports/{report_id}/download`
**Авторизация:** требуется

**Параметры пути:**

* `report_id` – UUID.

**Ответ 200:** `ReportDownloadLink`.

---

### 7.6. Перегенерация отчёта

**Path:** `POST /api/reports/{report_id}:regenerate`
**Авторизация:** требуется (создатель или админ)

**Параметры пути:**

* `report_id` – UUID.

**Тело запроса:** можно оставить пустым (`{}`) – все параметры берутся из исходного отчёта.

**Ответ 200/202:** `ReportOperationOut` (аналогично запуску новой операции).

---

## 8. Обработка ошибок

Единый формат:

```json
{
  "detail": "Сообщение об ошибке"
}
```

Основные коды:

* `400 Bad Request` – некорректные данные (`type`/`format` неизвестны, фильтры невалидны);
* `401 Unauthorized` – нет или неверный токен;
* `403 Forbidden` – пользователь не имеет права на запрос или просмотр отчёта;
* `404 Not Found` – операция или отчёт не найдены;
* `409 Conflict` – (опционально) если уже идёт генерация такого же отчёта и запрещено дублировать;
* `500 Internal Server Error` – внутренняя ошибка.

---

## 9. Dockerfile

Стандартный для всех микросервисов:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Фрагмент `docker-compose.yml`:

```yaml
  reports-service:
    build:
      context: ./services/reports-service
    container_name: reports-service
    env_file:
      - .env
    environment:
      SERVICE_NAME: reports-service
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: otp_user
      DB_PASSWORD: otp_password
      DB_NAME: otp_main
      REPORT_STORAGE_PATH: /data/reports
      REPORT_STORAGE_BASE_URL: https://files.example.com/reports/
    depends_on:
      - postgres
    volumes:
      - reports_data:/data/reports
    ports:
      - "8008:8000"

volumes:
  reports_data:
```

---

## 10. Минимальные тесты

### Юнит-тесты `reports_service`

Покрыть:

1. `start_generation`:

   * создаётся операция со статусом `pending` / `completed`;
   * создаётся запись в `reports` (при синхронной генерации).

2. `get_operation_status`:

   * корректный возврат данных по существующей операции;
   * ошибка 404, если операция не найдена.

3. `regenerate_report`:

   * создаётся новая операция с теми же `type`/`format`/`filters_json`;
   * не падает, если исходный отчёт в статусе `completed`.

### Интеграционные тесты HTTP

* `POST /api/reports:generate` – запускает операцию и возвращает `operation_id`;
* `GET /api/reports/operations/{operation_id}` – показывает смену статуса до `completed`;
* `GET /api/reports` – возвращает список отчётов;
* `GET /api/reports/{report_id}` – возвращает метаданные;
* `GET /api/reports/{report_id}/download` – возвращает ссылку на скачивание;
* `POST /api/reports/{report_id}:regenerate` – запускает новую операцию.

---

Этого объёма достаточно, чтобы разработчик, не участвовавший в проектировании, смог корректно реализовать микросервис «Отчёт» и встроить его в существующую микросервисную архитектуру (с паттерном длительной операции: **запуск → статус → готовый отчёт → скачивание → перегенерация**).

```
```

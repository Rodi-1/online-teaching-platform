````markdown
# Микросервис «Уведомления» – техническое задание

Этот документ описывает, **что нужно реализовать** в микросервисе «Уведомления» в рамках проекта онлайн-платформы обучения.

Микросервис отвечает за:

- хранение уведомлений для пользователей (внутренний «колокольчик» в интерфейсе);
- получение списка уведомлений пользователем;
- пометку уведомлений как прочитанных (по одному и массово);
- подсчёт количества непрочитанных уведомлений;
- приём запросов от других микросервисов на создание уведомлений.

**Не отвечает** за:

- отправку email/SMS/push во внешние сервисы (можно сделать заглушкой или вынести в отдельный сервис);
- логику бизнес-событий (кто и когда должен получить уведомление — это решают другие микросервисы).

---

## 1. Общие требования и стек

**Язык:** Python  
**Фреймворк:** FastAPI (желательно, как и в других сервисах)

Рекомендуемые библиотеки:

- FastAPI – HTTP API;
- Pydantic – схемы запросов и ответов;
- SQLAlchemy – доступ к PostgreSQL;
- Alembic – миграции (желательно);
- стандартный `logging` для логов.

---

## 2. Структура директорий микросервиса

Папка: `services/notifications-service`

```text
notifications-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # точка входа FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── notifications.py   # все HTTP-эндпоинты уведомлений
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # конфиг (DB_HOST и пр.)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py             # engine + SessionLocal
│   │   └── migrations/            # alembic (по желанию)
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
│
├── tests/
│   ├── __init__.py
│   └── test_api_notifications.py
│
├── Dockerfile
├── requirements.txt
└── README.md
````

---

## 3. Конфигурация и переменные окружения

Через `core/config.py` прочитать:

* `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` – доступ к PostgreSQL;
* `ENV` – `local` / `dev` / `prod`;
* опционально `LOG_LEVEL`.

`db/session.py` должен:

* создать `SQLAlchemy` engine с использованием переменных окружения;
* предоставить `SessionLocal` (sessionmaker).

---

## 4. Модель данных

### 4.1. Таблица `notifications`

Одна основная таблица для всех пользовательских уведомлений.

Поля:

* `id` – UUID, PK;
* `user_id` – UUID, ID пользователя (из микросервиса «Пользователь»);
* `type` – строка (`homework`, `test`, `schedule`, `achievement`, `system` и т.п.);
* `title` – строка, заголовок уведомления;
* `body` – строка, основной текст уведомления;
* `data` – JSON / text, произвольные дополнительные данные:

  * `course_id`, `homework_id`, `test_id`, `due_at` и т.п.;
* `is_read` – boolean, прочитано/не прочитано;
* `created_at` – datetime – когда уведомление создано;
* `read_at` – datetime, nullable – когда помечено как прочитанное.

Дополнительно (по желанию):

* `send_email` – boolean, было ли отправлено по email;
* `send_push` – boolean, было ли отправлено push-уведомление.

Индексы:

* по `user_id`;
* по `(user_id, is_read)`.

---

## 5. Pydantic-схемы

В `models/schemas.py`:

### 5.1. Выходные объекты

* `NotificationOut` – единичное уведомление:

  ```json
  {
    "id": "UUID",
    "user_id": "UUID",
    "type": "homework",
    "title": "Новое домашнее задание",
    "body": "По курсу \"Алгебра\" выдано новое ДЗ.",
    "data": {
      "course_id": "UUID",
      "homework_id": "UUID",
      "due_at": "2025-03-01T18:00:00Z"
    },
    "is_read": false,
    "created_at": "2025-02-18T12:00:00Z",
    "read_at": null
  }
  ```

* `NotificationsListResponse`:

  ```json
  {
    "items": [ /* массив NotificationOut */ ],
    "total": 10,
    "offset": 0,
    "count": 20
  }
  ```

* `UnreadCountResponse`:

  ```json
  {
    "user_id": "UUID",
    "type_filter": null,
    "unread_count": 3
  }
  ```

### 5.2. Входные схемы

* `NotificationCreateInternal` – для создания уведомления из других сервисов:

  ```json
  {
    "user_id": "UUID",
    "type": "homework",
    "title": "Новое домашнее задание",
    "body": "По курсу \"Алгебра\" выдано новое ДЗ. Дедлайн: 01.03.2025 18:00.",
    "data": {
      "course_id": "UUID",
      "homework_id": "UUID",
      "due_at": "2025-03-01T18:00:00Z"
    },
    "send_email": true,
    "send_push": true
  }
  ```

(Поля `send_email` / `send_push` можно просто игнорировать или логировать.)

---

## 6. Репозиторий и сервис

### 6.1. `notifications_repo.py`

Примерный функционал:

* `create_notification(data: NotificationCreateInternal) -> Notification`;
* `list_notifications_for_user(user_id, filters, offset, count) -> (list[Notification], total)`
  фильтры: `status` (`unread/read/all`), `type`, `from`, `to`;
* `get_notification(notification_id) -> Notification | None`;
* `mark_read(notification_id) -> Notification`;
* `mark_all_read(user_id, type) -> int` – возвращает количество обновлённых строк;
* `count_unread(user_id, type) -> int`.

### 6.2. `notifications_service.py`

Логика:

* оборачивает репозиторий, добавляет доп.проверки:

  * уведомления может читать/отмечать только владелец (`user_id из токена`);
* для массовой пометки «прочитано»:

  * вызывается `mark_all_read` по `user_id` (и `type`, если указан);
* при создании уведомления:

  * просто сохраняет его в БД;
  * (опционально) отправляет задачу/лог в очередь для email/push.

---

## 7. REST API эндпоинты

Все пути – с префиксом `/api`.

### 7.1. Получение списка уведомлений пользователя

**Path:** `GET /api/notifications/me`
**Авторизация:** требуется (любой авторизованный пользователь)

**Query-параметры:**

* `status` – `unread` / `read` / `all` (по умолчанию `all`);
* `type` – фильтр по типу (`homework`, `test`, `schedule`, `achievement`, `system`, опционально);
* `from` – datetime, не раньше какой даты;
* `to` – datetime, не позже какой даты;
* `offset` – целое, по умолчанию 0;
* `count` – целое, по умолчанию 20.

Логика:

* получить `user_id` из JWT;
* выбрать уведомления только этого пользователя;
* применить фильтры + пагинацию.

**Ответ 200:** `NotificationsListResponse`.

---

### 7.2. Отметка одного уведомления как прочитанного

**Path:** `POST /api/notifications/{notification_id}/read`
**Авторизация:** требуется

**Параметры пути:**

* `notification_id` – UUID.

Логика:

* получить `user_id` из токена;
* найти уведомление;
* проверить, что `notification.user_id == current_user_id`;
* установить `is_read = true`, `read_at = now`.

**Ответ 200:** `NotificationOut` – обновлённое уведомление.

Ошибки:

* 404 – если уведомление не найдено;
* 403 – если уведомление принадлежит другому пользователю.

---

### 7.3. Массовая пометка уведомлений как прочитанных

**Path:** `POST /api/notifications:mark-all-read`
**Авторизация:** требуется

**Query-параметры:**

* `type` – опциональный фильтр по типу уведомлений (если указан – помечаются прочитанными только этого типа).

Тело запроса можно оставить пустым.

Логика:

* получить `user_id` из токена;
* обновить все `notifications` этого пользователя (`is_read = true, read_at = now`), с учётом `type`, если передан.

**Ответ 200:** например:

```json
{
  "user_id": "UUID",
  "updated_count": 5,
  "type_filter": null
}
```

---

### 7.4. Создание уведомления для пользователя (внутренний вызов)

**Path:** `POST /api/notifications`
**Авторизация:** только внутренние сервисы (по сервисному токену / роли `service`)

**Тело запроса:** `NotificationCreateInternal`.

Логика:

* сохранить уведомление в таблицу `notifications` с `is_read = false`;
* (опционально) отправить события в очередь для внешних каналов;
* вернуть созданный объект.

**Ответ 201:** `NotificationOut`.

---

### 7.5. Получение количества непрочитанных уведомлений

**Path:** `GET /api/notifications/me/unread-count`
**Авторизация:** требуется

**Query-параметры:**

* `type` – опционально, фильтр по типу уведомлений.

Логика:

* по `user_id` из токена посчитать количество записей, где `is_read = false` (и `type`, если задан).

**Ответ 200:** `UnreadCountResponse`.

---

## 8. Обработка ошибок

Формат ошибок – общий для всех сервисов:

```json
{
  "detail": "Сообщение об ошибке"
}
```

Типичные коды:

* 400 – некорректные параметры (например, неправильный формат даты);
* 401 – неавторизован (нет токена / токен неверен);
* 403 – нет прав (доступ к чужим уведомлениям);
* 404 – уведомление не найдено;
* 500 – внутренняя ошибка сервера.

---

## 9. Dockerfile

Стандартный `Dockerfile`, как у других микросервисов:

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
  notifications-service:
    build:
      context: ./services/notifications-service
    container_name: notifications-service
    env_file:
      - .env
    environment:
      SERVICE_NAME: notifications-service
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: otp_user
      DB_PASSWORD: otp_password
      DB_NAME: otp_main
    depends_on:
      - postgres
    ports:
      - "8005:8000"
```

---

## 10. Минимальные тесты

Рекомендуется реализовать:

* **юнит-тесты** для `notifications_service`:

  * корректное создание уведомления;
  * пометка одного уведомления как прочитанного;
  * массовая пометка по пользователю и типу;
  * корректный подсчёт непрочитанных.

* **интеграционные тесты** HTTP:

  * `GET /api/notifications/me` – возвращает список уведомлений только текущего пользователя;
  * `POST /api/notifications/{id}/read` – помечает как прочитанное;
  * `POST /api/notifications:mark-all-read` – массовая пометка;
  * `GET /api/notifications/me/unread-count` – возвращает корректное число;
  * `POST /api/notifications` – создаёт уведомление (только при наличии сервисной авторизации).

Этого достаточно, чтобы другой разработчик корректно реализовал микросервис «Уведомления» и вписал его в существующую микросервисную архитектуру проекта.

```
```

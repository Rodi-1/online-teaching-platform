# Reports Service

Микросервис генерации отчётов для платформы онлайн-обучения.

## Описание

Reports Service отвечает за:
- Запуск длительных операций генерации отчётов
- Хранение метаданных операций (статус, прогресс, ошибки)
- Хранение готовых отчётов (метаданные + ссылка на файл)
- Выдачу списка отчётов и информации по одному отчёту
- Получение ссылки для скачивания
- Перегенерацию отчёта с теми же параметрами

## Технологии

- **Python 3.11+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с PostgreSQL
- **Pydantic** - валидация данных
- **PostgreSQL** - база данных

## Структура проекта

```
reports-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── reports.py          # Все HTTP endpoints
│   ├── core/
│   │   ├── config.py                # Конфигурация
│   │   └── security.py              # Безопасность
│   ├── db/
│   │   ├── session.py               # Сессии БД
│   │   └── migrations/              # Alembic миграции
│   ├── models/
│   │   ├── db_models.py             # ORM модели
│   │   └── schemas.py               # Pydantic схемы
│   ├── repositories/
│   │   └── reports_repo.py          # Репозиторий
│   ├── services/
│   │   └── reports_service.py       # Бизнес-логика
│   └── main.py                      # Точка входа FastAPI
├── tests/                           # Тесты
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

### Генерация отчётов

- `POST /api/reports:generate` - Запустить генерацию отчёта (teacher/admin/manager)
- `GET /api/reports/operations/{id}` - Получить статус операции

### Управление отчётами

- `GET /api/reports` - Получить список отчётов
- `GET /api/reports/{id}` - Получить информацию об отчёте
- `GET /api/reports/{id}/download` - Получить ссылку для скачивания
- `POST /api/reports/{id}:regenerate` - Перегенерировать отчёт

## Модели данных

### ReportOperation (Операция генерации)
- `id` - UUID операции
- `status` - статус (pending/in_progress/completed/failed)
- `type` - тип отчёта (course_performance/student_progress/attendance)
- `format` - формат (pdf/xlsx)
- `requested_by` - кто запросил
- `requested_at`, `started_at`, `finished_at` - временные метки
- `progress_percent` - прогресс (0-100)
- `report_id` - ссылка на готовый отчёт
- `error_message` - сообщение об ошибке
- `filters_json` - фильтры отчёта

### Report (Готовый отчёт)
- `id` - UUID отчёта
- `type` - тип отчёта
- `format` - формат
- `status` - статус (completed/failed/expired)
- `created_by` - кто создал
- `created_at`, `ready_at` - временные метки
- `filters_json` - фильтры
- `file_path` - путь к файлу
- `download_url` - ссылка для скачивания
- `size_bytes` - размер файла

## Типы отчётов

1. **course_performance** - Успеваемость по курсу
   - Фильтры: course_id, from, to

2. **student_progress** - Прогресс ученика
   - Фильтры: student_id, from, to

3. **attendance** - Посещаемость
   - Фильтры: course_id, from, to

## Форматы отчётов

- **pdf** - PDF документ
- **xlsx** - Excel таблица

> **Примечание**: В текущей реализации генерация - это заглушка, создающая текстовый файл. 
> В production реализации здесь будет:
> 1. Получение данных из других сервисов (gradebook, schedule, etc.)
> 2. Генерация PDF/XLSX с библиотеками (reportlab, openpyxl)
> 3. Сохранение в файловое хранилище

## Переменные окружения

```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=reports_service
DB_PASSWORD=your_password
DB_NAME=reports_service_db

# Report storage
REPORT_STORAGE_PATH=/data/reports
REPORT_STORAGE_BASE_URL=https://files.example.com/reports/

# Environment
ENV=local  # local, dev, prod
LOG_LEVEL=INFO
```

## Запуск

### Docker

```bash
docker build -t reports-service .
docker run -p 8000:8000 --env-file .env reports-service
```

### Локально (разработка)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
# Из корня проекта
docker-compose up -d reports-service
```

API документация: http://localhost:8008/docs

## Паттерн длительной операции

Сервис реализует паттерн длительной операции:

1. **Запуск**: `POST /api/reports:generate` → возвращает `operation_id`
2. **Отслеживание**: `GET /api/reports/operations/{id}` → получение статуса
3. **Готовый отчёт**: когда `status=completed`, получаем `report_id`
4. **Скачивание**: `GET /api/reports/{id}/download` → получение ссылки
5. **Перегенерация**: `POST /api/reports/{id}:regenerate` → новая операция

Это позволяет:
- Не блокировать HTTP-запрос на время генерации
- Отслеживать прогресс
- Обрабатывать ошибки
- Кешировать результаты

## Безопасность

- Header-based авторизация (`x-user-id`, `x-user-role`)
- Role-based access control
  - Генерация: teacher, admin, manager
  - Просмотр: создатель или admin
- Валидация всех входных данных
- Контроль доступа к операциям и отчётам

## Тестирование

```bash
pytest
```

Тесты включают:
- Генерацию отчётов
- Отслеживание статуса операций
- Получение списка отчётов
- Скачивание отчётов
- Перегенерацию
- Проверку прав доступа

## Интеграция

### Будущая интеграция с другими сервисами:

- **Gradebook Service** - данные об оценках
- **Schedule Service** - данные о посещаемости
- **User Service** - информация о пользователях
- **Notifications Service** - уведомления о готовности отчёта

## Лицензия

MIT


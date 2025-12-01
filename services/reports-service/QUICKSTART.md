# Быстрый старт - Reports Service

## Запуск через Docker Compose (рекомендуется)

Из корня проекта:

```bash
# Запустить все сервисы (включая reports-service)
docker-compose up -d

# Или запустить только reports-service
docker-compose up -d reports-service

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f reports-service
```

## Доступ к API

- **API**: http://localhost:8008
- **Swagger UI**: http://localhost:8008/docs
- **ReDoc**: http://localhost:8008/redoc
- **Health check**: http://localhost:8008/health

## Тестирование API

Все запросы требуют заголовки для авторизации:
- `x-user-id`: UUID пользователя
- `x-user-role`: роль (teacher, manager, admin)

### 1. Запустить генерацию отчёта

```bash
curl -X POST http://localhost:8008/api/reports:generate \
  -H "x-user-id: 12345678-1234-5678-1234-567812345678" \
  -H "x-user-role: teacher" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "course_performance",
    "format": "xlsx",
    "filters": {
      "course_id": "12345678-1234-5678-1234-567812345678",
      "from": "2025-02-01T00:00:00Z",
      "to": "2025-02-28T23:59:59Z"
    }
  }'
```

**Ответ:**
```json
{
  "operation_id": "uuid-here",
  "status": "pending",
  "type": "course_performance",
  "format": "xlsx",
  "requested_by": "12345678-1234-5678-1234-567812345678",
  "requested_at": "2025-03-01T09:00:00Z"
}
```

### 2. Отследить статус операции

```bash
curl -X GET http://localhost:8008/api/reports/operations/{operation_id} \
  -H "x-user-id: 12345678-1234-5678-1234-567812345678" \
  -H "x-user-role: teacher"
```

**Ответ при завершении:**
```json
{
  "operation_id": "uuid-here",
  "status": "completed",
  "type": "course_performance",
  "format": "xlsx",
  "requested_by": "...",
  "requested_at": "...",
  "started_at": "...",
  "finished_at": "...",
  "progress_percent": 100,
  "report_id": "report-uuid-here",
  "error_message": null
}
```

### 3. Получить список отчётов

```bash
curl -X GET "http://localhost:8008/api/reports?offset=0&count=20" \
  -H "x-user-id: 12345678-1234-5678-1234-567812345678" \
  -H "x-user-role: teacher"

# С фильтрами
curl -X GET "http://localhost:8008/api/reports?type=course_performance&format=xlsx" \
  -H "x-user-id: 12345678-1234-5678-1234-567812345678" \
  -H "x-user-role: teacher"
```

### 4. Получить информацию об отчёте

```bash
curl -X GET http://localhost:8008/api/reports/{report_id} \
  -H "x-user-id: 12345678-1234-5678-1234-567812345678" \
  -H "x-user-role: teacher"
```

### 5. Получить ссылку для скачивания

```bash
curl -X GET http://localhost:8008/api/reports/{report_id}/download \
  -H "x-user-id: 12345678-1234-5678-1234-567812345678" \
  -H "x-user-role: teacher"
```

**Ответ:**
```json
{
  "report_id": "uuid-here",
  "download_url": "https://files.example.com/reports/rep-12345678.xlsx",
  "expires_at": "2025-03-01T12:00:00Z"
}
```

### 6. Перегенерировать отчёт

```bash
curl -X POST http://localhost:8008/api/reports/{report_id}:regenerate \
  -H "x-user-id: 12345678-1234-5678-1234-567812345678" \
  -H "x-user-role: teacher"
```

Возвращает новый `operation_id` с теми же параметрами.

## Запуск тестов

```bash
cd services/reports-service

# Установить зависимости
pip install -r requirements.txt

# Запустить тесты
pytest

# С подробным выводом
pytest -v

# С покрытием
pytest --cov=app
```

## Переменные окружения

```env
# Database
REPORTS_SERVICE_DB_USER=reports_service
REPORTS_SERVICE_DB_PASSWORD=your_password
REPORTS_SERVICE_DB_NAME=reports_service_db

# Report storage
REPORT_STORAGE_PATH=/data/reports
REPORT_STORAGE_BASE_URL=https://files.example.com/reports/

# Environment
ENV=local
LOG_LEVEL=INFO
```

## Типичные сценарии использования

### Сценарий 1: Генерация отчёта по успеваемости курса

1. Teacher запрашивает генерацию: `POST /api/reports:generate`
2. Система возвращает `operation_id` со статусом "pending"
3. Teacher периодически проверяет статус: `GET /api/reports/operations/{id}`
4. Когда статус "completed", получает `report_id`
5. Teacher загружает отчёт: `GET /api/reports/{report_id}/download`

### Сценарий 2: Просмотр истории отчётов

1. Teacher запрашивает список: `GET /api/reports`
2. Система возвращает все ранее созданные отчёты
3. Teacher может фильтровать по типу, формату, датам
4. Teacher выбирает нужный отчёт и скачивает

### Сценарий 3: Перегенерация отчёта

1. Teacher находит старый отчёт: `GET /api/reports`
2. Teacher запрашивает перегенерацию: `POST /api/reports/{id}:regenerate`
3. Система создаёт новую операцию с теми же параметрами
4. Процесс идентичен первому сценарию

## Валидация и ограничения

### Типы отчётов:
- `course_performance` - успеваемость по курсу
- `student_progress` - прогресс ученика
- `attendance` - посещаемость

### Форматы:
- `pdf` - PDF документ
- `xlsx` - Excel таблица

### Права доступа:
- **Генерация**: только teacher, admin, manager
- **Просмотр операций**: создатель или admin
- **Просмотр отчётов**: создатель или admin
- **Скачивание**: создатель или admin
- **Перегенерация**: создатель или admin

## Troubleshooting

### Порт занят

Измените порт в `docker-compose.yml`:
```yaml
ports:
  - "8009:8000"  # Вместо 8008
```

### База данных не инициализировалась

```bash
# Пересоздать контейнеры
docker-compose down -v
docker-compose up -d
```

### Файлы отчётов не сохраняются

Убедитесь, что volume настроен в docker-compose:
```yaml
volumes:
  - reports_data:/data/reports
```

### Ошибка авторизации

Проверьте заголовки:
- `x-user-id` - корректный UUID
- `x-user-role` - одна из: teacher, admin, manager (не student!)

## Swagger UI

Самый простой способ тестировать API:

1. Откройте http://localhost:8008/docs
2. Добавьте заголовки в каждый запрос:
   - `x-user-id`: ваш UUID
   - `x-user-role`: teacher
3. Тестируйте endpoints прямо в браузере

## Полезные команды

```bash
# Посмотреть логи
docker-compose logs -f reports-service

# Перезапустить сервис
docker-compose restart reports-service

# Остановить сервис
docker-compose stop reports-service

# Войти в контейнер
docker exec -it reports-service bash

# Посмотреть сгенерированные файлы
docker exec reports-service ls -la /data/reports

# Проверить подключение к БД
docker exec -it reports-service python -c "from app.db.session import engine; print(engine.connect())"
```

## Следующие шаги

1. Изучите API через Swagger UI: http://localhost:8008/docs
2. Протестируйте все endpoints
3. Посмотрите примеры в тестах: `tests/test_api_reports.py`
4. Изучите код в `app/` директории

## Полезные ссылки

- [README.md](README.md) - Полная документация
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Детальный отчет
- [Основной README](../../README.md) - Документация проекта

Удачи! 🚀


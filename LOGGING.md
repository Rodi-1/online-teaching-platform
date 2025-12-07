# Логирование

## Обзор

Проект использует **структурированное JSON-логирование** для всех микросервисов с централизованным сбором логов через **Loki** и **Promtail**.

## Компоненты системы логирования

### 1. Python JSON Logger
Каждый микросервис использует библиотеку `python-json-logger` для генерации структурированных логов в формате JSON.

### 2. Loki
**Loki** - система централизованного хранения и индексации логов от Grafana Labs.

- **URL**: http://localhost:3100
- **Конфигурация**: `infra/loki/loki-config.yml`
- **Retention**: 7 дней (168 часов)

### 3. Promtail
**Promtail** - агент для сбора логов из Docker контейнеров и отправки в Loki.

- **Конфигурация**: `infra/promtail/promtail-config.yml`
- **Источник**: Docker сокет (`/var/run/docker.sock`)
- **Парсинг**: Автоматический парсинг JSON логов

### 4. Grafana Explore
Просмотр и поиск логов через Grafana:
- **URL**: http://localhost:3000/explore
- **Источник данных**: Loki

## Структура логов

### Формат JSON лога
```json
{
  "timestamp": "2025-12-07T10:30:45.123456Z",
  "level": "INFO",
  "service": "user-service",
  "logger": "app.api.v1.users",
  "module": "users",
  "function": "create_user",
  "line": 42,
  "message": "User created successfully",
  "request_id": "abc-123-def-456",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/v1/users",
  "status_code": 201,
  "duration_ms": 45.2,
  "client_host": "172.18.0.1"
}
```

### Обязательные поля
- `timestamp` - время в ISO 8601 формате (UTC)
- `level` - уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `service` - имя микросервиса
- `logger` - имя логгера (обычно имя модуля)
- `module` - модуль Python
- `function` - функция, из которой вызван лог
- `line` - номер строки
- `message` - сообщение лога

### Дополнительные поля
- `request_id` - уникальный ID запроса для трейсинга
- `user_id` - ID пользователя (если доступен)
- `method` - HTTP метод
- `path` - путь запроса
- `status_code` - HTTP статус код
- `duration_ms` - длительность выполнения в миллисекундах
- `client_host` - IP адрес клиента
- `error` - текст ошибки (для ERROR логов)
- `exception` - полный traceback (для ERROR логов)

## Уровни логирования

### DEBUG
Детальная информация для отладки. Не используется в production.
```python
logger.debug("Processing user data", extra={"user_id": user.id})
```

### INFO
Общая информация о работе приложения. Стандартный уровень.
```python
logger.info("User logged in successfully", extra={"user_id": user.id})
```

### WARNING
Предупреждения о потенциальных проблемах.
```python
logger.warning("Rate limit approaching", extra={"requests": 90, "limit": 100})
```

### ERROR
Ошибки, которые нужно исправить, но приложение продолжает работать.
```python
logger.error("Failed to send email", extra={"user_id": user.id, "error": str(e)}, exc_info=True)
```

### CRITICAL
Критические ошибки, требующие немедленного внимания.
```python
logger.critical("Database connection lost", exc_info=True)
```

## Использование логирования в коде

### Получение логгера
```python
from app.core.logging_config import get_logger

logger = get_logger(__name__)
```

### Базовое логирование
```python
# Простое сообщение
logger.info("Application started")

# С контекстом
logger.info(
    "User created",
    extra={
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }
)
```

### Логирование ошибок
```python
try:
    result = perform_operation()
except Exception as e:
    logger.error(
        f"Operation failed: {str(e)}",
        extra={
            "operation": "perform_operation",
            "error": str(e)
        },
        exc_info=True  # Добавляет полный traceback
    )
```

### Логирование в middleware
Автоматически добавляется в `main.py`:
```python
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info("Request started", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path
    })
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info("Request completed", extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        })
        
        return response
    except Exception as e:
        logger.error("Request failed", extra={
            "request_id": request_id,
            "error": str(e)
        }, exc_info=True)
        raise
```

## Поиск и фильтрация логов в Grafana

### Открыть Explore
1. Перейдите на http://localhost:3000/explore
2. Выберите источник данных **Loki**

### Базовые запросы LogQL

#### Логи конкретного сервиса
```logql
{service="user-service"}
```

#### Логи по уровню
```logql
{service="user-service", level="ERROR"}
```

#### Логи за последний час
```logql
{service="user-service"} |= "error"
```

#### Поиск по тексту
```logql
{service="user-service"} |= "User created"
```

#### Фильтрация по полю JSON
```logql
{service="user-service"} | json | user_id="550e8400-e29b-41d4-a716-446655440000"
```

#### Логи медленных запросов (> 1s)
```logql
{service="user-service"} | json | duration_ms > 1000
```

#### Статистика по статус-кодам
```logql
sum by (status_code) (count_over_time({service="user-service"} | json [5m]))
```

### Трейсинг запроса по request_id
```logql
{} | json | request_id="abc-123-def-456"
```
Это покажет все логи по всем сервисам для данного запроса.

### Логи с ошибками за последний час
```logql
{level="ERROR"} [1h]
```

### Топ-10 самых частых ошибок
```logql
topk(10, count by (message) (rate({level="ERROR"} [1h])))
```

## Конфигурация уровня логирования

### Через переменные окружения
В `docker-compose.yml` или `.env`:
```yaml
environment:
  LOG_LEVEL: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### В коде (app/core/config.py)
```python
class Settings(BaseSettings):
    LOG_LEVEL: str = "INFO"
```

## Best Practices

### 1. Всегда используйте структурированное логирование
❌ Плохо:
```python
logger.info(f"User {user_id} created order {order_id}")
```

✅ Хорошо:
```python
logger.info("User created order", extra={
    "user_id": user_id,
    "order_id": order_id
})
```

### 2. Добавляйте контекст
```python
logger.info(
    "Payment processed",
    extra={
        "payment_id": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "user_id": user.id,
        "status": payment.status
    }
)
```

### 3. Не логируйте чувствительные данные
❌ Не логировать:
- Пароли
- Токены
- Полные номера карт
- Персональные данные (если не требуется)

### 4. Используйте правильные уровни
- **DEBUG**: Временная отладочная информация
- **INFO**: Нормальные события приложения
- **WARNING**: Необычные ситуации, но не ошибки
- **ERROR**: Ошибки, требующие внимания
- **CRITICAL**: Критические ошибки, требующие немедленного действия

### 5. Логируйте начало и конец важных операций
```python
logger.info("Starting report generation", extra={"report_type": report_type})
try:
    result = generate_report(report_type)
    logger.info("Report generated successfully", extra={
        "report_type": report_type,
        "duration_ms": duration
    })
except Exception as e:
    logger.error("Report generation failed", extra={
        "report_type": report_type,
        "error": str(e)
    }, exc_info=True)
```

### 6. Используйте request_id для трейсинга
Request ID автоматически добавляется middleware и доступен через:
```python
request.state.request_id
```

### 7. Логируйте метрики производительности
```python
start_time = time.time()
result = heavy_operation()
duration_ms = (time.time() - start_time) * 1000

logger.info("Heavy operation completed", extra={
    "operation": "heavy_operation",
    "duration_ms": round(duration_ms, 2),
    "result_size": len(result)
})
```

## Troubleshooting

### Логи не появляются в Loki
1. Проверьте, что Promtail запущен: `docker ps | grep promtail`
2. Проверьте логи Promtail: `docker logs promtail`
3. Убедитесь, что логи в JSON формате: `docker logs user-service`
4. Проверьте подключение Loki в Grafana: Configuration > Data Sources

### Логи не в JSON формате
Убедитесь, что:
1. Модуль `logging_config.py` импортирован в `main.py`
2. Вызван `setup_logging()` при старте приложения
3. Установлена библиотека `python-json-logger`

### Не работает фильтрация в Grafana
1. Используйте `| json` для парсинга JSON логов
2. Убедитесь, что поле существует в логах
3. Проверьте синтаксис LogQL запроса

## Мониторинг логов

### Алерты на основе логов

В Grafana можно настроить алерты на основе логов:

1. **Частые ошибки**:
```logql
count_over_time({level="ERROR"} [5m]) > 10
```

2. **Критические ошибки**:
```logql
count_over_time({level="CRITICAL"} [1m]) > 0
```

3. **Медленные запросы**:
```logql
count_over_time({} | json | duration_ms > 5000 [5m]) > 5
```

## Ротация и хранение

- **Retention**: 7 дней (настройка в `loki-config.yml`)
- **Compression**: gzip (автоматически)
- **Индексация**: по labels (service, level, etc.)

## Дополнительные ресурсы

- [Grafana Loki Documentation](https://grafana.com/docs/loki/latest/)
- [LogQL Tutorial](https://grafana.com/docs/loki/latest/logql/)
- [Python JSON Logger](https://github.com/nhairs/python-json-logger)
- [Best Practices for Logging](https://dev.to/sarthology/10-tips-for-better-logging-in-production-1l53)


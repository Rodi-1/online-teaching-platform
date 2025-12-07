# Мониторинг и метрики

## Обзор

Проект использует комплексную систему мониторинга на базе **Prometheus** и **Grafana** для сбора и визуализации метрик всех микросервисов и PostgreSQL.

## Компоненты системы мониторинга

### 1. Prometheus
**Prometheus** - система сбора и хранения временных рядов метрик.

- **URL**: http://localhost:9090
- **Конфигурация**: `infra/prometheus/prometheus.yml`
- **Интервал сбора**: 15 секунд

#### Цели сбора метрик (targets):
- Все микросервисы (user, homework, gradebook, profile, notifications, tests, schedule, reports)
- PostgreSQL через postgres-exporter
- Сам Prometheus

### 2. Grafana
**Grafana** - платформа визуализации и аналитики метрик.

- **URL**: http://localhost:3000
- **Логин**: `admin`
- **Пароль**: `admin`
- **Источники данных**: Prometheus, Loki

#### Предустановленные дашборды:

**Microservices Overview** - обзор всех микросервисов:
- Request Rate (RPS) - количество запросов в секунду
- Response Time (p50, p95, p99) - время ответа (перцентили)
- Error Rate - процент ошибок
- Active Requests - текущие активные запросы
- HTTP Status Codes Distribution - распределение статус-кодов
- Request Count by Service - общее количество запросов по сервисам
- Average Response Time by Endpoint - среднее время ответа по эндпоинтам

**PostgreSQL Database Monitoring** - мониторинг базы данных:
- Database Connections - количество подключений
- Queries Per Second - количество запросов к БД в секунду
- Cache Hit Ratio - процент попаданий в кэш
- Transaction Rate - количество транзакций (commit/rollback)
- Database Size - размер баз данных
- Tuple Operations - операции с записями (insert, update, delete, fetch)
- Lock Statistics - статистика блокировок
- Deadlocks - количество deadlock'ов
- Checkpoint Statistics - статистика контрольных точек

### 3. PostgreSQL Exporter
Экспортирует метрики PostgreSQL в формат Prometheus.

- **URL**: http://localhost:9187
- **Метрики**: Подключения, запросы, размер БД, кэш, блокировки и т.д.

## Метрики микросервисов

Каждый микросервис предоставляет endpoint `/metrics` в формате Prometheus.

### Автоматические HTTP метрики

Генерируются библиотекой `prometheus-fastapi-instrumentator`:

```promql
# Общее количество HTTP запросов
http_requests_total{service="service-name", method="GET", handler="/api/endpoint", status="200"}

# Длительность HTTP запросов (histogram)
http_request_duration_seconds{service="service-name", method="GET", handler="/api/endpoint"}

# Текущие активные запросы (gauge)
http_requests_in_progress{service="service-name", method="GET", handler="/api/endpoint"}
```

### Кастомные метрики приложения

```promql
# Информация о приложении
app_info{service="service-name", version="1.0.0"}

# Запросы к базе данных
db_queries_total{service="service-name", operation="SELECT", table="users"}

# Длительность запросов к БД (histogram)
db_query_duration_seconds{service="service-name", operation="INSERT", table="homeworks"}

# Активные подключения к БД (gauge)
db_connections_active{service="service-name"}

# Бизнес-операции
business_operations_total{service="service-name", operation="user_registration", status="success"}

# Длительность бизнес-операций (histogram)
business_operation_duration_seconds{service="service-name", operation="generate_report"}
```

## Примеры PromQL запросов

### Количество запросов в секунду по сервисам
```promql
sum(rate(http_requests_total[5m])) by (service)
```

### Среднее время ответа за последние 5 минут
```promql
avg(rate(http_request_duration_seconds_sum[5m])) by (service) / avg(rate(http_request_duration_seconds_count[5m])) by (service)
```

### Процент ошибок (5xx статус-коды)
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service) * 100
```

### 95-й перцентиль времени ответа
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
```

### Топ-5 медленных эндпоинтов
```promql
topk(5, avg(rate(http_request_duration_seconds_sum[5m])) by (service, handler) / avg(rate(http_request_duration_seconds_count[5m])) by (service, handler))
```

### Количество подключений к PostgreSQL
```promql
pg_stat_database_numbackends
```

### Cache Hit Ratio PostgreSQL
```promql
sum(pg_stat_database_blks_hit) / (sum(pg_stat_database_blks_hit) + sum(pg_stat_database_blks_read)) * 100
```

### Запросы к БД в секунду
```promql
rate(pg_stat_database_xact_commit[5m]) + rate(pg_stat_database_xact_rollback[5m])
```

## Использование метрик в коде

### Tracking database queries
```python
from app.core.metrics import track_db_query

# В репозитории или сервисе
with track_db_query("user-service", "SELECT", "users"):
    users = db.query(User).all()
```

### Tracking business operations
```python
from app.core.metrics import track_business_operation

# В бизнес-логике
with track_business_operation("user-service", "user_registration"):
    # Выполнение регистрации пользователя
    user = create_user(data)
    send_welcome_email(user)
```

## Алертинг

### Рекомендуемые алерты

1. **Высокий процент ошибок** (> 5%):
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service) > 0.05
```

2. **Медленные запросы** (p95 > 1s):
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)) > 1
```

3. **Низкий Cache Hit Ratio** (< 90%):
```promql
sum(pg_stat_database_blks_hit) / (sum(pg_stat_database_blks_hit) + sum(pg_stat_database_blks_read)) < 0.90
```

4. **Много подключений к БД** (> 80% от max):
```promql
pg_stat_database_numbackends / pg_settings_max_connections > 0.80
```

## Troubleshooting

### Метрики не собираются
1. Проверьте статус targets в Prometheus: http://localhost:9090/targets
2. Убедитесь, что все сервисы запущены и доступны
3. Проверьте endpoint `/metrics` напрямую: http://localhost:8001/metrics

### Grafana не показывает данные
1. Проверьте подключение к Prometheus: Configuration > Data Sources
2. Убедитесь, что выбран правильный временной диапазон
3. Проверьте, что метрики существуют через Prometheus UI

### PostgreSQL Exporter не работает
1. Проверьте логи контейнера: `docker logs postgres-exporter`
2. Убедитесь, что PostgreSQL доступен
3. Проверьте переменную окружения `DATA_SOURCE_NAME`

## Производительность

Система мониторинга спроектирована с учетом минимального влияния на производительность:

- Метрики собираются асинхронно
- Используется pull-модель (Prometheus сам запрашивает метрики)
- Histogram buckets оптимизированы для типичных времен ответа
- Структурированное логирование не блокирует основной поток

## Best Practices

1. **Всегда логируйте контекст**: используйте `extra={}` для добавления контекстной информации
2. **Используйте метрики для бизнес-событий**: track_business_operation для важных операций
3. **Мониторьте SLI/SLO**: определите и отслеживайте ключевые показатели качества сервиса
4. **Создавайте алерты для критических метрик**: не полагайтесь только на визуализацию
5. **Регулярно проверяйте дашборды**: включите мониторинг в процесс разработки

## Дополнительные ресурсы

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter)


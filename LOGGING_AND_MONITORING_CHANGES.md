# Изменения для внедрения логирования и мониторинга

## Дата создания
7 декабря 2025

## Цели
1. Централизованное структурированное логирование всех микросервисов
2. Мониторинг метрик через Prometheus
3. Визуализация метрик через Grafana
4. Мониторинг PostgreSQL метрик

## Список изменений

### 1. Инфраструктурные компоненты (docker-compose.yml)

#### 1.1 Добавление Prometheus
- Образ: `prom/prometheus:latest`
- Порт: 9090
- Конфигурационный файл: `infra/prometheus/prometheus.yml`
- Сбор метрик со всех микросервисов и PostgreSQL exporter

#### 1.2 Добавление Grafana
- Образ: `grafana/grafana:latest`
- Порт: 3000
- Настройка источников данных (Prometheus, Loki)
- Предустановленные дашборды для микросервисов и PostgreSQL
- Конфигурационные файлы:
  - `infra/grafana/datasources.yml`
  - `infra/grafana/dashboards.yml`
  - `infra/grafana/dashboard-services.json`
  - `infra/grafana/dashboard-postgres.json`

#### 1.3 Добавление Loki (централизованное хранение логов)
- Образ: `grafana/loki:latest`
- Порт: 3100
- Конфигурационный файл: `infra/loki/loki-config.yml`
- Хранение структурированных логов

#### 1.4 Добавление Promtail (сборщик логов)
- Образ: `grafana/promtail:latest`
- Конфигурационный файл: `infra/promtail/promtail-config.yml`
- Сбор логов из Docker контейнеров
- Отправка логов в Loki

#### 1.5 Добавление PostgreSQL Exporter
- Образ: `prometheuscommunity/postgres-exporter:latest`
- Порт: 9187
- Экспорт метрик PostgreSQL в формате Prometheus

### 2. Изменения в микросервисах

#### 2.1 Обновление requirements.txt (для всех сервисов)
Добавление библиотек:
- `prometheus-client==0.21.0` - клиент Prometheus для метрик
- `python-json-logger==2.0.7` - структурированное JSON логирование
- `prometheus-fastapi-instrumentator==7.0.0` - автоматическая инструментация FastAPI

#### 2.2 Создание модуля логирования
Файл: `app/core/logging.py` (для каждого сервиса)
- Настройка структурированного JSON логирования
- Интеграция с python-json-logger
- Контекстная информация (service_name, request_id, user_id)
- Уровни логирования из переменных окружения

#### 2.3 Создание модуля метрик
Файл: `app/core/metrics.py` (для каждого сервиса)
- Настройка Prometheus метрик
- Кастомные метрики:
  - `http_requests_total` - счетчик HTTP запросов
  - `http_request_duration_seconds` - длительность запросов (histogram)
  - `http_requests_in_progress` - запросы в процессе (gauge)
  - `database_queries_total` - счетчик запросов к БД
  - `database_query_duration_seconds` - длительность запросов к БД

#### 2.4 Обновление main.py (для каждого сервиса)
- Инициализация логгера
- Добавление middleware для логирования запросов
- Интеграция prometheus-fastapi-instrumentator
- Endpoint `/metrics` для Prometheus

#### 2.5 Обновление роутеров
- Добавление логирования в критических точках
- Логирование ошибок с контекстом
- Использование structured logging

### 3. Конфигурационные файлы

#### 3.1 infra/prometheus/prometheus.yml
- Конфигурация scrape_configs для всех сервисов
- Интервал сбора метрик: 15s
- Targets:
  - user-service:8000
  - homework-service:8000
  - gradebook-service:8000
  - profile-service:8000
  - notifications-service:8000
  - tests-service:8000
  - schedule-service:8000
  - reports-service:8000
  - postgres-exporter:9187

#### 3.2 infra/loki/loki-config.yml
- Настройка хранения логов
- Retention: 168h (7 дней)
- Compression: gzip

#### 3.3 infra/promtail/promtail-config.yml
- Сбор логов из Docker
- Парсинг JSON логов
- Добавление labels (service, container_name)

#### 3.4 infra/grafana/datasources.yml
- Prometheus как источник данных
- Loki как источник данных для логов

#### 3.5 infra/grafana/dashboards.yml
- Автоматическая загрузка дашбордов

#### 3.6 Grafana дашборды
- **dashboard-services.json**: Мониторинг микросервисов
  - Request rate (RPS)
  - Response time (p50, p95, p99)
  - Error rate
  - Active requests
  - Database queries metrics
  
- **dashboard-postgres.json**: Мониторинг PostgreSQL
  - Connections
  - Queries per second
  - Cache hit ratio
  - Transaction rate
  - Database size
  - Lock statistics

### 4. Изменения по сервисам

#### Все сервисы получат:
1. `app/core/logging.py` - модуль логирования
2. `app/core/metrics.py` - модуль метрик
3. Обновленный `app/main.py` - с интеграцией логирования и метрик
4. Обновленный `requirements.txt` - с новыми зависимостями

#### Список сервисов для обновления:
- user-service
- homework-service
- gradebook-service
- profile-service
- notifications-service
- tests-service
- schedule-service
- reports-service

### 5. Документация

#### 5.1 MONITORING.md
- Описание системы мониторинга
- Доступ к Grafana, Prometheus, Loki
- Описание метрик
- Примеры запросов PromQL
- Руководство по дашбордам

#### 5.2 LOGGING.md
- Описание структуры логов
- Уровни логирования
- Поиск и фильтрация логов в Grafana
- Best practices для логирования

#### 5.3 Обновление README.md
- Добавление информации о мониторинге
- Порты новых сервисов
- Ссылки на новую документацию

## Технические детали

### Формат JSON логов
```json
{
  "timestamp": "2025-12-07T10:30:00.123456Z",
  "level": "INFO",
  "service": "user-service",
  "message": "User logged in successfully",
  "request_id": "abc-123-def",
  "user_id": "user-uuid",
  "method": "POST",
  "path": "/api/v1/auth/login",
  "status_code": 200,
  "duration_ms": 45.2
}
```

### Метрики Prometheus

#### HTTP метрики (автоматические через instrumentator):
- `http_requests_total{method, handler, status}`
- `http_request_duration_seconds{method, handler}`
- `http_requests_in_progress{method, handler}`

#### Кастомные метрики приложения:
- `app_info{service, version}` - информация о сервисе
- `db_queries_total{service, operation}` - запросы к БД
- `db_query_duration_seconds{service, operation}` - длительность запросов к БД

### Доступ к сервисам после развертывания

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Loki**: http://localhost:3100 (internal)

## Преимущества

1. **Централизованное логирование**:
   - Все логи в одном месте (Loki)
   - Структурированный формат (JSON)
   - Быстрый поиск и фильтрация в Grafana

2. **Мониторинг в реальном времени**:
   - Метрики всех сервисов
   - Мониторинг производительности БД
   - Алертинг при возникновении проблем

3. **Удобная визуализация**:
   - Готовые дашборды в Grafana
   - Корреляция метрик и логов
   - Исторические данные

4. **Production-ready**:
   - Минимальное влияние на производительность
   - Асинхронная отправка метрик
   - Отказоустойчивость

## Порядок внедрения

1. Создание инфраструктурных конфигурационных файлов
2. Обновление docker-compose.yml
3. Создание модулей логирования и метрик
4. Обновление всех микросервисов
5. Создание Grafana дашбордов
6. Создание документации
7. Тестирование системы мониторинга

## Проверка работоспособности

После развертывания:
1. Проверить доступность Grafana (http://localhost:3000)
2. Проверить Prometheus targets (http://localhost:9090/targets)
3. Проверить поступление логов в Loki через Grafana
4. Проверить метрики на дашбордах
5. Сгенерировать тестовую нагрузку и проверить отображение метрик


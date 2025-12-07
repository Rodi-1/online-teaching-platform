# Команды для проверки мониторинга и логирования

## 1. Запуск системы

```bash
# Остановить старые контейнеры
docker compose down

# Собрать и запустить все сервисы
docker compose up -d --build

# Проверить статус всех контейнеров
docker compose ps
```

## 2. Проверка компонентов мониторинга

### Prometheus
```bash
# Открыть в браузере
start http://localhost:9090

# Проверить targets
start http://localhost:9090/targets

# Все должны быть UP (зеленые)
```

### Grafana
```bash
# Открыть в браузере
start http://localhost:3000

# Логин: admin
# Пароль: admin

# После входа:
# 1. Перейти в Dashboards > Browse
# 2. Открыть "Microservices Overview"
# 3. Открыть "PostgreSQL Database Monitoring"
```

### Loki (через Grafana)
```bash
# 1. В Grafana нажать на иконку компаса (Explore)
# 2. Выбрать источник данных: Loki
# 3. Ввести запрос: {service="user-service"}
# 4. Нажать Run Query
```

## 3. Проверка метрик сервисов

```bash
# Проверить метрики user-service
curl http://localhost:8001/metrics

# Проверить метрики homework-service
curl http://localhost:8002/metrics

# Проверить метрики gradebook-service
curl http://localhost:8003/metrics

# Проверить метрики profile-service
curl http://localhost:8004/metrics

# Проверить метрики notifications-service
curl http://localhost:8005/metrics

# Проверить метрики tests-service
curl http://localhost:8006/metrics

# Проверить метрики schedule-service
curl http://localhost:8007/metrics

# Проверить метрики reports-service
curl http://localhost:8008/metrics

# Проверить метрики PostgreSQL
curl http://localhost:9187/metrics
```

## 4. Проверка JSON логов

```bash
# Просмотр логов user-service (должны быть в JSON формате)
docker logs user-service --tail 10

# Просмотр логов в реальном времени
docker logs user-service -f

# Проверить, что логи в JSON формате
docker logs user-service 2>&1 | grep -o '{.*}' | head -1 | python -m json.tool
```

## 5. Генерация тестовых запросов

```bash
# Health check - генерирует метрики
curl http://localhost:8001/health

# Получить информацию о сервисе
curl http://localhost:8001/

# Попытка входа (будет ошибка, но сгенерирует логи и метрики)
curl -X POST http://localhost:8001/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"test\"}"

# Создание пользователя (если нужно сгенерировать успешный запрос)
curl -X POST http://localhost:8001/api/users ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"newuser@example.com\",\"password\":\"Test123!\",\"first_name\":\"Test\",\"last_name\":\"User\",\"role\":\"student\"}"
```

## 6. Примеры PromQL запросов (в Prometheus)

```promql
# Количество запросов в секунду
sum(rate(http_requests_total[5m])) by (service)

# Среднее время ответа
avg(rate(http_request_duration_seconds_sum[5m])) by (service) / avg(rate(http_request_duration_seconds_count[5m])) by (service)

# Процент ошибок
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service) * 100

# 95-й перцентиль времени ответа
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))

# Количество подключений к PostgreSQL
pg_stat_database_numbackends
```

## 7. Примеры LogQL запросов (в Grafana Explore)

```logql
# Все логи user-service
{service="user-service"}

# Только ошибки
{level="ERROR"}

# Логи с фильтрацией по методу
{service="user-service"} | json | method="POST"

# Медленные запросы (> 1 секунда)
{} | json | duration_ms > 1000

# Поиск по тексту
{service="user-service"} |= "User created"

# Подсчет ошибок за последние 5 минут
count_over_time({level="ERROR"}[5m])

# Топ сервисов по количеству логов
topk(5, sum by (service) (count_over_time({}[5m])))
```

## 8. Проверка работы алертов и дашбордов

### В Grafana:

```bash
# 1. Открыть Microservices Overview dashboard
# 2. Убедиться, что есть данные на графиках
# 3. Проверить временной диапазон (Last 15 minutes)
# 4. Сделать несколько запросов к API
# 5. Подождать 15-30 секунд
# 6. Обновить дашборд и увидеть новые метрики
```

## 9. Troubleshooting команды

```bash
# Проверить логи компонентов мониторинга
docker logs prometheus --tail 20
docker logs grafana --tail 20
docker logs loki --tail 20
docker logs promtail --tail 20
docker logs postgres-exporter --tail 20

# Проверить использование ресурсов
docker stats

# Проверить сеть
docker network ls
docker network inspect online-teaching-platform_app-network

# Перезапустить конкретный сервис
docker-compose restart user-service

# Перезапустить все сервисы мониторинга
docker-compose restart prometheus grafana loki promtail postgres-exporter

# Полная пересборка
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 10. Очистка и переустановка

```bash
# Остановить и удалить все контейнеры и volumes
docker compose down -v

# Удалить все образы проекта
docker compose down --rmi all -v

# Очистить Docker систему (осторожно!)
docker system prune -a --volumes

# Пересоздать все с нуля
docker compose up -d --build --force-recreate
```

## 11. Проверка конфигурации

```bash
# Проверить docker-compose.yml на ошибки
docker compose config

# Проверить Prometheus конфигурацию
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Проверить подключение к PostgreSQL
docker exec postgres-exporter sh -c 'echo "SELECT 1" | psql $DATA_SOURCE_NAME'
```

## 12. Экспорт данных

```bash
# Экспорт snapshot из Prometheus
curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Экспорт дашборда из Grafana (требуется API key)
# Сначала создайте API key в Grafana (Configuration > API Keys)
# Затем:
curl -H "Authorization: Bearer YOUR_API_KEY" ^
  http://localhost:3000/api/dashboards/uid/DASHBOARD_UID
```

## 13. Быстрая проверка всей системы

```powershell
# PowerShell скрипт для проверки всех компонентов

Write-Host "=== Проверка компонентов мониторинга ===" -ForegroundColor Green

# Prometheus
try {
    $prometheus = Invoke-RestMethod -Uri "http://localhost:9090/-/healthy" -TimeoutSec 5
    Write-Host "✅ Prometheus: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Prometheus: FAIL" -ForegroundColor Red
}

# Grafana
try {
    $grafana = Invoke-RestMethod -Uri "http://localhost:3000/api/health" -TimeoutSec 5
    Write-Host "✅ Grafana: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Grafana: FAIL" -ForegroundColor Red
}

# Микросервисы
$services = @(
    @{name="user-service"; port=8001},
    @{name="homework-service"; port=8002},
    @{name="gradebook-service"; port=8003},
    @{name="profile-service"; port=8004},
    @{name="notifications-service"; port=8005},
    @{name="tests-service"; port=8006},
    @{name="schedule-service"; port=8007},
    @{name="reports-service"; port=8008}
)

foreach ($service in $services) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:$($service.port)/health" -TimeoutSec 5
        Write-Host "✅ $($service.name): OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($service.name): FAIL" -ForegroundColor Red
    }
}

Write-Host "`n=== Проверка завершена ===" -ForegroundColor Green
```

Сохраните это как `check_monitoring.ps1` и запустите:
```powershell
.\check_monitoring.ps1
```

## Полезные ссылки

- **Prometheus UI**: http://localhost:9090
- **Prometheus Targets**: http://localhost:9090/targets
- **Grafana**: http://localhost:3000 (admin/admin)
- **User Service**: http://localhost:8001/docs
- **Homework Service**: http://localhost:8002/docs

## Ожидаемые результаты

✅ Все Docker контейнеры запущены (17 контейнеров)
✅ Все Prometheus targets в статусе UP
✅ Grafana показывает два дашборда с данными
✅ Loki получает и индексирует логи
✅ Логи в JSON формате
✅ Endpoint /metrics доступен на всех сервисах
✅ PostgreSQL метрики собираются

Если что-то не работает, смотрите раздел Troubleshooting в документации.


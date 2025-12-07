# 🔧 Исправление: Самоинструментация endpoint `/metrics`

## Проблема

После предыдущего исправления параметр `excluded_handlers` был изменён с `["/metrics", "/health", "/"]` на `[]`, что привело к **самоинструментации** endpoint `/metrics`.

### Что происходило:

```python
Instrumentator(
    # ...
    excluded_handlers=[],  # ❌ Пусто - инструментируются ВСЕ запросы
    # ...
)
```

**Негативные эффекты:**
1. ❌ **Рекурсивный сбор метрик**: Prometheus запрашивает `/metrics` → это записывается как запрос → увеличивает `http_requests_total`
2. ❌ **Завышенные счётчики**: Каждые 15 секунд Prometheus делает 8 запросов к `/metrics` (по одному на каждый сервис)
3. ❌ **Бесполезные данные**: Метрики о запросах к `/metrics` не несут ценной информации
4. ❌ **Overhead**: Дополнительная обработка для служебных запросов

### Пример завышенных метрик:

```promql
# До исправления:
http_requests_total{handler="/metrics", method="GET"} = 240  # За 1 час (каждые 15 сек)
http_requests_total{handler="/health", method="GET"} = 20    # Реальные health checks

# После исправления:
http_requests_total{handler="/metrics"} = <не существует>    # Исключён
http_requests_total{handler="/health", method="GET"} = 20    # Без изменений
```

## ✅ Решение

Вернули `/metrics` в `excluded_handlers`:

```python
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=False,
    should_respect_env_var=False,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],  # ✅ Exclude metrics endpoint to prevent self-instrumentation
    inprogress_name="http_requests_in_progress",
    inprogress_labels=True
).instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")
```

### Почему только `/metrics`?

| Endpoint | Исключён? | Причина |
|----------|-----------|---------|
| `/metrics` | ✅ Да | Служебный endpoint Prometheus - не должен инструментироваться |
| `/health` | ❌ Нет | **Полезно мониторить** - показывает работу health check систем |
| `/` | ❌ Нет | Root endpoint - может содержать полезную информацию |

## 📊 Результаты

### До исправления:
```bash
$ curl http://localhost:8001/metrics | grep 'http_requests_total{handler="/metrics"'
http_requests_total{handler="/metrics",method="GET",status="200"} 48.0
```
❌ Самоинструментация активна

### После исправления:
```bash
$ curl http://localhost:8001/metrics | grep 'http_requests_total{handler="/metrics"'
# (пусто - метрика отсутствует)
```
✅ Самоинструментация устранена

### Health checks продолжают мониториться:
```bash
$ curl http://localhost:8001/metrics | grep 'http_requests_total{handler="/health"'
http_requests_total{handler="/health",method="GET",status="200"} 20.0
```
✅ Полезные метрики собираются

## 🎯 Best Practice

**Общее правило:** Служебные endpoints для мониторинга систем **не должны** генерировать метрики о самих себе.

**Типичные исключения:**
- `/metrics` - endpoint Prometheus
- `/actuator/prometheus` - Spring Boot
- `/__health` - некоторые фреймворки
- `/debug/vars` - Go expvar

**Что стоит мониторить:**
- `/health` - проверки здоровья приложения
- `/ready` - готовность к приёму трафика
- `/api/*` - все бизнес-endpoints
- `/` - главная страница

## 📝 Исправленные файлы

✅ `services/user-service/app/core/metrics.py`  
✅ `services/homework-service/app/core/metrics.py`  
✅ `services/gradebook-service/app/core/metrics.py`  
✅ `services/profile-service/app/core/metrics.py`  
✅ `services/notifications-service/app/core/metrics.py`  
✅ `services/tests-service/app/core/metrics.py`  
✅ `services/schedule-service/app/core/metrics.py`  
✅ `services/reports-service/app/core/metrics.py`  

## 🔍 Проверка

```powershell
# Перезапустить контейнеры
docker compose up -d --build

# Подождать 10 секунд и сгенерировать трафик
Start-Sleep -Seconds 10
.\test_traffic.ps1

# Проверить что /metrics не инструментируется
@(8001..8008) | ForEach-Object {
    $port = $_
    $hasMetricsMetric = (curl "http://localhost:$port/metrics" -UseBasicParsing).Content -match 'http_requests_total.*handler="/metrics"'
    if ($hasMetricsMetric) {
        Write-Host "Port $port : ❌ STILL HAS /metrics self-instrumentation" -ForegroundColor Red
    } else {
        Write-Host "Port $port : ✅ No /metrics self-instrumentation" -ForegroundColor Green
    }
}

# Проверить что /health мониторится
$healthMetric = (curl "http://localhost:8001/metrics" -UseBasicParsing).Content -match 'http_requests_total.*handler="/health"'
if ($healthMetric) {
    Write-Host "✅ /health endpoint is being monitored" -ForegroundColor Green
} else {
    Write-Host "❌ /health endpoint NOT monitored (unexpected)" -ForegroundColor Red
}
```

**Ожидаемый результат:**
- ✅ 8 сервисов без `/metrics` самоинструментации
- ✅ `/health` метрики присутствуют

## 💡 Takeaway

**Проблема:** В погоне за полным мониторингом можно случайно включить самоинструментацию служебных endpoints.

**Решение:** Всегда исключайте endpoint метрик из инструментации:
```python
excluded_handlers=["/metrics"]
```

**Дополнительно:** Рассмотрите исключение других служебных endpoints, если они создают шум в метриках.

---

**Дата:** 2025-12-07  
**Тип:** Bug fix / Best practice  
**Приоритет:** Средний (не критично, но влияет на точность метрик)  
**Риск:** Минимальный (только меняет что именно мониторится)


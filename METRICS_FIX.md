# 🐛 Проблема с метриками - РЕШЕНО ✅

## Что было не так?

### Проблема:
Prometheus не мог получить метрики от микросервисов - все targets показывали:
```
Error scraping target: server returned HTTP status 404 Not Found
```

## 🔍 Причина

**Короткий ответ:** Endpoint `/metrics` не был зарегистрирован в FastAPI приложении.

**Подробно:**

1. **Первоначальная попытка (не сработало):**
   - Использовали `instrumentator.expose(app, endpoint="/metrics")`
   - Но добавляли его в `metrics.py` внутри функции `setup_metrics()`
   - FastAPI не видел этот endpoint как зарегистрированный route

2. **Конфликт с `excluded_handlers`:**
   - В Instrumentator был параметр: `excluded_handlers=["/metrics", "/health", "/"]`
   - Это исключало `/metrics` из инструментации
   - Но это не было основной проблемой

3. **Реальная проблема:**
   - `.expose()` метод не создавал route правильно в контексте FastAPI
   - Нужно было явно добавить `@app.get("/metrics")` декоратор

## ✅ Решение

Добавили ручную регистрацию `/metrics` endpoint в `metrics.py`:

```python
from fastapi import Response
from prometheus_client import REGISTRY, generate_latest

def setup_metrics(app, service_name: str, service_version: str):
    # ... настройка instrumentator ...
    
    # Добавить /metrics endpoint вручную
    @app.get("/metrics", include_in_schema=False)
    def metrics_endpoint():
        """Prometheus metrics endpoint"""
        return Response(content=generate_latest(REGISTRY), media_type="text/plain")
    
    return instrumentator
```

**Почему это работает:**
- `@app.get("/metrics")` явно регистрирует route в FastAPI
- `generate_latest(REGISTRY)` возвращает все метрики в формате Prometheus
- `Response(..., media_type="text/plain")` отдаёт метрики как plain text

## 📊 Результат

✅ Все 8 микросервисов теперь отдают метрики:
- http://localhost:8001/metrics (user-service)
- http://localhost:8002/metrics (homework-service)
- http://localhost:8003/metrics (gradebook-service)
- http://localhost:8004/metrics (profile-service)
- http://localhost:8005/metrics (notifications-service)
- http://localhost:8006/metrics (tests-service)
- http://localhost:8007/metrics (schedule-service)
- http://localhost:8008/metrics (reports-service)

## 🔧 Что изменили

**Файлы:**
1. `services/*/app/core/metrics.py` - добавлен ручной endpoint `/metrics`
2. Убрали `/metrics` из `excluded_handlers`
3. Убрали дублирующиеся вызовы `.expose()` из `main.py`

## 📈 Проверка

```powershell
# Проверить все сервисы
@(8001..8008) | ForEach-Object {
    curl "http://localhost:$_/metrics" | Select-String "http_requests_total"
}

# Проверить Prometheus targets
start http://localhost:9090/targets

# Должны быть все "UP" ✅
```

## 💡 Урок

**Prometheus FastAPI Instrumentator** не всегда корректно регистрирует `/metrics` endpoint через `.expose()`.

**Лучшая практика:**
- Явно регистрировать `/metrics` как FastAPI route
- Использовать `prometheus_client.generate_latest(REGISTRY)`
- Это даёт полный контроль над endpoint'ом

## 🎯 Следующие шаги

1. Откройте Prometheus: http://localhost:9090/targets
   - Все targets должны быть "UP" ✅

2. Проверьте метрики:
   ```promql
   http_requests_total
   ```

3. Создайте дашборды в Grafana:
   - http://localhost:3000

4. Наслаждайтесь! 🎉

---

**Время решения:** ~1 час  
**Попыток до решения:** 5  
**Главный инсайт:** Иногда простое ручное решение лучше, чем полагаться на "магию" библиотеки.


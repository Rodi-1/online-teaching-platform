# 📊 Мониторинг и Логирование - Быстрая Шпаргалка

## 🎯 Кто за что отвечает

### **ЛОГИ** 📝
```
Микросервисы → Promtail → Loki → Grafana
```
- **Promtail** - собирает логи из Docker контейнеров
- **Loki** - хранит логи (http://localhost:3100)
- **Grafana** - показывает логи

### **МЕТРИКИ** 📈
```
Микросервисы → Prometheus → Grafana
PostgreSQL → postgres-exporter → Prometheus
```
- **Prometheus** - собирает метрики (http://localhost:9090)
- **postgres-exporter** - метрики PostgreSQL
- **Grafana** - показывает метрики

---

## ✅ Проверка работоспособности

```powershell
# Запустите скрипт проверки
.\check_monitoring.ps1
```

### Результат вашей проверки:
- ✅ Все 8 микросервисов отвечают
- ✅ Prometheus работает (2/10 targets активны)
- ✅ Loki собирает логи от 14 сервисов!
- ✅ Grafana работает
- ✅ postgres-exporter работает

---

## 🚀 3 шага к готовым дашбордам

### Шаг 1: Откройте Grafana
```
http://localhost:3000
Логин: admin
Пароль: admin
```

### Шаг 2: Добавьте Data Sources

**A. Prometheus (метрики):**
1. Menu → Connections → Data Sources → Add data source
2. Выберите **Prometheus**
3. URL: `http://prometheus:9090`
4. Save & Test

**B. Loki (логи):**
1. Add data source → **Loki**
2. URL: `http://loki:3100`
3. Save & Test

### Шаг 3: Импортируйте готовые дашборды

**Вариант А: Мой готовый дашборд**
1. Dashboards → New → Import
2. Upload file: `grafana-dashboard-metrics.json`
3. Import

**Вариант Б: Из Grafana.com**
1. Dashboards → New → Import
2. Введите ID: **11133** (FastAPI Dashboard)
3. Select Prometheus data source
4. Import

Повторите для:
- **13639** - Loki Dashboard (для логов)
- **9628** - PostgreSQL Dashboard

---

## 🔍 Быстрая проверка данных

### Prometheus (метрики)
Откройте: http://localhost:9090/graph

Попробуйте запросы:
```promql
# Запросы в секунду по сервисам
sum(rate(http_requests_total[5m])) by (service)

# Время ответа p95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Активные подключения к БД
sum(pg_stat_database_numbackends)
```

### Loki (логи)
Grafana → Explore (иконка компаса) → Data source: Loki

```logql
# Все логи от микросервисов
{container_name=~".*-service"}

# Только ошибки
{container_name=~".*-service"} |= "ERROR"

# Медленные запросы (>1 сек)
{container_name=~".*-service"} | json | duration_ms > 1000
```

---

## 📈 Полезные метрики

### Для дашбордов создайте панели:

**1. HTTP Requests/sec**
```promql
sum(rate(http_requests_total[5m])) by (service)
```

**2. Response Time (95th percentile)**
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
```

**3. Error Rate %**
```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

**4. Database Connections**
```promql
sum(pg_stat_database_numbackends)
```

**5. Top 5 Slowest Endpoints**
```promql
topk(5, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))
```

---

## 🎨 Рекомендуемые дашборды из коробки

| ID | Название | Для чего |
|----|----------|----------|
| 11133 | FastAPI Dashboard | Метрики всех микросервисов |
| 13639 | Loki Dashboard | Просмотр логов |
| 9628 | PostgreSQL | Метрики БД |

Импорт: Dashboards → Import → введите ID → Import

---

## 🆘 Troubleshooting

### "No data" в панелях Grafana

**Проверьте targets в Prometheus:**
```
http://localhost:9090/targets
```
Все должны быть "UP"

**Проверьте что сервис отдаёт метрики:**
```powershell
curl http://localhost:8001/health
curl http://localhost:9187/metrics  # postgres-exporter
```

### Data source "cannot connect"

В Grafana используйте **имена контейнеров**, а не localhost:
- ✅ `http://prometheus:9090`
- ✅ `http://loki:3100`
- ❌ ~~http://localhost:9090~~

---

## 📊 Что видно в логах (Loki)

У вас уже собираются логи от:
- ✅ user-service
- ✅ homework-service
- ✅ gradebook-service
- ✅ profile-service
- ✅ notifications-service
- ✅ tests-service
- ✅ schedule-service
- ✅ reports-service
- ✅ postgres
- ✅ prometheus, grafana, loki, promtail

Все логи в JSON формате с полями:
- `timestamp` - время
- `level` - INFO/ERROR/WARNING
- `message` - текст
- `service` - название сервиса
- `request_id` - ID запроса (для трейсинга)
- `duration_ms` - время выполнения

---

## 🎯 Следующие действия

1. ✅ Откройте Grafana: http://localhost:3000
2. ✅ Добавьте Prometheus и Loki data sources
3. ✅ Импортируйте дашборды (11133, 13639, 9628)
4. ✅ Посмотрите на метрики и логи
5. ✅ Создайте свой custom dashboard

**Полезные ссылки:**
- [Grafana Dashboards Library](https://grafana.com/grafana/dashboards/)
- [Prometheus Query Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [LogQL Cheat Sheet](https://megamorf.gitlab.io/cheat-sheets/loki/)

---

## 💡 Бонус: Алерты

В Grafana можно настроить уведомления:

1. **Alerting** → **Alert rules** → **New alert rule**
2. Пример условия: `Error rate > 5%`
3. Уведомления: email, Slack, Telegram, etc.

**Примеры алертов:**
- Error rate > 5% за последние 5 минут
- Response time p95 > 1 секунда
- Database connections > 80% от лимита
- Сервис не отвечает (down > 1 минута)


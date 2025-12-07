# 📊 Grafana Setup Guide - Настройка визуализации

## 🎯 Что у вас есть

### **Логи (Logs)**
- **Promtail** → собирает логи из контейнеров
- **Loki** → хранит логи (http://localhost:3100)
- **Grafana** → показывает логи (http://localhost:3000)

### **Метрики (Metrics)**
- **Prometheus** → собирает метрики (http://localhost:9090)
- **postgres-exporter** → метрики PostgreSQL
- **FastAPI** → метрики каждого микросервиса
- **Grafana** → показывает метрики

---

## 🚀 Быстрая проверка (5 минут)

### Шаг 1: Проверка что всё работает

```powershell
# Запустите скрипт проверки
.\check_monitoring.ps1
```

### Шаг 2: Проверка Prometheus вручную

Откройте браузер: http://localhost:9090

Попробуйте запросы:
```promql
# Количество запросов к микросервисам
http_requests_total

# Использование памяти PostgreSQL
pg_stat_database_tup_fetched
```

### Шаг 3: Проверка Loki вручную

Откройте: http://localhost:3100/metrics

Должны быть метрики типа `loki_ingester_chunks_created_total`

---

## 🎨 Настройка Grafana (10 минут)

### 1️⃣ Первый вход в Grafana

1. Откройте: http://localhost:3000
2. Логин: `admin`
3. Пароль: `admin`
4. При первом входе попросит сменить пароль (можно пропустить)

---

### 2️⃣ Добавление Data Sources

#### **A. Добавить Prometheus (для метрик)**

1. **Меню** → **Connections** → **Data Sources** → **Add data source**
2. Выберите **Prometheus**
3. Настройки:
   ```
   Name: Prometheus
   URL: http://prometheus:9090
   ```
4. Нажмите **Save & Test** (должна быть зелёная галочка)

#### **B. Добавить Loki (для логов)**

1. **Add data source** → **Loki**
2. Настройки:
   ```
   Name: Loki
   URL: http://loki:3100
   ```
3. Нажмите **Save & Test**

---

### 3️⃣ Создание первого Dashboard для метрик

#### **Способ 1: Автоматический (рекомендуется)**

Я создам готовый JSON dashboard. Выполните:

```powershell
# Будет создан файл grafana-dashboard-metrics.json
# Его можно импортировать в Grafana
```

Затем в Grafana:
1. **Dashboards** → **New** → **Import**
2. Нажмите **Upload JSON file**
3. Выберите файл `grafana-dashboard-metrics.json`
4. Нажмите **Import**

#### **Способ 2: Вручную**

1. **Dashboards** → **New Dashboard** → **Add visualization**
2. Выберите **Data source: Prometheus**
3. В поле **Metric** введите запрос:

**Панель 1: HTTP Requests per Second**
```promql
rate(http_requests_total[5m])
```

**Панель 2: Response Time (95th percentile)**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Панель 3: Active Database Connections**
```promql
sum(pg_stat_database_numbackends)
```

**Панель 4: Request Rate by Service**
```promql
sum(rate(http_requests_total[5m])) by (service)
```

4. Нажмите **Apply** для каждой панели
5. Нажмите **Save dashboard** (иконка дискеты)

---

### 4️⃣ Создание Dashboard для логов

1. **Dashboards** → **New Dashboard** → **Add visualization**
2. Выберите **Data source: Loki**
3. В **Query** введите:

**Запрос 1: Все логи от user-service**
```logql
{container_name="user-service"}
```

**Запрос 2: Только ошибки**
```logql
{container_name=~".*-service"} |= "ERROR"
```

**Запрос 3: Логи с высокой задержкой (>1 секунда)**
```logql
{container_name=~".*-service"} | json | duration_ms > 1000
```

**Запрос 4: Количество ошибок в минуту**
```logql
sum(count_over_time({container_name=~".*-service"} |= "ERROR" [1m]))
```

4. Выберите визуализацию:
   - **Logs** - для просмотра логов
   - **Time series** - для графиков по времени
   - **Stat** - для числовых показателей

---

## 📈 Полезные запросы

### **Prometheus (Метрики)**

```promql
# CPU Usage (если настроен node-exporter)
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# HTTP Error Rate
sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# PostgreSQL Query Duration
rate(pg_stat_statements_mean_time_seconds[5m])

# Top 5 Slowest Endpoints
topk(5, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))
```

### **Loki (Логи)**

```logql
# Все логи от микросервисов
{container_name=~".*-service"}

# Логи с уровнем ERROR или WARNING
{container_name=~".*-service"} |~ "ERROR|WARNING"

# Логи с конкретным request_id
{container_name=~".*-service"} | json | request_id="ваш-request-id"

# Топ 10 самых медленных запросов
topk(10, avg_over_time({container_name=~".*-service"} | json | unwrap duration_ms [5m]))

# Количество логов по сервисам
sum(count_over_time({container_name=~".*-service"}[5m])) by (container_name)

# Запросы к конкретному endpoint
{container_name=~".*-service"} | json | path="/api/users"
```

---

## 🎨 Готовые Dashboard Templates

### **Option 1: FastAPI Dashboard**

Импортируйте готовый dashboard:
1. **Dashboards** → **Import**
2. **Import via grafana.com**: введите ID **11133**
3. Выберите **Data source: Prometheus**
4. Нажмите **Import**

### **Option 2: Loki Dashboard**

1. **Dashboards** → **Import**
2. ID: **13639** (Loki Dashboard)
3. Data source: **Loki**
4. Import

### **Option 3: PostgreSQL Dashboard**

1. **Dashboards** → **Import**
2. ID: **9628** (PostgreSQL Database)
3. Data source: **Prometheus**
4. Import

---

## 🔍 Проверка что данные собираются

### **Проверка метрик в Prometheus:**

```bash
# Откройте http://localhost:9090/targets
# Все targets должны быть в состоянии "UP"
```

Если видите метрики типа:
- `http_requests_total` - FastAPI работает ✅
- `pg_stat_database_*` - PostgreSQL exporter работает ✅

### **Проверка логов в Loki:**

Откройте Grafana → **Explore** (иконка компаса) → выберите **Loki**

Запрос:
```logql
{container_name=~".*"}
```

Должны видеть логи от контейнеров ✅

---

## 🚨 Если что-то не работает

### Проблема: "No data" в Grafana

**Для метрик:**
```powershell
# Проверьте что Prometheus видит сервисы
curl http://localhost:9090/api/v1/targets

# Проверьте метрики микросервиса
curl http://localhost:8001/health
```

**Для логов:**
```powershell
# Проверьте что Loki работает
curl http://localhost:3100/ready

# Проверьте что Promtail отправляет логи
docker logs promtail --tail 20
```

### Проблема: "Cannot connect to data source"

В Grafana data sources используйте **имена контейнеров** а не localhost:
- ✅ `http://prometheus:9090`
- ✅ `http://loki:3100`
- ❌ ~~`http://localhost:9090`~~

---

## 📊 Рекомендуемая структура dashboards

### Dashboard 1: **System Overview** (общее)
- Total requests/sec по всем сервисам
- Error rate
- Response time (p95, p99)
- Active database connections

### Dashboard 2: **Service Detail** (по каждому сервису)
- Requests per endpoint
- Response time per endpoint
- Error logs in real-time
- Request/Response samples

### Dashboard 3: **Database Performance**
- Query count
- Slow queries
- Connection pool usage
- Database size

### Dashboard 4: **Logs Explorer**
- Live tail всех логов
- Error/Warning filter
- Search by request_id

---

## 💡 Tips

1. **Используйте Variables** в dashboards для переключения между сервисами
2. **Настройте Alerts** для критичных метрик (error rate > 5%)
3. **Используйте Time Range** в правом верхнем углу
4. **Делайте snapshots** важных dashboard'ов
5. **Включите Auto-refresh** для live monitoring

---

## 🎯 Следующие шаги

1. ✅ Проверьте что все сервисы работают: `.\check_monitoring.ps1`
2. ✅ Войдите в Grafana: http://localhost:3000
3. ✅ Добавьте Prometheus и Loki data sources
4. ✅ Импортируйте готовые dashboards (ID: 11133, 13639, 9628)
5. ✅ Создайте свой dashboard для бизнес-метрик

**Полезные ссылки:**
- Prometheus queries: https://prometheus.io/docs/prometheus/latest/querying/basics/
- LogQL (Loki): https://grafana.com/docs/loki/latest/logql/
- Grafana dashboards: https://grafana.com/grafana/dashboards/


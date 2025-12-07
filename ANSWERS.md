# ❓ Ответы на ваши вопросы

## 1️⃣ Что отвечает за логи, а что за метрики?

### 📝 **ЛОГИ** - текстовые записи событий

**Кто собирает:**
- **Promtail** (порт 9080) - агент сбора логов из Docker контейнеров
- **Loki** (порт 3100) - хранилище логов (как Elasticsearch, но проще)
- **Grafana** (порт 3000) - визуализация

**Что логируется:**
```json
{
  "timestamp": "2025-12-07T01:06:23Z",
  "level": "INFO",
  "service": "user-service",
  "message": "Request completed",
  "request_id": "abc-123",
  "method": "GET",
  "path": "/api/users",
  "status_code": 200,
  "duration_ms": 45
}
```

**Откуда берутся:**
- Ваши микросервисы пишут логи → stdout/stderr
- Docker сохраняет их в `/var/lib/docker/containers/`
- Promtail читает эти файлы и отправляет в Loki
- Grafana показывает логи через запросы к Loki

---

### 📊 **МЕТРИКИ** - числовые показатели

**Кто собирает:**
- **Prometheus** (порт 9090) - база данных для метрик
- **postgres-exporter** (порт 9187) - метрики PostgreSQL
- **FastAPI Instrumentator** - встроен в каждый микросервис
- **Grafana** (порт 3000) - визуализация

**Что собирается:**
```
# Счётчик запросов
http_requests_total{service="user-service", status="200"} = 1523

# Время ответа (гистограмма)
http_request_duration_seconds{service="user-service", quantile="0.95"} = 0.124

# Активные подключения к БД
pg_stat_database_numbackends = 12
```

**Откуда берутся:**
- Каждый микросервис экспортирует метрики на `/metrics` (или через instrumentator)
- Prometheus каждые 15 секунд делает HTTP GET к этим endpoints
- Сохраняет данные в своей time-series БД
- Grafana строит графики через PromQL запросы

---

### 🔍 **Главное различие:**

| Аспект | Логи 📝 | Метрики 📊 |
|--------|---------|-----------|
| **Тип данных** | Текст (события) | Числа (измерения) |
| **Объём** | Много (каждое событие) | Мало (агрегаты) |
| **Хранение** | Loki | Prometheus |
| **Сбор** | Promtail | Prometheus scraping |
| **Запросы** | LogQL | PromQL |
| **Для чего** | Debugging, трейсинг | Мониторинг, алерты |

---

## 2️⃣ Как проверить что всё реально логируется и данные собираются?

### ✅ Автоматическая проверка

```powershell
# Запустите скрипт
.\check_monitoring.ps1
```

**Результаты вашей последней проверки:**
- ✅ Все 8 микросервисов отвечают
- ✅ Prometheus работает (2/10 targets активны)
- ✅ **Loki собирает логи от 14 источников!**
  - user-service, homework-service, gradebook-service
  - profile-service, notifications-service, tests-service
  - schedule-service, reports-service
  - postgres, prometheus, grafana, loki, promtail, postgres-exporter
- ✅ Grafana доступна

---

### 📝 Ручная проверка ЛОГОВ

#### **Способ 1: Через Loki API**

```powershell
# Проверка что Loki работает
curl http://localhost:3100/ready

# Список сервисов с логами
curl http://localhost:3100/loki/api/v1/label/container_name/values

# Получить последние логи
curl "http://localhost:3100/loki/api/v1/query_range?query={container_name=~\".*-service\"}&limit=10"
```

#### **Способ 2: Через Grafana**

1. Откройте: http://localhost:3000
2. Логин: `admin`, Пароль: `admin`
3. Нажмите иконку **Explore** (компас слева)
4. Выберите data source: **Loki**
5. В поле запроса введите:
   ```logql
   {container_name=~".*-service"}
   ```
6. Нажмите **Run query**

**Что должны увидеть:**
```
[INFO] user-service - Request started
[INFO] user-service - Request completed (45ms)
[INFO] homework-service - Database query executed
...
```

#### **Способ 3: Проверка в реальном времени**

```powershell
# Генерируем трафик к сервисам
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Смотрим что логи появились
docker logs user-service --tail 5
```

---

### 📊 Ручная проверка МЕТРИК

#### **Способ 1: Prometheus UI**

1. Откройте: http://localhost:9090
2. В поле запроса (Expression) введите:
   ```promql
   http_requests_total
   ```
3. Нажмите **Execute**
4. Переключитесь на вкладку **Graph**

**Что должны увидеть:**
- График запросов по каждому сервису
- Если график пустой → генерируйте трафик:
  ```powershell
  curl http://localhost:8001/health
  curl http://localhost:8002/health
  # и т.д.
  ```

#### **Способ 2: Проверка targets**

1. Откройте: http://localhost:9090/targets
2. Должны видеть список сервисов
3. **State** должен быть **UP** (зелёный)

**Что проверяется:**
- ✅ `job="postgres-exporter"` - метрики PostgreSQL
- ✅ `job="prometheus"` - собственные метрики Prometheus
- ⚠️ Если targets "DOWN" → сервис недоступен

#### **Способ 3: Прямой доступ к метрикам**

```powershell
# Метрики микросервиса (если endpoint настроен)
curl http://localhost:8001/metrics

# Метрики PostgreSQL
curl http://localhost:9187/metrics

# Метрики Prometheus
curl http://localhost:9090/metrics
```

**Пример вывода:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{service="user-service",method="GET",status="200"} 1523
```

---

### 🧪 Генерация тестовых данных

Создам скрипт для генерации трафика:

```powershell
# test_traffic.ps1
Write-Host "Generating test traffic..." -ForegroundColor Cyan

$services = @(8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008)

for ($i = 1; $i -le 20; $i++) {
    foreach ($port in $services) {
        try {
            Invoke-WebRequest -Uri "http://localhost:$port/health" -UseBasicParsing | Out-Null
            Write-Host "." -NoNewline -ForegroundColor Green
        } catch {
            Write-Host "x" -NoNewline -ForegroundColor Red
        }
    }
    Start-Sleep -Seconds 1
}

Write-Host "`nDone! Check Grafana now." -ForegroundColor Cyan
```

Сохраните и запустите:
```powershell
.\test_traffic.ps1
```

Затем проверьте в Grafana - должны появиться графики!

---

## 3️⃣ Как настроить Grafana чтобы она отображала что-то?

### 🚀 Пошаговая инструкция (10 минут)

#### **Шаг 1: Вход в Grafana**

1. Откройте: http://localhost:3000
2. Логин: `admin`
3. Пароль: `admin`
4. При первом входе попросит сменить пароль (можно нажать **Skip**)

---

#### **Шаг 2: Добавить Data Sources**

**A. Prometheus (для метрик):**

1. Нажмите **☰** (меню) слева вверху
2. **Connections** → **Data Sources**
3. Нажмите **Add data source**
4. Выберите **Prometheus**
5. Заполните:
   ```
   Name: Prometheus
   URL: http://prometheus:9090
   ```
   ⚠️ **Важно:** используйте `prometheus:9090`, а не `localhost:9090`!
6. Нажмите **Save & Test**
7. Должно быть: ✅ "Data source is working"

**B. Loki (для логов):**

1. **Add data source** → **Loki**
2. Заполните:
   ```
   Name: Loki
   URL: http://loki:3100
   ```
3. **Save & Test**
4. ✅ "Data source is working"

---

#### **Шаг 3: Импортировать готовые дашборды**

**Вариант А: Мой готовый дашборд**

1. **Dashboards** (иконка 4 квадратов слева)
2. **New** → **Import**
3. Нажмите **Upload JSON file**
4. Выберите файл `grafana-dashboard-metrics.json`
5. Нажмите **Import**

**Вариант Б: Из Grafana.com**

1. **Dashboards** → **New** → **Import**
2. В поле **Import via grafana.com** введите ID: `11133`
3. Нажмите **Load**
4. В **Prometheus** выберите "Prometheus" (созданный на шаге 2)
5. Нажмите **Import**

Повторите для:
- **ID 13639** - Loki Dashboard (выбрать Loki data source)
- **ID 9628** - PostgreSQL Dashboard (выбрать Prometheus)

---

#### **Шаг 4: Создать свой дашборд вручную**

**Панель 1: Запросы в секунду**

1. **Dashboards** → **New Dashboard** → **Add visualization**
2. Выберите **Data source: Prometheus**
3. В поле **Metric** введите:
   ```promql
   sum(rate(http_requests_total[5m])) by (service)
   ```
4. В **Options** справа:
   - Title: `HTTP Requests per Second`
   - Legend: `{{service}}`
5. Нажмите **Apply**

**Панель 2: Время ответа (p95)**

1. **Add** → **Visualization**
2. Data source: **Prometheus**
3. Query:
   ```promql
   histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
   ```
4. Title: `Response Time (95th percentile)`
5. Unit: `seconds (s)`
6. **Apply**

**Панель 3: Error Rate**

1. **Add** → **Visualization**
2. Выберите тип панели: **Stat**
3. Query:
   ```promql
   sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
   ```
4. Title: `Error Rate %`
5. Unit: `percent (0-100)`
6. В **Thresholds**:
   - 0-1: зелёный
   - 1-5: жёлтый
   - 5+: красный
7. **Apply**

**Панель 4: Логи в реальном времени**

1. **Add** → **Visualization**
2. Data source: **Loki**
3. Query:
   ```logql
   {container_name=~".*-service"} |= "ERROR"
   ```
4. Title: `Recent Errors`
5. Visualization type: **Logs**
6. **Apply**

**Сохранить дашборд:**
1. Нажмите **Save dashboard** (иконка дискеты вверху)
2. Введите название: `My Microservices Dashboard`
3. **Save**

---

### 🎨 Полезные настройки дашбордов

#### **Автообновление:**
- Правый верхний угол → выберите `5s` или `10s`
- Дашборд будет автоматически обновляться

#### **Time Range:**
- Правый верхний угол → выберите `Last 15 minutes` или `Last 1 hour`

#### **Variables (переменные):**
1. **Dashboard settings** (⚙️) → **Variables** → **New variable**
2. Name: `service`
3. Type: `Query`
4. Query:
   ```promql
   label_values(http_requests_total, service)
   ```
5. Теперь можете использовать `$service` в запросах

---

### 🔍 Explore (Исследование)

**Для быстрой проверки без создания дашбордов:**

1. Нажмите **Explore** (иконка компаса слева)
2. Выберите **Prometheus** или **Loki**
3. Введите запрос и нажмите **Run query**

**Примеры для Prometheus:**
```promql
# Все метрики микросервисов
http_requests_total

# Топ-5 endpoint'ов по количеству запросов
topk(5, sum(rate(http_requests_total[5m])) by (path))
```

**Примеры для Loki:**
```logql
# Все логи
{container_name=~".*-service"}

# Только ошибки за последний час
{container_name=~".*-service"} |= "ERROR"

# Медленные запросы
{container_name=~".*-service"} | json | duration_ms > 1000
```

---

## 📚 Полезные файлы

Я создал для вас:

1. **check_monitoring.ps1** - скрипт проверки что всё работает
2. **GRAFANA_SETUP_GUIDE.md** - подробное руководство
3. **MONITORING_CHEATSHEET.md** - краткая шпаргалка
4. **MONITORING_ARCHITECTURE.md** - схема архитектуры
5. **grafana-dashboard-metrics.json** - готовый дашборд

---

## 🎯 Ваш следующий шаг

```powershell
# 1. Проверьте что всё работает
.\check_monitoring.ps1

# 2. Откройте Grafana
start http://localhost:3000

# 3. Добавьте data sources (Prometheus и Loki)

# 4. Импортируйте дашборды (11133, 13639, 9628)

# 5. Посмотрите на красивые графики! 📊
```

Удачи! 🚀


# 🔴 Проблема: Контейнеры постоянно перезапускаются

## Что случилось?

Из вашего Docker Desktop видно, что:
- ✅ **Запущены:** postgres, prometheus, grafana, promtail, postgres-exporter (5 контейнеров)
- ❌ **Перезапускаются:** user-service, homework-service, gradebook-service, profile-service, notifications-service, tests-service, schedule-service, reports-service, loki (9 контейнеров)

**Статус "Restarting"** означает, что контейнеры падают с ошибкой и Docker пытается их перезапустить.

## 🔍 Диагностика

### Способ 1: Через PowerShell скрипт

**Откройте НОВЫЙ PowerShell терминал** (важно!) и выполните:

```powershell
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform
.\diagnose_containers.ps1
```

### Способ 2: Вручную посмотреть логи

Откройте **НОВЫЙ PowerShell** и выполните:

```powershell
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform

# Посмотреть логи user-service
docker logs user-service --tail 50

# Посмотреть логи homework-service
docker logs homework-service --tail 50

# Посмотреть логи loki
docker logs loki --tail 50
```

### Способ 3: Через Docker Desktop

1. Откройте Docker Desktop
2. Нажмите на контейнер `user-service`
3. Перейдите на вкладку **Logs**
4. Посмотрите на ошибки

## 🎯 Вероятные причины

### 1. Отсутствуют Python зависимости

**Ошибка в логах будет:**
```
ModuleNotFoundError: No module named 'prometheus_client'
ModuleNotFoundError: No module named 'pythonjsonlogger'
```

**Решение:**
```powershell
# НОВЫЙ PowerShell терминал
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform

# Пересоберите образы БЕЗ кэша
docker compose build --no-cache
docker compose up -d
```

### 2. Проблемы с Loki конфигурацией

**Ошибка в логах будет:**
```
error parsing config
failed to create compactor
```

**Решение:**
```powershell
# Удалите старые данные Loki
docker compose down
docker volume rm online-teaching-platform_loki_data
docker compose up -d
```

### 3. База данных не готова

**Ошибка в логах будет:**
```
sqlalchemy.exc.OperationalError
could not connect to server
```

**Решение:**
```powershell
# Убедитесь, что PostgreSQL полностью запущен
docker logs online-teaching-postgres

# Перезапустите сервисы
docker compose restart user-service homework-service gradebook-service
```

## ✅ Универсальное решение (работает в 90% случаев)

Откройте **НОВЫЙ PowerShell терминал** и выполните:

```powershell
# 1. Перейти в директорию проекта
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform

# 2. Полностью остановить и удалить все
docker compose down -v

# 3. Удалить старые образы
docker compose down --rmi all

# 4. Пересобрать БЕЗ кэша
docker compose build --no-cache

# 5. Запустить
docker compose up -d

# 6. Подождать 60 секунд
Start-Sleep -Seconds 60

# 7. Проверить статус
docker compose ps

# 8. Посмотреть логи
docker compose logs
```

## 🔧 Пошаговая диагностика

### Шаг 1: Проверьте логи

```powershell
docker logs user-service --tail 50
```

Найдите строки с **ERROR** или **Exception**.

### Шаг 2: Проверьте, что requirements.txt правильный

```powershell
# Должны быть эти строки в файле
cat services\user-service\requirements.txt | Select-String "prometheus"
```

Должно вывести:
```
prometheus-client==0.21.0
prometheus-fastapi-instrumentator==7.0.0
python-json-logger==2.0.7
```

### Шаг 3: Проверьте PostgreSQL

```powershell
docker exec online-teaching-postgres pg_isready -U postgres
```

Должно вывести: `postgres:5432 - accepting connections`

### Шаг 4: Проверьте, что образы собрались

```powershell
docker images | Select-String "online-teaching-platform"
```

Должно показать 8 образов микросервисов.

## 📝 Что делать дальше?

1. **Откройте НОВЫЙ PowerShell терминал** (в текущем проблемы с вводом)
2. Выполните команды диагностики выше
3. Скопируйте текст ошибки из логов
4. В зависимости от ошибки примените соответствующее решение

## 🆘 Если ничего не помогает

### Вариант 1: Полная очистка Docker

```powershell
# ОСТОРОЖНО! Удалит ВСЕ контейнеры, образы и volumes
docker system prune -a --volumes -f

# Затем заново соберите проект
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform
docker compose up -d --build
```

### Вариант 2: Запуск только одного сервиса для теста

```powershell
# Запустить только PostgreSQL и user-service
docker compose up -d postgres
Start-Sleep -Seconds 10
docker compose up user-service

# Смотрим логи в реальном времени
docker compose logs -f user-service
```

## 💡 Частые проблемы

| Симптом | Причина | Решение |
|---------|---------|---------|
| `ModuleNotFoundError` | Не установлены зависимости | `docker compose build --no-cache` |
| `Connection refused` | БД не готова | Подождать 30 сек, перезапустить |
| `Port already in use` | Порт занят | Остановить конфликтующий процесс |
| `permission denied` | Проблемы с volumes | `docker compose down -v` |
| `OOM killed` | Не хватает памяти | Увеличить память Docker Desktop |

## ⚠️ Важно!

**Используйте НОВЫЙ PowerShell терминал!** В вашем текущем терминале видны символы `qс` перед командами, что говорит о проблемах с буфером. Это мешает правильному выполнению команд Docker.

### Как открыть новый терминал:

1. **Windows Terminal:** Нажмите `Ctrl + Shift + T`
2. **PowerShell:** Нажмите `Win + X` → `Windows PowerShell`
3. **Через Cursor:** Terminal → New Terminal

---

После диагностики отпишите, какую ошибку видите в логах, и я помогу с конкретным решением!


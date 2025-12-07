# 🚀 Quick Start - Docker Compose v2

## Быстрые команды (копируй и выполняй)

### 1️⃣ Первый запуск или после ошибок

```powershell
# Откройте PowerShell в директории проекта и выполните:
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform

# Удалить старые контейнеры (если есть конфликт)
docker rm -f loki prometheus grafana promtail postgres-exporter

# Остановить всё
docker compose down

# Запустить всё заново
docker compose up -d --build

# Подождать 30 секунд
Start-Sleep -Seconds 30

# Проверить
docker compose ps
```

### 2️⃣ Или используйте готовый скрипт

```powershell
.\cleanup_and_restart.ps1
```

### 3️⃣ Проверка системы

```powershell
.\check_monitoring.ps1
```

## 🔗 Быстрый доступ

После запуска откройте в браузере:

- 📊 **Grafana**: http://localhost:3000 (admin/admin)
- 📈 **Prometheus**: http://localhost:9090
- 🔍 **User Service API**: http://localhost:8001/docs
- 📉 **Метрики User Service**: http://localhost:8001/metrics

## ⚡ Основные команды Docker Compose v2

```powershell
# Запустить всё
docker compose up -d

# Остановить всё
docker compose down

# Проверить статус
docker compose ps

# Логи всех сервисов
docker compose logs -f

# Логи одного сервиса
docker compose logs -f user-service

# Перезапустить сервис
docker compose restart user-service

# Пересобрать образы
docker compose build

# Полная очистка
docker compose down -v
```

## 🆘 Если что-то не работает

### Проблема: Конфликт имен контейнеров

```powershell
docker rm -f loki prometheus grafana promtail postgres-exporter
docker compose down
docker compose up -d
```

### Проблема: Контейнеры не запускаются

```powershell
# Смотрим логи
docker compose logs

# Или конкретного сервиса
docker logs user-service
```

### Проблема: Нужен полный рестарт

```powershell
docker compose down -v
docker system prune -f
docker compose up -d --build
```

## 📚 Полная документация

- **DOCKER_COMPOSE_V2_MIGRATION.md** - что изменилось
- **MONITORING_QUICKSTART.md** - подробный гайд по мониторингу
- **TROUBLESHOOTING_DOCKER.md** - решение проблем
- **MONITORING.md** - документация по метрикам
- **LOGGING.md** - документация по логам

## ✅ Проверка после запуска

1. **Контейнеры запущены?**
   ```powershell
   docker compose ps
   # Должно быть 17 контейнеров со статусом "Up"
   ```

2. **Prometheus собирает метрики?**
   - Открыть: http://localhost:9090/targets
   - Все должны быть зелёные (UP)

3. **Grafana работает?**
   - Открыть: http://localhost:3000
   - Войти: admin/admin
   - Открыть дашборды

4. **Логи в JSON?**
   ```powershell
   docker logs user-service --tail 5
   # Должен быть JSON формат
   ```

## 🎯 Что дальше?

1. Изучите дашборды в Grafana
2. Попробуйте запросы в Prometheus
3. Поищите логи в Grafana Explore (Loki)
4. Сгенерируйте нагрузку на API
5. Следите за метриками в реальном времени

---

💡 **Совет:** Добавьте эту страницу в закладки для быстрого доступа!


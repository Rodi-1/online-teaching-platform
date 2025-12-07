# Инструкция по исправлению ошибки запуска

## Проблема
При запуске `docker-compose up -d` возникла ошибка:
```
Error response from daemon: Conflict. The container name "/loki" is already in use
```

## Причина
Старые контейнеры мониторинга (loki, prometheus, grafana и др.) не были удалены и конфликтуют с новыми.

## Решение

### Вариант 1: Быстрое решение (рекомендуется)

Откройте **новый** PowerShell терминал (важно - новый!) и выполните:

```powershell
# Перейдите в директорию проекта
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform

# Удалите старые контейнеры
docker rm -f loki prometheus grafana promtail postgres-exporter

# Остановите все контейнеры проекта
docker-compose down

# Запустите заново
docker-compose up -d --build
```

### Вариант 2: Через готовый скрипт

Откройте **новый** PowerShell терминал и выполните:

```powershell
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform
.\cleanup_and_restart.ps1
```

### Вариант 3: Полная очистка (если не помогли предыдущие)

```powershell
cd D:\Mirea\4Kyrs\Mikroservis\online-teaching-platform

# Остановить и удалить все контейнеры, сети и volumes
docker compose down -v

# Удалить ВСЕ остановленные контейнеры
docker container prune -f

# Запустить заново
docker compose up -d --build
```

## Проверка после запуска

Подождите 30-60 секунд и проверьте статус:

```powershell
# Проверить статус всех контейнеров
docker compose ps

# Должно быть запущено 17 контейнеров:
# - 8 микросервисов
# - postgres
# - prometheus
# - grafana
# - loki
# - promtail
# - postgres-exporter
# И все должны быть в статусе "Up"

# Запустить проверку системы
.\check_monitoring.ps1
```

## Почему возникла проблема?

Вероятно, вы ранее запускали какие-то другие Docker контейнеры с такими же именами, или выполняли `docker-compose up` без предварительного `docker-compose down`.

## Что делать, если проблема не исчезла?

1. Проверьте, что используется правильный `docker-compose.yml`:
```powershell
docker compose config
```

2. Проверьте запущенные контейнеры:
```powershell
docker ps -a
```

3. Удалите ВРУЧНУЮ конфликтующий контейнер:
```powershell
docker ps -a | Select-String "loki"
docker rm -f <CONTAINER_ID_от_loki>
```

4. Если ничего не помогает, полный рестарт Docker Desktop:
   - Закройте Docker Desktop
   - Откройте снова
   - Выполните Вариант 3 (полная очистка)

## После успешного запуска

1. Откройте Grafana: http://localhost:3000 (admin/admin)
2. Откройте Prometheus: http://localhost:9090
3. Проверьте метрики: http://localhost:8001/metrics
4. Проверьте логи: `docker logs user-service`

## Важно!

⚠️ **ВСЕГДА открывайте НОВЫЙ PowerShell терминал** для выполнения команд Docker, если в текущем терминале были проблемы с вводом. Это связано с буферизацией командной строки.

## Контакты для помощи

Если проблема сохраняется, создайте Issue в GitHub с:
- Выводом `docker ps -a`
- Выводом `docker compose ps`
- Логами: `docker compose logs > logs.txt`


# Скрипт для очистки старых контейнеров и перезапуска системы
# cleanup_and_restart.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Очистка и перезапуск системы" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Остановить и удалить все контейнеры проекта
Write-Host "[1/5] Остановка всех контейнеров..." -ForegroundColor Yellow
docker compose down 2>&1 | Out-Null

# Удалить конфликтующие контейнеры
Write-Host "[2/5] Удаление старых контейнеров..." -ForegroundColor Yellow
$oldContainers = docker ps -a --filter "name=loki" --filter "name=prometheus" --filter "name=grafana" --filter "name=promtail" --filter "name=postgres-exporter" --format "{{.Names}}"

if ($oldContainers) {
    foreach ($container in $oldContainers) {
        Write-Host "  Удаление: $container" -ForegroundColor Gray
        docker rm -f $container 2>&1 | Out-Null
    }
    Write-Host "  ✅ Старые контейнеры удалены" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  Старых контейнеров не найдено" -ForegroundColor Gray
}

# Очистка неиспользуемых образов (опционально)
Write-Host "[3/5] Очистка неиспользуемых образов..." -ForegroundColor Yellow
docker image prune -f 2>&1 | Out-Null
Write-Host "  ✅ Очистка завершена" -ForegroundColor Green

# Сборка и запуск
Write-Host "[4/5] Сборка образов..." -ForegroundColor Yellow
docker compose build --no-cache 2>&1 | Write-Host

Write-Host "`n[5/5] Запуск всех сервисов..." -ForegroundColor Yellow
docker compose up -d

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✅ Система запущена!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Подождите 30 секунд для полного запуска..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "`nПроверка статуса..." -ForegroundColor Yellow
docker compose ps

Write-Host "`n" -NoNewline
Write-Host "Для проверки системы запустите:" -ForegroundColor Green
Write-Host "  .\check_monitoring.ps1" -ForegroundColor Cyan
Write-Host ""


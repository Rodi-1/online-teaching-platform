# Скрипт проверки системы мониторинга и логирования
# check_monitoring.ps1

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Проверка системы мониторинга" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# Функция для проверки HTTP endpoint
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [int]$Timeout = 5
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $Timeout -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $Name" -ForegroundColor Green -NoNewline
            Write-Host " - OK" -ForegroundColor Gray
            return $true
        } else {
            Write-Host "❌ $Name" -ForegroundColor Red -NoNewline
            Write-Host " - Status: $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ $Name" -ForegroundColor Red -NoNewline
        Write-Host " - НЕДОСТУПЕН" -ForegroundColor Yellow
        return $false
    }
}

# Проверка Docker
Write-Host "`n[1/5] Проверка Docker контейнеров..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$containers = docker ps --format "{{.Names}}" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker не запущен или недоступен!" -ForegroundColor Red
    exit 1
}

$requiredContainers = @(
    "user-service",
    "homework-service", 
    "gradebook-service",
    "profile-service",
    "notifications-service",
    "tests-service",
    "schedule-service",
    "reports-service",
    "prometheus",
    "grafana",
    "loki",
    "promtail",
    "postgres-exporter",
    "online-teaching-postgres"
)

foreach ($container in $requiredContainers) {
    if ($containers -contains $container) {
        Write-Host "✅ $container" -ForegroundColor Green -NoNewline
        $status = docker inspect -f '{{.State.Status}}' $container 2>$null
        Write-Host " - $status" -ForegroundColor Gray
        if ($status -ne "running") {
            $allOk = $false
        }
    } else {
        Write-Host "❌ $container - НЕ НАЙДЕН" -ForegroundColor Red
        $allOk = $false
    }
}

# Проверка компонентов мониторинга
Write-Host "`n[2/5] Проверка компонентов мониторинга..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$prometheusOk = Test-Endpoint "Prometheus" "http://localhost:9090/-/healthy"
$grafanaOk = Test-Endpoint "Grafana" "http://localhost:3000/api/health"

if (-not $prometheusOk -or -not $grafanaOk) {
    $allOk = $false
}

# Проверка микросервисов
Write-Host "`n[3/5] Проверка микросервисов..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

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
    $serviceOk = Test-Endpoint $service.name "http://localhost:$($service.port)/health"
    if (-not $serviceOk) {
        $allOk = $false
    }
}

# Проверка метрик
Write-Host "`n[4/5] Проверка endpoint'ов метрик..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$userMetricsOk = Test-Endpoint "user-service /metrics" "http://localhost:8001/metrics"
$postgresMetricsOk = Test-Endpoint "postgres-exporter" "http://localhost:9187/metrics"

if (-not $userMetricsOk -or -not $postgresMetricsOk) {
    $allOk = $false
}

# Проверка Prometheus targets
Write-Host "`n[5/5] Проверка Prometheus targets..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    $targets = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/targets" -TimeoutSec 5
    $activeTargets = $targets.data.activeTargets
    
    $upCount = ($activeTargets | Where-Object { $_.health -eq "up" }).Count
    $downCount = ($activeTargets | Where-Object { $_.health -ne "up" }).Count
    $totalCount = $activeTargets.Count
    
    Write-Host "Всего targets: $totalCount" -ForegroundColor Gray
    Write-Host "✅ UP: $upCount" -ForegroundColor Green
    
    if ($downCount -gt 0) {
        Write-Host "❌ DOWN: $downCount" -ForegroundColor Red
        $allOk = $false
        
        # Показать какие targets down
        $activeTargets | Where-Object { $_.health -ne "up" } | ForEach-Object {
            Write-Host "  ❌ $($_.labels.job) - $($_.health)" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "❌ Не удалось получить targets из Prometheus" -ForegroundColor Red
    $allOk = $false
}

# Итоговый результат
Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
if ($allOk) {
    Write-Host "  ✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Система мониторинга работает корректно!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Полезные ссылки:" -ForegroundColor Yellow
    Write-Host "  - Prometheus:  http://localhost:9090" -ForegroundColor Cyan
    Write-Host "  - Grafana:     http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
    Write-Host "  - User API:    http://localhost:8001/docs" -ForegroundColor Cyan
    Write-Host ""
    exit 0
} else {
    Write-Host "  ❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Рекомендации по устранению:" -ForegroundColor Yellow
    Write-Host "  1. Проверьте логи контейнеров: docker-compose logs" -ForegroundColor Gray
    Write-Host "  2. Перезапустите сервисы: docker-compose restart" -ForegroundColor Gray
    Write-Host "  3. Пересоберите контейнеры: docker-compose up -d --build" -ForegroundColor Gray
    Write-Host "  4. Проверьте документацию: MONITORING.md и LOGGING.md" -ForegroundColor Gray
    Write-Host ""
    exit 1
}


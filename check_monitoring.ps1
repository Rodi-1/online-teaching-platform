# Monitoring and Logging Check Script
# check_monitoring.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Monitoring & Logging Health Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Function to check endpoint
function Test-Endpoint {
    param($url, $name)
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline
            Write-Host " $name is responding"
            return $true
        }
    } catch {
        Write-Host "[FAIL]" -ForegroundColor Red -NoNewline
        Write-Host " $name is not responding: $_"
        return $false
    }
}

Write-Host "`n[1/5] Checking Microservices Metrics..." -ForegroundColor Yellow
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
    Test-Endpoint "http://localhost:$($service.port)/health" $service.name | Out-Null
}

Write-Host "`n[2/5] Checking Prometheus..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Test-Endpoint "http://localhost:9090/-/healthy" "Prometheus" | Out-Null

# Check if Prometheus is scraping targets
try {
    $targets = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/targets" -UseBasicParsing
    $upTargets = ($targets.data.activeTargets | Where-Object { $_.health -eq "up" }).Count
    $totalTargets = $targets.data.activeTargets.Count
    Write-Host "  Active targets: $upTargets / $totalTargets" -ForegroundColor Cyan
} catch {
    Write-Host "  Could not check Prometheus targets" -ForegroundColor Yellow
}

Write-Host "`n[3/5] Checking Loki..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Test-Endpoint "http://localhost:3100/ready" "Loki" | Out-Null

# Check if Loki has received logs
try {
    $logsCheck = Invoke-RestMethod -Uri "http://localhost:3100/loki/api/v1/label/service/values" -UseBasicParsing
    if ($logsCheck.data.Count -gt 0) {
        Write-Host "  Found logs from services: $($logsCheck.data -join ', ')" -ForegroundColor Cyan
    } else {
        Write-Host "  No logs received yet (may need a few minutes)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Could not check Loki logs" -ForegroundColor Yellow
}

Write-Host "`n[4/5] Checking Grafana..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Test-Endpoint "http://localhost:3000/api/health" "Grafana" | Out-Null

Write-Host "`n[5/5] Checking PostgreSQL Exporter..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Test-Endpoint "http://localhost:9187/metrics" "postgres-exporter" | Out-Null

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nAccess URLs:" -ForegroundColor Yellow
Write-Host "  Grafana:    http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "  Loki:       http://localhost:3100" -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Open Grafana: http://localhost:3000" -ForegroundColor Gray
Write-Host "  2. Login with admin/admin" -ForegroundColor Gray
Write-Host "  3. Follow the setup guide to add dashboards" -ForegroundColor Gray
Write-Host ""

# Test Traffic Generator
# test_traffic.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Test Traffic Generator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

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

$iterations = 20
$successCount = 0
$failCount = 0

Write-Host "Generating $iterations rounds of test traffic..." -ForegroundColor Yellow
Write-Host "Each dot = successful request, X = failed" -ForegroundColor Gray
Write-Host ""

for ($i = 1; $i -le $iterations; $i++) {
    Write-Host "Round $i/$iterations : " -NoNewline -ForegroundColor Cyan
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($service.port)/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "." -NoNewline -ForegroundColor Green
                $successCount++
            }
        } catch {
            Write-Host "x" -NoNewline -ForegroundColor Red
            $failCount++
        }
    }
    
    Write-Host ""
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Successful requests: $successCount" -ForegroundColor Green
Write-Host "Failed requests: $failCount" -ForegroundColor Red
Write-Host "Total requests: $($successCount + $failCount)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open Prometheus: http://localhost:9090" -ForegroundColor Gray
Write-Host "   Query: http_requests_total" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open Grafana: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Check your dashboards for new data" -ForegroundColor Gray
Write-Host ""
Write-Host "3. View logs in Grafana Explore:" -ForegroundColor Gray
Write-Host '   Query: {container_name=~".*-service"}' -ForegroundColor Gray
Write-Host ""


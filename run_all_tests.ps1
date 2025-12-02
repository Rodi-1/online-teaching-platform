# PowerShell script to run tests for all microservices
# Usage: .\run_all_tests.ps1

$ErrorActionPreference = "Continue"

$services = @(
    "user-service",
    "homework-service",
    "gradebook-service",
    "profile-service",
    "notifications-service",
    "tests-service",
    "schedule-service",
    "reports-service"
)

$results = @{}
$totalPassed = 0
$totalFailed = 0

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Running Tests for All Microservices               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

foreach ($service in $services) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "📦 Testing $service..." -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    $servicePath = "services\$service"
    
    if (-not (Test-Path $servicePath)) {
        Write-Host "❌ Service directory not found: $servicePath" -ForegroundColor Red
        $results[$service] = "MISSING"
        $totalFailed++
        continue
    }
    
    Push-Location $servicePath
    
    # Install dependencies quietly
    Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt --quiet 2>$null
    
    # Run tests
    Write-Host "`n🧪 Running tests...`n" -ForegroundColor Yellow
    python -m pytest tests/ -v --tb=short 2>&1 | Tee-Object -Variable testOutput
    $exitCode = $LASTEXITCODE
    
    Pop-Location
    
    if ($exitCode -eq 0) {
        Write-Host "`n✅ Tests PASSED for $service" -ForegroundColor Green
        $results[$service] = "PASSED"
        $totalPassed++
    } else {
        Write-Host "`n❌ Tests FAILED for $service (exit code: $exitCode)" -ForegroundColor Red
        $results[$service] = "FAILED"
        $totalFailed++
    }
}

# Summary
Write-Host "`n`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    TEST SUMMARY                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

foreach ($service in $services) {
    $status = $results[$service]
    $icon = if ($status -eq "PASSED") { "✅" } elseif ($status -eq "FAILED") { "❌" } else { "⚠️" }
    $color = if ($status -eq "PASSED") { "Green" } elseif ($status -eq "FAILED") { "Red" } else { "Yellow" }
    
    Write-Host "$icon $service : " -NoNewline
    Write-Host $status -ForegroundColor $color
}

Write-Host "`n" -NoNewline
Write-Host "📊 Total: " -NoNewline
Write-Host "$totalPassed passed" -ForegroundColor Green -NoNewline
Write-Host ", " -NoNewline
Write-Host "$totalFailed failed" -ForegroundColor Red

if ($totalFailed -eq 0) {
    Write-Host "`n🎉 All tests passed successfully!`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️  Some tests failed. Please check the output above.`n" -ForegroundColor Yellow
    exit 1
}


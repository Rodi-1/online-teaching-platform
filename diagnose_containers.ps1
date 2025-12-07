# Container diagnostics script
# diagnose_containers.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Container Diagnostics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check status
Write-Host "[1/4] Container Status:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
docker compose ps

# Check microservice logs
Write-Host "`n[2/4] Logs for user-service:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
docker logs user-service --tail 30

Write-Host "`n[3/4] Logs for loki:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
docker logs loki --tail 30

Write-Host "`n[4/4] Dependencies Check:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# Check that PostgreSQL is running
$pgStatus = docker ps --filter "name=postgres" --format "{{.Status}}"
Write-Host "PostgreSQL: $pgStatus"

# Check PostgreSQL connection
Write-Host "`nAttempting to connect to PostgreSQL..."
docker exec online-teaching-postgres pg_isready -U postgres

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Diagnostics Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Recommendations:" -ForegroundColor Yellow
Write-Host "1. Check logs above for errors" -ForegroundColor Gray
Write-Host "2. If you see Python import errors - dependency issue" -ForegroundColor Gray
Write-Host "3. If you see database connection errors - PostgreSQL issue" -ForegroundColor Gray
Write-Host "4. Run: docker compose down && docker compose up -d --build" -ForegroundColor Gray
Write-Host ""


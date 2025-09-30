# Test if services are running
Write-Host "Testing Quantum-Safe Blockchain Guardrail Services..." -ForegroundColor Green

# Test Backend API
Write-Host "`nTesting Backend API (Port 5000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Backend API is running!" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Cyan
} catch {
    Write-Host "Backend API is not responding" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Main Application
Write-Host "`nTesting Main Application (Port 3000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Main Application is running!" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Cyan
} catch {
    Write-Host "Main Application is not responding" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test React Frontend
Write-Host "`nTesting React Frontend (Port 3000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "React Frontend is running!" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Cyan
} catch {
    Write-Host "React Frontend is not responding" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nService test complete!" -ForegroundColor Green
Write-Host "`nIf services are running, you can access:" -ForegroundColor Cyan
Write-Host "   Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:5000" -ForegroundColor White
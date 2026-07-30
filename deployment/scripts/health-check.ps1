Write-Host "Running Health Check..." -ForegroundColor Cyan
cd ../docker
docker compose ps
Write-Host "Checking API Gateway..." -ForegroundColor Cyan
curl -UseBasicParsing http://localhost/api/health
Write-Host "`nHealth Check Complete." -ForegroundColor Green

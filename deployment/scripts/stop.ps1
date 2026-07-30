Write-Host "Stopping Agentverse..." -ForegroundColor Yellow
cd ../docker
docker compose down
Write-Host "Agentverse has been stopped." -ForegroundColor Green

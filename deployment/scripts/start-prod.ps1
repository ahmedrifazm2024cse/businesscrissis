Write-Host "Starting Agentverse in PRODUCTION mode..." -ForegroundColor Cyan
cd ../docker
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
Write-Host "Agentverse production environment is booting." -ForegroundColor Green

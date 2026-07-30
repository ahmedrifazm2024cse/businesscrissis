Write-Host "Starting Agentverse in DEVELOPMENT mode..." -ForegroundColor Cyan
cd ../docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
Write-Host "Agentverse development environment is booting. Use 'docker compose logs -f' to monitor." -ForegroundColor Green

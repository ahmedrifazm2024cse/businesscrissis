Write-Host "Starting Agentverse in BARE-METAL mode (No Docker)..." -ForegroundColor Cyan

$services = @(
    # Infrastructure Services
    @{ path = "backend\eventbus"; name = "EventBus"; port = 8009 },
    @{ path = "backend\memory"; name = "SharedMemory"; port = 8012 },
    @{ path = "backend\workflow"; name = "WorkflowEngine"; port = 8011 },
    @{ path = "backend\security"; name = "Security"; port = 8105 },
    @{ path = "backend\monitoring"; name = "Monitoring"; port = 8101 },
    @{ path = "backend\metrics"; name = "Metrics"; port = 8102 },
    @{ path = "backend\audit"; name = "Audit"; port = 8106 },
    @{ path = "backend\config"; name = "Config"; port = 8103 },
    @{ path = "backend\cache"; name = "Cache"; port = 8104 },
    @{ path = "backend\scheduler"; name = "Scheduler"; port = 8107 },
    @{ path = "backend\analytics"; name = "Analytics"; port = 8108 },
    
    # Commander API
    @{ path = "backend\commander"; name = "Commander"; port = 8000 },
    
    # Executive Agents
    @{ path = "backend\executive_agents\decision"; name = "DecisionAgent"; port = 8010 },
    @{ path = "backend\executive_agents\workflow_manager"; name = "WorkflowManagerAgent"; port = 8013 },
    @{ path = "backend\executive_agents\communication_pr"; name = "PRAgent"; port = 8014 },
    @{ path = "backend\executive_agents\resource_allocator"; name = "ResourceAgent"; port = 8015 },
    @{ path = "backend\executive_agents\notification"; name = "NotificationAgent"; port = 8016 },
    @{ path = "backend\executive_agents\report_generator"; name = "ReportAgent"; port = 8017 },
    @{ path = "backend\executive_agents\knowledge_manager"; name = "KnowledgeAgent"; port = 8018 }
)

# Start all Python APIs
foreach ($svc in $services) {
    Write-Host "Starting $($svc.name) on Port $($svc.port)..." -ForegroundColor Yellow
    
    # We open a new minimized PowerShell window for each service to keep things clean
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ..\..\$($svc.path); if (Test-Path requirements.txt) { pip install -r requirements.txt -q }; uvicorn main:app --port $($svc.port) --host 0.0.0.0" -WindowStyle Minimized
}

# Start the React Frontend
Write-Host "Starting React Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ..\..\frontend; npm install; npm run dev" -WindowStyle Normal

Write-Host "======================================================" -ForegroundColor Green
Write-Host "Agentverse is booting up on Bare-Metal Windows!" -ForegroundColor Green
Write-Host "19 PowerShell windows have been opened in the background." -ForegroundColor Green
Write-Host "Access the Dashboard at: http://localhost:5173" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Green

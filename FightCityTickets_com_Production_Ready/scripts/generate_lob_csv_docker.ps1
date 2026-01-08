# Generate Lob CSV from database inside Docker container (PowerShell)

Write-Host "🔍 Generating Lob Campaign CSV from database..." -ForegroundColor Cyan
Write-Host ""

# Check if API container is running
$containerName = "fightsftickets_api_1"
$containerExists = docker ps -a --filter "name=$containerName" --format "{{.Names}}"

if (-not $containerExists) {
    Write-Host "❌ Container $containerName not found!" -ForegroundColor Red
    Write-Host "   Make sure Docker containers are running: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Run the generator inside the API container
Write-Host "Running generator inside container..." -ForegroundColor Yellow
docker exec -it $containerName python backend/generate_lob_csv.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ CSV file should be generated!" -ForegroundColor Green
    Write-Host "📄 Check: lob_campaign_audience.csv" -ForegroundColor Cyan
    
    # Try to copy from container if file doesn't exist locally
    if (-not (Test-Path "lob_campaign_audience.csv")) {
        Write-Host ""
        Write-Host "📋 Copying file from container..." -ForegroundColor Yellow
        docker cp "${containerName}:/app/lob_campaign_audience.csv" "lob_campaign_audience.csv"
    }
} else {
    Write-Host ""
    Write-Host "❌ Error generating CSV. Check container logs:" -ForegroundColor Red
    Write-Host "   docker logs $containerName" -ForegroundColor Yellow
}


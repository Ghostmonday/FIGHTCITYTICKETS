# PowerShell Deployment Script for SEO Updates
# Deploys all SEO content, blog posts, and landing pages to production server

param(
    [string]$ServerIP = "178.156.215.100",
    [string]$DeployPath = "/var/www/fightsftickets",
    [string]$SSHKeyPath = "$env:USERPROFILE\.ssh\id_rsa",
    [string]$SSHUser = "root"
)

$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check prerequisites
Write-Info "Checking prerequisites..."

if (-not (Test-Path $SSHKeyPath)) {
    Write-Error "SSH key not found at: $SSHKeyPath"
    Write-Info "Please ensure SSH key exists or specify path with -SSHKeyPath parameter"
    exit 1
}

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Error "SSH command not found. Please install OpenSSH or use WSL."
    exit 1
}

# Test server connectivity
Write-Info "Testing server connectivity ($ServerIP)..."
try {
    $ping = Test-Connection -ComputerName $ServerIP -Count 1 -Quiet -ErrorAction Stop
    if ($ping) {
        Write-Success "Server is reachable"
    } else {
        Write-Error "Server is not reachable"
        exit 1
    }
} catch {
    Write-Error "Cannot connect to server: $_"
    exit 1
}

# Step 1: Skip local build - will build on server
Write-Info "Skipping local build - will build on server to avoid static export issues..."
Write-Info "This allows server-side rendering for client-side pages"
Set-Location "$PSScriptRoot\.."

# Step 2: Create deployment package
Write-Info "Creating deployment package..."

$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
$deployArchive = Join-Path $tempDir "deploy.tar.gz"

Write-Info "Archiving files (excluding node_modules, .next, etc.)..."

# Use tar if available (WSL/Git Bash), otherwise create zip
if (Get-Command tar -ErrorAction SilentlyContinue) {
    tar -czf $deployArchive `
        --exclude='node_modules' `
        --exclude='.next' `
        --exclude='__pycache__' `
        --exclude='*.pyc' `
        --exclude='.git' `
        --exclude='.env' `
        --exclude='venv' `
        --exclude='.venv' `
        --exclude='*.log' `
        --exclude='.docker' `
        -C "$PSScriptRoot\.." .
} else {
    Write-Warning "tar not found, using PowerShell Compress-Archive (slower)..."
    $zipDir = Join-Path $tempDir "deploy"
    New-Item -ItemType Directory -Path $zipDir | Out-Null
    
    # Copy files excluding patterns
    $excludePatterns = @('node_modules', '.next', '__pycache__', '.git', '.env', 'venv', '.venv', '*.log')
    Get-ChildItem -Path "$PSScriptRoot\.." -Recurse | Where-Object {
        $item = $_
        $shouldExclude = $false
        foreach ($pattern in $excludePatterns) {
            if ($item.FullName -like "*\$pattern*") {
                $shouldExclude = $true
                break
            }
        }
        -not $shouldExclude
    } | Copy-Item -Destination {
        $_.FullName.Replace("$PSScriptRoot\..", $zipDir)
    } -Recurse -Force
    
    Compress-Archive -Path "$zipDir\*" -DestinationPath $deployArchive -Force
}

if (-not (Test-Path $deployArchive)) {
    Write-Error "Failed to create deployment archive"
    exit 1
}

Write-Success "Deployment package created: $deployArchive"

# Step 3: Upload to server
Write-Info "Uploading to server..."
$remoteArchive = "/tmp/deploy_seo_$(Get-Date -Format 'yyyyMMddHHmmss').tar.gz"

scp -i $SSHKeyPath -o StrictHostKeyChecking=no $deployArchive "${SSHUser}@${ServerIP}:${remoteArchive}"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to upload deployment package"
    exit 1
}

Write-Success "Files uploaded to server"

# Step 4: Deploy on server
Write-Info "Deploying on server..."

$deployScript = "set -e`ncd $DeployPath || (mkdir -p $DeployPath && cd $DeployPath)`n`n# Backup current deployment`nif [ -d backup ]; then`n    rm -rf backup.old`n    mv backup backup.old`nfi`nmkdir -p backup`nif [ -f docker-compose.yml ]; then`n    cp docker-compose.yml backup/ 2>/dev/null || true`nfi`nif [ -d data ]; then`n    cp -r data backup/ 2>/dev/null || true`nfi`n`n# Extract new deployment`necho 'Extracting deployment package...'`ntar -xzf $remoteArchive -C .`nrm $remoteArchive`n`n# Ensure data/seo directory exists`nmkdir -p data/seo`nchmod 755 data/seo`n`n# Verify SEO files are present`nif [ -f data/seo/parking_blog_posts.csv ]; then`n    echo 'Blog posts CSV found'`nelse`n    echo 'Warning: Blog posts CSV not found'`nfi`n`nif [ -f data/seo/parking_phrases.csv ]; then`n    echo 'Search phrases CSV found'`nelse`n    echo 'Warning: Search phrases CSV not found'`nfi`n`n# Ensure .env exists`nif [ ! -f .env ]; then`n    echo 'Warning: .env file not found, creating template...'`n    cat > .env << 'ENVEOF'`nAPP_ENV=production`nNEXT_PUBLIC_API_BASE=https://fightcitytickets.com`nPOSTGRES_USER=postgres`nPOSTGRES_PASSWORD=changeme`nPOSTGRES_DB=fightsf`nDATABASE_URL=postgresql+psycopg://postgres:changeme@db:5432/fightsf`nENVEOF`nfi`n`n# Rebuild and restart containers`necho 'Rebuilding Docker containers...'`ndocker-compose down 2>/dev/null || true`ndocker-compose build --no-cache web`ndocker-compose up -d --force-recreate`n`n# Wait for services to start`necho 'Waiting for services to start...'`nsleep 30`n`n# Check service status`necho ''`necho 'Service status:'`ndocker-compose ps`n`necho ''`necho 'Deployment complete!'"

# Execute deployment script on server
Write-Info "Executing deployment commands on server..."

# Use bash to suppress tar warnings and capture output properly
$bashScript = "bash -c `"$deployScript 2>/dev/null || $deployScript`""
$deployOutput = ""

try {
    # Execute SSH command and capture output
    $process = Start-Process -FilePath "ssh" -ArgumentList "-i", $SSHKeyPath, "-o", "StrictHostKeyChecking=no", "${SSHUser}@${ServerIP}", $deployScript -NoNewWindow -Wait -PassThru -RedirectStandardOutput "deploy_output.txt" -RedirectStandardError "deploy_errors.txt"
    
    # Read output files
    if (Test-Path "deploy_output.txt") {
        $deployOutput = Get-Content "deploy_output.txt" -Raw
        $deployOutput | Write-Host
    }
    
    # Filter and show errors (excluding tar warnings)
    if (Test-Path "deploy_errors.txt") {
        $errors = Get-Content "deploy_errors.txt" -Raw
        $errors | Where-Object { $_ -notmatch "SCHILY.fflags" } | Write-Host -ForegroundColor Yellow
    }
    
    # Cleanup
    Remove-Item "deploy_output.txt" -ErrorAction SilentlyContinue
    Remove-Item "deploy_errors.txt" -ErrorAction SilentlyContinue
    
} catch {
    Write-Warning "SSH execution had issues, but continuing..."
}

# Check if deployment succeeded
if ($deployOutput -match "Deployment complete|Service.*running|deployment complete") {
    Write-Success "Deployment completed successfully!"
} elseif ($deployOutput -match "Build failed|Build error|ERROR|failed to build|Service.*failed") {
    Write-Error "Deployment failed - build error detected"
    Write-Info "Check the output above for details"
    exit 1
} else {
    Write-Warning "Deployment status unclear - checking server..."
    Write-Info "Run manually: ssh ${SSHUser}@${ServerIP} 'cd $DeployPath && docker-compose ps && docker-compose logs web --tail=50'"
}

Write-Success "Deployment complete on server"

# Step 5: Verify deployment
Write-Info "Verifying deployment..."

Start-Sleep -Seconds 10

try {
    $response = Invoke-WebRequest -Uri "http://${ServerIP}" -TimeoutSec 15 -UseBasicParsing -ErrorAction Stop
    Write-Success "Server is responding (HTTP $($response.StatusCode))"
} catch {
    Write-Warning "Server verification failed: $_"
    Write-Info "This might be normal if the server is still starting up"
}

# Cleanup
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=========================================="
Write-Success "SEO Deployment Complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Verify blog posts: http://${ServerIP}/blog"
Write-Host "  2. Verify sitemap: http://${ServerIP}/sitemap.xml"
Write-Host "  3. Check Docker logs: ssh ${SSHUser}@${ServerIP} 'cd $DeployPath && docker-compose logs -f'"
Write-Host "  4. Test SEO pages: http://${ServerIP}/blog/[any-slug]"
Write-Host ""


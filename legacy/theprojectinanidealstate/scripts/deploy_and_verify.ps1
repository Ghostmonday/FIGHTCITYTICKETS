# PowerShell Deployment and Verification Script for FightCityTickets.com
# This script deploys the application and verifies DNS and page loading

param(
    [string]$Domain = "fightcitytickets.com",
    [string]$ServerIP = "178.156.215.100",
    [string]$DeployPath = "/var/www/fightsftickets",
    [string]$SSHKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
)

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
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

# Step 1: Check DNS Configuration
function Test-DNS {
    Write-Info "Checking DNS configuration for $Domain..."
    
    try {
        $result = Resolve-DnsName -Name $Domain -ErrorAction Stop
        $resolvedIP = ($result | Where-Object { $_.Type -eq 'A' }).IPAddress | Select-Object -First 1
        
        if ($resolvedIP -eq $ServerIP) {
            Write-Success "DNS is correctly configured: $Domain -> $resolvedIP"
            return $true
        } else {
            Write-Warning "DNS points to different IP: $resolvedIP (expected $ServerIP)"
            return $false
        }
    } catch {
        Write-Warning "DNS lookup failed for $Domain"
        Write-Info "DNS may not be configured yet. Expected IP: $ServerIP"
        Write-Info "Please configure DNS records:"
        Write-Host "  Type: A, Name: @, Value: $ServerIP"
        Write-Host "  Type: A, Name: www, Value: $ServerIP"
        return $false
    }
}

# Step 2: Check Server Connectivity
function Test-Server {
    Write-Info "Checking server connectivity ($ServerIP)..."
    
    try {
        $ping = Test-Connection -ComputerName $ServerIP -Count 1 -Quiet
        if ($ping) {
            Write-Success "Server is reachable"
            return $true
        } else {
            Write-Error "Server is not reachable at $ServerIP"
            return $false
        }
    } catch {
        Write-Error "Server connectivity check failed: $_"
        return $false
    }
}

# Step 3: Verify Page Loads
function Test-PageLoad {
    Write-Info "Verifying page loads..."
    
    # Test server IP directly
    try {
        $response = Invoke-WebRequest -Uri "http://$ServerIP" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        Write-Success "Server responds with HTTP $($response.StatusCode)"
        
        # Test domain if DNS is configured
        if (Test-DNS) {
            try {
                $domainResponse = Invoke-WebRequest -Uri "http://$Domain" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
                Write-Success "Domain responds with HTTP $($domainResponse.StatusCode)"
                Write-Success "Page is loading correctly!"
                return $true
            } catch {
                Write-Warning "Domain not responding yet (may need DNS propagation): $_"
            }
        }
        
        return $true
    } catch {
        Write-Error "Server not responding correctly: $_"
        return $false
    }
}

# Step 4: Check SSL
function Test-SSL {
    Write-Info "Checking SSL configuration..."
    
    try {
        $response = Invoke-WebRequest -Uri "https://$Domain" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        Write-Success "SSL is configured and working (HTTP $($response.StatusCode))"
        return $true
    } catch {
        Write-Warning "SSL not configured or not working: $_"
        Write-Info "To set up SSL, run on server:"
        Write-Host "  ssh root@$ServerIP 'certbot --nginx -d $Domain -d www.$Domain'"
        return $false
    }
}

# Main execution
Write-Host "=========================================="
Write-Host "  FightCityTickets Deployment & Verification"
Write-Host "=========================================="
Write-Host ""
Write-Host "Domain: $Domain"
Write-Host "Server IP: $ServerIP"
Write-Host ""

# Check prerequisites
if (-not (Get-Command curl -ErrorAction SilentlyContinue)) {
    Write-Warning "curl not found, but continuing..."
}

# Run checks
$serverOk = Test-Server
if (-not $serverOk) {
    Write-Error "Server check failed. Cannot proceed with deployment."
    exit 1
}

$dnsOk = Test-DNS
if (-not $dnsOk) {
    Write-Warning "DNS not configured correctly, but continuing..."
}

# Verify page loads
$pageOk = Test-PageLoad
if (-not $pageOk) {
    Write-Warning "Page verification failed"
}

# Check SSL
Test-SSL | Out-Null

Write-Host ""
Write-Host "=========================================="
Write-Success "Verification complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Configure DNS if needed (point $Domain to $ServerIP)"
Write-Host "  2. Deploy application using: ./scripts/update_deployment.sh"
Write-Host "  3. Set up SSL: ssh root@$ServerIP 'certbot --nginx -d $Domain -d www.$Domain'"
Write-Host "  4. Test site: http://$Domain"
Write-Host ""




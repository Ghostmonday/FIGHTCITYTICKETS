# PowerShell script to check Hetzner server
$serverIP = "5.161.239.203"
$username = "root"
$password = "170cdwfqwQ-E1SKQ-_UXUVuU"

# Install SSH module if needed
if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "Installing Posh-SSH module..."
    Install-Module -Name Posh-SSH -Force -Scope CurrentUser
}

Import-Module Posh-SSH

# Create credential
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($username, $securePassword)

# Connect and run commands
$session = New-SSHSession -ComputerName $serverIP -Credential $credential -AcceptKey

if ($session) {
    Write-Host "Connected successfully!"
    
    # Check current directory and files
    $result1 = Invoke-SSHCommand -SessionId $session.SessionId -Command "pwd && ls -la"
    Write-Host "`n=== Current Directory ===" 
    Write-Host $result1.Output
    
    # Check Docker containers
    $result2 = Invoke-SSHCommand -SessionId $session.SessionId -Command "docker ps -a"
    Write-Host "`n=== Docker Containers ===" 
    Write-Host $result2.Output
    
    # Check deployment directory
    $result3 = Invoke-SSHCommand -SessionId $session.SessionId -Command "cd /var/www && ls -la 2>/dev/null || echo 'Directory not found'"
    Write-Host "`n=== /var/www Directory ===" 
    Write-Host $result3.Output
    
    # Check if fightcitytickets directory exists
    $result4 = Invoke-SSHCommand -SessionId $session.SessionId -Command "cd /var/www/fightcitytickets && pwd && ls -la 2>/dev/null || echo 'Directory not found'"
    Write-Host "`n=== /var/www/fightcitytickets ===" 
    Write-Host $result4.Output
    
    # Check docker-compose status
    $result5 = Invoke-SSHCommand -SessionId $session.SessionId -Command "cd /var/www/fightcitytickets && docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null || echo 'docker-compose not found'"
    Write-Host "`n=== Docker Compose Status ===" 
    Write-Host $result5.Output
    
    # Check nginx status
    $result6 = Invoke-SSHCommand -SessionId $session.SessionId -Command "systemctl status nginx --no-pager 2>/dev/null | head -20 || nginx -v 2>&1"
    Write-Host "`n=== Nginx Status ===" 
    Write-Host $result6.Output
    
    # Check environment files
    $result7 = Invoke-SSHCommand -SessionId $session.SessionId -Command "cd /var/www/fightcitytickets && find . -name '.env*' -type f 2>/dev/null | head -5"
    Write-Host "`n=== Environment Files ===" 
    Write-Host $result7.Output
    
    # Check git status
    $result8 = Invoke-SSHCommand -SessionId $session.SessionId -Command "cd /var/www/fightcitytickets && git status 2>/dev/null || echo 'Not a git repo'"
    Write-Host "`n=== Git Status ===" 
    Write-Host $result8.Output
    
    Remove-SSHSession -SessionId $session.SessionId
} else {
    Write-Host "Failed to connect to server"
}
















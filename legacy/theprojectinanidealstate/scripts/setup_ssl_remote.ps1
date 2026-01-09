# PowerShell script to set up SSL on remote server
# Run from Windows PowerShell

$SERVER_IP = "178.156.215.100"
$SERVER_USER = "root"
$DOMAIN = "fightcitytickets.com"

Write-Host "🔒 Setting up SSL for $DOMAIN on $SERVER_IP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Upload SSL setup scripts
Write-Host "`n📤 Uploading SSL setup scripts..." -ForegroundColor Yellow
scp scripts/setup_ssl.sh "${SERVER_USER}@${SERVER_IP}:/tmp/setup_ssl.sh"
scp scripts/configure_nginx_ssl.sh "${SERVER_USER}@${SERVER_IP}:/tmp/configure_nginx_ssl.sh"

# Make scripts executable and run
Write-Host "`n🚀 Running SSL setup on server..." -ForegroundColor Yellow
ssh "${SERVER_USER}@${SERVER_IP}" "chmod +x /tmp/setup_ssl.sh /tmp/configure_nginx_ssl.sh && /tmp/setup_ssl.sh"

Write-Host "`n🔧 Configuring Nginx for SSL..." -ForegroundColor Yellow
ssh "${SERVER_USER}@${SERVER_IP}" "/tmp/configure_nginx_ssl.sh"

# Cleanup
Write-Host "`n🧹 Cleaning up..." -ForegroundColor Yellow
ssh "${SERVER_USER}@${SERVER_IP}" "rm /tmp/setup_ssl.sh /tmp/configure_nginx_ssl.sh"

# Test HTTPS
Write-Host "`n🧪 Testing HTTPS..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "https://$DOMAIN" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ HTTPS is working! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "`n🌐 Your site is now available at:" -ForegroundColor Green
    Write-Host "   https://$DOMAIN" -ForegroundColor White
    Write-Host "   https://www.$DOMAIN" -ForegroundColor White
} catch {
    Write-Host "⚠️  HTTPS test failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   This might be normal if DNS is still propagating or Nginx needs a moment to restart." -ForegroundColor Gray
    Write-Host "   Try again in a few minutes." -ForegroundColor Gray
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "✅ SSL setup complete!" -ForegroundColor Green


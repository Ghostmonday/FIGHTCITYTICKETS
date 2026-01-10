$smtpServer = "127.0.0.1"
$smtpPort = 1025
$username = "NeuralDraftLLC@pm.me"
$password = "xwJEhrVNZxk8h969pRlxGw"
$from = "NeuralDraftLLC@pm.me"
$to = "support@digitalocean.com"
$subject = "URGENT: Instance has no outbound network / NIC down (NO-CARRIER, no default route)"

$body = @"
Hello DigitalOcean Support,

I have an Ubuntu 24.04.3 LTS droplet in the SFO3 region that currently has no outbound network connectivity.

Symptoms (confirmed at OS level):
- Primary interface reports NO-CARRIER and state DOWN
- No default route present
- ping 8.8.8.8 returns Network is unreachable
- DNS resolution fails due to no route to host
- All outbound traffic is blocked (HTTPS, package updates, Certbot, etc.)

Evidence:
- ip addr show indicates the primary NIC is down (NO-CARRIER)
- ip route shows no default gateway
- Issue persists after restarting networking and systemd-resolved

This appears to be a provider-level NIC attachment or routing issue, not an OS misconfiguration.

Please investigate:
- NIC attachment for this droplet
- Default gateway and routing at the hypervisor or VPC level
- Any account or network-level restrictions affecting outbound traffic

This instance is currently non-functional until routing is restored.

Best regards,
Amir
"@

$smtp = New-Object Net.Mail.SmtpClient($smtpServer, $smtpPort)
$smtp.EnableSsl = $true
$smtp.Credentials = New-Object Net.NetworkCredential($username, $password)
$smtp.Send($from, $to, $subject, $body)
Write-Host "EMAIL SENT"

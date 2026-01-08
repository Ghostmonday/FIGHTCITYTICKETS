# Memory Optimization Script
# Safely terminates non-critical processes to free memory

param(
    [switch]$DryRun = $false,
    [int]$MinMemoryMB = 100  # Only terminate processes using more than this amount
)

Write-Host "=== Memory Optimization Script ===" -ForegroundColor Cyan
Write-Host ""

# Get current memory status
$totalMemory = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
$freeMemory = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
$usedMemory = $totalMemory - $freeMemory
$usagePercent = ($usedMemory / $totalMemory) * 100

Write-Host "Current Memory Status:" -ForegroundColor Yellow
Write-Host "  Total RAM: $([math]::Round($totalMemory, 2)) GB" -ForegroundColor White
Write-Host "  Used RAM: $([math]::Round($usedMemory, 2)) GB ($([math]::Round($usagePercent, 1))%)" -ForegroundColor $(if($usagePercent -gt 80){"Red"}elseif($usagePercent -gt 60){"Yellow"}else{"Green"})
Write-Host "  Free RAM: $([math]::Round($freeMemory, 2)) GB" -ForegroundColor Green
Write-Host ""

# Critical system processes - NEVER terminate
$criticalProcesses = @("csrss", "winlogon", "services", "lsass", "svchost", "explorer", "dwm", "smss", "system", "spoolsv", "wininit", "dwm", "conhost", "audiodg", "winlogon")

# Safe-to-terminate user applications
$safeToTerminate = @(
    "chrome", "firefox", "msedge", "edge", "discord", "spotify", "steam", 
    "notepad", "code", "cursor", "vscode", "slack", "teams", "zoom", 
    "skype", "itunes", "vlc", "winrar", "7z", "acrobat", "acrord32", 
    "reader", "photoshop", "illustrator", "excel", "winword", "powerpnt", 
    "outlook", "thunderbird", "devenv", "idea64", "pycharm64", "goland64",
    "postman", "fiddler", "wireshark", "obs64", "obs32", "obs"
)

# Get processes using significant memory
$processes = Get-Process | Where-Object { 
    $_.WorkingSet64 -gt ($MinMemoryMB * 1MB) -and 
    $criticalProcesses -notcontains $_.ProcessName.ToLower()
} | Sort-Object WorkingSet64 -Descending

Write-Host "Processes Using Significant Memory (>$MinMemoryMB MB):" -ForegroundColor Yellow
Write-Host ""

$totalMemoryFreed = 0
$processesToTerminate = @()

foreach ($proc in $processes) {
    $memMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
    $procName = $proc.ProcessName.ToLower()
    
    $isSafe = $false
    foreach ($safe in $safeToTerminate) {
        if ($procName -eq $safe -or $procName -like "*$safe*") {
            $isSafe = $true
            break
        }
    }
    
    if ($isSafe) {
        $status = "✅ Safe to Terminate"
        $color = "Green"
        $processesToTerminate += $proc
        $totalMemoryFreed += $memMB
    } elseif ($criticalProcesses -contains $procName) {
        $status = "❌ CRITICAL - DO NOT TERMINATE"
        $color = "Red"
    } else {
        $status = "⚠️  Unknown - Check First"
        $color = "Yellow"
    }
    
    Write-Host "$($proc.ProcessName.PadRight(25)) $($memMB.ToString().PadLeft(8)) MB  $status" -ForegroundColor $color
}

Write-Host ""
Write-Host "Total Memory That Can Be Freed: $([math]::Round($totalMemoryFreed, 2)) MB" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No processes were terminated" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to actually terminate processes" -ForegroundColor Yellow
} elseif ($processesToTerminate.Count -eq 0) {
    Write-Host "No safe processes found to terminate" -ForegroundColor Yellow
} else {
    Write-Host "Terminating $($processesToTerminate.Count) processes..." -ForegroundColor Yellow
    Write-Host ""
    
    $terminated = 0
    $failed = 0
    
    foreach ($proc in $processesToTerminate) {
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction Stop
            Write-Host "✅ Terminated: $($proc.ProcessName) ($([math]::Round($proc.WorkingSet64/1MB,2)) MB)" -ForegroundColor Green
            $terminated++
            Start-Sleep -Milliseconds 100
        } catch {
            Write-Host "❌ Failed to terminate: $($proc.ProcessName) - $($_.Exception.Message)" -ForegroundColor Red
            $failed++
        }
    }
    
    Write-Host ""
    Write-Host "Termination Complete:" -ForegroundColor Cyan
    Write-Host "  Successfully terminated: $terminated" -ForegroundColor Green
    Write-Host "  Failed: $failed" -ForegroundColor $(if($failed -gt 0){"Red"}else{"Green"})
    
    # Show new memory status
    Start-Sleep -Seconds 2
    $newFreeMemory = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
    $memoryFreed = $newFreeMemory - $freeMemory
    
    Write-Host ""
    Write-Host "New Memory Status:" -ForegroundColor Yellow
    Write-Host "  Free RAM: $([math]::Round($newFreeMemory, 2)) GB" -ForegroundColor Green
    Write-Host "  Memory Freed: $([math]::Round($memoryFreed, 2)) MB" -ForegroundColor Green
}

Write-Host ""
Write-Host "Script Complete!" -ForegroundColor Green


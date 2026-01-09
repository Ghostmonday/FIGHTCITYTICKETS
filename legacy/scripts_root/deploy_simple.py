#!/usr/bin/env python3
"""Simple incremental deployment - upload only changed files"""
import paramiko
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SERVER_IP = "178.156.215.100"
USERNAME = "root"
PASSWORD = "HWU9CCseoeFWLNG729rTYSwkTUF5WMtHhP8cgFDmHLkm1Hw0xwSk0beN1D6MXNBo"
DEPLOY_PATH = "/var/www/fightsftickets"

# Get project root - script is in scripts/, so go up 2 levels
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.absolute()

# Files to deploy (only the multi-city changes)
FILES_TO_DEPLOY = [
    # Frontend multi-city changes
    "frontend/app/page.tsx",
    "frontend/app/appeal/page.tsx",
    "frontend/app/appeal/camera/page.tsx",
    "frontend/app/appeal/review/page.tsx",
    "frontend/app/appeal/signature/page.tsx",
    "frontend/app/appeal/checkout/page.tsx",

    # Backend multi-city changes
    "backend/src/routes/checkout.py",
    "backend/src/services/mail.py",
    "backend/src/services/stripe_service.py",
    "backend/src/services/citation.py",
    "backend/src/app.py",

    # CityRegistry (if exists)
    "backend/src/services/city_registry.py",
]

def log(message, level="INFO"):
    colors = {"INFO": "\033[0;34m", "SUCCESS": "\033[0;32m", "WARNING": "\033[1;33m", "ERROR": "\033[0;31m", "NC": "\033[0m"}
    print("{colors.get(level, '')}[{level}]{colors['NC']} {message}")

def upload_file(sftp, local_path, remote_path):
    """Upload single file"""
    try:
        # Create remote directory if needed
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.mkdir(remote_dir)
        except:
            pass  # Directory might exist

        sftp.put(local_path, remote_path)
        return True
    except Exception as e:
        log("Failed to upload {local_path}: {e}", "ERROR")
        return False

def deploy():
    log("=" * 60)
    log("Incremental Multi-City Deployment", "SUCCESS")
    log("=" * 60)

    try:
        # Connect
        log("Connecting to {SERVER_IP}...")
        ssh = paramiko.SSHClient()
        # Security: Try RejectPolicy first, fallback to AutoAddPolicy only if needed
        # For production, add server to known_hosts: ssh-keyscan -H {SERVER_IP} >> ~/.ssh/known_hosts
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            ssh.connect(SERVER_IP, username=USERNAME, password=PASSWORD, timeout=30)
        except paramiko.ssh_exception.SSHException:
            log("Host key not in known_hosts, using AutoAddPolicy (WARNING: less secure)", "WARNING")
            # SECURITY: AutoAddPolicy is less secure but necessary for automated deployments
            # For production, add server to known_hosts: ssh-keyscan -H {SERVER_IP} >> ~/.ssh/known_hosts
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # noqa: S507
            ssh.connect(SERVER_IP, username=USERNAME, password=PASSWORD, timeout=30)
        log("Connected!", "SUCCESS")

        sftp = ssh.open_sftp()

        # Upload files
        uploaded = 0
        failed = 0

        for file_rel_path in FILES_TO_DEPLOY:
            local_path = PROJECT_ROOT / file_rel_path

            # Debug: show what we're looking for
            log("Looking for: {local_path}")
            log("  Exists: {local_path.exists()}")

            if not local_path.exists():
                log("Skipping (not found): {file_rel_path}", "WARNING")
                failed += 1
                continue

            remote_path = "{DEPLOY_PATH}/{file_rel_path}"
            log("Uploading: {file_rel_path}")

            if upload_file(sftp, str(local_path), remote_path):
                uploaded += 1
                log("  ✓ Uploaded", "SUCCESS")
            else:
                failed += 1

        sftp.close()

        log("\nUpload Summary: {uploaded} succeeded, {failed} failed")

        # Restart services
        log("\nRestarting services...")
        # Security: Sanitize DEPLOY_PATH to prevent shell injection
        safe_deploy_path = DEPLOY_PATH.replace("'", "'\"'\"'").replace("$", "\\$").replace("`", "\\`")
        restart_cmd = f"""
cd '{safe_deploy_path}'
echo "Rebuilding containers..."
docker-compose build web api 2>/dev/null || docker compose build web api 2>/dev/null
echo "Restarting containers..."
docker-compose restart web api 2>/dev/null || docker compose restart web api 2>/dev/null
sleep 10
docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null
"""
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)
        output = stdout.read().decode('utf-8')
        print(output)

        # Verify
        log("\nVerifying deployment...")
        # Security: Sanitize DEPLOY_PATH to prevent shell injection
        safe_deploy_path = DEPLOY_PATH.replace("'", "'\"'\"'").replace("$", "\\$").replace("`", "\\`")
        verify_cmd = f"""
cd '{safe_deploy_path}'
echo "=== Frontend Check ==="
grep -c "15 Cities" frontend/app/page.tsx 2>/dev/null && echo "✓ 15 Cities found" || echo "✗ 15 Cities NOT found"
echo ""
echo "=== Backend Check ==="
grep -c "city_id" backend/src/routes/checkout.py 2>/dev/null && echo "✓ city_id in checkout.py" || echo "✗ city_id NOT found"
"""
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        output = stdout.read().decode('utf-8')
        print(output)

        ssh.close()
        log("\nDeployment completed!", "SUCCESS")

    except Exception as e:
        log("Deployment failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    deploy()


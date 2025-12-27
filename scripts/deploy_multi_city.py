#!/usr/bin/env python3
"""Deploy latest multi-city code to Hetzner server"""
import paramiko
import tarfile
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Server configuration
SERVER_IP = "178.156.215.100"
USERNAME = "root"
PASSWORD = "HWU9CCseoeFWLNG729rTYSwkTUF5WMtHhP8cgFDmHLkm1Hw0xwSk0beN1D6MXNBo"
DEPLOY_PATH = "/var/www/fightsftickets"
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Exclude patterns for deployment
EXCLUDE_PATTERNS = [
    '.git',
    '.next',
    'node_modules',
    '__pycache__',
    '*.pyc',
    '.venv',
    'venv',
    '.env',
    '.env.local',
    '*.log',
    '.DS_Store',
    'docs/archive',
    '*.md',
    'scripts/temp_ssh_key',
    'scripts/check_server.py',
    'scripts/check_deployed_code.py',
    'SERVER_DEPLOYMENT_STATUS.md',
    'REALITY_CHECK.md',
    'SYSTEM_TEST_REPORT.md',
    'HONEST_CITY_STATUS.md',
    'REVENUE_PROJECTION.md',
    'CITY_STATUS.md',
]

def log(message, level="INFO"):
    """Print colored log message"""
    colors = {
        "INFO": "\033[0;34m",
        "SUCCESS": "\033[0;32m",
        "WARNING": "\033[1;33m",
        "ERROR": "\033[0;31m",
        "NC": "\033[0m"
    }
    prefix = "[{level}]"
    print("{colors.get(level, '')}{prefix}{colors['NC']} {message}")

def should_exclude(path):
    """Check if path should be excluded from deployment"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def create_deployment_archive():
    """Create tar.gz archive of codebase"""
    log("Creating deployment archive...")

    temp_dir = tempfile.mkdtemp()
    archive_path = os.path.join(temp_dir, "deployment.tar.gz")

    with tarfile.open(archive_path, "w:gz") as tar:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)

                if not should_exclude(file_path):
                    try:
                        tar.add(file_path, arcname=rel_path)
                    except Exception as e:
                        log("Warning: Could not add {rel_path}: {e}", "WARNING")

    log("Archive created: {archive_path} ({os.path.getsize(archive_path) / 1024 / 1024:.2f} MB)")
    return archive_path

def run_ssh_command(ssh, command, description=""):
    """Run SSH command and return output"""
    if description:
        log(description)
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    exit_status = stdout.channel.recv_exit_status()

    if exit_status != 0:
        log("Command failed (exit {exit_status}): {command}", "ERROR")
        if error:
            log("Error: {error}", "ERROR")

    return output, error, exit_status

def upload_file(ssh, local_path, remote_path):
    """Upload file via SFTP"""
    log("Uploading {os.path.basename(local_path)}...")
    sftp = ssh.open_sftp()
    try:
        sftp.put(local_path, remote_path)
        log("Uploaded to {remote_path}", "SUCCESS")
    finally:
        sftp.close()

def deploy():
    """Main deployment function"""
    log("=" * 60)
    log("Multi-City Code Deployment", "SUCCESS")
    log("=" * 60)

    # Step 1: Create archive
    archive_path = create_deployment_archive()

    try:
        # Step 2: Connect to server
        log("Connecting to {SERVER_IP}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, username=USERNAME, password=PASSWORD, timeout=30)
        log("Connected successfully!", "SUCCESS")

        # Step 3: Backup current deployment
        log("Creating backup...")
        backup_cmd = """
cd {DEPLOY_PATH}
BACKUP_DIR="/var/backups/fightsftickets"
mkdir -p $BACKUP_DIR
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf $BACKUP_DIR/$BACKUP_NAME backend frontend docker-compose.yml .env 2>/dev/null || true
echo "Backup created: $BACKUP_DIR/$BACKUP_NAME"
"""
        run_ssh_command(ssh, backup_cmd, "Backing up current deployment...")

        # Step 4: Upload archive
        remote_archive = "/tmp/deployment_{os.getpid()}.tar.gz"
        upload_file(ssh, archive_path, remote_archive)

        # Step 5: Extract archive
        log("Extracting deployment archive...")
        extract_cmd = """
cd {DEPLOY_PATH}
tar -xzf {remote_archive} --strip-components=0 2>&1 || tar -xzf {remote_archive} 2>&1
rm -f {remote_archive}
echo "Extraction completed"
"""
        run_ssh_command(ssh, extract_cmd)

        # Step 6: Rebuild and restart services
        log("Rebuilding Docker containers...")
        rebuild_cmd = """
cd {DEPLOY_PATH}
echo "Stopping services..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
echo "Building services..."
docker-compose build --no-cache 2>/dev/null || docker compose build --no-cache 2>/dev/null
echo "Starting services..."
docker-compose up -d 2>/dev/null || docker compose up -d 2>/dev/null
echo "Waiting for services to start..."
sleep 15
docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null
"""
        output, _, _ = run_ssh_command(ssh, rebuild_cmd)
        print(output)

        # Step 7: Verify deployment
        log("Verifying deployment...")
        verify_cmd = """
sleep 5
curl -f http://localhost:8000/health 2>/dev/null && echo " - API Health: OK" || echo " - API Health: FAILED"
curl -f http://localhost:3000 2>/dev/null > /dev/null && echo " - Frontend: OK" || echo " - Frontend: FAILED"
"""
        output, _, _ = run_ssh_command(ssh, verify_cmd)
        print(output)

        # Step 8: Check for multi-city code
        log("Verifying multi-city code deployment...")
        check_cmd = """
cd {DEPLOY_PATH}
echo "=== Frontend Multi-City Check ==="
grep -c "15 Cities" frontend/app/page.tsx 2>/dev/null && echo "✓ Frontend: 15 Cities found" || echo "✗ Frontend: 15 Cities NOT found"
grep -c "formatCityName" frontend/app/page.tsx 2>/dev/null && echo "✓ Frontend: formatCityName found" || echo "✗ Frontend: formatCityName NOT found"
echo ""
echo "=== Backend Multi-City Check ==="
grep -c "city_id" backend/src/routes/checkout.py 2>/dev/null && echo "✓ Backend: city_id in checkout.py" || echo "✗ Backend: city_id NOT in checkout.py"
grep -c "CityRegistry" backend/src/services/mail.py 2>/dev/null && echo "✓ Backend: CityRegistry in mail.py" || echo "✗ Backend: CityRegistry NOT in mail.py"
find backend -name "*city*" -o -name "*registry*" 2>/dev/null | head -5 && echo "✓ CityRegistry files found" || echo "✗ CityRegistry files NOT found"
"""
        output, _, _ = run_ssh_command(ssh, check_cmd)
        print(output)

        ssh.close()
        log("Deployment completed!", "SUCCESS")

    except Exception as e:
        log("Deployment failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup local archive
        if os.path.exists(archive_path):
            os.remove(archive_path)
            log("Cleaned up local archive")

if __name__ == "__main__":
    deploy()
















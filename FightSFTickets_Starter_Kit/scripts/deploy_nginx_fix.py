#!/usr/bin/env python3
"""Deploy nginx fix and updated docker-compose.yml"""
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
DEPLOY_PATH = "/var/www/fightcitytickets"

# Get project root - script is in scripts/, so go up 2 levels
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.absolute()

# Files to deploy
FILES_TO_DEPLOY = [
    "docker-compose.yml",
    "nginx/nginx.conf",
    "nginx/conf.d/fightcitytickets.conf",
    "scripts/fix_deployment.sh",
]

def log(message, level="INFO"):
    colors = {"INFO": "\033[0;34m", "SUCCESS": "\033[0;32m", "WARNING": "\033[1;33m", "ERROR": "\033[0;31m", "NC": "\033[0m"}
    print(f"{colors.get(level, '')}[{level}]{colors['NC']} {message}")

def upload_file(sftp, local_path, remote_path):
    """Upload single file"""
    try:
        # Create remote directory if needed
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.mkdir(remote_dir)
        except:
            pass  # Directory might exist
        # Create parent directories recursively
        parts = remote_dir.split('/')
        current_path = ''
        for part in parts:
            if part:
                current_path += '/' + part
                try:
                    sftp.mkdir(current_path)
                except:
                    pass

        sftp.put(str(local_path), remote_path)
        return True
    except Exception as e:
        log(f"Failed to upload {local_path}: {e}", "ERROR")
        return False

def deploy():
    log("=" * 60)
    log("Deploying Nginx Fix", "SUCCESS")
    log("=" * 60)

    try:
        # Connect
        log(f"Connecting to {SERVER_IP}...")
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

            if not local_path.exists():
                log(f"Skipping (not found): {file_rel_path}", "WARNING")
                failed += 1
                continue

            remote_path = f"{DEPLOY_PATH}/{file_rel_path}"
            log(f"Uploading: {file_rel_path}")

            if upload_file(sftp, local_path, remote_path):
                uploaded += 1
                log(f"  ✓ Uploaded", "SUCCESS")
            else:
                failed += 1

        sftp.close()

        log(f"\nUpload Summary: {uploaded} succeeded, {failed} failed")

        # Stop existing containers
        log("\nStopping existing containers...")
        stop_cmd = f"""
cd {DEPLOY_PATH}
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
"""
        stdin, stdout, stderr = ssh.exec_command(stop_cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if output:
            print(output)
        if error:
            print(error)

        # Create nginx directories if they don't exist
        log("\nCreating nginx directories...")
        mkdir_cmd = f"""
cd {DEPLOY_PATH}
mkdir -p nginx/conf.d
chmod 755 nginx
chmod 755 nginx/conf.d
"""
        stdin, stdout, stderr = ssh.exec_command(mkdir_cmd)
        output = stdout.read().decode('utf-8')
        if output:
            print(output)

        # Restart services with new configuration
        log("\nStarting services with nginx...")
        restart_cmd = f"""
cd {DEPLOY_PATH}
echo "Building and starting containers..."
docker-compose up -d --build 2>&1 || docker compose up -d --build 2>&1
sleep 5
echo ""
echo "=== Container Status ==="
docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null
"""
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        print(output)
        if error:
            print(error)

        # Verify nginx is running
        log("\nVerifying nginx container...")
        verify_cmd = f"""
cd {DEPLOY_PATH}
echo "=== Checking nginx container ==="
docker-compose ps nginx 2>/dev/null || docker compose ps nginx 2>/dev/null
echo ""
echo "=== Testing HTTP endpoint ==="
curl -s -o /dev/null -w "HTTP Status: %{{http_code}}\n" http://localhost/health || echo "HTTP test failed"
echo ""
echo "=== Recent nginx logs ==="
docker-compose logs --tail=10 nginx 2>/dev/null || docker compose logs --tail=10 nginx 2>/dev/null || echo "No nginx logs"
"""
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        output = stdout.read().decode('utf-8')
        print(output)

        ssh.close()
        log("\nDeployment completed!", "SUCCESS")
        log("\nNext steps:")
        log("1. Verify DNS is pointing to the server: nslookup fightcitytickets.com")
        log("2. Set up SSL: certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com")
        log("3. Test the site: curl http://fightcitytickets.com")

    except Exception as e:
        log(f"Deployment failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    deploy()


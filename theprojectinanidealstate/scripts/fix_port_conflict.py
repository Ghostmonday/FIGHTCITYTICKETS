#!/usr/bin/env python3
"""Fix port 80 conflict and restart nginx"""
import paramiko
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SERVER_IP = "178.156.215.100"
USERNAME = "root"
PASSWORD = "HWU9CCseoeFWLNG729rTYSwkTUF5WMtHhP8cgFDmHLkm1Hw0xwSk0beN1D6MXNBo"
DEPLOY_PATH = "/var/www/fightcitytickets"

def log(message, level="INFO"):
    colors = {"INFO": "\033[0;34m", "SUCCESS": "\033[0;32m", "WARNING": "\033[1;33m", "ERROR": "\033[0;31m", "NC": "\033[0m"}
    print(f"{colors.get(level, '')}[{level}]{colors['NC']} {message}")

def main():
    try:
        log("Connecting to server...")
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

        # Check what's using port 80
        log("\nChecking what's using port 80...")
        check_port_cmd = "netstat -tulpn | grep :80 || ss -tulpn | grep :80 || lsof -i :80 || echo 'Cannot check port'"
        stdin, stdout, stderr = ssh.exec_command(check_port_cmd)
        output = stdout.read().decode('utf-8')
        print(output)

        # Stop system nginx if running
        log("\nStopping system nginx (if running)...")
        stop_nginx_cmd = """
systemctl stop nginx 2>/dev/null || service nginx stop 2>/dev/null || true
systemctl disable nginx 2>/dev/null || true
"""
        stdin, stdout, stderr = ssh.exec_command(stop_nginx_cmd)
        output = stdout.read().decode('utf-8')
        if output:
            print(output)

        # Stop apache if running
        log("\nStopping apache (if running)...")
        stop_apache_cmd = """
systemctl stop apache2 2>/dev/null || service apache2 stop 2>/dev/null || true
systemctl disable apache2 2>/dev/null || true
"""
        stdin, stdout, stderr = ssh.exec_command(stop_apache_cmd)
        output = stdout.read().decode('utf-8')
        if output:
            print(output)

        # Kill any process on port 80
        log("\nKilling processes on port 80...")
        kill_port_cmd = """
fuser -k 80/tcp 2>/dev/null || true
"""
        stdin, stdout, stderr = ssh.exec_command(kill_port_cmd)
        output = stdout.read().decode('utf-8')
        if output:
            print(output)

        # Wait a moment
        import time
        time.sleep(2)

        # Restart docker containers
        log("\nRestarting docker containers...")
        restart_cmd = f"""
cd {DEPLOY_PATH}
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
sleep 2
docker-compose up -d 2>&1 || docker compose up -d 2>&1
sleep 5
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
echo "=== Container Status ==="
docker-compose ps nginx 2>/dev/null || docker compose ps nginx 2>/dev/null
echo ""
echo "=== Testing HTTP endpoint ==="
curl -s -o /dev/null -w "HTTP Status: %{{http_code}}\n" http://localhost/health || echo "HTTP test failed"
echo ""
echo "=== Nginx logs ==="
docker-compose logs --tail=20 nginx 2>/dev/null || docker compose logs --tail=20 nginx 2>/dev/null || echo "No nginx logs"
"""
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        output = stdout.read().decode('utf-8')
        print(output)

        ssh.close()
        log("\nPort conflict fix completed!", "SUCCESS")

    except Exception as e:
        log(f"Failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


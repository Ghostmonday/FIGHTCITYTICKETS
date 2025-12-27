#!/usr/bin/env python3
"""Check Hetzner server deployment status"""
import paramiko
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Try both IPs - user provided 5.161.239.203, but scripts reference 178.156.215.100
SERVER_IPS = ["5.161.239.203", "178.156.215.100"]
USERNAME = "root"
PASSWORD = "HWU9CCseoeFWLNG729rTYSwkTUF5WMtHhP8cgFDmHLkm1Hw0xwSk0beN1D6MXNBo"

def run_command(ssh, command):
    """Run a command via SSH and return output"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    exit_status = stdout.channel.recv_exit_status()
    return output, error, exit_status

def main():
    ssh = None
    connected_ip = None

    # Try each IP and port combination
    ports = [22, 2222, 22022]  # Common SSH ports

    for server_ip in SERVER_IPS:
        for port in ports:
            print("Trying to connect to {server_ip}:{port}...")
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(server_ip, port=port, username=USERNAME, password=PASSWORD, timeout=10)
                print("[OK] Connected successfully to {server_ip}:{port}!\n")
                connected_ip = server_ip
                break
            except Exception as e:
                print("[FAIL] {server_ip}:{port} - {str(e)[:50]}")
                if ssh:
                    ssh.close()
                ssh = None
        if ssh:
            break

    if not ssh:
        print("\n[ERROR] Could not connect to any server IP/port combination")
        print("\nTroubleshooting:")
        print("1. Check if server is running")
        print("2. Check firewall settings")
        print("3. Verify IP addresses are correct")
        print("4. Check if SSH is enabled on the server")
        sys.exit(1)

    try:

        # Check current directory
        print("=" * 60)
        print("CURRENT DIRECTORY")
        print("=" * 60)
        output, _, _ = run_command(ssh, "pwd")
        print(output)

        # List files
        print("=" * 60)
        print("ROOT DIRECTORY CONTENTS")
        print("=" * 60)
        output, _, _ = run_command(ssh, "ls -la")
        print(output)

        # Check Docker containers
        print("=" * 60)
        print("DOCKER CONTAINERS")
        print("=" * 60)
        output, _, _ = run_command(ssh, "docker ps -a")
        print(output)

        # Check deployment directory
        print("=" * 60)
        print("/var/www DIRECTORY")
        print("=" * 60)
        output, _, _ = run_command(ssh, "ls -la /var/www 2>/dev/null || echo 'Directory not found'")
        print(output)

        # Check fightsftickets directory (actual name on server)
        print("=" * 60)
        print("/var/www/fightsftickets DIRECTORY")
        print("=" * 60)
        output, _, _ = run_command(ssh, "cd /var/www/fightsftickets && pwd && ls -la 2>/dev/null || echo 'Directory not found'")
        print(output)

        # Check where docker-compose is running from
        print("=" * 60)
        print("DOCKER COMPOSE WORKING DIRECTORY")
        print("=" * 60)
        output, _, _ = run_command(ssh, "docker inspect fightsftickets_web_1 --format '{{.Config.Labels}}' 2>/dev/null || echo 'Cannot inspect container'")
        print(output)

        # Find docker-compose files
        print("=" * 60)
        print("FINDING DOCKER-COMPOSE FILES")
        print("=" * 60)
        output, _, _ = run_command(ssh, "find /var/www -name 'docker-compose*.yml' -o -name 'compose*.yml' 2>/dev/null | head -10")
        print(output)

        # Check docker-compose process
        print("=" * 60)
        print("DOCKER COMPOSE PROCESS INFO")
        print("=" * 60)
        output, _, _ = run_command(ssh, "ps aux | grep -i docker-compose | grep -v grep || echo 'No docker-compose process found'")
        print(output)


        # Check nginx status
        print("=" * 60)
        print("NGINX STATUS")
        print("=" * 60)
        output, _, _ = run_command(ssh, "systemctl status nginx --no-pager 2>/dev/null | head -20 || nginx -v 2>&1")
        print(output)

        # Check environment files
        print("=" * 60)
        print("ENVIRONMENT FILES")
        print("=" * 60)
        output, _, _ = run_command(ssh, "find /var/www/fightsftickets -name '.env*' -type f 2>/dev/null | head -10")
        print(output)

        # Check git status
        print("=" * 60)
        print("GIT STATUS")
        print("=" * 60)
        output, _, _ = run_command(ssh, "cd /var/www/fightsftickets && git status 2>/dev/null || echo 'Not a git repo'")
        print(output)

        # Check git branch
        print("=" * 60)
        print("GIT BRANCH")
        print("=" * 60)
        output, _, _ = run_command(ssh, "cd /var/www/fightsftickets && git branch -a 2>/dev/null || echo 'Not a git repo'")
        print(output)

        # Check backend code structure
        print("=" * 60)
        print("BACKEND CODE STRUCTURE")
        print("=" * 60)
        output, _, _ = run_command(ssh, "find /var/www/fightsftickets -type f -name '*.py' 2>/dev/null | head -20 || echo 'No Python files found'")
        print(output)

        # Check frontend code structure
        print("=" * 60)
        print("FRONTEND CODE STRUCTURE")
        print("=" * 60)
        output, _, _ = run_command(ssh, "find /var/www/fightsftickets -type f \\( -name '*.tsx' -o -name '*.ts' -o -name '*.jsx' -o -name '*.js' \\) 2>/dev/null | head -20 || echo 'No frontend files found'")
        print(output)

        # Check container volumes and mounts
        print("=" * 60)
        print("CONTAINER VOLUMES AND MOUNTS")
        print("=" * 60)
        output, _, _ = run_command(ssh, "docker inspect fightsftickets_api_1 --format '{{json .Mounts}}' 2>/dev/null | python3 -m json.tool 2>/dev/null || docker inspect fightsftickets_api_1 --format '{{.Mounts}}' 2>/dev/null")
        print(output)

        # Check recent logs
        print("=" * 60)
        print("RECENT BACKEND LOGS (last 30 lines)")
        print("=" * 60)
        output, _, _ = run_command(ssh, "docker logs --tail=30 fightsftickets_api_1 2>&1 || echo 'No logs found'")
        print(output)

        # Check recent frontend logs
        print("=" * 60)
        print("RECENT FRONTEND LOGS (last 30 lines)")
        print("=" * 60)
        output, _, _ = run_command(ssh, "docker logs --tail=30 fightsftickets_web_1 2>&1 || echo 'No logs found'")
        print(output)

        # Check nginx config
        print("=" * 60)
        print("NGINX CONFIGURATION")
        print("=" * 60)
        output, _, _ = run_command(ssh, "ls -la /etc/nginx/sites-enabled/ 2>/dev/null && cat /etc/nginx/sites-enabled/* 2>/dev/null | head -50 || echo 'Cannot read nginx config'")
        print(output)

        print("\n[OK] Disconnected")

    except Exception as e:
        print("[ERROR] Error during execution: {e}")
        sys.exit(1)
    finally:
        if ssh:
            ssh.close()

if __name__ == "__main__":
    main()


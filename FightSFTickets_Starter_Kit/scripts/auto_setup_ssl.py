#!/usr/bin/env python3
"""
Automated SSL Setup Script
Checks DNS, then sets up SSL certificate automatically
"""

import socket
import subprocess
import sys
import time

DOMAIN = "fightsftickets.com"  # CORRECTED domain name
SERVER_IP = "178.156.215.100"
SERVER_USER = "root"

def check_dns(hostname, expected_ip):
    """Check if DNS resolves to expected IP."""
    try:
        ip = socket.gethostbyname(hostname)
        return ip == expected_ip, ip
    except socket.gaierror:
        return False, None

def wait_for_dns(max_wait=300):
    """Wait for DNS to be configured."""
    print("Waiting for DNS to be configured...")
    print("Make sure you've set up DNS in Namecheap first!")
    print()

    start_time = time.time()
    check_count = 0

    while time.time() - start_time < max_wait:
        check_count += 1
        root_ok, root_ip = check_dns(DOMAIN, SERVER_IP)
        www_ok, www_ip = check_dns("www.{DOMAIN}", SERVER_IP)

        if check_count % 6 == 0:  # Print status every 30 seconds
            print("[{int(time.time() - start_time)}s] Checking DNS...")
            if root_ip:
                print("  {DOMAIN} -> {root_ip} {'[OK]' if root_ok else '[WRONG IP]'}")
            if www_ip:
                print("  www.{DOMAIN} -> {www_ip} {'[OK]' if www_ok else '[WRONG IP]'}")

        if root_ok and www_ok:
            print()
            print("[OK] DNS is configured correctly!")
            print("  {DOMAIN} -> {root_ip}")
            print("  www.{DOMAIN} -> {www_ip}")
            return True

        time.sleep(5)

    print()
    print("[ERROR] DNS not configured after waiting. Please configure DNS first.")
    return False

def setup_ssl_via_ssh():
    """SSH into server and set up SSL."""
    print()
    print("=" * 60)
    print("Setting up SSL certificate...")
    print("=" * 60)
    print()

    # Commands to run on server
    commands = """
set -e
echo "Installing Certbot..."
apt-get update -qq
apt-get install -y certbot python3-certbot-nginx

echo ""
echo "Getting SSL certificate..."
certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect

echo ""
echo "Setting up auto-renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "Verifying certificate..."
certbot certificates

echo ""
echo "[OK] SSL setup complete!"
"""

    print("Connecting to server and setting up SSL...")
    print("(This may take a few minutes)")
    print()

    try:
        # SSH and run commands
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "{SERVER_USER}@{SERVER_IP}",
            "bash -s"
        ]

        process = subprocess.Popen(
            ssh_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=commands, timeout=300)

        if process.returncode == 0:
            print(stdout)
            print()
            print("=" * 60)
            print("[OK] SSL certificate installed successfully!")
            print("=" * 60)
            print()
            print("Your site is now available at:")
            print("  https://{DOMAIN}")
            print("  https://www.{DOMAIN}")
            print()
            return True
        else:
            print("[ERROR] SSL setup failed:")
            print(stderr)
            return False

    except subprocess.TimeoutExpired:
        print("[ERROR] SSL setup timed out")
        return False
    except Exception as e:
        print("[ERROR] Failed to set up SSL: {e}")
        print()
        print("You may need to set up SSL manually:")
        print("  ssh {SERVER_USER}@{SERVER_IP}")
        print("  certbot --nginx -d {DOMAIN} -d www.{DOMAIN}")
        return False

def main():
    print("=" * 60)
    print("Automated SSL Setup for fightcitytickets.com")
    print("=" * 60)
    print()
    print("This script will:")
    print("1. Check if DNS is configured")
    print("2. Wait for DNS to propagate (if needed)")
    print("3. Set up SSL certificate automatically")
    print()
    print("IMPORTANT: Make sure DNS is configured in Namecheap first!")
    print("See: DNS_QUICK_SETUP.md for DNS setup instructions")
    print()
    print("Starting automated setup...")
    print()

    # Check DNS first
    print("Step 1: Checking DNS configuration...")
    root_ok, root_ip = check_dns(DOMAIN, SERVER_IP)
    www_ok, www_ip = check_dns("www.{DOMAIN}", SERVER_IP)

    if root_ok and www_ok:
        print("[OK] DNS is already configured!")
        print("  {DOMAIN} -> {root_ip}")
        print("  www.{DOMAIN} -> {www_ip}")
    else:
        print("[WARNING] DNS not configured yet")
        if root_ip:
            print("  {DOMAIN} -> {root_ip} (expected {SERVER_IP})")
        else:
            print("  {DOMAIN} -> Not resolving")
        if www_ip:
            print("  www.{DOMAIN} -> {www_ip} (expected {SERVER_IP})")
        else:
            print("  www.{DOMAIN} -> Not resolving")
        print()

        if not wait_for_dns():
            print()
            print("Please configure DNS first, then run this script again.")
            sys.exit(1)

    # Set up SSL
    if setup_ssl_via_ssh():
        print()
        print("=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Update your .env file:")
        print("   CORS_ORIGINS=https://{DOMAIN},https://www.{DOMAIN}")
        print("   APP_URL=https://{DOMAIN}")
        print("   API_URL=https://{DOMAIN}")
        print()
        print("2. Restart your services:")
        print("   ssh root@178.156.215.100")
        print("   cd /var/www/fightcitytickets")
        print("   docker-compose restart")
        print()
        print("3. Test your site:")
        print("   https://{DOMAIN}")
        print("=" * 60)
    else:
        print()
        print("SSL setup failed. Please set up manually:")
        print("  ssh {SERVER_USER}@{SERVER_IP}")
        print("  certbot --nginx -d {DOMAIN} -d www.{DOMAIN}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print("\n[ERROR] {e}")
        sys.exit(1)


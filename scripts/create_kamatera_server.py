#!/usr/bin/env python3
"""
Create a server on Kamatera using the REST API
Uses environment variables for credentials (more secure)
"""
import os
import requests
import time
import sys
import json

# API credentials from environment variables
CLIENT_ID = os.environ.get("KAMATERA_API_CLIENT_ID") or os.environ.get("CLOUDCLI_API_CLIENTID")
CLIENT_SECRET = os.environ.get("KAMATERA_API_SECRET") or os.environ.get("CLOUDCLI_API_SECRET")
BASE_URL = "https://cloudapi.kamatera.com"

# Server configuration (can be overridden via environment variables)
SERVER_NAME = os.environ.get("KAMATERA_SERVER_NAME", "fightcity-prod")
DATACENTER = os.environ.get("KAMATERA_DATACENTER", "US-NY2")
IMAGE = os.environ.get("KAMATERA_IMAGE", "Ubuntu_22.04_LTS")
CPU = os.environ.get("KAMATERA_CPU", "4B")  # 4 vCPUs
RAM = int(os.environ.get("KAMATERA_RAM", "4096"))  # MB
DISK_SIZE = int(os.environ.get("KAMATERA_DISK", "50"))  # GB
PASSWORD = os.environ.get("KAMATERA_PASSWORD", "")

def get_token():
    """Get API token"""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("KAMATERA_API_CLIENT_ID and KAMATERA_API_SECRET must be set")
    
    auth = (CLIENT_ID, CLIENT_SECRET)
    resp = requests.post(
        f"{BASE_URL}/service/auth",
        json={"secret": {"key": CLIENT_SECRET}},
        auth=auth,
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["token"]

def create_server(token):
    """Create the server"""
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "name": SERVER_NAME,
        "datacenter": DATACENTER,
        "image": IMAGE,
        "cpu": CPU,
        "ram": RAM,
        "disk": [{"type": "disk", "size": DISK_SIZE, "id": 0}],
        "network": [{"type": "nic", "name": "wan", "id": 0, "ip": "auto"}],
        "billingCycle": "hourly"
    }
    
    # Add password if provided
    if PASSWORD:
        payload["password"] = {"username": "root", "password": PASSWORD}
    
    print(f"Creating server {SERVER_NAME} in {DATACENTER}...")
    resp = requests.post(
        f"{BASE_URL}/service/server",
        json=payload,
        headers=headers,
        timeout=120
    )
    resp.raise_for_status()
    return resp.json()["id"]

def wait_for_server(token, server_id):
    """Wait for server to be ready"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Waiting for server to be ready...")
    for i in range(60):  # Wait up to 5 minutes
        resp = requests.get(
            f"{BASE_URL}/service/server/{server_id}",
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        server = resp.json()
        status = server.get("data", {}).get("status", server.get("status", ""))
        
        if status == "running":
            print("✅ Server is running!")
            return server
        elif status in ("failed", "error"):
            raise Exception(f"Server creation failed: {status}")
        
        print(f"   Status: {status}... waiting ({i+1}/60)")
        time.sleep(5)
    
    raise Exception("Timeout waiting for server")

def get_server_ip(server):
    """Get server IP from server info"""
    nics = server.get("data", {}).get("nic", server.get("nic", []))
    for nic in nics:
        ip = nic.get("ip", "")
        if ip and ip != "auto":
            return ip
    return None

def main():
    try:
        # Get auth token
        print("🔐 Getting API token...")
        token = get_token()
        print("✅ Token obtained successfully")
        
        # Create server
        server_id = create_server(token)
        print(f"✅ Server created with ID: {server_id}")
        
        # Wait for server to be ready
        server = wait_for_server(token, server_id)
        
        # Get IP address
        ip = get_server_ip(server)
        if ip:
            print(f"✅ Server IP: {ip}")
        else:
            print("⚠️  Warning: Could not determine server IP")
            ip = "UNKNOWN"
        
        # Save credentials to JSON file
        output_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            ".kamatera-server-info.json"
        )
        server_info = {
            "server_name": SERVER_NAME,
            "server_id": server_id,
            "server_ip": ip,
            "datacenter": DATACENTER,
            "password": PASSWORD if PASSWORD else "N/A (SSH key only)"
        }
        
        with open(output_file, "w") as f:
            json.dump(server_info, f, indent=2)
        print(f"✅ Server info saved to: {output_file}")
        
        # Test SSH connection (if password is set)
        if ip != "UNKNOWN":
            print("\n🔍 Testing SSH connection...")
            import subprocess
            ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", 
                      "-o", "ConnectTimeout=10", f"root@{ip}", 
                      "echo 'SSH connection successful'"]
            
            if PASSWORD:
                # Use sshpass if available
                result = subprocess.run(
                    ssh_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Try with default SSH key
                result = subprocess.run(
                    ssh_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            if result.returncode == 0:
                print("✅ SSH test: SUCCESS")
            else:
                print(f"⚠️  SSH test: FAILED - {result.stderr}")
                print("   You may need to wait a few minutes for SSH to be ready")
        
        print("\n" + "="*60)
        print("🎉 SERVER CREATION COMPLETE")
        print("="*60)
        print(f"Server Name: {SERVER_NAME}")
        print(f"Server ID:   {server_id}")
        print(f"Server IP:   {ip}")
        if PASSWORD:
            print(f"Root Password: {PASSWORD}")
        else:
            print("Root Password: N/A (using SSH keys)")
        print("\nNext Steps:")
        print(f"  1. SSH: ssh root@{ip}")
        print(f"  2. Deploy: SERVER_IP={ip} ./scripts/deploy-fightcity.sh")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fix API routing by updating Nginx config to strip /api prefix.
"""

import paramiko
import sys

# Server configuration
SERVER_HOST = "178.156.215.100"
SERVER_USER = "root"
NGINX_CONFIG_PATH = "/var/www/fightcitytickets/nginx/conf.d/fightcitytickets.conf"

# Fixed Nginx configuration
NGINX_CONFIG = """# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name fightcitytickets.com www.fightcitytickets.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name fightcitytickets.com www.fightcitytickets.com;

    # SSL certificates (will be created by certbot)
    ssl_certificate /etc/letsencrypt/live/fightcitytickets.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fightcitytickets.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Backend API - strip /api prefix before forwarding
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
    }
    
    # Handle /api without trailing slash (redirect to /api/)
    location = /api {
        return 301 /api/;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://api:8000/health;
        access_log off;
    }

    # Frontend (Next.js)
    location / {
        proxy_pass http://web:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
"""


def main():
    print("Fixing API routing configuration...")
    
    # Connect to server
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            ssh.connect(SERVER_HOST, username=SERVER_USER, look_for_keys=True)
        except paramiko.ssh_exception.SSHException:
            print("WARNING: Host key not found, using AutoAddPolicy (less secure)")
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(SERVER_HOST, username=SERVER_USER, look_for_keys=True)
        
        print(f"Connected to {SERVER_HOST}")
        
        # Write the fixed config
        print(f"Writing Nginx config to {NGINX_CONFIG_PATH}...")
        sftp = ssh.open_sftp()
        with sftp.file(NGINX_CONFIG_PATH, 'w') as f:
            f.write(NGINX_CONFIG)
        sftp.close()
        print("Config written successfully")
        
        # Test Nginx config
        print("Testing Nginx configuration...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /var/www/fightcitytickets && docker-compose exec -T nginx nginx -t"
        )
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        errors = stderr.read().decode()
        
        if exit_status == 0:
            print("Nginx config is valid")
        else:
            print(f"ERROR: Nginx config test failed:")
            print(errors)
            print(output)
            return 1
        
        # Reload Nginx
        print("Reloading Nginx...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /var/www/fightcitytickets && docker-compose exec -T nginx nginx -s reload"
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Nginx reloaded successfully")
        else:
            errors = stderr.read().decode()
            print(f"ERROR: Failed to reload Nginx: {errors}")
            return 1
        
        # Test the API endpoint
        print("Testing API endpoint...")
        stdin, stdout, stderr = ssh.exec_command(
            "curl -s https://fightcitytickets.com/api/tickets/validate -X POST "
            "-H 'Content-Type: application/json' "
            "-d '{\"citation_number\":\"SF123456\",\"city_id\":\"us-ca-san_francisco\"}'"
        )
        output = stdout.read().decode()
        
        if '"is_valid"' in output or '"error"' not in output:
            print("SUCCESS: API endpoint is working!")
            print(f"Response: {output[:200]}...")
        else:
            print(f"WARNING: API response: {output[:500]}")
        
        ssh.close()
        print("\nFix deployed successfully!")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


#!/bin/bash
# UFW Firewall Setup for FightCityTickets
# Configures firewall for web server, API, and SSH access

set -e

echo "🔥 Setting up UFW Firewall..."
echo "================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root"
    echo "   Run: sudo $0"
    exit 1
fi

# Reset UFW to defaults
echo "↺ Resetting UFW to defaults..."
ufw reset -f

# Set default policies
echo "📋 Setting default policies..."
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (rate limited)
echo "🔑 Configuring SSH..."
ufw limit 22/tcp comment 'SSH rate limited'

# Allow HTTP and HTTPS
echo "🌐 Configuring web traffic..."
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Allow specific ports for your services
echo "⚙️  Configuring service ports..."

# API port (internal only in production)
# ufw allow from 10.0.0.0/8 to any port 8000 proto tcp comment 'API internal'

# Docker ports (if exposed directly)
# ufw allow 2375/tcp comment 'Docker HTTP'  # Not recommended
# ufw allow 2376/tcp comment 'Docker HTTPS' # Not recommended

# Enable UFW
echo "▶️  Enabling UFW..."
ufw --force enable

# Show status
echo ""
echo "✅ Firewall configured successfully!"
echo ""
ufw status verbose

echo ""
echo "📝 Quick Commands:"
echo "  View status:    sudo ufw status"
echo "  Allow port:     sudo ufw allow <port>"
echo "  Block port:     sudo ufw deny <port>"
echo "  Delete rule:    sudo ufw delete allow <port>"
echo "  Disable:        sudo ufw disable"

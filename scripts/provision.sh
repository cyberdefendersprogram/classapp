#!/bin/bash
#
# Provision a fresh Ubuntu 24.04 droplet for Class Portal
#
# Usage: curl -sSL https://raw.githubusercontent.com/cyberdefendersprogram/classapp/main/scripts/provision.sh | bash
#

set -euo pipefail

echo "=== Class Portal Provisioning Script ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Update system
echo ">>> Updating system packages..."
apt update && apt upgrade -y

# Install Docker
echo ">>> Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "Docker already installed"
fi

# Install Docker Compose plugin (if not included)
echo ">>> Verifying Docker Compose..."
docker compose version || {
    apt install -y docker-compose-plugin
}

# Install Nginx
echo ">>> Installing Nginx..."
apt install -y nginx

# Install Certbot
echo ">>> Installing Certbot..."
apt install -y certbot python3-certbot-nginx

# Configure firewall
echo ">>> Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Create directories
echo ">>> Creating application directories..."
mkdir -p /opt/classapp/env
mkdir -p /var/lib/classapp
mkdir -p /etc/classapp

# Set permissions
chmod 700 /opt/classapp/env
chmod 700 /etc/classapp
chmod 755 /var/lib/classapp

# Create docker-compose.yml
echo ">>> Creating docker-compose.yml..."
cat > /opt/classapp/docker-compose.yml << 'EOF'
services:
  app:
    image: ghcr.io/GITHUB_USER/classapp:latest
    ports:
      - "127.0.0.1:8000:8000"
    env_file:
      - ./env/.env
    volumes:
      - /var/lib/classapp:/var/lib/classapp
      - /etc/classapp:/etc/classapp:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
EOF

echo ""
echo "=== Provisioning Complete ==="
echo ""
echo "Next steps:"
echo ""
echo "1. Copy your .env file to /opt/classapp/env/.env"
echo "   Example:"
echo "   scp .env root@YOUR_DROPLET:/opt/classapp/env/.env"
echo ""
echo "2. Copy service-account.json to /etc/classapp/"
echo "   Example:"
echo "   scp service-account.json root@YOUR_DROPLET:/etc/classapp/"
echo ""
echo "3. Update docker-compose.yml with your GitHub username:"
echo "   sed -i 's/GITHUB_USER/your-username/g' /opt/classapp/docker-compose.yml"
echo ""
echo "4. Copy nginx config to /etc/nginx/sites-available/classapp"
echo "   Then enable it:"
echo "   ln -s /etc/nginx/sites-available/classapp /etc/nginx/sites-enabled/"
echo "   nginx -t && systemctl reload nginx"
echo ""
echo "5. Get TLS certificate:"
echo "   certbot --nginx -d your-domain.com"
echo ""
echo "6. Start the application:"
echo "   cd /opt/classapp && docker compose up -d"
echo ""
echo "7. Add GitHub secrets for deployment:"
echo "   - DROPLET_HOST: Your droplet IP"
echo "   - DROPLET_USER: root (or your user)"
echo "   - DROPLET_SSH_KEY: Private SSH key"
echo ""

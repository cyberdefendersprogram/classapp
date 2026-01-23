# Class Portal Deployment Guide

## Prerequisites

- DigitalOcean account
- Domain name pointed to your droplet IP
- GitHub repository with Actions enabled
- Google Cloud service account JSON file

## 1. Create Droplet

Create an Ubuntu 24.04 droplet on DigitalOcean:
- Size: Basic $6/month (1 vCPU, 1GB RAM) is sufficient
- Region: Choose closest to your students
- SSH Key: Add your SSH key

## 2. Provision the Droplet

SSH into your droplet and run the provisioning script:

```bash
ssh root@YOUR_DROPLET_IP
curl -sSL https://raw.githubusercontent.com/YOUR_USER/classapp/main/scripts/provision.sh | bash
```

This installs Docker, Nginx, Certbot, and configures the firewall.

## 3. Configure Environment

Create the `.env` file on the droplet:

```bash
cat > /opt/classapp/env/.env << 'EOF'
# Application
SECRET_KEY=your-secure-random-key-here
BASE_URL=https://your-domain.com

# Database
SQLITE_PATH=/var/lib/classapp/classapp.db

# Google Sheets
GOOGLE_SERVICE_ACCOUNT_PATH=/etc/classapp/service-account.json
ROSTER_SHEET_ID=your-google-sheet-id
ROSTER_SHEET_NAME=roster
GRADES_SHEET_NAME=grades

# Forward Email
FORWARDEMAIL_API_URL=https://api.forwardemail.net/v1/emails
FORWARDEMAIL_USER=classapp@cyberdefendersprogram.com
FORWARDEMAIL_PASS=your-forwardemail-password

# Magic Link
MAGIC_LINK_TTL_MINUTES=15
RATE_LIMIT_PER_EMAIL_15M=3
EOF

chmod 600 /opt/classapp/env/.env
```

## 4. Upload Service Account

Copy your Google service account JSON:

```bash
scp service-account.json root@YOUR_DROPLET_IP:/etc/classapp/
chmod 600 /etc/classapp/service-account.json
```

## 5. Configure Nginx

Copy the nginx config:

```bash
scp nginx/classapp.conf root@YOUR_DROPLET_IP:/etc/nginx/sites-available/classapp
```

On the droplet, edit to set your domain:

```bash
sed -i 's/YOUR_DOMAIN.com/your-actual-domain.com/g' /etc/nginx/sites-available/classapp
ln -s /etc/nginx/sites-available/classapp /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # Remove default site
nginx -t && systemctl reload nginx
```

## 6. Get TLS Certificate

```bash
certbot --nginx -d your-domain.com
```

## 7. Update Docker Compose

Update the GitHub user in docker-compose:

```bash
sed -i 's/GITHUB_USER/your-github-username/g' /opt/classapp/docker-compose.yml
```

## 8. Configure GitHub Secrets

In your GitHub repository, go to Settings > Secrets and variables > Actions.

Add these secrets:

| Secret | Description |
|--------|-------------|
| `DROPLET_HOST` | Your droplet IP address |
| `DROPLET_USER` | SSH user (usually `root`) |
| `DROPLET_SSH_KEY` | Private SSH key for deployment |

## 9. Deploy

Push to the `main` branch to trigger deployment:

```bash
git push origin main
```

Or manually trigger via GitHub Actions > Deploy > Run workflow.

## 10. Verify

Check the application:

```bash
# On the droplet
docker compose -f /opt/classapp/docker-compose.yml logs -f

# Or check health
curl https://your-domain.com/health
```

## Maintenance

### View Logs

```bash
cd /opt/classapp
docker compose logs -f
```

### Restart Application

```bash
cd /opt/classapp
docker compose restart
```

### Update Manually

```bash
cd /opt/classapp
docker compose pull
docker compose up -d
docker image prune -f
```

### Backup Database

```bash
cp /var/lib/classapp/classapp.db /var/lib/classapp/classapp.db.backup
```

### Renew TLS Certificate

Certbot auto-renews, but to manually renew:

```bash
certbot renew
```

## Troubleshooting

### Application not starting

```bash
# Check container status
docker compose ps

# Check logs
docker compose logs app

# Check health endpoint directly
curl http://127.0.0.1:8000/health
```

### 502 Bad Gateway

- Check if the container is running: `docker compose ps`
- Check if port 8000 is listening: `ss -tlnp | grep 8000`
- Check nginx config: `nginx -t`

### Email not sending

- Verify Forward Email credentials in `.env`
- Check application logs for email errors
- Ensure IMAP is enabled in Forward Email dashboard

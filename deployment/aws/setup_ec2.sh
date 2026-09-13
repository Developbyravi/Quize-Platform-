#!/bin/bash
# ==============================================================================
# AWS EC2 Free Tier Deployment Script for Engineering Day Coding Challenge
# Ubuntu 22.04 LTS / 24.04 LTS compatible
# ==============================================================================

set -e

echo "=== 1. Updating System Packages ==="
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-venv nginx git curl

echo "=== 2. Creating Application Directory ==="
sudo mkdir -p /var/www/engday-backend
sudo chown -R $USER:$USER /var/www/engday-backend

echo "=== 3. Setting Up Python Virtual Environment ==="
python3 -m venv /var/www/engday-backend/venv
source /var/www/engday-backend/venv/bin/activate

echo "=== 4. Installing Python Dependencies ==="
pip install --upgrade pip
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings passlib bcrypt pyjwt python-multipart httpx pytest

echo "=== 5. Setting Up Systemd Service ==="
sudo cp deployment/aws/engday-backend.service /etc/systemd/system/engday-backend.service
sudo systemctl daemon-reload
sudo systemctl enable engday-backend
sudo systemctl start engday-backend

echo "=== 6. Configuring Nginx Reverse Proxy ==="
sudo cp deployment/aws/nginx.conf /etc/nginx/sites-available/engday
sudo ln -sf /etc/nginx/sites-available/engday /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
echo "Backend running on port 8000 reverse-proxied via Nginx on port 80."

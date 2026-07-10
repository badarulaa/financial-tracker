#!/bin/bash

set -e

PROJECT_DIR="/root/finance/financial-tracker"
SERVICE_NAME="financial-tracker"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"

echo "🚀 Starting deployment..."

cd $PROJECT_DIR

echo "📥 Pulling latest code..."
git pull > /dev/null

echo "🐍 Activating virtual environment..."
source $VENV_PATH

echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "🔄 Restarting service..."
sudo systemctl restart $SERVICE_NAME

echo "⏳ Checking service status..."

sleep 2

if systemctl is-active --quiet $SERVICE_NAME
then
    echo "✅ Deployment successful! Bot is running."
else
    echo "❌ Deployment failed! Service is not running."
    echo "📜 Last logs:"
    journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi

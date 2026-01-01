#!/bin/bash
# Django Deployment Script
# This script pulls the latest changes, runs migrations, and restarts the server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - Adjust these paths as needed
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_DIR/venv"
BRANCH="main"
SERVICE_NAME="django-backend"  # Change this to your systemd service name if using systemd

echo -e "${GREEN}Starting deployment...${NC}"

# Change to project directory
cd "$PROJECT_DIR"

# Step 1: Pull latest changes from main branch
echo -e "${YELLOW}Step 1: Pulling latest changes from $BRANCH branch...${NC}"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"
echo -e "${GREEN}✓ Code updated${NC}"

# Step 2: Activate virtual environment
echo -e "${YELLOW}Step 2: Activating virtual environment...${NC}"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Step 3: Install/update dependencies
echo -e "${YELLOW}Step 3: Installing/updating dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies updated${NC}"

# Step 4: Backup database (if using SQLite)
if [ -f "db.sqlite3" ]; then
    echo -e "${YELLOW}Step 4: Backing up database...${NC}"
    BACKUP_DIR="$PROJECT_DIR/db_backups"
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
    cp db.sqlite3 "$BACKUP_FILE"
    echo -e "${GREEN}✓ Database backed up to $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}Step 4: No database file found, skipping backup${NC}"
fi

# Step 5: Run migrations
echo -e "${YELLOW}Step 5: Running database migrations...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations completed${NC}"

# Step 6: Collect static files (if needed)
echo -e "${YELLOW}Step 6: Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear || echo -e "${YELLOW}⚠ Static files collection skipped (may not be configured)${NC}"
echo -e "${GREEN}✓ Static files collected${NC}"

# Step 7: Restart the server
echo -e "${YELLOW}Step 7: Restarting server...${NC}"

# Try different restart methods based on what's available
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    # Using systemd
    echo -e "${YELLOW}Restarting via systemd...${NC}"
    sudo systemctl restart "$SERVICE_NAME"
    echo -e "${GREEN}✓ Server restarted via systemd${NC}"
elif command -v supervisorctl &> /dev/null; then
    # Using Supervisor
    echo -e "${YELLOW}Restarting via Supervisor...${NC}"
    supervisorctl restart "$SERVICE_NAME" || supervisorctl restart all
    echo -e "${GREEN}✓ Server restarted via Supervisor${NC}"
elif [ -f "$PROJECT_DIR/gunicorn.pid" ]; then
    # Using Gunicorn with PID file
    echo -e "${YELLOW}Restarting Gunicorn...${NC}"
    kill -HUP $(cat "$PROJECT_DIR/gunicorn.pid")
    echo -e "${GREEN}✓ Gunicorn reloaded${NC}"
else
    echo -e "${RED}⚠ Warning: Could not automatically restart server${NC}"
    echo -e "${YELLOW}Please restart your server manually using one of these methods:${NC}"
    echo -e "  - systemd: sudo systemctl restart $SERVICE_NAME"
    echo -e "  - supervisor: supervisorctl restart $SERVICE_NAME"
    echo -e "  - gunicorn: kill -HUP \$(cat gunicorn.pid)"
    echo -e "  - manual: Find and restart your WSGI server process"
fi

# Step 8: Verify deployment
echo -e "${YELLOW}Step 8: Verifying deployment...${NC}"
sleep 2  # Give server time to start

# Check if server is responding (adjust URL as needed)
if command -v curl &> /dev/null; then
    if curl -f -s http://localhost:8000/api/test/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server is responding${NC}"
    else
        echo -e "${YELLOW}⚠ Server may not be responding yet (this is normal if it's still starting)${NC}"
    fi
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"


# Deployment Guide

This guide covers deploying the Django backend to a production server.

## Prerequisites

1. **Server Requirements:**
   - Linux server (Ubuntu/Debian recommended)
   - Python 3.8 or higher
   - Git installed
   - Nginx (recommended for reverse proxy)
   - PostgreSQL or MySQL (recommended for production, though SQLite works for small deployments)

2. **Initial Server Setup:**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and pip
   sudo apt install python3 python3-pip python3-venv git -y
   
   # Install Nginx (optional but recommended)
   sudo apt install nginx -y
   ```

## Deployment Script

The `deploy.sh` script automates the deployment process. It performs:
1. Pulls latest changes from main branch
2. Activates virtual environment
3. Updates dependencies
4. Backs up database
4. Runs migrations
5. Collects static files
6. Restarts the server

### Making the Script Executable

```bash
chmod +x deploy.sh
```

### Running the Deployment

```bash
./deploy.sh
```

## Production Server Setup

### 1. Install Gunicorn

Add Gunicorn to your `requirements.txt`:

```txt
gunicorn==21.2.0
```

Then install it:
```bash
pip install gunicorn
```

### 2. Create a Systemd Service (Recommended)

Create `/etc/systemd/system/django-backend.service`:

```ini
[Unit]
Description=Django Backend Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/project/venv/bin"
ExecStart=/path/to/your/project/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --pid /path/to/your/project/gunicorn.pid \
    backend.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Important:** Replace `/path/to/your/project` with your actual project path.

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable django-backend
sudo systemctl start django-backend
sudo systemctl status django-backend
```

Update `SERVICE_NAME` in `deploy.sh` to match your service name.

### 3. Nginx Configuration (Recommended)

Create `/etc/nginx/sites-available/django-backend`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS (if using SSL)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/django-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Production Settings

**CRITICAL:** Update `backend/settings.py` for production:

```python
import os
from pathlib import Path

# Security settings
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (if you have user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Database (consider PostgreSQL for production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security middleware settings
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
```

### 5. Environment Variables

Create a `.env` file (and add it to `.gitignore`):

```bash
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Install `python-decouple` or `django-environ` to load environment variables:

```bash
pip install python-decouple
```

Then update `settings.py`:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')
```

## Additional Deployment Considerations

### 1. Database Backups

The deployment script automatically backs up SQLite databases. For production:
- Set up automated daily backups
- Consider using PostgreSQL with `pg_dump`
- Store backups off-server (S3, etc.)

### 2. Logging

Configure proper logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 3. Monitoring

Consider setting up:
- **Health check endpoint** for monitoring services
- **Error tracking** (Sentry, Rollbar)
- **Performance monitoring** (New Relic, Datadog)
- **Uptime monitoring** (UptimeRobot, Pingdom)

### 4. SSL/TLS Certificate

Use Let's Encrypt for free SSL certificates:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 5. Firewall Configuration

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 6. Process Manager Alternatives

If not using systemd, consider:
- **Supervisor**: `sudo apt install supervisor`
- **PM2**: For Node.js-style process management
- **Docker**: Containerize your application

## Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG = False`
- [ ] Set a secure `SECRET_KEY` from environment variable
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up proper database (PostgreSQL recommended)
- [ ] Configure static files collection
- [ ] Set up SSL/TLS certificate
- [ ] Configure firewall
- [ ] Set up automated backups
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Test the deployment script in staging
- [ ] Document any custom deployment steps

## Troubleshooting

### Server won't start
```bash
# Check logs
sudo journalctl -u django-backend -f
# Or if using supervisor
supervisorctl tail -f django-backend
```

### Migration errors
```bash
# Check for migration conflicts
python manage.py showmigrations
# Rollback if needed (be careful!)
python manage.py migrate app_name migration_number
```

### Static files not serving
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear
# Check Nginx configuration
sudo nginx -t
```

### Permission issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /path/to/your/project
# Fix permissions
sudo chmod -R 755 /path/to/your/project
```

## Quick Deploy Command

After initial setup, you can deploy with a single command:

```bash
./deploy.sh
```

The script will handle everything automatically!


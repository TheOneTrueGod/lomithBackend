# Django Backend Setup Script
Write-Host "Setting up Django backend..." -ForegroundColor Green

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create Django project
Write-Host "Creating Django project..." -ForegroundColor Yellow
django-admin startproject backend .

# Create Django app
Write-Host "Creating Django app..." -ForegroundColor Yellow
python manage.py startapp api

Write-Host "Setup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "2. Run migrations: python manage.py migrate" -ForegroundColor Cyan
Write-Host "3. Start server: python manage.py runserver" -ForegroundColor Cyan


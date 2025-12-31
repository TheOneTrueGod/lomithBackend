# Database Initialization Script
Write-Host "Initializing database..." -ForegroundColor Green

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Run migrations
Write-Host "Running migrations..." -ForegroundColor Yellow
python manage.py migrate

# Create hardcoded test user
Write-Host "Creating test user..." -ForegroundColor Yellow
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='testuser').exists() or User.objects.create_user('testuser', 'test@example.com', 'testpass')"

Write-Host "Database initialization complete!" -ForegroundColor Green
Write-Host "Test user created: username='testuser', password='testpass'" -ForegroundColor Cyan


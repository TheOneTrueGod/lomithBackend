# Django Backend API

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Setup

### Prerequisites

- Python 3.8 or higher
- PowerShell (for running setup scripts on Windows)

### Installation Steps

1. **Run the setup script** to create the virtual environment, install dependencies, and initialize the Django project:

   ```powershell
   .\setup.ps1
   ```

   This will:
   - Create a Python virtual environment in the `venv` folder
   - Install all required dependencies (Django, Django REST Framework, JWT authentication)
   - Create the Django project structure

2. **Initialize the database** to set up database tables and create a test user:

   ```powershell
   .\init_db.ps1
   ```

   This will:
   - Run Django migrations to create database tables
   - Create a hardcoded test user (username: `testuser`, password: `testpass`)

3. **Start the development server**:

   ```bash
   python start
   ```

   Or alternatively, you can manually activate the virtual environment and run the server:

   ```powershell
   .\venv\Scripts\Activate.ps1
   python manage.py runserver
   ```

   The server will start on `http://127.0.0.1:8000/`

### API Endpoints

Once the server is running, you can access the following endpoints:

- **GET** `/api/test/` - Test endpoint that returns "Hello World"
- **POST** `/api/login/` - Login endpoint that returns a JWT access token (valid for 24 hours)
- **GET** `/api/protected/` - Protected endpoint that requires authentication

For detailed API documentation, see [AGENTS.MD](AGENTS.MD).

### Quick Test

Test the API endpoints:

```bash
# Test endpoint
curl http://127.0.0.1:8000/api/test/

# Login (get access token)
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"testuser\", \"password\": \"testpass\"}"

# Protected endpoint (use the access_token from login response)
curl http://127.0.0.1:8000/api/protected/ \
  -H "Authorization: Bearer <your_access_token>"
```


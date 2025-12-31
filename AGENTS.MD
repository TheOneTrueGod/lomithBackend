# Django Backend API - Agent Documentation

## Overview

This is a Django REST Framework backend API with JWT authentication. The API provides three endpoints: a test endpoint, a login endpoint, and a protected endpoint that requires authentication.

## Project Structure

```
Djangotest/
├── backend/              # Django project configuration
│   ├── settings.py      # Django settings with REST framework and JWT config
│   ├── urls.py          # Main URL routing
│   └── ...
├── api/                  # API application
│   ├── views.py         # API endpoint views
│   ├── urls.py          # API URL routing
│   └── ...
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── setup.ps1            # Initial setup script
└── init_db.ps1           # Database initialization script
```

## Setup Instructions

### 1. Initial Setup

Run the setup script to create the virtual environment, install dependencies, and create the Django project structure:

```powershell
.\setup.ps1
```

This script will:
- Create a Python virtual environment
- Install Django, Django REST Framework, and djangorestframework-simplejwt
- Create the Django project structure
- Create the API application

### 2. Initialize Database

Run the database initialization script to set up the database and create a test user:

```powershell
.\init_db.ps1
```

This script will:
- Run Django migrations to create database tables
- Create a hardcoded test user (username: `testuser`, password: `testpass`)

### 3. Start the Development Server

Activate the virtual environment and start the server:

```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

The server will start on `http://127.0.0.1:8000/`

## API Endpoints

### 1. Test Endpoint

**GET** `/api/test/`

Returns a simple "Hello World" message. No authentication required.

**Response:**
```json
{
    "message": "Hello World"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/api/test/
```

### 2. Login Endpoint

**POST** `/api/login/`

Accepts any username and password (hardcoded authentication) and returns a JWT access token valid for 24 hours.

**Request Body:**
```json
{
    "username": "any_username",
    "password": "any_password"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "expires_in": 86400
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

### 3. Protected Endpoint

**GET** `/api/protected/`

Returns a welcome message with the authenticated user's name if a valid token is provided, or "Please login" if the token is invalid or missing.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (Valid Token):**
```json
{
    "message": "Welcome testuser"
}
```

**Response (Invalid/Missing Token):**
```json
{
    "message": "Please login"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/api/protected/ \
  -H "Authorization: Bearer <your_access_token>"
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication via `djangorestframework-simplejwt`.

- **Access Token Lifetime:** 24 hours (configured in `backend/settings.py`)
- **Token Format:** Bearer token in the Authorization header
- **Current Implementation:** Hardcoded authentication - accepts any username/password and returns a token for the hardcoded test user

## Configuration

### JWT Settings

Located in `backend/settings.py`:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### REST Framework Settings

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

## Dependencies

- **Django 4.2.7** - Web framework
- **djangorestframework 3.14.0** - REST API framework
- **djangorestframework-simplejwt 5.3.0** - JWT authentication

## Notes

- The current implementation uses hardcoded values and does not perform real database authentication
- The login endpoint accepts any username/password combination and returns a token for the hardcoded test user
- A test user must be created via `init_db.ps1` before the login endpoint will work
- The protected endpoint validates JWT tokens and extracts user information from the token

## Future Enhancements

- Implement real database authentication
- Add user registration endpoint
- Add password validation
- Implement refresh token endpoint
- Add user management features


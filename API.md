# API Documentation

## Base Configuration

- **Base URL**: `http://127.0.0.1:8000`
- **API Prefix**: `/api`
- **Full Base URL**: `http://127.0.0.1:8000/api`
- **Authentication**: JWT Bearer Token
- **Token Lifetime**: 24 hours
- **Content-Type**: `application/json` (for POST requests)

## Authentication

This API uses JWT (JSON Web Token) authentication. To access protected endpoints:

1. First, call the `/api/login/` endpoint to obtain an access token
2. Include the token in the `Authorization` header as: `Authorization: Bearer <access_token>`
3. The token is valid for 24 hours from issuance

**Note**: The login endpoint currently accepts any username/password combination and returns a token for a hardcoded test user.

---

## Endpoints

### 1. Test Endpoint

A simple test endpoint that returns "Hello World". No authentication required.

**Endpoint**: `GET /api/test/`

**Full URL**: `http://127.0.0.1:8000/api/test/`

**Authentication**: None required

**Request**: No request body or parameters needed

**Response**:
- **Status Code**: `200 OK`
- **Body**:
```json
{
    "message": "Hello World"
}
```

**Example Request**:
```bash
curl http://127.0.0.1:8000/api/test/
```

---

### 2. Login Endpoint

Authenticates a user and returns a JWT access token valid for 24 hours.

**Endpoint**: `POST /api/login/`

**Full URL**: `http://127.0.0.1:8000/api/login/`

**Authentication**: None required

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```

**Note**: Currently accepts any username/password combination. Both fields are required.

**Success Response**:
- **Status Code**: `200 OK`
- **Body**:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "expires_in": 86400
}
```

**Error Responses**:

- **Status Code**: `400 Bad Request` - Missing username or password
  ```json
  {
      "error": "Username and password are required"
  }
  ```

- **Status Code**: `500 Internal Server Error` - System not initialized
  ```json
  {
      "error": "System not initialized. Please run migrations and create test user."
  }
  ```

**Example Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

---

### 3. Protected Endpoint

Returns a personalized welcome message. Requires valid JWT authentication token.

**Endpoint**: `GET /api/protected/`

**Full URL**: `http://127.0.0.1:8000/api/protected/`

**Authentication**: Required (JWT Bearer Token)

**Request Headers**:
```
Authorization: Bearer <access_token>
```

**Request**: No request body or parameters needed

**Success Response** (Valid Token):
- **Status Code**: `200 OK`
- **Body**:
```json
{
    "message": "Welcome testuser"
}
```

**Error Response** (Invalid/Missing Token):
- **Status Code**: `401 Unauthorized`
- **Body**:
```json
{
    "message": "Please login"
}
```

**Example Request**:
```bash
curl http://127.0.0.1:8000/api/protected/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Request (Without Token - Will Fail)**:
```bash
curl http://127.0.0.1:8000/api/protected/
```

---

## Complete Workflow Example

### Step 1: Test the API
```bash
curl http://127.0.0.1:8000/api/test/
```

### Step 2: Login and Get Token
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

**Response**:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 86400
}
```

### Step 3: Use Protected Endpoint
```bash
curl http://127.0.0.1:8000/api/protected/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Response**:
```json
{
    "message": "Welcome testuser"
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request (missing required fields)
- `401 Unauthorized` - Authentication required or invalid token
- `500 Internal Server Error` - Server error (e.g., system not initialized)

Error responses include a JSON body with an `error` or `message` field describing the issue.

---

## Notes for AI Agents

When interacting with this API:

1. **Always use the full URL**: `http://127.0.0.1:8000/api/<endpoint>`
2. **For POST requests**: Include `Content-Type: application/json` header
3. **For protected endpoints**: Include `Authorization: Bearer <token>` header
4. **Token management**: Tokens expire after 24 hours. Re-authenticate if you receive 401 errors
5. **Current implementation**: Login accepts any credentials but returns a token for the hardcoded test user
6. **Base path**: All API endpoints are prefixed with `/api/`

## Endpoint Summary Table

| Endpoint | Method | Path | Auth Required | Description |
|----------|--------|------|---------------|-------------|
| Test | GET | `/api/test/` | No | Returns "Hello World" |
| Login | POST | `/api/login/` | No | Returns JWT access token |
| Protected | GET | `/api/protected/` | Yes | Returns welcome message with username |


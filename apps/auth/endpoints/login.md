POST /api/login/
Authenticate a user and return a JWT access token valid for 24 hours.
**Authentication**: No authentication required. This endpoint is used to obtain an access token.
**Request Params**: Request body - `username` (string, required), `password` (string, required). 
**Response Params**: `{ access_token: string, token_type: string, expires_in: number }`. On success (200): Returns JWT access token with token type "Bearer" and expiration time in seconds (86400 = 24 hours). On error: Returns `{ error: string }` with status 401 (Invalid email or password) or 500 (System not initialized. Please run migrations and create test user.).


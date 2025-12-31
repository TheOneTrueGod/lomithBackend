POST /api/create-user/
Create a new user account and return a JWT access token valid for 24 hours.
**Authentication**: No authentication required. This endpoint is used to register a new user.
**Request Params**: Request body - `username` (string, required), `email` (string, required), `password` (string, required). 
**Response Params**: On success (201): Returns `{ message: string, user: { id: number, username: string, email: string }, access_token: string, token_type: string, expires_in: number }`. On error: Returns `{ error: string }` with status 400 (Username is required / Email is required / Password is required / Invalid email format / Username already exists / Email already exists / Password must be at least 8 characters long) or 500 (Failed to create user).


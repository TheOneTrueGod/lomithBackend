GET /api/ai-integrations/
Get all AI integrations for the authenticated user.
**Authentication**: Requires JWT Bearer token in Authorization header: `Authorization: Bearer <access_token>`. Obtain token from `/api/login/` endpoint.
**Request Params**: None.
**Response Params**: `{ integrations: Array<{ id: number, provider: string, model: string, base_url: string | null, name: string | null, is_active: boolean, created_at: string, updated_at: string, has_api_key: boolean }> }`. Returns list of all integrations for the authenticated user. API keys are never returned in responses for security.

GET /api/ai-integrations/<provider>/
Get a specific AI integration by provider for the authenticated user.
**Authentication**: Requires JWT Bearer token in Authorization header: `Authorization: Bearer <access_token>`. Obtain token from `/api/login/` endpoint.
**Request Params**: Path parameter - `provider` (string, required, the AI provider name e.g., 'openai', 'anthropic', 'google').
**Response Params**: `{ id: number, provider: string, model: string, base_url: string | null, name: string | null, is_active: boolean, created_at: string, updated_at: string, has_api_key: boolean }`. Returns 404 if integration not found. API keys are never returned in responses for security.

POST /api/ai-integrations/
Create a new AI integration for the authenticated user. Provider is auto-detected from API key format if not provided.
**Authentication**: Requires JWT Bearer token in Authorization header: `Authorization: Bearer <access_token>`. Obtain token from `/api/login/` endpoint.
**Request Params**: Request body - `api_key` (string, required), `provider` (string, optional, auto-detected from API key if not provided, values: 'openai' | 'anthropic' | 'google'), `model` (string, optional, defaults to provider's default model), `base_url` (string, optional, defaults to provider's default URL), `name` (string, optional, defaults to provider name), `is_active` (boolean, optional, default: true).
**Response Params**: `{ id: number, provider: string, model: string, base_url: string | null, name: string | null, is_active: boolean, created_at: string, updated_at: string, has_api_key: boolean }`. On success (201 if created, 200 if updated): Returns created/updated integration. On error: Returns `{ error: string }` with status 400 (api_key is required / provider is required and could not be auto-detected) or 500 (Failed to create integration). API keys are never returned in responses for security.

PUT /api/ai-integrations/<provider>/
Update an existing AI integration for the authenticated user.
**Authentication**: Requires JWT Bearer token in Authorization header: `Authorization: Bearer <access_token>`. Obtain token from `/api/login/` endpoint.
**Request Params**: Path parameter - `provider` (string, required, the AI provider name e.g., 'openai', 'anthropic', 'google'). Request body - `api_key` (string, optional), `model` (string, optional), `base_url` (string, optional), `name` (string, optional), `is_active` (boolean, optional). All request body fields are optional - only provided fields will be updated.
**Response Params**: `{ id: number, provider: string, model: string, base_url: string | null, name: string | null, is_active: boolean, created_at: string, updated_at: string, has_api_key: boolean }`. On success (200): Returns updated integration. On error: Returns `{ error: string }` with status 404 (Integration not found) or 500 (Failed to update integration). API keys are never returned in responses for security.


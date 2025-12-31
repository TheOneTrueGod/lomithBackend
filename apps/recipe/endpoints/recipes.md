GET /api/recipes/
Get a paginated list of recipes with optional filtering by search query, user ID, and detail level.
**Authentication**: Requires JWT Bearer token in Authorization header: `Authorization: Bearer <access_token>`. Obtain token from `/api/login/` endpoint.
**Request Params**: Query parameters - `page` (int, optional, default: 1), `page_size` (int, optional, default: 10), `search` (string, optional), `user_id` (string, optional), `detail_level` (string, optional, default: 'detailed', values: 'simple' | 'detailed').
**Response Params**: `{ recipes: Array<Recipe | SimpleRecipe>, pagination: { page: number, page_size: number, total: number, total_pages: number, has_next: boolean, has_previous: boolean } }`. Recipe type depends on `detail_level`: 'simple' excludes ingredients and steps fields.

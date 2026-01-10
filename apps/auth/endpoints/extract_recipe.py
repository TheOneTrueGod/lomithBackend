"""
Extract Recipe from URL Endpoint.

This endpoint uses AI integrations to extract recipe information from a website URL.
"""
import json
import re
import requests
from urllib.parse import urlparse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from apps.auth.models import AIIntegration
import google.generativeai as genai


def _validate_url(url):
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _build_ai_prompt(url):
    """Build the AI prompt for recipe extraction."""
    return f"""You are a recipe extraction assistant. Visit the following website URL and extract recipe information:

URL: {url}

Please analyze the webpage and extract the following recipe information:

1. **Title**: The name of the recipe
2. **Description**: A brief description of the recipe
3. **Prep Time**: Preparation time in minutes (as a number)
4. **Cook Time**: Cooking time in minutes (as a number)
5. **Servings**: Number of servings (as a number)
6. **Image URL**: If there's a recipe image, provide its URL (optional)
7. **Ingredients**: A list of ingredients with:
   - name: The ingredient name
   - amount: The quantity/amount (e.g., "2", "1/2", "1 cup")
   - unit: The unit of measurement (e.g., "cup", "tbsp", "tsp", "g", "oz", or empty string if none)
8. **Steps**: A list of cooking steps with:
   - instructions: Clear step-by-step instructions
   - ingredients: An array of ingredient names (from the ingredients list) that are used in this step
9. **Tags**: Suggest 3-5 relevant tags for this recipe based on cuisine type, dietary restrictions, meal type, etc.

IMPORTANT: 
- Do NOT include: id, userId, createdAt, updatedAt, or source fields (these are system-specific)
- The source will be set to the URL automatically
- Return ONLY valid JSON in the following format:
{{
  "title": "string",
  "description": "string",
  "prepTime": number,
  "cookTime": number,
  "servings": number,
  "imageUrl": "string or null",
  "ingredients": [
    {{
      "name": "string",
      "amount": "string",
      "unit": "string"
    }}
  ],
  "steps": [
    {{
      "instructions": "string",
      "ingredients": ["ingredient name 1", "ingredient name 2"]
    }}
  ],
  "tags": ["tag1", "tag2", "tag3"]
}}

If you cannot find a recipe on the page, return: {{"error": "No recipe found on this page"}}"""


def _call_openai_api(api_key, model, base_url, prompt):
    """Call OpenAI API."""
    if base_url:
        # If base_url is provided, ensure it ends with /chat/completions
        if base_url.endswith('/chat/completions'):
            url = base_url
        elif base_url.endswith('/'):
            url = f"{base_url}chat/completions"
        else:
            url = f"{base_url}/chat/completions"
    else:
        url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    response = requests.post(url, headers=headers, json=body, timeout=60)
    response.raise_for_status()
    
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_anthropic_api(api_key, model, base_url, prompt):
    """Call Anthropic API."""
    if base_url:
        # If base_url is provided, ensure it ends with /v1/messages
        if base_url.endswith('/v1/messages'):
            url = base_url
        elif base_url.endswith('/v1'):
            url = f"{base_url}/messages"
        else:
            url = f"{base_url}/v1/messages"
    else:
        url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    # Anthropic API accepts content as either a string or an array of content blocks
    # Using array format for better compatibility
    body = {
        "model": model,
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=body, timeout=60)
    
    # Better error handling to see the actual error message
    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = error_data.get('error', {})
            if isinstance(error_message, dict):
                error_detail = error_message.get('message', str(error_message))
                error_type = error_message.get('type', 'unknown')
                raise Exception(f"Anthropic API error ({error_type}): {error_detail}")
            else:
                raise Exception(f"Anthropic API error: {error_message}")
        except (ValueError, KeyError):
            # If we can't parse the error, include the raw response
            raise Exception(f"Anthropic API error (HTTP {response.status_code}): {response.text[:500]}")
    
    data = response.json()
    return data["content"][0]["text"]


def _call_google_api(api_key, model, base_url, prompt):
    """Call Google API."""
    # Configure the API key
    genai.configure(api_key=api_key)
    
    # Use the provided model or default to gemini-2.5-flash
    # Note: gemini-pro is deprecated. Use gemini-2.5-flash, gemini-2.5-pro, or gemini-pro-latest
    model_name = model if model else "gemini-2.5-flash"
    
    # Create the generative model
    generative_model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }
    )
    
    # Generate content
    response = generative_model.generate_content(prompt)
    
    # Return the text content
    return response.text


def _call_ai_provider(integration, prompt):
    """Call the appropriate AI provider based on integration type."""
    api_key = integration.decrypted_api_key
    provider = integration.provider.lower()
    model = integration.model
    base_url = integration.base_url
    
    if provider == "openai":
        return _call_openai_api(api_key, model, base_url, prompt)
    elif provider == "anthropic":
        return _call_anthropic_api(api_key, model, base_url, prompt)
    elif provider == "google":
        return _call_google_api(api_key, model, base_url, prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _validate_recipe_response(data):
    """Validate the recipe response structure."""
    required_fields = ['title', 'description', 'prepTime', 'cookTime', 'servings', 'ingredients', 'steps', 'tags']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate types
    if not isinstance(data['prepTime'], (int, float)) or data['prepTime'] < 0:
        raise ValueError("prepTime must be a non-negative number")
    
    if not isinstance(data['cookTime'], (int, float)) or data['cookTime'] < 0:
        raise ValueError("cookTime must be a non-negative number")
    
    if not isinstance(data['servings'], (int, float)) or data['servings'] < 1:
        raise ValueError("servings must be a positive number")
    
    # Validate ingredients
    if not isinstance(data['ingredients'], list) or len(data['ingredients']) == 0:
        raise ValueError("ingredients must be a non-empty array")
    
    for ingredient in data['ingredients']:
        if not isinstance(ingredient, dict):
            raise ValueError("Each ingredient must be an object")
        for field in ['name', 'amount', 'unit']:
            if field not in ingredient:
                raise ValueError(f"Each ingredient must have '{field}' field")
    
    # Validate steps
    if not isinstance(data['steps'], list) or len(data['steps']) == 0:
        raise ValueError("steps must be a non-empty array")
    
    for step in data['steps']:
        if not isinstance(step, dict):
            raise ValueError("Each step must be an object")
        if 'instructions' not in step:
            raise ValueError("Each step must have 'instructions' field")
        if 'ingredients' not in step:
            raise ValueError("Each step must have 'ingredients' field")
        if not isinstance(step['ingredients'], list):
            raise ValueError("Step ingredients must be an array")
    
    # Validate tags
    if not isinstance(data['tags'], list):
        raise ValueError("tags must be an array")
    
    return True


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extract_recipe(request, id):
    """
    Extract recipe information from a website URL using the specified AI integration.
    
    Path Parameters:
        - id (integer): The AI integration ID to use for extraction
    
    Request Body:
        - url (string, required): The URL of the webpage containing the recipe to extract
    
    Returns:
        Response with extracted recipe data or error message
    """
    try:
        # Get URL from request body
        url = request.data.get('url')
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate URL format
        if not _validate_url(url):
            return Response(
                {'error': 'Invalid URL format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get AI integration
        try:
            integration = AIIntegration.objects.get(id=id, user=request.user)
        except AIIntegration.DoesNotExist:
            return Response(
                {'error': 'AI integration not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify integration is active
        if not integration.is_active:
            return Response(
                {'error': 'AI integration is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify API key exists
        api_key = integration.decrypted_api_key
        if not api_key:
            return Response(
                {'error': 'AI integration has no API key configured'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build prompt
        prompt = _build_ai_prompt(url)
        
        # Call AI provider
        try:
            ai_response = _call_ai_provider(integration, prompt)
        except Exception as e:
            return Response(
                {'error': f'Failed to extract recipe: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Parse JSON response
        try:
            # Try to extract JSON from the response (in case AI wraps it in markdown)
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_response = json_match.group(0)
            
            recipe_data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            return Response(
                {'error': f'Failed to parse AI response: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Check if AI returned an error
        if 'error' in recipe_data:
            if recipe_data['error'] == 'No recipe found on this page':
                return Response(recipe_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': f"AI returned error: {recipe_data['error']}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Validate response structure
        try:
            _validate_recipe_response(recipe_data)
        except ValueError as e:
            return Response(
                {'error': f'Invalid recipe data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Return successful response
        return Response(recipe_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'An unexpected error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


"""
Recipes API endpoint.
Handles HTTP requests and responses for recipe operations.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.recipe.services.recipes_service import RecipesService
from apps.recipe.repositories.mocked_recipes_repository import MockedRecipesRepository


# Initialize service with mocked repository
# In the future, this can be swapped for a database repository
_recipes_service = RecipesService(MockedRecipesRepository())


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_or_create(request):
    """
    Handle GET (list) or POST (create) requests for recipes.
    """
    if request.method == 'GET':
        return get_list(request)
    elif request.method == 'POST':
        return create(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_list(request):
    """
    Get a paginated list of recipes with optional filtering.
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - page_size (int): Number of items per page (default: 10)
        - search (str): Optional search query to filter recipes by title, description, or tags
        - user_id (str): Optional user ID to filter recipes by owner
        - detail_level (str): 'simple' or 'detailed' (default: 'detailed')
            - 'simple': Excludes ingredients and steps
            - 'detailed': Includes all recipe fields
    
    Returns:
        Response with recipes list and pagination metadata
    """
    try:
        # Parse query parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        search = request.query_params.get('search', None)
        user_id = request.query_params.get('user_id', None)
        detail_level = request.query_params.get('detail_level', 'detailed')
        
        # Validate parameters
        if page < 1:
            return Response(
                {'error': 'page must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if page_size < 1:
            return Response(
                {'error': 'page_size must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if detail_level not in ['simple', 'detailed']:
            return Response(
                {'error': "detail_level must be 'simple' or 'detailed'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get recipes from service
        result = _recipes_service.get_list(
            page=page,
            page_size=page_size,
            search=search,
            user_id=user_id,
            detail_level=detail_level
        )
        
        return Response(result, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response(
            {'error': f'Invalid parameter: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_by_id(request, recipe_id):
    """
    Get a recipe by its ID.
    
    Path Parameters:
        - recipe_id (str): The ID of the recipe to retrieve
    
    Query Parameters:
        - detail_level (str): 'simple' or 'detailed' (default: 'detailed')
            - 'simple': Excludes ingredients and steps
            - 'detailed': Includes all recipe fields
    
    Returns:
        Response with recipe data or 404 if not found
    """
    try:
        detail_level = request.query_params.get('detail_level', 'detailed')
        
        if detail_level not in ['simple', 'detailed']:
            return Response(
                {'error': "detail_level must be 'simple' or 'detailed'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recipe = _recipes_service.get_by_id(recipe_id, detail_level=detail_level)
        
        if recipe:
            return Response(recipe, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Recipe not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    """
    Create a new recipe.
    
    Request Body:
        - All required recipe fields (id, userId, title, description, etc.)
    
    Returns:
        Response with created recipe data or 400 if validation fails
    """
    try:
        recipe_data = request.data
        
        # Validate required fields
        required_fields = ['id', 'userId', 'title', 'description', 'prepTime', 
                          'cookTime', 'servings', 'imageUrl', 'ingredients', 
                          'steps', 'tags', 'createdAt', 'updatedAt']
        
        missing_fields = [field for field in required_fields if field not in recipe_data]
        if missing_fields:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create recipe
        created_recipe = _recipes_service.create(recipe_data)
        
        return Response(created_recipe, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def detail_update_delete(request, recipe_id):
    """
    Handle GET (detail), PUT (update), or DELETE requests for a specific recipe.
    """
    if request.method == 'GET':
        return get_by_id(request, recipe_id)
    elif request.method == 'PUT':
        return update(request, recipe_id)
    elif request.method == 'DELETE':
        return delete(request, recipe_id)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, recipe_id):
    """
    Update an existing recipe.
    
    Path Parameters:
        - recipe_id (str): The ID of the recipe to update
    
    Request Body:
        - Fields to update (partial updates supported)
    
    Returns:
        Response with updated recipe data or 404 if not found
    """
    try:
        recipe_data = request.data
        
        # Update recipe
        updated_recipe = _recipes_service.update(recipe_id, recipe_data)
        
        if updated_recipe:
            return Response(updated_recipe, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Recipe not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete(request, recipe_id):
    """
    Delete a recipe by its ID.
    
    Path Parameters:
        - recipe_id (str): The ID of the recipe to delete
    
    Returns:
        Response with success message or 404 if not found
    """
    try:
        deleted = _recipes_service.delete(recipe_id)
        
        if deleted:
            return Response(
                {'message': 'Recipe deleted successfully'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Recipe not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

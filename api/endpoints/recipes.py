"""
Recipes API endpoint.
Handles HTTP requests and responses for recipe operations.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.services.recipes_service import RecipesService
from api.repositories.mocked_recipes_repository import MockedRecipesRepository


# Initialize service with mocked repository
# In the future, this can be swapped for a database repository
_recipes_service = RecipesService(MockedRecipesRepository())


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


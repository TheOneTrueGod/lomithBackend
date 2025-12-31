"""
Service layer for recipe business logic.
Handles filtering, pagination, formatting, and data transformation.
"""
from typing import List, Dict, Optional, Literal
from apps.recipe.repositories.recipes_repository import RecipesRepository
from db.mocked.recipes import Recipe


class RecipesService:
    """Service for recipe operations and business logic."""
    
    def __init__(self, repository: RecipesRepository):
        """
        Initialize the service with a repository.
        
        Args:
            repository: Repository implementation for data access
        """
        self.repository = repository
    
    def get_list(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        user_id: Optional[str] = None,
        detail_level: Literal['simple', 'detailed'] = 'detailed'
    ) -> Dict:
        """
        Get a paginated list of recipes with optional filtering and formatting.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            search: Optional search query to filter recipes
            user_id: Optional user ID to filter recipes by owner
            detail_level: 'simple' excludes ingredients and steps, 'detailed' includes all fields
            
        Returns:
            Dict containing:
                - recipes: List of recipe dictionaries
                - pagination: Dict with page, page_size, total, total_pages, has_next, has_previous
        """
        # Get paginated recipes and total count from repository
        # Repository handles all filtering (user_id + search) and pagination in one query
        paginated_recipes, total = self.repository.get_list(
            user_id=user_id,
            search=search,
            page=page,
            page_size=page_size
        )
        
        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0  # Ceiling division
        
        # Format recipes based on detail level
        formatted_recipes = [
            self._format_recipe(recipe, detail_level)
            for recipe in paginated_recipes
        ]
        
        return {
            'recipes': formatted_recipes,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
            }
        }
    
    def _format_recipe(self, recipe: Recipe, detail_level: Literal['simple', 'detailed']) -> Dict:
        """
        Format a recipe based on the requested detail level.
        
        Args:
            recipe: The recipe to format
            detail_level: 'simple' excludes ingredients and steps
            
        Returns:
            Formatted recipe dictionary
        """
        if detail_level == 'simple':
          formatted = {
							'id': recipe['id'],
							'userId': recipe['userId'],
							'title': recipe['title'],
							'description': recipe['description'],
							'imageUrl': recipe['imageUrl'],
							'tags': recipe['tags'],
					}
        else:
            # Return full recipe with all fields
            formatted = recipe.copy()
        
        return formatted
    
    def get_by_id(self, recipe_id: str, detail_level: Literal['simple', 'detailed'] = 'detailed') -> Optional[Dict]:
        """
        Get a recipe by its ID.
        
        Args:
            recipe_id: The ID of the recipe to retrieve
            detail_level: 'simple' excludes ingredients and steps, 'detailed' includes all fields
            
        Returns:
            Formatted recipe dictionary if found, None otherwise
        """
        recipe = self.repository.get_by_id(recipe_id)
        if recipe:
            return self._format_recipe(recipe, detail_level)
        return None
    
    def create(self, recipe_data: Dict) -> Dict:
        """
        Create a new recipe.
        
        Args:
            recipe_data: Dictionary containing recipe data (must include all required fields)
            
        Returns:
            The created recipe dictionary
        """
        # Convert dict to Recipe type (type checking will be handled by repository)
        recipe = self.repository.create(recipe_data)
        return self._format_recipe(recipe, 'detailed')
    
    def update(self, recipe_id: str, recipe_data: Dict) -> Optional[Dict]:
        """
        Update an existing recipe.
        
        Args:
            recipe_id: The ID of the recipe to update
            recipe_data: Dictionary containing updated recipe fields
            
        Returns:
            The updated recipe dictionary if found, None otherwise
        """
        recipe = self.repository.update(recipe_id, recipe_data)
        if recipe:
            return self._format_recipe(recipe, 'detailed')
        return None
    
    def delete(self, recipe_id: str) -> bool:
        """
        Delete a recipe by its ID.
        
        Args:
            recipe_id: The ID of the recipe to delete
            
        Returns:
            True if the recipe was deleted, False if not found
        """
        return self.repository.delete(recipe_id)


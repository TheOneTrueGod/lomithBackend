"""
Mocked implementation of RecipesRepository using in-memory data.
"""
from typing import List, Optional, Tuple
from db.mocked.recipes import Recipe, mock_recipes
from .recipes_repository import RecipesRepository


class MockedRecipesRepository(RecipesRepository):
    """Repository implementation using mocked recipe data."""
    
    def __init__(self):
        """Initialize with mocked recipe data."""
        self._recipes = mock_recipes
    
    def get_list(
        self,
        user_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Recipe], int]:
        """
        Retrieve a paginated list of recipes with optional filtering.
        All filtering, searching, and pagination is handled in one pass.
        """
        # Start with all recipes
        filtered_recipes = self._recipes.copy()
        
        # Apply user_id filter if provided
        if user_id:
            filtered_recipes = [
                recipe for recipe in filtered_recipes
                if recipe.get('userId') == user_id
            ]
        
        # Apply search filter if provided
        if search:
            query_lower = search.lower()
            search_results = []
            
            for recipe in filtered_recipes:
                # Search in title
                if query_lower in recipe.get('title', '').lower():
                    search_results.append(recipe)
                    continue
                
                # Search in description
                if query_lower in recipe.get('description', '').lower():
                    search_results.append(recipe)
                    continue
                
                # Search in tags
                tags = recipe.get('tags', [])
                if any(query_lower in tag.lower() for tag in tags):
                    search_results.append(recipe)
                    continue
            
            filtered_recipes = search_results
        
        # Calculate total count before pagination
        total = len(filtered_recipes)
        
        # Apply pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_recipes = filtered_recipes[start_index:end_index]
        
        return paginated_recipes, total


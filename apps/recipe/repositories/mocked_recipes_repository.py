"""
Mocked implementation of RecipesRepository using in-memory data.
"""
import copy
from typing import List, Optional, Tuple
from db.mocked.recipes import Recipe, mock_recipes
from .recipes_repository import RecipesRepository


class MockedRecipesRepository(RecipesRepository):
    """Repository implementation using mocked recipe data."""
    
    def __init__(self):
        """Initialize with mocked recipe data."""
        # Store a reference to the original mock_recipes
        # We'll make copies when needed for modifications
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
        # Start with all recipes (shallow copy is fine for read operations)
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
        
        # Return deep copies to prevent modifications to the original recipes
        return [copy.deepcopy(recipe) for recipe in paginated_recipes], total
    
    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        Retrieve a recipe by its ID.
        Returns a deep copy of the recipe to prevent modifications to the original.
        """
        for recipe in self._recipes:
            if recipe.get('id') == recipe_id:
                # Return a deep copy to prevent modifications to the original
                return copy.deepcopy(recipe)
        return None
    
    def create(self, recipe: Recipe) -> Recipe:
        """
        Create a new recipe.
        Makes a deep copy of the provided recipe and adds it to the list.
        """
        # Make a deep copy to avoid modifying the original
        new_recipe = copy.deepcopy(recipe)
        # Add to the recipes list
        self._recipes.append(new_recipe)
        # Return a deep copy of what was added
        return copy.deepcopy(new_recipe)
    
    def update(self, recipe_id: str, recipe_data: Recipe) -> Optional[Recipe]:
        """
        Update an existing recipe.
        Finds the recipe, makes a deep copy, applies updates, and returns the modified copy.
        """
        for i, recipe in enumerate(self._recipes):
            if recipe.get('id') == recipe_id:
                # Make a deep copy of the original recipe
                updated_recipe = copy.deepcopy(recipe)
                # Apply updates from recipe_data
                updated_recipe.update(recipe_data)
                # Update the recipe in the list
                self._recipes[i] = updated_recipe
                # Return a deep copy of the updated recipe
                return copy.deepcopy(updated_recipe)
        return None
    
    def delete(self, recipe_id: str) -> bool:
        """
        Delete a recipe by its ID.
        """
        for i, recipe in enumerate(self._recipes):
            if recipe.get('id') == recipe_id:
                del self._recipes[i]
                return True
        return False


"""
Abstract repository interface for recipe data access.
This allows swapping between mocked data and database implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from db.mocked.recipes import Recipe


class RecipesRepository(ABC):
    """Abstract base class for recipe data repositories."""
    
    @abstractmethod
    def get_list(
        self,
        user_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Recipe], int]:
        """
        Retrieve a paginated list of recipes with optional filtering.
        All filtering, searching, and pagination is handled in one query.
        
        Args:
            user_id: Optional user ID to filter recipes by owner
            search: Optional search query to filter recipes by title, description, or tags
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple[List[Recipe], int]: (paginated recipes, total count before pagination)
        """
        pass
    
    @abstractmethod
    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        Retrieve a recipe by its ID.
        
        Args:
            recipe_id: The ID of the recipe to retrieve
            
        Returns:
            Recipe if found, None otherwise
        """
        pass
    
    @abstractmethod
    def create(self, recipe: Recipe) -> Recipe:
        """
        Create a new recipe.
        
        Args:
            recipe: The recipe data to create (must include all required fields)
            
        Returns:
            The created recipe
        """
        pass
    
    @abstractmethod
    def update(self, recipe_id: str, recipe_data: Recipe) -> Optional[Recipe]:
        """
        Update an existing recipe.
        
        Args:
            recipe_id: The ID of the recipe to update
            recipe_data: The updated recipe data
            
        Returns:
            The updated recipe if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, recipe_id: str) -> bool:
        """
        Delete a recipe by its ID.
        
        Args:
            recipe_id: The ID of the recipe to delete
            
        Returns:
            True if the recipe was deleted, False if not found
        """
        pass


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


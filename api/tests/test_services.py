"""
Tests for the recipes service layer.
"""

from django.test import TestCase
from unittest.mock import Mock, MagicMock
from api.services.recipes_service import RecipesService
from api.repositories.recipes_repository import RecipesRepository
from db.mocked.recipes import Recipe


# Mock recipe constants for use across all tests
MOCK_RECIPE_MINIMAL = {
    "id": "1",
    "title": "Test Recipe",
    "userId": "1",
}

MOCK_RECIPE_MINIMAL_2 = {
    "id": "2",
    "title": "Another Recipe",
    "userId": "1",
}

MOCK_RECIPE_FULL = {
    "id": "1",
    "userId": "1",
    "title": "Test Recipe",
    "description": "A test recipe",
    "prepTime": 10,
    "cookTime": 20,
    "servings": 4,
    "imageUrl": "http://example.com/image.jpg",
    "tags": ["Test"],
    "createdAt": "2023-01-01T00:00:00Z",
    "updatedAt": "2023-01-01T00:00:00Z",
    "ingredients": [{"id": "1-1", "name": "Flour"}],
    "steps": [{"id": "1-1", "instructions": "Mix"}],
}

MOCK_RECIPE_FULL_2 = {
    "id": "1",
    "userId": "2",
    "title": "Test Recipe 2",
    "description": "A test recipe",
    "prepTime": 10,
    "cookTime": 20,
    "servings": 4,
    "imageUrl": "http://example.com/image.jpg",
    "tags": ["Test"],
    "createdAt": "2023-01-01T00:00:00Z",
    "updatedAt": "2023-01-01T00:00:00Z",
    "ingredients": [{"id": "1-1", "name": "Flour"}],
    "steps": [{"id": "1-1", "instructions": "Mix"}],
}

MOCK_RECIPE_FULL_NO_INGREDIENTS_STEPS = {
    "id": "1",
    "userId": "1",
    "title": "Test Recipe",
    "description": "A test recipe",
    "prepTime": 10,
    "cookTime": 20,
    "servings": 4,
    "imageUrl": "http://example.com/image.jpg",
    "tags": ["Test"],
    "createdAt": "2023-01-01T00:00:00Z",
    "updatedAt": "2023-01-01T00:00:00Z",
    "ingredients": [],
    "steps": [],
}

class RecipesServiceTest(TestCase):
    """Test cases for RecipesService."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = Mock(spec=RecipesRepository)
        self.service = RecipesService(self.mock_repository)

    def test_get_list_calls_repository_with_correct_parameters(self):
        """Test that service calls repository with correct parameters."""
        # Setup mock
        mock_recipes = [MOCK_RECIPE_MINIMAL, MOCK_RECIPE_MINIMAL_2]
        self.mock_repository.get_list.return_value = (mock_recipes, 2)

        # Call service
        result = self.service.get_list(
            page=1, page_size=10, search="test", user_id="1", detail_level="detailed"
        )

        # Verify repository was called correctly
        self.mock_repository.get_list.assert_called_once_with(
            user_id="1", search="test", page=1, page_size=10
        )

        # Verify result structure
        self.assertIn("recipes", result)
        self.assertIn("pagination", result)

    def test_pagination_metadata_calculation(self):
        """Test pagination metadata is calculated correctly."""
        mock_recipes = [{"id": str(i)} for i in range(5)]
        self.mock_repository.get_list.return_value = (mock_recipes, 25)

        result = self.service.get_list(page=2, page_size=10)

        pagination = result["pagination"]
        self.assertEqual(pagination["page"], 2)
        self.assertEqual(pagination["page_size"], 10)
        self.assertEqual(pagination["total"], 25)
        self.assertEqual(pagination["total_pages"], 3)  # Ceiling of 25/10
        self.assertTrue(pagination["has_next"])
        self.assertTrue(pagination["has_previous"])

    def test_pagination_no_next_on_last_page(self):
        """Test has_next is False on last page."""
        mock_recipes = [MOCK_RECIPE_MINIMAL]
        self.mock_repository.get_list.return_value = (mock_recipes, 1)

        result = self.service.get_list(page=1, page_size=10)

        pagination = result["pagination"]
        self.assertFalse(pagination["has_next"])
        self.assertFalse(pagination["has_previous"])

    def test_pagination_no_previous_on_first_page(self):
        """Test has_previous is False on first page."""
        mock_recipes = [MOCK_RECIPE_MINIMAL, MOCK_RECIPE_MINIMAL_2]
        self.mock_repository.get_list.return_value = (mock_recipes, 15)

        result = self.service.get_list(page=1, page_size=10)

        pagination = result["pagination"]
        self.assertTrue(pagination["has_next"])
        self.assertFalse(pagination["has_previous"])

    def test_pagination_zero_total(self):
        """Test pagination with zero total results."""
        self.mock_repository.get_list.return_value = ([], 0)

        result = self.service.get_list()

        pagination = result["pagination"]
        self.assertEqual(pagination["total"], 0)
        self.assertEqual(pagination["total_pages"], 0)
        self.assertFalse(pagination["has_next"])
        self.assertFalse(pagination["has_previous"])

    def test_detail_level_detailed_includes_all_fields(self):
        """Test that detailed level includes ingredients and steps."""
        self.mock_repository.get_list.return_value = ([MOCK_RECIPE_FULL], 1)

        result = self.service.get_list(detail_level="detailed")

        recipe = result["recipes"][0]
        self.assertIn("ingredients", recipe)
        self.assertIn("steps", recipe)
        self.assertEqual(recipe["ingredients"], MOCK_RECIPE_FULL["ingredients"])
        self.assertEqual(recipe["steps"], MOCK_RECIPE_FULL["steps"])

    def test_detail_level_simple_excludes_ingredients_and_steps(self):
        """Test that simple level excludes ingredients and steps."""
        self.mock_repository.get_list.return_value = ([MOCK_RECIPE_FULL], 1)

        result = self.service.get_list(detail_level="simple")

        recipe = result["recipes"][0]
        # Should include basic fields
        self.assertIn("id", recipe)
        self.assertIn("title", recipe)
        self.assertIn("description", recipe)
        self.assertIn("tags", recipe)

        # Should NOT include ingredients and steps
        self.assertNotIn("ingredients", recipe)
        self.assertNotIn("steps", recipe)

    def test_detail_level_simple_includes_all_required_fields(self):
        """Test that simple level includes all required fields."""
        self.mock_repository.get_list.return_value = ([MOCK_RECIPE_FULL_NO_INGREDIENTS_STEPS], 1)

        result = self.service.get_list(detail_level="simple")

        recipe = result["recipes"][0]
        required_fields = [
            "id",
            "userId",
            "title",
            "description",
            "imageUrl",
            "tags",
        ]
        for field in required_fields:
            self.assertIn(
                field, recipe, f"Field '{field}' should be present in simple format"
            )

    def test_format_recipe_does_not_modify_original(self):
        """Test that formatting doesn't modify the original recipe."""
        recipe_copy = MOCK_RECIPE_FULL.copy()

        # Format as simple (should not modify original)
        formatted = self.service._format_recipe(recipe_copy, "simple")

        # Original should still have ingredients and steps
        self.assertIn("ingredients", recipe_copy)
        self.assertIn("steps", recipe_copy)

        # Formatted should not
        self.assertNotIn("ingredients", formatted)
        self.assertNotIn("steps", formatted)

    def test_multiple_recipes_formatting(self):
        """Test that multiple recipes are formatted correctly."""
        mock_recipes = [MOCK_RECIPE_FULL, MOCK_RECIPE_FULL_2]
        self.mock_repository.get_list.return_value = (mock_recipes, 2)

        result = self.service.get_list(detail_level="simple")

        self.assertEqual(len(result["recipes"]), 2)
        for recipe in result["recipes"]:
            self.assertNotIn("ingredients", recipe)
            self.assertNotIn("steps", recipe)

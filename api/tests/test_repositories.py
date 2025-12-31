"""
Tests for the recipes repository layer.
"""
from django.test import TestCase
from api.repositories.mocked_recipes_repository import MockedRecipesRepository


class MockedRecipesRepositoryTest(TestCase):
    """Test cases for MockedRecipesRepository."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repository = MockedRecipesRepository()
    
    def test_get_all_recipes(self):
        """Test retrieving all recipes without filters."""
        recipes, total = self.repository.get_list()
        
        self.assertGreater(total, 0)
        self.assertEqual(len(recipes), min(10, total))  # Default page_size is 10
        self.assertEqual(total, len(self.repository._recipes))
    
    def test_get_all_recipes_with_large_page_size(self):
        """Test retrieving all recipes with page_size larger than total."""
        recipes, total = self.repository.get_list(page_size=100)
        
        self.assertGreater(total, 0)
        self.assertEqual(len(recipes), total)
    
    def test_pagination_first_page(self):
        """Test pagination - first page."""
        recipes, total = self.repository.get_list(page=1, page_size=2)
        
        self.assertEqual(len(recipes), 2)
        self.assertGreater(total, 2)
    
    def test_pagination_second_page(self):
        """Test pagination - second page."""
        recipes_page1, total = self.repository.get_list(page=1, page_size=2)
        recipes_page2, _ = self.repository.get_list(page=2, page_size=2)
        
        # Ensure different recipes on different pages
        self.assertNotEqual(recipes_page1[0]['id'], recipes_page2[0]['id'])
        self.assertEqual(len(recipes_page2), 1)
    
    def test_pagination_last_page(self):
        """Test pagination - last page with partial results."""
        recipes, total = self.repository.get_list(page=1, page_size=2)
        total_pages = (total + 1) // 2  # Ceiling division
        last_page_recipes, _ = self.repository.get_list(page=total_pages, page_size=2)
        
        self.assertGreater(len(last_page_recipes), 0)
        self.assertLessEqual(len(last_page_recipes), 2)
    
    def test_filter_by_user_id(self):
        """Test filtering recipes by user ID."""
        recipes, total = self.repository.get_list(user_id='1')
        
        self.assertGreater(total, 0)
        # All recipes should belong to user '1'
        for recipe in recipes:
            self.assertEqual(recipe['userId'], '1')
    
    def test_filter_by_nonexistent_user_id(self):
        """Test filtering by a user ID that doesn't exist."""
        recipes, total = self.repository.get_list(user_id='999')
        
        self.assertEqual(total, 0)
        self.assertEqual(len(recipes), 0)
    
    def test_search_by_title(self):
        """Test searching recipes by title."""
        recipes, total = self.repository.get_list(search='Spaghetti')
        
        self.assertGreater(total, 0)
        # All results should contain 'Spaghetti' in title (case-insensitive)
        for recipe in recipes:
            self.assertIn('spaghetti', recipe['title'].lower())
    
    def test_search_by_description(self):
        """Test searching recipes by description."""
        recipes, total = self.repository.get_list(search='Italian')
        
        self.assertGreater(total, 0)
        # Results should match search term in title, description, or tags
        found_match = False
        for recipe in recipes:
            if 'italian' in recipe['title'].lower():
                found_match = True
                break
            if 'italian' in recipe['description'].lower():
                found_match = True
                break
            if any('italian' in tag.lower() for tag in recipe.get('tags', [])):
                found_match = True
                break
        self.assertTrue(found_match)
    
    def test_search_by_tags(self):
        """Test searching recipes by tags."""
        recipes, total = self.repository.get_list(search='Pasta')
        
        self.assertGreater(total, 0)
        # At least one result should have 'Pasta' in tags
        found_in_tags = any(
            'pasta' in tag.lower()
            for recipe in recipes
            for tag in recipe.get('tags', [])
        )
        self.assertTrue(found_in_tags)
    
    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        recipes_lower, total_lower = self.repository.get_list(search='spaghetti')
        recipes_upper, total_upper = self.repository.get_list(search='SPAGHETTI')
        
        self.assertEqual(total_lower, total_upper)
        self.assertEqual(len(recipes_lower), len(recipes_upper))
    
    def test_search_no_results(self):
        """Test searching with a query that returns no results."""
        recipes, total = self.repository.get_list(search='NonexistentRecipeXYZ')
        
        self.assertEqual(total, 0)
        self.assertEqual(len(recipes), 0)
    
    def test_user_id_and_search_combined(self):
        """Test combining user_id filter with search."""
        recipes, total = self.repository.get_list(user_id='1', search='Spaghetti')
        
        # All results should belong to user '1' and match search
        for recipe in recipes:
            self.assertEqual(recipe['userId'], '1')
            self.assertTrue(
                'spaghetti' in recipe['title'].lower() or
                'spaghetti' in recipe['description'].lower() or
                any('spaghetti' in tag.lower() for tag in recipe.get('tags', []))
            )
    
    def test_user_id_and_search_no_results(self):
        """Test combining user_id and search that yields no results."""
        recipes, total = self.repository.get_list(
            user_id='1',
            search='NonexistentRecipeXYZ'
        )
        
        self.assertEqual(total, 0)
        self.assertEqual(len(recipes), 0)
    
    def test_pagination_with_filters(self):
        """Test pagination combined with user_id and search filters."""
        recipes_page1, total = self.repository.get_list(
            user_id='1',
            search='Classic',
            page=1,
            page_size=1
        )
        
        self.assertGreater(total, 0)
        self.assertEqual(len(recipes_page1), 1)
        
        # Verify the recipe matches filters
        recipe = recipes_page1[0]
        self.assertEqual(recipe['userId'], '1')
        self.assertTrue('classic' in recipe['title'].lower())
    
    def test_total_count_accuracy(self):
        """Test that total count reflects filtered results, not paginated results."""
        recipes_page1, total = self.repository.get_list(page=1, page_size=2)
        recipes_page2, total2 = self.repository.get_list(page=2, page_size=2)
        
        # Total should be the same across pages
        self.assertEqual(total, total2)
        # Total should reflect all results, not just current page
        self.assertGreaterEqual(total, len(recipes_page1) + len(recipes_page2))




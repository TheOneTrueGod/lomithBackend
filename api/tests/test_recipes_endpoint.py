"""
Tests for the recipes API endpoint.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class RecipesEndpointTest(TestCase):
    """Test cases for the recipes API endpoint."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # Create API client
        self.client = APIClient()
        
        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_get_list_requires_authentication(self):
        """Test that endpoint requires authentication."""
        client = APIClient()  # Client without authentication
        response = client.get('/api/recipes/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_list_with_authentication(self):
        """Test getting recipes list with authentication."""
        response = self.client.get('/api/recipes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recipes', response.data)
        self.assertIn('pagination', response.data)
    
    def test_get_list_default_parameters(self):
        """Test getting recipes with default parameters."""
        response = self.client.get('/api/recipes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Check structure
        self.assertIn('recipes', data)
        self.assertIn('pagination', data)
        
        # Check pagination defaults
        pagination = data['pagination']
        self.assertEqual(pagination['page'], 1)
        self.assertEqual(pagination['page_size'], 10)
    
    def test_get_list_with_page_parameter(self):
        """Test getting recipes with page parameter."""
        response = self.client.get('/api/recipes/?page=1')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pagination']['page'], 1)
    
    def test_get_list_with_page_size_parameter(self):
        """Test getting recipes with page_size parameter."""
        response = self.client.get('/api/recipes/?page_size=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pagination']['page_size'], 5)
        self.assertLessEqual(len(response.data['recipes']), 5)
    
    def test_get_list_with_search_parameter(self):
        """Test getting recipes with search parameter."""
        response = self.client.get('/api/recipes/?search=Spaghetti')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # At least one recipe should match search
        recipes = response.data['recipes']
        if recipes:
            found_match = any(
                'spaghetti' in recipe['title'].lower() or
                'spaghetti' in recipe.get('description', '').lower()
                for recipe in recipes
            )
            self.assertTrue(found_match)
    
    def test_get_list_with_user_id_parameter(self):
        """Test getting recipes with user_id parameter."""
        response = self.client.get('/api/recipes/?user_id=1')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All recipes should belong to user '1'
        for recipe in response.data['recipes']:
            self.assertEqual(recipe['userId'], '1')
    
    def test_get_list_with_detail_level_simple(self):
        """Test getting recipes with detail_level=simple."""
        response = self.client.get('/api/recipes/?detail_level=simple')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Recipes should not have ingredients or steps
        for recipe in response.data['recipes']:
            self.assertNotIn('ingredients', recipe)
            self.assertNotIn('steps', recipe)
            # But should have other fields
            self.assertIn('title', recipe)
            self.assertIn('description', recipe)
    
    def test_get_list_with_detail_level_detailed(self):
        """Test getting recipes with detail_level=detailed."""
        response = self.client.get('/api/recipes/?detail_level=detailed')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Recipes should have all fields including ingredients and steps
        if response.data['recipes']:
            recipe = response.data['recipes'][0]
            self.assertIn('ingredients', recipe)
            self.assertIn('steps', recipe)
    
    def test_get_list_combined_parameters(self):
        """Test getting recipes with multiple parameters combined."""
        response = self.client.get(
            '/api/recipes/?page=1&page_size=2&search=Classic&user_id=1&detail_level=simple'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Check pagination
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['page_size'], 2)
        self.assertLessEqual(len(data['recipes']), 2)
        
        # Check that recipes match filters
        for recipe in data['recipes']:
            self.assertEqual(recipe['userId'], '1')
            self.assertNotIn('ingredients', recipe)
            self.assertNotIn('steps', recipe)
    
    def test_get_list_invalid_page_parameter(self):
        """Test getting recipes with invalid page parameter."""
        response = self.client.get('/api/recipes/?page=0')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_list_negative_page_parameter(self):
        """Test getting recipes with negative page parameter."""
        response = self.client.get('/api/recipes/?page=-1')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_list_invalid_page_size_parameter(self):
        """Test getting recipes with invalid page_size parameter."""
        response = self.client.get('/api/recipes/?page_size=0')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_list_invalid_detail_level_parameter(self):
        """Test getting recipes with invalid detail_level parameter."""
        response = self.client.get('/api/recipes/?detail_level=invalid')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('detail_level', response.data['error'])
    
    def test_get_list_non_integer_page_parameter(self):
        """Test getting recipes with non-integer page parameter."""
        response = self.client.get('/api/recipes/?page=abc')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_list_non_integer_page_size_parameter(self):
        """Test getting recipes with non-integer page_size parameter."""
        response = self.client.get('/api/recipes/?page_size=abc')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_list_pagination_metadata(self):
        """Test that pagination metadata is correct."""
        response = self.client.get('/api/recipes/?page=1&page_size=2')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pagination = response.data['pagination']
        
        # Check all pagination fields exist
        self.assertIn('page', pagination)
        self.assertIn('page_size', pagination)
        self.assertIn('total', pagination)
        self.assertIn('total_pages', pagination)
        self.assertIn('has_next', pagination)
        self.assertIn('has_previous', pagination)
        
        # Check types
        self.assertIsInstance(pagination['has_next'], bool)
        self.assertIsInstance(pagination['has_previous'], bool)
    
    def test_get_list_empty_search_results(self):
        """Test getting recipes with search that returns no results."""
        response = self.client.get('/api/recipes/?search=NonexistentRecipeXYZ123')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pagination']['total'], 0)
        self.assertEqual(len(response.data['recipes']), 0)
    
    def test_get_list_empty_user_id_results(self):
        """Test getting recipes with user_id that has no recipes."""
        response = self.client.get('/api/recipes/?user_id=999')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pagination']['total'], 0)
        self.assertEqual(len(response.data['recipes']), 0)




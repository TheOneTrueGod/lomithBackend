"""
Tests for the create user API endpoint.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class CreateUserEndpointTest(TestCase):
    """Test cases for the create user API endpoint."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.valid_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }
    
    def test_create_user_success(self):
        """Test successful user creation."""
        response = self.client.post('/api/create-user/', self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User created successfully')
        self.assertIn('user', response.data)
        self.assertIn('id', response.data['user'])
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['token_type'], 'Bearer')
        self.assertEqual(response.data['expires_in'], 86400)
        
        # Verify user was actually created in database
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('securepass123'))
    
    def test_create_user_missing_username(self):
        """Test user creation with missing username."""
        data = self.valid_user_data.copy()
        del data['username']
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Username is required')
        
        # Verify user was not created
        self.assertFalse(User.objects.filter(email='newuser@example.com').exists())
    
    def test_create_user_missing_email(self):
        """Test user creation with missing email."""
        data = self.valid_user_data.copy()
        del data['email']
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email is required')
        
        # Verify user was not created
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_create_user_missing_password(self):
        """Test user creation with missing password."""
        data = self.valid_user_data.copy()
        del data['password']
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Password is required')
        
        # Verify user was not created
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_create_user_empty_username(self):
        """Test user creation with empty username."""
        data = self.valid_user_data.copy()
        data['username'] = ''
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Username is required')
    
    def test_create_user_empty_email(self):
        """Test user creation with empty email."""
        data = self.valid_user_data.copy()
        data['email'] = ''
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email is required')
    
    def test_create_user_empty_password(self):
        """Test user creation with empty password."""
        data = self.valid_user_data.copy()
        data['password'] = ''
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Password is required')
    
    def test_create_user_whitespace_username(self):
        """Test user creation with whitespace-only username."""
        data = self.valid_user_data.copy()
        data['username'] = '   '
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Username is required')
    
    def test_create_user_whitespace_email(self):
        """Test user creation with whitespace-only email."""
        data = self.valid_user_data.copy()
        data['email'] = '   '
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email is required')
    
    def test_create_user_username_trimming(self):
        """Test that username whitespace is trimmed."""
        data = self.valid_user_data.copy()
        data['username'] = '  trimmeduser  '
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'trimmeduser')
        
        # Verify user was created with trimmed username
        self.assertTrue(User.objects.filter(username='trimmeduser').exists())
        self.assertFalse(User.objects.filter(username='  trimmeduser  ').exists())
    
    def test_create_user_email_trimming(self):
        """Test that email whitespace is trimmed."""
        data = self.valid_user_data.copy()
        data['email'] = '  trimmed@example.com  '
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], 'trimmed@example.com')
    
    def test_create_user_invalid_email_format(self):
        """Test user creation with invalid email format."""
        data = self.valid_user_data.copy()
        data['email'] = 'notanemail'
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid email format')
        
        # Verify user was not created
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_create_user_invalid_email_no_at(self):
        """Test user creation with email missing @ symbol."""
        data = self.valid_user_data.copy()
        data['email'] = 'invalidemail.com'
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid email format')
    
    def test_create_user_invalid_email_no_domain(self):
        """Test user creation with email missing domain."""
        data = self.valid_user_data.copy()
        data['email'] = 'user@'
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid email format')
    
    def test_create_user_duplicate_username(self):
        """Test user creation with duplicate username."""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        data = self.valid_user_data.copy()
        data['username'] = 'existinguser'
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Username already exists')
        
        # Verify only one user with that username exists
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email."""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        data = self.valid_user_data.copy()
        data['email'] = 'existing@example.com'
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email already exists')
        
        # Verify only one user with that email exists
        self.assertEqual(User.objects.filter(email='existing@example.com').count(), 1)
    
    def test_create_user_password_too_short(self):
        """Test user creation with password shorter than 8 characters."""
        data = self.valid_user_data.copy()
        data['password'] = 'short'
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Password must be at least 8 characters long')
        
        # Verify user was not created
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_create_user_password_exactly_8_characters(self):
        """Test user creation with password exactly 8 characters (minimum)."""
        data = self.valid_user_data.copy()
        data['password'] = '12345678'
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_create_user_password_7_characters(self):
        """Test user creation with password 7 characters (below minimum)."""
        data = self.valid_user_data.copy()
        data['password'] = '1234567'
        
        response = self.client.post('/api/create-user/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Password must be at least 8 characters long')
    
    def test_create_user_jwt_token_valid(self):
        """Test that the returned JWT token is valid and can be used."""
        response = self.client.post('/api/create-user/', self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        access_token = response.data['access_token']
        
        # Create a new client with the token
        authenticated_client = APIClient()
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Try to access a protected endpoint
        protected_response = authenticated_client.get('/api/protected/')
        
        # Should succeed if token is valid
        self.assertEqual(protected_response.status_code, status.HTTP_200_OK)
        self.assertIn('message', protected_response.data)
    
    def test_create_user_response_structure(self):
        """Test that the response has the correct structure."""
        response = self.client.post('/api/create-user/', self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check all required fields exist
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('access_token', response.data)
        self.assertIn('token_type', response.data)
        self.assertIn('expires_in', response.data)
        
        # Check user object structure
        user_data = response.data['user']
        self.assertIn('id', user_data)
        self.assertIn('username', user_data)
        self.assertIn('email', user_data)
        
        # Check types
        self.assertIsInstance(response.data['message'], str)
        self.assertIsInstance(user_data['id'], int)
        self.assertIsInstance(user_data['username'], str)
        self.assertIsInstance(user_data['email'], str)
        self.assertIsInstance(response.data['access_token'], str)
        self.assertIsInstance(response.data['token_type'], str)
        self.assertIsInstance(response.data['expires_in'], int)
    
    def test_create_user_multiple_users(self):
        """Test creating multiple different users."""
        user1_data = {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'password123'
        }
        user2_data = {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'password456'
        }
        
        response1 = self.client.post('/api/create-user/', user1_data, format='json')
        response2 = self.client.post('/api/create-user/', user2_data, format='json')
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Verify both users were created
        self.assertTrue(User.objects.filter(username='user1').exists())
        self.assertTrue(User.objects.filter(username='user2').exists())
        self.assertEqual(User.objects.count(), 2)


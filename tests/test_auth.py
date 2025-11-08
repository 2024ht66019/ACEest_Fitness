"""
Authentication route tests.
"""
import pytest
from app.models.user import User


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_register_page_loads(self, client):
        """Test registration page is accessible."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_page_loads(self, client):
        """Test login page is accessible."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_successful_registration(self, client, app):
        """Test user can register successfully."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPassword123',
            'password2': 'NewPassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
    
    def test_registration_duplicate_username(self, client, init_database):
        """Test registration fails with duplicate username."""
        response = client.post('/auth/register', data={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'Password123',
            'password2': 'Password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data or b'already' in response.data.lower()
    
    def test_registration_password_mismatch(self, client):
        """Test registration fails when passwords don't match."""
        response = client.post('/auth/register', data={
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password': 'Password123',
            'password2': 'DifferentPassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Passwords must match' in response.data or b'match' in response.data.lower()
    
    def test_successful_login(self, client, init_database):
        """Test user can login successfully."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Welcome' in response.data
    
    def test_login_invalid_credentials(self, client, init_database):
        """Test login fails with invalid credentials."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data or b'invalid' in response.data.lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login fails for non-existent user."""
        response = client.post('/auth/login', data={
            'username': 'nonexistentuser',
            'password': 'SomePassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data or b'invalid' in response.data.lower()
    
    def test_logout(self, logged_in_client):
        """Test user can logout."""
        response = logged_in_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Try accessing protected page
        response = logged_in_client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
    
    def test_protected_route_requires_login(self, client):
        """Test protected routes redirect to login."""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect
        assert b'/auth/login' in response.data or response.location.endswith('/auth/login')

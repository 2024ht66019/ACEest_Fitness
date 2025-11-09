"""
API endpoint tests.
"""
import pytest
import json


class TestAPIEndpoints:
    """Test API functionality."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_home_page_loads(self, client):
        """Test home page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ACEest Fitness' in response.data or b'fitness' in response.data.lower()
    
    def test_dashboard_requires_authentication(self, client):
        """Test dashboard requires login."""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect
    
    def test_dashboard_loads_when_authenticated(self, logged_in_client):
        """Test authenticated user can access dashboard."""
        response = logged_in_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'workout' in response.data.lower()
    
    def test_404_error_page(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_static_files_accessible(self, client):
        """Test static CSS file is accessible."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200 or response.status_code == 304

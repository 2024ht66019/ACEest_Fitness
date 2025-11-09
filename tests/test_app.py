"""
Simple tests for ACEest Fitness v1.0
"""
import pytest
from app import app, workouts


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client
    
    # Clear workouts after each test
    workouts.clear()


def test_home_page(client):
    """Test home page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'ACEest Fitness' in response.data


def test_add_workout_success(client):
    """Test successful workout addition"""
    response = client.post('/add', data={
        'workout': 'Running',
        'duration': '30'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'added successfully' in response.data


def test_add_workout_missing_fields(client):
    """Test adding workout with missing fields"""
    response = client.post('/add', data={
        'workout': 'Running'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'enter both workout and duration' in response.data


def test_add_workout_invalid_duration(client):
    """Test adding workout with invalid duration"""
    response = client.post('/add', data={
        'workout': 'Running',
        'duration': 'invalid'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'must be a positive number' in response.data


def test_view_workouts_empty(client):
    """Test viewing workouts when none exist"""
    response = client.get('/view')
    assert response.status_code == 200
    assert b'No workouts logged yet' in response.data


def test_view_workouts_with_data(client):
    """Test viewing workouts after adding some"""
    client.post('/add', data={'workout': 'Running', 'duration': '30'})
    client.post('/add', data={'workout': 'Cycling', 'duration': '45'})
    
    response = client.get('/view')
    assert response.status_code == 200
    assert b'Running' in response.data
    assert b'Cycling' in response.data
    assert b'30 minutes' in response.data
    assert b'45 minutes' in response.data


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['version'] == '1.0'

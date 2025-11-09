"""
Pytest configuration and fixtures for ACEest Fitness application tests.
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models.user import User
from models.workout import Workout
from datetime import datetime, timezone


@pytest.fixture(scope='session')
def app():
    """Create application instance for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory DB for tests
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def init_database(app):
    """Initialize database with test data."""
    with app.app_context():
        # Clean up any existing data first
        db.session.query(Workout).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com'
        )
        test_user.set_password('TestPassword123')
        db.session.add(test_user)
        
        # Create another user for testing
        another_user = User(
            username='anotheruser',
            email='another@example.com'
        )
        another_user.set_password('AnotherPass123')
        db.session.add(another_user)
        
        db.session.commit()
        
        # Create test workout
        workout = Workout(
            user_id=test_user.id,
            category='Workout',
            exercise_name='Running',
            duration=30,
            notes='Morning run',
            workout_date=datetime.now(timezone.utc).date()
        )
        db.session.add(workout)
        db.session.commit()
        
        yield
        
        # Cleanup
        db.session.query(Workout).delete()
        db.session.query(User).delete()
        db.session.commit()


@pytest.fixture(scope='function')
def logged_in_client(client, init_database, app):
    """Create authenticated test client."""
    with app.app_context():
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPassword123'
        }, follow_redirects=True)
    return client


@pytest.fixture(scope='function')
def test_user(app, init_database):
    """Get test user from database."""
    with app.app_context():
        return User.query.filter_by(username='testuser').first()

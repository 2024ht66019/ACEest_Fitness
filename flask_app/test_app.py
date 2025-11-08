"""
Basic tests for ACEest Fitness application
Run with: pytest test_app.py
"""

import pytest
from app import create_app, db
from models.user import User
from models.workout import Workout
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


class TestUserModel:
    """Test User model"""
    
    def test_user_creation(self, app):
        """Test creating a user"""
        with app.app_context():
            user = User(username='testuser', email='test@test.com')
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.check_password('password123')
    
    def test_bmi_calculation(self, app):
        """Test BMI calculation"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@test.com',
                height_cm=175,
                weight_kg=70
            )
            
            expected_bmi = 70 / (1.75 ** 2)
            assert abs(user.bmi - expected_bmi) < 0.01
    
    def test_bmr_calculation(self, app):
        """Test BMR calculation for male"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@test.com',
                age=25,
                gender='M',
                height_cm=175,
                weight_kg=70
            )
            
            # Mifflin-St Jeor: 10*70 + 6.25*175 - 5*25 + 5
            expected_bmr = 10*70 + 6.25*175 - 5*25 + 5
            assert user.bmr == expected_bmr


class TestWorkoutModel:
    """Test Workout model"""
    
    def test_workout_creation(self, app):
        """Test creating a workout"""
        with app.app_context():
            user = User(username='testuser', email='test@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            workout = Workout(
                user_id=user.id,
                category='Workout',
                exercise_name='Push-ups',
                duration=30
            )
            
            db.session.add(workout)
            db.session.commit()
            
            assert workout.id is not None
            assert workout.exercise_name == 'Push-ups'
    
    def test_calorie_calculation(self, app):
        """Test calorie calculation"""
        with app.app_context():
            workout = Workout(
                user_id=1,
                category='Workout',
                exercise_name='Running',
                duration=30
            )
            
            # MET formula: (6.0 * 3.5 * 70 / 200) * 30
            calories = workout.calculate_calories(70, 6.0)
            expected = (6.0 * 3.5 * 70 / 200) * 30
            
            assert abs(calories - expected) < 0.01


class TestRoutes:
    """Test application routes"""
    
    def test_index_page(self, client):
        """Test landing page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ACEest Fitness' in response.data
    
    def test_about_page(self, client):
        """Test about page loads"""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_register_page(self, client):
        """Test register page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'Sign Up' in response.data
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects when not logged in"""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect


class TestAuthentication:
    """Test authentication functionality"""
    
    def test_user_registration(self, client, app):
        """Test user registration"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check user was created
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'new@test.com'
    
    def test_user_login(self, client, app):
        """Test user login"""
        # First create a user
        with app.app_context():
            user = User(username='testuser', email='test@test.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # Try to login
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

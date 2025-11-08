"""
Model tests for User and Workout models.
"""
import pytest
from app.models.user import User
from app.models.workout import Workout
from datetime import datetime, timedelta


class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self, app):
        """Test creating a user."""
        with app.app_context():
            user = User(username='modeltest', email='modeltest@example.com')
            user.set_password('TestPass123')
            
            assert user.username == 'modeltest'
            assert user.email == 'modeltest@example.com'
            assert user.password_hash is not None
            assert user.password_hash != 'TestPass123'
    
    def test_password_hashing(self, app):
        """Test password is properly hashed."""
        with app.app_context():
            user = User(username='hashtest', email='hash@example.com')
            user.set_password('MySecretPassword')
            
            assert user.check_password('MySecretPassword') is True
            assert user.check_password('WrongPassword') is False
    
    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(username='reprtest', email='repr@example.com')
            assert 'reprtest' in repr(user)
    
    def test_user_relationship_with_workouts(self, app, init_database, test_user):
        """Test user-workout relationship."""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert len(user.workouts) > 0
            assert isinstance(user.workouts[0], Workout)


class TestWorkoutModel:
    """Test Workout model functionality."""
    
    def test_workout_creation(self, app, test_user):
        """Test creating a workout."""
        with app.app_context():
            workout = Workout(
                user_id=test_user.id,
                workout_type='Testing',
                duration=25,
                calories_burned=250,
                notes='Test workout'
            )
            
            assert workout.workout_type == 'Testing'
            assert workout.duration == 25
            assert workout.calories_burned == 250
            assert workout.notes == 'Test workout'
    
    def test_workout_date_default(self, app, test_user):
        """Test workout date defaults to current time."""
        with app.app_context():
            before = datetime.utcnow()
            workout = Workout(
                user_id=test_user.id,
                workout_type='Testing',
                duration=20,
                calories_burned=200
            )
            after = datetime.utcnow()
            
            assert workout.workout_date is not None
            assert before <= workout.workout_date <= after
    
    def test_workout_repr(self, app, test_user):
        """Test workout string representation."""
        with app.app_context():
            workout = Workout(
                user_id=test_user.id,
                workout_type='Running',
                duration=30,
                calories_burned=300
            )
            
            repr_str = repr(workout)
            assert 'Running' in repr_str
    
    def test_workout_user_relationship(self, app, init_database):
        """Test workout-user relationship."""
        with app.app_context():
            workout = Workout.query.first()
            assert workout.user is not None
            assert isinstance(workout.user, User)
            assert workout.user.username == 'testuser'
    
    def test_workout_calculation_fields(self, app, test_user):
        """Test workout numeric fields."""
        with app.app_context():
            workout = Workout(
                user_id=test_user.id,
                workout_type='Cycling',
                duration=60,
                calories_burned=500,
                notes='Long ride'
            )
            
            # Calculate calories per minute
            calories_per_minute = workout.calories_burned / workout.duration
            assert abs(calories_per_minute - 8.33) < 0.1

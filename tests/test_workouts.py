"""
Workout functionality tests.
"""
import pytest
from models.workout import Workout
from datetime import datetime


class TestWorkouts:
    """Test workout functionality."""
    
    def test_log_workout_page_loads(self, logged_in_client):
        """Test log workout page is accessible."""
        response = logged_in_client.get('/workouts/add')
        assert response.status_code == 200
        assert b'Add Workout' in response.data or b'workout' in response.data.lower()
    
    def test_log_workout_requires_login(self, client):
        """Test log workout requires authentication."""
        response = client.get('/workouts/add')
        assert response.status_code == 302  # Redirect to login
    
    def test_create_workout_success(self, logged_in_client, app, test_user):
        """Test successful workout creation."""
        response = logged_in_client.post('/workouts/add', data={
            'category': 'Workout',
            'exercise_name': 'Cycling',
            'duration': 45,
            'notes': 'Evening bike ride'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify workout created
        with app.app_context():
            workout = Workout.query.filter_by(
                user_id=test_user.id,
                exercise_name='Cycling'
            ).first()
            assert workout is not None
            assert workout.duration == 45
    
    def test_view_workouts_list(self, logged_in_client, init_database):
        """Test viewing list of workouts."""
        response = logged_in_client.get('/workouts/')
        assert response.status_code == 200
        assert b'Running' in response.data  # From init_database fixture
    
    @pytest.mark.skip(reason="workouts/view.html template not implemented yet")
    def test_workout_detail_view(self, logged_in_client, app, test_user):
        """Test viewing individual workout details."""
        with app.app_context():
            workout = Workout.query.filter_by(user_id=test_user.id).first()
            workout_id = workout.id
        
        response = logged_in_client.get(f'/workouts/{workout_id}')
        assert response.status_code == 200
        assert b'Running' in response.data
        assert b'30' in response.data  # Duration
    
    @pytest.mark.skip(reason="workouts/edit.html template not implemented yet")
    def test_edit_workout(self, logged_in_client, app, test_user):
        """Test editing a workout."""
        with app.app_context():
            workout = Workout.query.filter_by(user_id=test_user.id).first()
            workout_id = workout.id
        
        response = logged_in_client.post(f'/workouts/{workout_id}/edit', data={
            'category': 'Workout',
            'exercise_name': 'Running',
            'duration': 40,  # Changed from 30
            'notes': 'Updated morning run'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify changes
        with app.app_context():
            from flask_app.models.workout import Workout as FlaskWorkout
            workout = FlaskWorkout.query.get(workout_id)
            assert workout.duration == 40
    
    def test_delete_workout(self, logged_in_client, app, test_user):
        """Test deleting a workout."""
        with app.app_context():
            # Create a new workout to delete
            workout = Workout(
                user_id=test_user.id,
                category='Workout',
                exercise_name='Swimming',
                duration=20,
                calories_burned=200
            )
            app.extensions['sqlalchemy'].session.add(workout)
            app.extensions['sqlalchemy'].session.commit()
            workout_id = workout.id
        
        response = logged_in_client.post(f'/workouts/{workout_id}/delete', 
                                        follow_redirects=True)
        assert response.status_code == 200
        
        # Verify deletion
        with app.app_context():
            from models.workout import Workout as FlaskWorkout
            workout = FlaskWorkout.query.get(workout_id)
            assert workout is None
    
    def test_user_can_only_see_own_workouts(self, client, app, init_database):
        """Test users can only see their own workouts."""
        # Login as second user
        client.post('/auth/login', data={
            'username': 'anotheruser',
            'password': 'AnotherPass123'
        }, follow_redirects=True)
        
        response = client.get('/workouts/')
        assert response.status_code == 200
        # Should not see testuser's workouts
        assert b'Morning run' not in response.data
    
    def test_invalid_workout_duration(self, logged_in_client):
        """Test workout creation with invalid duration."""
        response = logged_in_client.post('/workouts/add', data={
            'category': 'Workout',
            'exercise_name': 'Running',
            'duration': -10,  # Invalid
            'notes': 'Test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show error or reload form
        assert b'Add Workout' in response.data or b'error' in response.data.lower() or b'must be a positive' in response.data
    
    def test_workout_type_validation(self, logged_in_client):
        """Test workout creation with valid workout categories."""
        valid_categories = ['Warm-up', 'Workout', 'Cool-down']
        
        for category in valid_categories:
            response = logged_in_client.post('/workouts/add', data={
                'category': category,
                'exercise_name': f'Test {category}',
                'duration': 30,
                'notes': f'Test {category}'
            }, follow_redirects=True)
            assert response.status_code == 200

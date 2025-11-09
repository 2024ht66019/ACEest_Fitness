"""
Workout model for tracking exercise sessions
"""

from datetime import datetime, timezone
from app import db


class Workout(db.Model):
    """Workout model for storing individual exercise sessions"""
    
    __tablename__ = 'workouts'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Workout details
    category = db.Column(db.String(50), nullable=False, index=True)  # Warm-up, Workout, Cool-down
    exercise_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    
    # Optional fields
    notes = db.Column(db.Text, nullable=True)
    intensity = db.Column(db.String(20), nullable=True)  # Low, Medium, High
    
    # Timestamps
    workout_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, **kwargs):
        """Initialize workout with default timestamps if not provided"""
        if 'workout_date' not in kwargs:
            kwargs['workout_date'] = datetime.now(timezone.utc).date()
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now(timezone.utc)
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = datetime.now(timezone.utc)
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f'<Workout {self.exercise_name} - {self.duration}min>'
    
    def to_dict(self):
        """Convert workout to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'category': self.category,
            'exercise_name': self.exercise_name,
            'duration': self.duration,
            'notes': self.notes,
            'intensity': self.intensity,
            'workout_date': self.workout_date.isoformat() if self.workout_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

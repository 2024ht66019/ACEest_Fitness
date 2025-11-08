"""
Workout model for tracking exercise sessions
"""

from datetime import datetime
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
    calories_burned = db.Column(db.Float, nullable=True)  # Calculated calories
    
    # Optional fields
    notes = db.Column(db.Text, nullable=True)
    intensity = db.Column(db.String(20), nullable=True)  # Low, Medium, High
    
    # Timestamps
    workout_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Workout {self.exercise_name} - {self.duration}min>'
    
    def calculate_calories(self, weight_kg, met_value):
        """
        Calculate calories burned using MET formula
        Calories = (MET × 3.5 × weight_kg / 200) × duration_minutes
        
        Args:
            weight_kg: User's weight in kilograms
            met_value: Metabolic Equivalent of Task value
        """
        if weight_kg and met_value and self.duration:
            self.calories_burned = round((met_value * 3.5 * weight_kg / 200) * self.duration, 2)
        return self.calories_burned
    
    def to_dict(self):
        """Convert workout to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'category': self.category,
            'exercise_name': self.exercise_name,
            'duration': self.duration,
            'calories_burned': self.calories_burned,
            'notes': self.notes,
            'intensity': self.intensity,
            'workout_date': self.workout_date.isoformat() if self.workout_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

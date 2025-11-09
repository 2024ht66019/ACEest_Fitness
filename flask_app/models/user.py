"""
User model for authentication and profile management
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for storing user account and profile information"""
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile fields
    full_name = db.Column(db.String(100), nullable=True)
    registration_id = db.Column(db.String(50), unique=True, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # M/F/Other
    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    
    # Calculated fields (computed properties)
    # BMI and BMR will be calculated on-the-fly
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    workouts = db.relationship('Workout', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify user password"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def bmi(self):
        """Calculate Body Mass Index (BMI)"""
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 2)
        return None
    
    @property
    def bmi_category(self):
        """
        Determine BMI category with enhanced classification
        Updated to include more detailed categories
        """
        if not self.bmi:
            return "Unknown"
        
        # Enhanced BMI categories
        if self.bmi < 16:
            return "Severely Underweight"
        elif 16 <= self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"
        elif 25 <= self.bmi < 30:
            return "Overweight"
        elif 30 <= self.bmi < 35:
            return "Obese Class I"
        elif 35 <= self.bmi < 40:
            return "Obese Class II"
        else:
            return "Obese Class III"
    
    @property
    def health_recommendation(self):
        """Provide health recommendation based on BMI category"""
        if not self.bmi:
            return "Please update your profile with height and weight information."
        
        recommendations = {
            "Severely Underweight": "Consult a healthcare provider immediately for nutritional guidance.",
            "Underweight": "Consider increasing calorie intake and strength training.",
            "Normal weight": "Maintain current weight with balanced diet and regular exercise.",
            "Overweight": "Focus on cardio exercises and calorie deficit diet.",
            "Obese Class I": "Consult a fitness trainer for personalized weight loss plan.",
            "Obese Class II": "Medical supervision recommended for weight management.",
            "Obese Class III": "Immediate medical consultation required for health assessment."
        }
        
        return recommendations.get(self.bmi_category, "Consult a healthcare provider.")
    
    @property
    def bmr(self):
        """
        Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
        BMR (Men) = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) + 5
        BMR (Women) = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) - 161
        """
        if not all([self.weight_kg, self.height_cm, self.age, self.gender]):
            return None
        
        base_bmr = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age)
        
        if self.gender.upper() == 'M':
            return round(base_bmr + 5, 0)
        elif self.gender.upper() == 'F':
            return round(base_bmr - 161, 0)
        else:
            # For other genders, use average
            return round(base_bmr - 78, 0)
    
    @property
    def tdee(self):
        """
        Calculate Total Daily Energy Expenditure (TDEE)
        Using moderate activity level (exercise 3-5 days/week)
        """
        if not self.bmr:
            return None
        return round(self.bmr * 1.55, 0)
    
    def get_workout_stats(self):
        """Get user's workout statistics"""
        total_workouts = self.workouts.count()
        total_duration = sum(workout.duration for workout in self.workouts)
        total_calories = sum(workout.calories_burned for workout in self.workouts if workout.calories_burned)
        
        return {
            'total_workouts': total_workouts,
            'total_duration': total_duration,
            'total_calories': total_calories,
            'average_duration': round(total_duration / total_workouts, 1) if total_workouts > 0 else 0
        }

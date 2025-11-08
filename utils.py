"""
Utility functions for ACEest Fitness application
"""

from datetime import datetime, timedelta
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def profile_complete_required(f):
    """Decorator to check if user has completed their profile"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not all([current_user.height_cm, current_user.weight_kg, current_user.age, current_user.gender]):
            flash('Please complete your profile first to access this feature.', 'warning')
            return redirect(url_for('auth.profile'))
        
        return f(*args, **kwargs)
    return decorated_function


def calculate_met_calories(met_value, weight_kg, duration_minutes):
    """
    Calculate calories burned using MET formula
    
    Args:
        met_value: Metabolic Equivalent of Task
        weight_kg: User's weight in kilograms
        duration_minutes: Duration of activity in minutes
    
    Returns:
        float: Calories burned
    """
    # Formula: Calories = (MET × 3.5 × weight_kg / 200) × duration_minutes
    if not all([met_value, weight_kg, duration_minutes]):
        return 0.0
    
    return round((met_value * 3.5 * weight_kg / 200) * duration_minutes, 2)


def get_date_range(days=7):
    """
    Get a date range for the last N days
    
    Args:
        days: Number of days to go back (default: 7)
    
    Returns:
        tuple: (start_date, end_date)
    """
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def format_duration(minutes):
    """
    Format duration in minutes to hours and minutes
    
    Args:
        minutes: Duration in minutes
    
    Returns:
        str: Formatted duration string
    """
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours} hr"
    
    return f"{hours} hr {mins} min"


def get_bmi_category(bmi):
    """
    Determine BMI category
    
    Args:
        bmi: Body Mass Index value
    
    Returns:
        str: BMI category
    """
    if not bmi:
        return "Unknown"
    
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def validate_workout_data(category, exercise_name, duration):
    """
    Validate workout input data
    
    Args:
        category: Workout category
        exercise_name: Name of the exercise
        duration: Duration in minutes
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    from config import Config
    
    if not category or category not in Config.WORKOUT_CATEGORIES:
        return False, "Invalid workout category"
    
    if not exercise_name or len(exercise_name.strip()) == 0:
        return False, "Exercise name is required"
    
    if len(exercise_name) > 100:
        return False, "Exercise name is too long (max 100 characters)"
    
    try:
        duration_int = int(duration)
        if duration_int <= 0:
            return False, "Duration must be a positive number"
        if duration_int > 1440:  # 24 hours
            return False, "Duration cannot exceed 24 hours"
    except (ValueError, TypeError):
        return False, "Duration must be a valid number"
    
    return True, ""

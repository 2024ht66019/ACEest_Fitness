"""
Routes package initialization
"""

from routes.auth import auth_bp
from routes.main import main_bp
from routes.workouts import workouts_bp
from routes.analytics import analytics_bp

__all__ = ['auth_bp', 'main_bp', 'workouts_bp', 'analytics_bp']

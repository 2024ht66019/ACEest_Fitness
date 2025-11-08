"""
Routes package initialization
"""

from .auth import auth_bp
from .main import main_bp
from .workouts import workouts_bp
from .analytics import analytics_bp

__all__ = ['auth_bp', 'main_bp', 'workouts_bp', 'analytics_bp']

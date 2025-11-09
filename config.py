"""
Configuration settings for ACEest Fitness application
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # Support both DATABASE_URL and fallback to SQLite
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///aceest_fitness.db'
    
    # Fix for Heroku/Docker postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using them
        'pool_recycle': 300,    # Recycle connections after 5 minutes
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Pagination
    WORKOUTS_PER_PAGE = 20
    
    # MET values for different exercise categories
    MET_VALUES = {
        'Warm-up': 3.0,
        'Workout': 6.0,
        'Cool-down': 2.5
    }
    
    # Exercise categories
    WORKOUT_CATEGORIES = ['Warm-up', 'Workout', 'Cool-down']


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_aceest_fitness.db'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

#!/usr/bin/env python
"""
Run script for ACEest Fitness application
Provides different modes for running the application
"""

import os
import sys
from app import create_app, db
from config import config

# Create application instance for Gunicorn
env = os.getenv('FLASK_ENV', 'production')
app = create_app(config.get(env, config['production']))

def run_development():
    """Run application in development mode"""
    dev_app = create_app(config['development'])
    dev_app.run(debug=True, host='0.0.0.0', port=5000)

def run_production():
    """Run application in production mode"""
    prod_app = create_app(config['production'])
    # In production, use gunicorn or similar WSGI server
    # This is just for demonstration
    prod_app.run(debug=False, host='0.0.0.0', port=5000)

def init_database():
    """Initialize the database"""
    init_app = create_app()
    with init_app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def drop_database():
    """Drop all database tables (use with caution!)"""
    drop_app = create_app()
    with drop_app.app_context():
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() == 'yes':
            db.drop_all()
            print("All database tables dropped!")
        else:
            print("Operation cancelled.")

def create_test_user():
    """Create a test user for development"""
    from models.user import User
    
    test_app = create_app()
    with test_app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print("Test user already exists!")
            return
        
        # Create test user
        user = User(
            username='testuser',
            email='test@aceest.com',
            full_name='Test User',
            age=25,
            gender='M',
            height_cm=175,
            weight_kg=70
        )
        user.set_password('password123')
        
        db.session.add(user)
        db.session.commit()
        
        print("Test user created successfully!")
        print("Username: testuser")
        print("Password: password123")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'dev':
            print("Starting development server...")
            run_development()
        elif command == 'prod':
            print("Starting production server...")
            run_production()
        elif command == 'init-db':
            print("Initializing database...")
            init_database()
        elif command == 'drop-db':
            print("Dropping database...")
            drop_database()
        elif command == 'create-test-user':
            print("Creating test user...")
            create_test_user()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: dev, prod, init-db, drop-db, create-test-user")
    else:
        # Default: run in development mode
        print("Starting development server (default)...")
        run_development()

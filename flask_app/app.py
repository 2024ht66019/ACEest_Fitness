"""
ACEest Fitness & Gym Management System
Main application entry point
Version: 1.0.0
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class=Config):
    """Application factory pattern for creating Flask app instance"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints (use explicit relative imports for package safety)
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.workouts import workouts_bp
    from .routes.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(workouts_bp, url_prefix='/workouts')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

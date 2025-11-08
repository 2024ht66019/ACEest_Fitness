"""
Main routes blueprint
Handles landing page, dashboard, and general pages
"""

from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_app.models.workout import Workout

main_bp = Blueprint('main', __name__)


@main_bp.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'ACEest Fitness'
    }), 200


@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - main hub after login"""
    # Get user statistics
    stats = current_user.get_workout_stats()
    
    # Get recent workouts (last 5)
    recent_workouts = current_user.workouts.order_by(
        Workout.workout_date.desc(), Workout.created_at.desc()
    ).limit(5).all()
    
    return render_template(
        'main/dashboard.html',
        stats=stats,
        recent_workouts=recent_workouts
    )


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')


@main_bp.route('/features')
def features():
    """Features page"""
    return render_template('main/features.html')

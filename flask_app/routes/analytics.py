"""
Analytics routes blueprint
Handles progress tracking, charts, and statistics
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from flask_app.app import db
from flask_app.models.workout import Workout
from flask_app.config import Config

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/')
@login_required
def progress():
    """Display progress tracking dashboard"""
    # Get overall statistics
    stats = current_user.get_workout_stats()
    
    # Get category breakdown
    category_stats = db.session.query(
        Workout.category,
        func.count(Workout.id).label('count'),
        func.sum(Workout.duration).label('total_duration'),
        func.sum(Workout.calories_burned).label('total_calories')
    ).filter(
        Workout.user_id == current_user.id
    ).group_by(Workout.category).all()
    
    # Format category stats
    category_data = {
        stat.category: {
            'count': stat.count,
            'duration': stat.total_duration or 0,
            'calories': round(stat.total_calories, 2) if stat.total_calories else 0
        }
        for stat in category_stats
    }
    
    return render_template(
        'analytics/progress.html',
        stats=stats,
        category_data=category_data,
        categories=Config.WORKOUT_CATEGORIES
    )


@analytics_bp.route('/api/chart-data')
@login_required
def chart_data():
    """API endpoint for chart data"""
    # Get last 30 days of workout data
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    # Query workouts grouped by date and category
    workout_data = db.session.query(
        Workout.workout_date,
        Workout.category,
        func.sum(Workout.duration).label('total_duration'),
        func.sum(Workout.calories_burned).label('total_calories')
    ).filter(
        Workout.user_id == current_user.id,
        Workout.workout_date >= start_date,
        Workout.workout_date <= end_date
    ).group_by(
        Workout.workout_date,
        Workout.category
    ).order_by(Workout.workout_date).all()
    
    # Format data for charts
    daily_data = {}
    for record in workout_data:
        date_str = record.workout_date.isoformat()
        if date_str not in daily_data:
            daily_data[date_str] = {
                'date': date_str,
                'categories': {},
                'total_duration': 0,
                'total_calories': 0
            }
        
        daily_data[date_str]['categories'][record.category] = {
            'duration': record.total_duration or 0,
            'calories': round(record.total_calories, 2) if record.total_calories else 0
        }
        daily_data[date_str]['total_duration'] += record.total_duration or 0
        daily_data[date_str]['total_calories'] += record.total_calories or 0
    
    # Convert to list and sort by date
    chart_data = sorted(daily_data.values(), key=lambda x: x['date'])
    
    return jsonify({
        'success': True,
        'data': chart_data
    })


@analytics_bp.route('/api/category-breakdown')
@login_required
def category_breakdown():
    """API endpoint for category breakdown data"""
    category_stats = db.session.query(
        Workout.category,
        func.count(Workout.id).label('count'),
        func.sum(Workout.duration).label('total_duration'),
        func.sum(Workout.calories_burned).label('total_calories')
    ).filter(
        Workout.user_id == current_user.id
    ).group_by(Workout.category).all()
    
    data = {
        stat.category: {
            'count': stat.count,
            'duration': stat.total_duration or 0,
            'calories': round(stat.total_calories, 2) if stat.total_calories else 0
        }
        for stat in category_stats
    }
    
    return jsonify({
        'success': True,
        'data': data
    })


@analytics_bp.route('/api/weekly-summary')
@login_required
def weekly_summary():
    """API endpoint for weekly summary"""
    # Get last 7 days
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    
    workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.workout_date >= start_date,
        Workout.workout_date <= end_date
    ).all()
    
    total_duration = sum(w.duration for w in workouts)
    total_calories = sum(w.calories_burned for w in workouts if w.calories_burned)
    workout_count = len(workouts)
    
    # Category breakdown
    category_breakdown = {}
    for category in Config.WORKOUT_CATEGORIES:
        cat_workouts = [w for w in workouts if w.category == category]
        category_breakdown[category] = {
            'count': len(cat_workouts),
            'duration': sum(w.duration for w in cat_workouts),
            'calories': sum(w.calories_burned for w in cat_workouts if w.calories_burned)
        }
    
    return jsonify({
        'success': True,
        'summary': {
            'total_workouts': workout_count,
            'total_duration': total_duration,
            'total_calories': round(total_calories, 2),
            'average_duration': round(total_duration / workout_count, 1) if workout_count > 0 else 0,
            'categories': category_breakdown
        }
    })

"""
Workout routes blueprint
Handles workout logging, viewing, and management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from models.workout import Workout
from config import Config

workouts_bp = Blueprint('workouts', __name__)


@workouts_bp.route('/')
@login_required
def list_workouts():
    """List all workouts for the current user"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    
    # Base query
    query = current_user.workouts.order_by(
        Workout.workout_date.desc(),
        Workout.created_at.desc()
    )
    
    # Filter by category if specified
    if category and category in Config.WORKOUT_CATEGORIES:
        query = query.filter_by(category=category)
    
    # Paginate results
    pagination = query.paginate(
        page=page,
        per_page=Config.WORKOUTS_PER_PAGE,
        error_out=False
    )
    
    workouts = pagination.items
    
    return render_template(
        'workouts/list.html',
        workouts=workouts,
        pagination=pagination,
        selected_category=category,
        categories=Config.WORKOUT_CATEGORIES
    )


@workouts_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_workout():
    """Add a new workout"""
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        exercise_name = request.form.get('exercise_name', '').strip()
        duration_str = request.form.get('duration', '0')
        notes = request.form.get('notes', '').strip()
        intensity = request.form.get('intensity', '').strip()
        workout_date_str = request.form.get('workout_date', '')
        
        # Validation
        if not all([category, exercise_name, duration_str]):
            flash('Category, exercise name, and duration are required.', 'danger')
            return render_template('workouts/add.html', categories=Config.WORKOUT_CATEGORIES)
        
        if category not in Config.WORKOUT_CATEGORIES:
            flash('Invalid workout category.', 'danger')
            return render_template('workouts/add.html', categories=Config.WORKOUT_CATEGORIES)
        
        try:
            duration = int(duration_str)
            if duration <= 0:
                raise ValueError
        except ValueError:
            flash('Duration must be a positive number.', 'danger')
            return render_template('workouts/add.html', categories=Config.WORKOUT_CATEGORIES)
        
        # Create workout with current date
        workout = Workout(
            user_id=current_user.id,
            category=category,
            exercise_name=exercise_name,
            duration=duration,
            workout_date=datetime.utcnow().date()
        )
        
        try:
            db.session.add(workout)
            db.session.commit()
            flash(f'Workout "{exercise_name}" added successfully!', 'success')
            return redirect(url_for('workouts.list_workouts'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the workout.', 'danger')
    
    return render_template('workouts/add.html', categories=Config.WORKOUT_CATEGORIES)


@workouts_bp.route('/<int:workout_id>')
@login_required
def view_workout(workout_id):
    """View a specific workout"""
    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('workouts/view.html', workout=workout)


@workouts_bp.route('/<int:workout_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workout(workout_id):
    """Edit a workout"""
    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        exercise_name = request.form.get('exercise_name', '').strip()
        duration_str = request.form.get('duration', '0')
        notes = request.form.get('notes', '').strip()
        intensity = request.form.get('intensity', '').strip()
        workout_date_str = request.form.get('workout_date', '')
        
        # Validation
        if not all([category, exercise_name, duration_str]):
            flash('Category, exercise name, and duration are required.', 'danger')
            return render_template('workouts/edit.html', workout=workout, categories=Config.WORKOUT_CATEGORIES)
        
        try:
            duration = int(duration_str)
            if duration <= 0:
                raise ValueError
        except ValueError:
            flash('Duration must be a positive number.', 'danger')
            return render_template('workouts/edit.html', workout=workout, categories=Config.WORKOUT_CATEGORIES)
        
        # Update workout basic fields only
        workout.category = category
        workout.exercise_name = exercise_name
        workout.duration = duration
        
        try:
            db.session.commit()
            flash('Workout updated successfully!', 'success')
            return redirect(url_for('workouts.view_workout', workout_id=workout.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the workout.', 'danger')
    
    return render_template('workouts/edit.html', workout=workout, categories=Config.WORKOUT_CATEGORIES)


@workouts_bp.route('/<int:workout_id>/delete', methods=['POST'])
@login_required
def delete_workout(workout_id):
    """Delete a workout"""
    workout = Workout.query.filter_by(
        id=workout_id,
        user_id=current_user.id
    ).first_or_404()
    
    try:
        db.session.delete(workout)
        db.session.commit()
        flash('Workout deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the workout.', 'danger')
    
    return redirect(url_for('workouts.list_workouts'))


@workouts_bp.route('/plan')
@login_required
def workout_plan():
    """Display workout plan guide"""
    return render_template('workouts/plan.html')


@workouts_bp.route('/diet')
@login_required
def diet_guide():
    """Display diet guide"""
    return render_template('workouts/diet.html')

"""ACEest Fitness & Gym Tracker
Simple workout tracker - Version 1.0
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# In-memory storage for workouts (resets on app restart)
workouts = []


@app.route('/')
def index():
    """Home page with workout form"""
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_workout():
    """Add a new workout"""
    workout_name = request.form.get('workout', '').strip()
    duration_str = request.form.get('duration', '').strip()
    
    if not workout_name or not duration_str:
        flash('Please enter both workout and duration.', 'error')
        return redirect(url_for('index'))
    
    try:
        duration = int(duration_str)
        if duration <= 0:
            raise ValueError
        
        workouts.append({
            'workout': workout_name,
            'duration': duration,
            'id': len(workouts)
        })
        
        flash(f"'{workout_name}' added successfully!", 'success')
    except ValueError:
        flash('Duration must be a positive number.', 'error')
    
    return redirect(url_for('index'))


@app.route('/view')
def view_workouts():
    """View all logged workouts"""
    return render_template('view.html', workouts=workouts)


@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'ACEest Fitness', 'version': '1.0'}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

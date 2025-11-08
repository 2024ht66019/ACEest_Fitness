# ACEest Fitness - Quick Start Guide

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher installed
- pip (Python package manager)
- Virtual environment tool (venv)

### 2. Installation Steps

```bash
# Navigate to the flask_app directory
cd flask_app

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Initialize the database
python run.py init-db

# (Optional) Create a test user
python run.py create-test-user
```

### 3. Running the Application

```bash
# Development mode (with debug enabled)
python run.py dev

# Or simply:
python app.py
```

The application will be available at: http://localhost:5000

### 4. First Steps

1. **Register a new account**
   - Go to http://localhost:5000
   - Click "Sign Up"
   - Fill in your details

2. **Complete your profile**
   - After login, go to Profile
   - Enter your physical details (height, weight, age, gender)
   - View your calculated BMI, BMR, and TDEE

3. **Log your first workout**
   - Click "Log Workout"
   - Select category (Warm-up, Workout, Cool-down)
   - Enter exercise name and duration
   - Submit

4. **Track your progress**
   - Visit the Progress Tracker
   - View charts and statistics
   - Monitor your fitness journey

### 5. Test User Credentials (if created)
- **Username:** testuser
- **Password:** password123

### 6. Available Commands

```bash
# Run in development mode
python run.py dev

# Run in production mode (use with gunicorn in real production)
python run.py prod

# Initialize database
python run.py init-db

# Drop all tables (WARNING: deletes all data)
python run.py drop-db

# Create test user
python run.py create-test-user
```

### 7. Project Structure Overview

```
flask_app/
├── app.py                  # Main application file
├── run.py                  # Run script with utilities
├── config.py               # Configuration settings
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── models/                 # Database models
├── routes/                 # Application routes/blueprints
├── templates/              # HTML templates
└── static/                 # CSS, JS, images
```

### 8. Key Features to Try

✅ User registration and authentication
✅ Profile management with health metrics
✅ Workout logging with automatic calorie calculation
✅ Progress visualization with charts
✅ Pre-designed workout plans
✅ Diet and nutrition guidelines

### 9. Troubleshooting

**Issue: ModuleNotFoundError**
- Solution: Make sure virtual environment is activated and all packages are installed

**Issue: Database errors**
- Solution: Run `python run.py init-db` to create tables

**Issue: Port already in use**
- Solution: Change the port in app.py or kill the process using port 5000

### 10. Support

For questions or issues:
1. Check the README.md for detailed documentation
2. Review the code comments in each file
3. Ensure all dependencies are properly installed

---

**Ready to Transform Your Fitness Journey!** 💪

Track. Train. Transform.

# ACEest Fitness & Gym Management System

A comprehensive Flask-based web application for tracking fitness activities, monitoring progress, and managing gym workouts.

## 🎯 Features

### Core Functionality
- **User Authentication**: Secure registration and login system with Flask-Login
- **Profile Management**: Store personal information including height, weight, age, and gender
- **Health Metrics**: Automatic BMI, BMR, and TDEE calculations
- **Workout Logging**: Track exercises with categories (Warm-up, Workout, Cool-down)
- **Calorie Tracking**: Automatic calorie calculation using MET values
- **Progress Analytics**: Visual charts and statistics for workout progress
- **Workout Plans**: Pre-designed workout routines for different fitness goals
- **Diet Guidance**: Nutritional recommendations based on fitness objectives

### Technical Highlights
- Modular architecture using Flask Blueprints
- SQLAlchemy ORM for database management
- Responsive Bootstrap 5 UI
- Interactive Chart.js visualizations
- RESTful API endpoints for analytics
- Pythonic code following PEP 8 standards

## 📋 Requirements

- Python 3.8+
- Flask 3.0.0
- SQLAlchemy 2.0+
- Modern web browser

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
cd flask_app
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# Set a secure SECRET_KEY for production
```

### 5. Initialize Database
```bash
python app.py
```
The database will be automatically created on first run.

### 6. Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 📁 Project Structure

```
flask_app/
├── app.py                  # Application entry point and factory
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── models/                # Database models
│   ├── __init__.py
│   ├── user.py           # User model with health metrics
│   └── workout.py        # Workout model with calorie calculations
├── routes/               # Application blueprints
│   ├── auth.py          # Authentication routes
│   ├── main.py          # Main pages and dashboard
│   ├── workouts.py      # Workout CRUD operations
│   └── analytics.py     # Progress tracking and charts
├── templates/           # Jinja2 templates
│   ├── base.html       # Base template with navbar
│   ├── auth/           # Authentication templates
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── main/           # Main page templates
│   │   ├── index.html
│   │   └── dashboard.html
│   ├── workouts/       # Workout templates
│   │   └── add.html
│   └── analytics/      # Analytics templates
│       └── progress.html
└── static/             # Static files
    └── css/
        └── style.css   # Custom styles
```

## 🎨 Key Components

### Models

#### User Model (`models/user.py`)
- User authentication and profile data
- Calculated properties: BMI, BMR, TDEE
- Relationship with workouts
- Password hashing with Werkzeug

#### Workout Model (`models/workout.py`)
- Exercise tracking with categories
- Calorie calculation using MET formula
- Duration and intensity tracking
- Date-based organization

### Blueprints

#### Auth Blueprint (`routes/auth.py`)
- User registration and validation
- Login/logout functionality
- Profile management with health metrics

#### Main Blueprint (`routes/main.py`)
- Landing page
- Dashboard with statistics
- Quick action cards

#### Workouts Blueprint (`routes/workouts.py`)
- Add, edit, delete workouts
- List workouts with pagination
- Category filtering
- Workout and diet guides

#### Analytics Blueprint (`routes/analytics.py`)
- Progress visualization
- Category breakdown
- API endpoints for chart data
- Weekly summaries

## 🔧 Configuration

### Environment Variables (.env)
```
SECRET_KEY=your-secret-key
FLASK_ENV=development
DATABASE_URL=sqlite:///aceest_fitness.db
```

### MET Values
Configurable in `config.py`:
- Warm-up: 3.0
- Workout: 6.0
- Cool-down: 2.5

## 📊 Usage Guide

### 1. Registration
- Navigate to `/auth/register`
- Create account with username, email, and password
- Login with credentials

### 2. Complete Profile
- Go to Profile page
- Enter personal information (age, gender, height, weight)
- View calculated BMI, BMR, and TDEE

### 3. Log Workouts
- Click "Log Workout" button
- Select category (Warm-up, Workout, Cool-down)
- Enter exercise name and duration
- Add optional notes and intensity
- Calories are automatically calculated

### 4. Track Progress
- Visit Progress Tracker page
- View bar and pie charts
- Check category breakdown table
- Monitor overall statistics

### 5. View Workout Plans & Diet Guide
- Access pre-designed workout routines
- Review nutritional guidelines
- Get recommendations for different fitness goals

## 🔐 Security Features

- Password hashing with Werkzeug
- Flask-Login session management
- CSRF protection (with Flask-WTF)
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)

## 🌐 API Endpoints

### Analytics APIs
- `GET /analytics/api/chart-data` - 30-day workout data
- `GET /analytics/api/category-breakdown` - Category statistics
- `GET /analytics/api/weekly-summary` - 7-day summary

All endpoints return JSON responses and require authentication.

## 🚀 Deployment

### Production Checklist
1. Set strong `SECRET_KEY` in environment variables
2. Change `FLASK_ENV=production`
3. Use production database (PostgreSQL recommended)
4. Enable HTTPS
5. Use gunicorn or similar WSGI server:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
   ```

## 🧪 Testing

```bash
# Install testing dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

## 📝 Version History

- **v1.0.0** - Initial release
  - User authentication and profiles
  - Workout tracking with calorie calculation
  - Progress analytics with charts
  - Workout plans and diet guides

## 👥 Contributing

This project follows Python PEP 8 coding standards and uses modular architecture for maintainability.

## 📄 License

This project is developed as part of DevOps coursework at BITS Pilani.

## 🙏 Acknowledgments

- Flask framework and community
- Bootstrap for responsive UI
- Chart.js for data visualization
- Font Awesome for icons

## 📧 Contact

For questions or feedback, please contact the development team.

---

**Track. Train. Transform.** 💪

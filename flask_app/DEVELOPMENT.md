# ACEest Fitness - Development Notes

## Version Information
- **Version:** 1.0.0
- **Date:** November 2024
- **Framework:** Flask 3.0.0
- **Python:** 3.8+

## Architecture Overview

### Design Patterns Used
1. **Application Factory Pattern**: Used in `app.py` with `create_app()` function
2. **Blueprint Pattern**: Modular route organization (auth, main, workouts, analytics)
3. **ORM Pattern**: SQLAlchemy for database abstraction
4. **MVC Pattern**: Models, Views (templates), Controllers (routes)

### Database Schema

#### User Table
- Primary fields: id, username, email, password_hash
- Profile fields: full_name, registration_id, age, gender, height_cm, weight_kg
- Computed properties: bmi, bmr, tdee, bmi_category
- Relationships: One-to-many with Workout

#### Workout Table
- Primary fields: id, user_id, category, exercise_name, duration
- Additional fields: calories_burned, notes, intensity
- Timestamps: workout_date, created_at, updated_at
- Relationship: Many-to-one with User

### MET Values (Metabolic Equivalent of Task)
Used for calorie calculation:
- Warm-up: 3.0 (light activity)
- Workout: 6.0 (moderate to vigorous activity)
- Cool-down: 2.5 (very light activity)

### Calorie Calculation Formula
```
Calories = (MET × 3.5 × weight_kg / 200) × duration_minutes
```

### Health Metrics Formulas

**BMI (Body Mass Index):**
```
BMI = weight_kg / (height_m²)
```

**BMR (Basal Metabolic Rate) - Mifflin-St Jeor Equation:**
```
Men: BMR = 10 × weight_kg + 6.25 × height_cm - 5 × age + 5
Women: BMR = 10 × weight_kg + 6.25 × height_cm - 5 × age - 161
```

**TDEE (Total Daily Energy Expenditure):**
```
TDEE = BMR × Activity_Factor
Using moderate activity (1.55)
```

## API Endpoints

### Authentication Routes (`/auth`)
- GET/POST `/register` - User registration
- GET/POST `/login` - User login
- GET `/logout` - User logout
- GET/POST `/profile` - Profile management

### Main Routes (`/`)
- GET `/` - Landing page
- GET `/dashboard` - User dashboard (requires auth)
- GET `/about` - About page
- GET `/features` - Features page

### Workout Routes (`/workouts`)
- GET `/` - List all workouts (with pagination)
- GET/POST `/add` - Add new workout
- GET `/<id>` - View workout details
- GET/POST `/<id>/edit` - Edit workout
- POST `/<id>/delete` - Delete workout
- GET `/plan` - Workout plan guide
- GET `/diet` - Diet guide

### Analytics Routes (`/analytics`)
- GET `/` - Progress tracker page
- GET `/api/chart-data` - Chart data API (JSON)
- GET `/api/category-breakdown` - Category stats API (JSON)
- GET `/api/weekly-summary` - Weekly summary API (JSON)

## Security Features

1. **Password Security**: Werkzeug password hashing
2. **Session Management**: Flask-Login for user sessions
3. **CSRF Protection**: Built-in Flask protection (can be enhanced with Flask-WTF)
4. **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
5. **XSS Prevention**: Jinja2 automatic escaping

## Code Standards

### Python Style
- Follows PEP 8 guidelines
- Docstrings for all functions and classes
- Type hints where applicable
- Maximum line length: 100 characters

### Naming Conventions
- Classes: PascalCase (e.g., `User`, `Workout`)
- Functions/Methods: snake_case (e.g., `calculate_bmi`, `add_workout`)
- Constants: UPPER_SNAKE_CASE (e.g., `MET_VALUES`, `WORKOUT_CATEGORIES`)
- Private methods: _leading_underscore (e.g., `_validate_input`)

### Template Organization
```
templates/
├── base.html              # Base template with navbar and footer
├── auth/                  # Authentication templates
│   ├── login.html
│   ├── register.html
│   └── profile.html
├── main/                  # Main page templates
│   ├── index.html
│   ├── dashboard.html
│   ├── about.html
│   └── features.html
├── workouts/              # Workout templates
│   ├── list.html
│   ├── add.html
│   ├── plan.html
│   └── diet.html
└── analytics/             # Analytics templates
    └── progress.html
```

## Future Enhancements

### Potential Features
1. **Social Features**: Follow friends, share workouts
2. **Goal Setting**: Set and track fitness goals
3. **Exercise Library**: Pre-defined exercises with instructions
4. **Workout Templates**: Save and reuse workout routines
5. **Export Data**: Export workout history to CSV/PDF
6. **Mobile App**: Native mobile application
7. **Integration**: Connect with fitness wearables
8. **AI Recommendations**: ML-based workout suggestions

### Technical Improvements
1. **Testing**: Unit tests, integration tests
2. **Caching**: Redis for performance optimization
3. **API**: RESTful API for mobile apps
4. **Real-time**: WebSocket for live updates
5. **Internationalization**: Multi-language support
6. **Cloud Storage**: Store workout images/videos

## Performance Considerations

### Database
- Indexed fields: username, email, user_id, workout_date, category
- Lazy loading for relationships
- Pagination for large datasets (20 items per page)

### Frontend
- CDN for Bootstrap and Chart.js
- Minified CSS and JavaScript
- Optimized images
- Efficient chart rendering

### Deployment Recommendations
1. Use PostgreSQL instead of SQLite for production
2. Enable HTTPS with SSL certificate
3. Use environment variables for sensitive data
4. Implement rate limiting
5. Set up proper logging
6. Use WSGI server (gunicorn) with nginx reverse proxy
7. Enable gzip compression
8. Implement CDN for static assets

## Testing Strategy

### Unit Tests
- Model methods (BMI, BMR, TDEE calculations)
- Utility functions
- Form validation

### Integration Tests
- Route handlers
- Authentication flow
- Database operations

### End-to-End Tests
- User registration and login
- Complete workout logging workflow
- Progress tracking

## Maintenance Notes

### Regular Tasks
- Update dependencies regularly
- Review and optimize database queries
- Monitor application logs
- Backup database
- Update security patches

### Code Review Checklist
- [ ] Code follows PEP 8 standards
- [ ] All functions have docstrings
- [ ] No hardcoded credentials
- [ ] Error handling implemented
- [ ] Input validation present
- [ ] Database queries optimized
- [ ] Templates properly escaped
- [ ] Tests pass successfully

---

**Version:** 1.0.0  
**Last Updated:** November 2024  
**Maintained by:** BITS Pilani DevOps Team

#!/usr/bin/env python
"""
Run script for ACEest Fitness application v1.0
Simple workout tracker
"""

import sys

# Import the app instance for Gunicorn
from app import app

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("ACEest Fitness & Gym Tracker v1.0")
        print("Usage: python run.py")
        sys.exit(0)
    
    print("Starting ACEest Fitness v1.0...")
    app.run(debug=True, host='0.0.0.0', port=5000)

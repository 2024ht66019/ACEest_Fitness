"""Compatibility wrapper package exposing the original Flask application factory and db.
This allows legacy imports like `from app import create_app, db` and `from app.models.user import User`.
The real implementation lives under `flask_app`.
"""
from flask_app.app import create_app, db  # re-export
from flask_app import models as models  # expose models subpackage

__all__ = ["create_app", "db", "models"]

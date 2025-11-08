#!/bin/bash
# Database initialization script for Docker PostgreSQL

set -e

echo "Initializing ACEest Fitness database..."
echo "Database: $POSTGRES_DB"
echo "User: $POSTGRES_USER"

# The database is automatically created by the postgres image
# Additional initialization can be added here if needed

echo "Database initialization complete!"

#!/bin/bash
set -e

# Database initialization script for ACEest Fitness
# This script runs automatically when PostgreSQL container starts

echo "Initializing ACEest Fitness database..."

# Create extensions if needed
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
    
    -- Create schema if needed
    CREATE SCHEMA IF NOT EXISTS public;
    
    GRANT ALL ON SCHEMA public TO "$POSTGRES_USER";
    GRANT ALL ON SCHEMA public TO public;
EOSQL

echo "Database initialization completed successfully!"

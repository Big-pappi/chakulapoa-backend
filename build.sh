#!/usr/bin/env bash
# =============================================================================
# Chakula Poa - Render.com Build Script
# =============================================================================
# This script is executed during Render.com deployment

set -o errexit  # Exit on error

echo "=== Chakula Poa Build Script ==="

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Setup initial data (only runs if data doesn't exist)
echo "Setting up initial data..."
python manage.py setup_initial_data || echo "Initial data already exists or setup failed"

echo "=== Build Complete ==="

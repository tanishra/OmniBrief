#!/bin/bash
set -e

echo "Running Database Migrations..."
alembic upgrade head

echo "Starting OmniBrief API via Gunicorn..."
# Run the gunicorn server pointing to app:app
exec gunicorn app:app -c gunicorn.conf.py

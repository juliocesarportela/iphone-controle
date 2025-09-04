#!/bin/bash

# Production startup script for Django application

# Set production environment
export DJANGO_SETTINGS_MODULE=iphone_import_system.production_settings

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
" || true

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 iphone_import_system.wsgi:application

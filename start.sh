#!/bin/bash

# Production startup script for Django application with enhanced debugging

# Set production environment
export DJANGO_SETTINGS_MODULE=iphone_import_system.production_settings

echo "=== Django Production Startup ==="
echo "Django Settings: $DJANGO_SETTINGS_MODULE"
echo "Port: ${PORT:-8000}"
echo "Python version: $(python --version)"
echo "Django version: $(python -c 'import django; print(django.get_version())')"

# Check database connection
echo "=== Checking database connection ==="
python manage.py check --database default || echo "Database check failed, continuing..."

# Run database migrations with verbose output
echo "=== Running database migrations ==="
python manage.py migrate --noinput --verbosity=2

# Create essential tables if they don't exist
echo "=== Ensuring auth tables exist ==="
python manage.py migrate auth --noinput || echo "Auth migration failed, continuing..."
python manage.py migrate contenttypes --noinput || echo "Contenttypes migration failed, continuing..."
python manage.py migrate sessions --noinput || echo "Sessions migration failed, continuing..."

# Collect static files
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --verbosity=2

# Create superuser with better error handling
echo "=== Creating superuser ==="
python manage.py shell -c "
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Superuser created successfully')
    else:
        print('✅ Superuser already exists')
except Exception as e:
    print(f'❌ Error creating superuser: {e}')
" || echo "Superuser creation failed, continuing..."

# Test basic Django functionality
echo "=== Testing Django setup ==="
python manage.py check || echo "Django check failed, continuing anyway..."

# Start the application with Gunicorn
echo "=== Starting Gunicorn server ==="
echo "Binding to 0.0.0.0:${PORT:-8000}"
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 --log-level info iphone_import_system.wsgi:application

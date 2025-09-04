web: gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 120 iphone_import_system.wsgi:application
release: python manage.py migrate --noinput --settings=iphone_import_system.production_settings

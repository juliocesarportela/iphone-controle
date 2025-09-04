from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Debug production environment and create admin user'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Production Debug Information ==='))
        
        # Database info
        self.stdout.write(f"Database Engine: {settings.DATABASES['default']['ENGINE']}")
        self.stdout.write(f"Database Name: {settings.DATABASES['default']['NAME']}")
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS("✅ Database connection: OK"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Database connection failed: {e}"))
            return
        
        # Check if auth tables exist
        try:
            User = get_user_model()
            user_count = User.objects.count()
            self.stdout.write(f"✅ User table exists. Total users: {user_count}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ User table error: {e}"))
            return
        
        # Create admin user
        try:
            User = get_user_model()
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
                self.stdout.write(self.style.SUCCESS("✅ Admin user created successfully"))
                self.stdout.write("Username: admin")
                self.stdout.write("Password: admin123")
            else:
                self.stdout.write(self.style.WARNING("⚠️ Admin user already exists"))
                
            # Also create a test user
            if not User.objects.filter(username='test').exists():
                User.objects.create_user(
                    username='test',
                    email='test@example.com',
                    password='test123'
                )
                self.stdout.write(self.style.SUCCESS("✅ Test user created"))
                self.stdout.write("Username: test")
                self.stdout.write("Password: test123")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating users: {e}"))
        
        # Environment info
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"SECRET_KEY: {'*' * 20} (hidden)")
        
        self.stdout.write(self.style.SUCCESS('=== Debug Complete ==='))

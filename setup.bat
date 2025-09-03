@echo off
echo ========================================
echo CONFIGURANDO AMBIENTE DJANGO
echo ========================================

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Instalando dependencias...
pip install django==5.0
pip install psycopg2-binary
pip install django-crispy-forms
pip install crispy-tailwind
pip install django-htmx
pip install python-decouple
pip install pillow
pip install openpyxl
pip install pandas
pip install django-extensions

echo.
echo Criando requirements.txt...
pip freeze > requirements.txt

echo.
echo Criando projeto Django...
django-admin startproject iphone_import_system .

echo.
echo Criando app core...
python manage.py startapp core

echo.
echo ========================================
echo SETUP CONCLUIDO!
echo ========================================
echo.
echo Proximos passos:
echo 1. Configure o banco de dados no settings.py
echo 2. Execute: python manage.py makemigrations
echo 3. Execute: python manage.py migrate
echo 4. Execute: python manage.py createsuperuser
echo ========================================

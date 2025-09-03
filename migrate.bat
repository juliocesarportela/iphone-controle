@echo off
echo ========================================
echo EXECUTANDO MIGRATIONS DO DJANGO
echo ========================================

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Executando migrations...
python manage.py migrate

echo.
echo Criando superusuario...
echo (Pressione Ctrl+C se nao quiser criar agora)
python manage.py createsuperuser

echo.
echo ========================================
echo MIGRATIONS CONCLUIDAS!
echo ========================================

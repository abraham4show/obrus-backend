@echo off
echo Deleting old database...
del /f db.sqlite3 2>nul

echo Running migrations in correct order...
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate users
python manage.py migrate

echo Done! Now create superuser with: python manage.py createsuperuser
pause

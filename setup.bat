@echo off
echo Setting up Obrus Django Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
    echo Please edit .env with your configuration before continuing!
    pause
    exit /b 1
)

REM Run migrations
echo Running migrations...
python manage.py migrate

REM Create superuser
echo Creating superuser...
python manage.py createsuperuser

echo.
echo Setup complete! Run 'python manage.py runserver' to start the development server.
pause

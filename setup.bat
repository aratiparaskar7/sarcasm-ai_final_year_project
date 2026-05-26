@echo off
echo ========================================
echo  Sarcasm Detection - Project Setup
echo ========================================

cd /d "c:\Final yr Project"

echo [0/5] Generating project files...
python setup_project.py
if errorlevel 1 ( echo ERROR: setup_project.py failed & pause & exit /b 1 )

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] Installing dependencies...
pip install -r sarcasm_detect\requirements.txt

echo [3/5] Creating media directories...
mkdir sarcasm_detect\media\images 2>nul
mkdir sarcasm_detect\media\audio 2>nul
mkdir sarcasm_detect\media\videos 2>nul

echo [4/5] Running Django migrations...
cd sarcasm_detect
python manage.py makemigrations
python manage.py migrate

echo [5/5] Creating superuser (optional - press Ctrl+C to skip)...
python manage.py createsuperuser

echo.
echo ========================================
echo  Setup complete! Run the server with:
echo  cd "c:\Final yr Project\sarcasm_detect"
echo  ..\venv\Scripts\activate.bat
echo  python manage.py runserver
echo ========================================
pause

@echo off
echo ============================================
echo   CineMatch - Django Movie Recommender
echo   Server: http://127.0.0.1:8000
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Installing dependencies...
pip install django pandas numpy scikit-learn
echo.

echo [2/3] Setting up database...
python manage.py migrate --run-syncdb 2>nul
echo.

echo [3/3] Starting Django server on http://127.0.0.1:8000 ...
echo.
echo  Open your browser at: http://127.0.0.1:8000
echo  API base URL:         http://127.0.0.1:8000/api/
echo  Press Ctrl+C to stop.
echo.
python manage.py runserver 127.0.0.1:8000
pause

@echo off
:: Launch Roblox Age Statistics
echo Starting Roblox Player Statistics...
echo.

:: Try to run Python with the script
python roblox_age_statistics.py

:: If that fails, try python3 (for some systems)
if %errorlevel% == 9009 (
    echo 'python' command not found. Trying 'python3'...
    python3 roblox_age_statistics.py
)

:: Check if script was not found
if %errorlevel% == 2 (
    echo.
    echo ERROR: Could not find 'roblox_age_statistics.py'
    echo Make sure this .bat file is in the same folder as the Python script.
    echo.
    pause
)

:: If Python is not installed
if %errorlevel% == 9009 (
    echo.
    echo ERROR: Python not found.
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
)

echo.
echo Tracker closed.
pause
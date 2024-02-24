@echo off
color 5
title Installing Dependencies...

:: Change directory to current directory
cd /d "%~dp0"
::echo Current directory: %CD% :: To debug if you are getting requrirements.txt not found error

:: Install requirements
echo Installing Requirements...
python -m pip install -r requirements.txt

:: Check for updates
cd tools
echo Checking for updates...
python update.py

@echo off

:START
cls
echo Welcome to songway!
echo.

echo Instructions:
echo 1. Download Instructions:
echo    - Download the project files to your computer.
echo.
echo 2. Run Startup Script:
echo    - Locate the startup.bat file in the downloaded folder.
echo    - Double-click startup.bat to run the script. This will initiate the application.
echo.
echo 3. Error Reporting:
echo    - If you encounter any errors or issues while running the application, please report them to https://discord.com/users/962552468292648990.
echo.
echo Additional Information:
echo - System Requirements:
echo   - Windows operating system.
echo   - Python installed (if required by the application).
echo.
echo - Contact Information:
echo   - For any inquiries or support, please contact https://discord.com/users/962552468292648990.
echo.
echo Press any key to exit.

:: Define color codes for rainbow effect
set "colors=4 6 2 3 5 9 1"
set "delay=2" 

:: Loop through colors and display information
for %%C in (%colors%) do (
    color %%C
    timeout /t %delay% >nul
)

:: Reset color and end of script
color 07

:: Wait for user input to exit
pause >nul

@echo off
:: Bugster CLI installer wrapper for Windows

echo ============================================================
echo Bugster CLI Installer
echo ============================================================

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Python is installed, continuing with installation...
) else (
    python3 --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Python is installed, continuing with installation...
    ) else (
        echo ❌ Python is not installed or not in your PATH
        echo.
        
        :: Check if we have winget available for automated installation
        winget --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo Would you like to install Python 3.12.7 automatically using winget? (Y/N)
            set /p choice="> "
            if /i "%choice%"=="Y" (
                echo Installing Python 3.12.7...
                winget install Python.Python.3.12 -h
                echo.
                echo Verifying installation...
                timeout /t 2 >nul
                
                :: Need to refresh PATH to see newly installed Python
                :: Create a temporary batch file to refresh environment variables and continue installation
                echo @echo off > %TEMP%\continue_install.bat
                echo setlocal >> %TEMP%\continue_install.bat
                echo set PATH=%%PATH%%;%%LOCALAPPDATA%%\Programs\Python\Python312;%%LOCALAPPDATA%%\Programs\Python\Python312\Scripts >> %TEMP%\continue_install.bat
                echo set PATH=%%PATH%%;%%PROGRAMFILES%%\Python312;%%PROGRAMFILES%%\Python312\Scripts >> %TEMP%\continue_install.bat
                echo echo Checking for Python... >> %TEMP%\continue_install.bat
                echo python --version >> %TEMP%\continue_install.bat
                echo if %%ERRORLEVEL%% EQU 0 ( >> %TEMP%\continue_install.bat
                echo   echo Python installed successfully >> %TEMP%\continue_install.bat
                echo   echo Downloading Bugster CLI installer... >> %TEMP%\continue_install.bat
                echo   curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/install.py ^> %%TEMP%%\bugster_install.py >> %TEMP%\continue_install.bat
                echo   python %%TEMP%%\bugster_install.py >> %TEMP%\continue_install.bat
                echo   del %%TEMP%%\bugster_install.py >> %TEMP%\continue_install.bat
                echo ) else ( >> %TEMP%\continue_install.bat
                echo   echo Python installation verification failed >> %TEMP%\continue_install.bat
                echo   echo Please restart your computer and try running the installer again >> %TEMP%\continue_install.bat
                echo ) >> %TEMP%\continue_install.bat
                echo pause >> %TEMP%\continue_install.bat
                
                echo.
                echo Installation will continue in a new window after Python is installed.
                echo Please run the installer again if any issues occur.
                start cmd /c %TEMP%\continue_install.bat
                exit /b 0
            ) else (
                goto :manual_install
            )
        ) else (
            :manual_install
            echo.
            echo To install Python on Windows:
            echo   1. Download the latest Python installer from https://www.python.org/downloads/windows/
            echo   2. Run the installer and make sure to check "Add Python to PATH"
            echo   3. Restart your computer and run this installer again
            echo.
            pause
            exit /b 1
        )
    )
)

:: Download and run the Python installer script
echo Downloading the Bugster CLI installer...
curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/install.py > %TEMP%\bugster_install.py
python %TEMP%\bugster_install.py
del %TEMP%\bugster_install.py

pause 
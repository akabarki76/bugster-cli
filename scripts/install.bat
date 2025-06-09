@echo off
setlocal enabledelayedexpansion

:: Bugster CLI installer wrapper for Windows

:: ANSI color codes for Windows 10+
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: Enable ANSI escape sequences
reg query HKCU\Console /v VirtualTerminalLevel >nul 2>&1
if %ERRORLEVEL% neq 0 (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
)

:: Print functions
:print_step
echo.
echo %BLUE%=^> %~1%NC%
exit /b

:print_error
echo %RED%%~1%NC%
exit /b

:print_success
echo %GREEN%%~1%NC%
exit /b

:print_warning
echo %YELLOW%%~1%NC%
exit /b

:: Show help message
:show_help
echo Bugster CLI Installer
echo.
echo Usage:
echo     install.bat [options]
echo.
echo Options:
echo     -v, --version VERSION    Install specific version (e.g., v0.2.8, v0.2.8-beta.1)
echo     -h, --help              Show this help message
echo.
echo Examples:
echo     install.bat                           # Install latest version
echo     install.bat -v v0.2.8                # Install specific version
echo     install.bat -v v0.2.8-beta.1         # Install beta version
exit /b

:: Parse command line arguments
set "VERSION=latest"
:parse_args
if "%~1"=="" goto :main
if /i "%~1"=="-h" (
    call :show_help
    exit /b 0
)
if /i "%~1"=="--help" (
    call :show_help
    exit /b 0
)
if /i "%~1"=="-v" (
    if "%~2"=="" (
        call :print_error "Version argument is missing"
        call :show_help
        exit /b 1
    )
    set "VERSION=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--version" (
    if "%~2"=="" (
        call :print_error "Version argument is missing"
        call :show_help
        exit /b 1
    )
    set "VERSION=%~2"
    shift
    shift
    goto :parse_args
)
call :print_error "Unknown option: %~1"
call :show_help
exit /b 1

:main
call :print_step "Checking Python installation..."

:: Check if Python 3.10+ is installed
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    call :print_success "✅ %PYTHON_VERSION% is installed, continuing with installation..."
) else (
    python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        for /f "tokens=*" %%i in ('python3 --version') do set PYTHON_VERSION=%%i
        call :print_success "✅ %PYTHON_VERSION% is installed, continuing with installation..."
    ) else (
        call :print_error "❌ Python 3.10 or higher is required"
        echo.
        
        :: Check if we have winget available for automated installation
        winget --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            call :print_warning "Would you like to install Python 3.12 automatically using winget? (Y/N)"
            set /p choice="> "
            if /i "!choice!"=="Y" (
                call :print_step "Installing Python 3.12..."
                winget install Python.Python.3.12 -h --accept-source-agreements --accept-package-agreements
                echo.
                call :print_step "Verifying installation..."
                timeout /t 2 >nul
                
                :: Need to refresh PATH to see newly installed Python
                :: Create a temporary batch file to refresh environment variables and continue installation
                echo @echo off > "%TEMP%\continue_install.bat"
                echo setlocal enabledelayedexpansion >> "%TEMP%\continue_install.bat"
                echo set PATH=%%PATH%%;%%LOCALAPPDATA%%\Programs\Python\Python312;%%LOCALAPPDATA%%\Programs\Python\Python312\Scripts >> "%TEMP%\continue_install.bat"
                echo set PATH=%%PATH%%;%%PROGRAMFILES%%\Python312;%%PROGRAMFILES%%\Python312\Scripts >> "%TEMP%\continue_install.bat"
                echo call :print_step "Checking Python installation..." >> "%TEMP%\continue_install.bat"
                echo python -c "import sys; sys.exit(0 if sys.version_info ^>= (3, 10) else 1)" >> "%TEMP%\continue_install.bat"
                echo if %%ERRORLEVEL%% EQU 0 ( >> "%TEMP%\continue_install.bat"
                echo   call :print_success "Python installed successfully" >> "%TEMP%\continue_install.bat"
                echo   call :print_step "Downloading Bugster CLI installer..." >> "%TEMP%\continue_install.bat"
                if "%VERSION%"=="latest" (
                    echo   curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/scripts/install.py ^> "%%TEMP%%\bugster_install.py" >> "%TEMP%\continue_install.bat"
                    echo   python "%%TEMP%%\bugster_install.py" >> "%TEMP%\continue_install.bat"
                ) else (
                    echo   curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/scripts/install.py ^> "%%TEMP%%\bugster_install.py" >> "%TEMP%\continue_install.bat"
                    echo   python "%%TEMP%%\bugster_install.py" --version "%VERSION%" >> "%TEMP%\continue_install.bat"
                )
                echo   del "%%TEMP%%\bugster_install.py" >> "%TEMP%\continue_install.bat"
                echo ) else ( >> "%TEMP%\continue_install.bat"
                echo   call :print_error "Python installation verification failed" >> "%TEMP%\continue_install.bat"
                echo   call :print_error "Please restart your computer and try running the installer again" >> "%TEMP%\continue_install.bat"
                echo ) >> "%TEMP%\continue_install.bat"
                echo pause >> "%TEMP%\continue_install.bat"
                
                call :print_step "Installation will continue in a new window after Python is installed."
                call :print_warning "Please run the installer again if any issues occur."
                start cmd /c "%TEMP%\continue_install.bat"
                exit /b 0
            ) else (
                goto :manual_install
            )
        ) else (
            :manual_install
            echo.
            call :print_warning "To install Python on Windows:"
            echo   1. Download the latest Python installer (3.10 or higher^) from https://www.python.org/downloads/windows/
            echo   2. Run the installer and make sure to check "Add Python to PATH"
            echo   3. Restart your computer and run this installer again
            echo.
            pause
            exit /b 1
        )
    )
)

:: Download and run the Python installer script
call :print_step "Downloading the Bugster CLI installer..."
if "%VERSION%"=="latest" (
    curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/scripts/install.py > "%TEMP%\bugster_install.py"
    python "%TEMP%\bugster_install.py"
) else (
    curl -sSL https://raw.githubusercontent.com/Bugsterapp/bugster-cli/main/scripts/install.py > "%TEMP%\bugster_install.py"
    python "%TEMP%\bugster_install.py" --version "%VERSION%"
)

set EXIT_CODE=%ERRORLEVEL%
del "%TEMP%\bugster_install.py"

if %EXIT_CODE% EQU 0 (
    call :print_warning "Please add the Bugster installation directory to your PATH if not already added:"
    echo %LOCALAPPDATA%\Programs\bugster
    echo.
    call :print_success "To use Bugster CLI, run: bugster --help"
)

pause
exit /b %EXIT_CODE% 
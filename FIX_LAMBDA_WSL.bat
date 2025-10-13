@echo off
echo ========================================
echo NeuroAgent Lambda Fix - WSL Automated
echo ========================================
echo.

REM Get current Windows path
set WINPATH=%CD%

echo Current directory: %WINPATH%
echo.
echo Starting WSL Lambda dependency fix...
echo This will take 5-10 minutes...
echo.

REM Convert Windows path to WSL path
REM C:\Users\... becomes /mnt/c/Users/...
set WSLPATH=/mnt/c/Users/thc1006/Desktop/dev/neuro-agent

wsl bash -c "cd %WSLPATH% && chmod +x scripts/fix_lambda_dependencies.sh && ./scripts/fix_lambda_dependencies.sh"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Lambda dependencies fixed
    echo ========================================
    echo.
    echo Next step: Deploy to AWS
    echo   cd infrastructure/cdk-clean
    echo   cdk deploy NeuroAgentStack
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Lambda fix failed
    echo ========================================
    echo.
    echo Check WSL installation:
    echo   wsl --list --verbose
    echo.
)

pause

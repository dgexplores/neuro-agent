@echo off
echo ========================================
echo Building Lambda Layer with Docker
echo ========================================
echo.
echo This will create a Lambda layer that is 100%% compatible
echo with AWS Lambda Python 3.11 runtime.
echo.

REM Clean old layer
echo Cleaning old lambda_layer...
if exist lambda_layer rmdir /s /q lambda_layer
mkdir lambda_layer

REM Build Docker image
echo Building Docker image...
docker build -f Dockerfile.lambda -t neuroagent-lambda-builder .

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)

REM Extract compiled packages from container
echo Extracting compiled packages from container...
docker create --name temp-lambda neuroagent-lambda-builder
docker cp temp-lambda:/asset/python lambda_layer/
docker rm temp-lambda

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to extract packages
    pause
    exit /b 1
)

REM Verify
echo.
echo ========================================
echo Verification
echo ========================================
for /f "tokens=3" %%a in ('dir /s /-c lambda_layer ^| find "File(s)"') do set FILE_COUNT=%%a
echo Files in lambda_layer: %FILE_COUNT%

for /f %%a in ('powershell -command "(Get-ChildItem lambda_layer -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB"') do set SIZE_MB=%%a
echo Size: ~%SIZE_MB% MB

echo.
echo Checking for key packages...
if exist "lambda_layer\python\fastapi" (echo [OK] fastapi) else (echo [MISSING] fastapi)
if exist "lambda_layer\python\pydantic" (echo [OK] pydantic) else (echo [MISSING] pydantic)
if exist "lambda_layer\python\pydantic_core" (echo [OK] pydantic_core) else (echo [MISSING] pydantic_core)
if exist "lambda_layer\python\annotated_types" (echo [OK] annotated_types) else (echo [MISSING] annotated_types)
if exist "lambda_layer\python\boto3" (echo [OK] boto3) else (echo [MISSING] boto3)
if exist "lambda_layer\python\mangum" (echo [OK] mangum) else (echo [MISSING] mangum)

echo.
echo ========================================
echo SUCCESS! Lambda layer built
echo ========================================
echo.
echo Next step: Deploy to AWS
echo Run: DEPLOY_LAMBDA_AFTER_WSL.bat
echo.
pause

@echo off
echo ========================================
echo Deploy Lambda to AWS After WSL Fix
echo ========================================
echo.

REM Check if lambda_layer exists
if not exist "lambda_layer\python" (
    echo ERROR: lambda_layer/python not found!
    echo Please run FIX_LAMBDA_WSL.bat first.
    pause
    exit /b 1
)

echo Lambda layer found. Checking size...
for /f "tokens=3" %%a in ('dir /s /-c lambda_layer ^| find "File(s)"') do set LAYER_SIZE=%%a
echo Layer size: %LAYER_SIZE% bytes
echo.

echo ========================================
echo Step 1: CDK Synth
echo ========================================
cd infrastructure\cdk-clean
call cdk synth

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: CDK synth failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2: CDK Deploy
echo ========================================
echo This will deploy the updated Lambda with dependencies...
echo.

call cdk deploy NeuroAgentStack --require-approval never

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Lambda deployed
    echo ========================================
    echo.
    echo Testing Lambda...
    cd ..\..
    curl https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health
    echo.
    echo.
    echo If you see {"status":"healthy"}, Lambda is working!
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: CDK deploy failed
    echo ========================================
    echo.
    echo Check CloudFormation console for details:
    echo https://console.aws.amazon.com/cloudformation/
    echo.
)

pause

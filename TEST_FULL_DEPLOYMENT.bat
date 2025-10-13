@echo off
echo ========================================
echo NeuroAgent Full Deployment Test
echo ========================================
echo.

echo Testing Frontend (Vercel)...
curl -s -o nul -w "Frontend Status: %%{http_code}\n" https://frontend-8dchdjadv-thc1006s-projects.vercel.app

echo.
echo Testing Backend Health (AWS)...
curl -s https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health

echo.
echo.
echo Testing Backend API Docs...
curl -s -o nul -w "API Docs Status: %%{http_code}\n" https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/docs

echo.
echo ========================================
echo Generating JWT Token for Testing...
echo ========================================
python scripts\generate_jwt.py demo-physician 24 > jwt_token.txt 2>&1
type jwt_token.txt | findstr "Bearer"

echo.
echo ========================================
echo Test Summary
echo ========================================
echo Frontend URL: https://frontend-8dchdjadv-thc1006s-projects.vercel.app
echo Backend URL: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/
echo API Docs: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/docs
echo.
echo JWT Token saved to: jwt_token.txt
echo.
echo To test diagnosis API:
echo   curl -X POST https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis \
echo     -H "Authorization: Bearer REDACTED" \
echo     -H "Content-Type: application/json" \
echo     -d @data/demo_cases.json
echo.

pause

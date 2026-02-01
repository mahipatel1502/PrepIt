@echo off
REM Firebase Authentication Setup Script for Windows

echo.
echo ============================================
echo    Firebase Authentication Setup
echo ============================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Creating from .env.example...
    copy .env.example .env
)

REM Check for Firebase Web API Key
findstr /C:"YOUR_WEB_API_KEY_HERE" .env >nul
if %errorlevel% equ 0 (
    goto :prompt_api_key
)

findstr /C:"FIREBASE_WEB_API_KEY" .env >nul
if %errorlevel% neq 0 (
    goto :prompt_api_key
)

goto :install_deps

:prompt_api_key
echo.
echo [WARNING] FIREBASE_WEB_API_KEY not configured!
echo.
echo To get your Firebase Web API Key:
echo   1. Go to https://console.firebase.google.com
echo   2. Select your project
echo   3. Click the gear icon (Settings) -^> Project Settings
echo   4. Under 'General' tab, find 'Web API Key'
echo   5. Copy the key (starts with 'AIza...')
echo.
set /p api_key="Enter your Firebase Web API Key: "

if not "%api_key%"=="" (
    echo FIREBASE_WEB_API_KEY=%api_key%>> .env
    echo [SUCCESS] API Key saved to .env
) else (
    echo [WARNING] No API key provided. Please update .env manually.
)

:install_deps
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ============================================
echo [SUCCESS] Setup complete!
echo ============================================
echo.
echo Next steps:
echo   1. Enable Email/Password in Firebase Console:
echo      https://console.firebase.google.com -^> Authentication -^> Sign-in method
echo.
echo   2. Start the server:
echo      uvicorn app.main:app --reload
echo.
echo   3. Test the API:
echo      http://localhost:8000/docs
echo.
echo Documentation:
echo   - MIGRATION_COMPLETE.md     - Overview and next steps
echo   - FIREBASE_AUTH_MIGRATION.md - Detailed guide
echo   - FIREBASE_AUTH_QUICKREF.md  - API reference
echo.
pause

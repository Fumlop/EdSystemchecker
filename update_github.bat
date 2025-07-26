@echo off
echo ========================================
echo Elite Dangerous PowerPlay Git Updater
echo ========================================

REM Check if we're in a git repository
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Not in a git repository
    pause
    exit /b 1
)

echo 🔄 Starting update process...

REM Run the GitHub update pipeline
echo 📊 Generating reports...
python python\github_update.py
if %errorlevel% neq 0 (
    echo ❌ Report generation failed
    pause
    exit /b 1
)

REM Check for changes
git diff --quiet
if %errorlevel% neq 0 (
    echo 📝 Changes detected, committing...
    
    REM Add all report files
    git add *.md json\*.json
    
    REM Create commit with timestamp
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set mydate=%%c-%%a-%%b
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a:%%b
    
    git commit -m "🤖 Auto-update PowerPlay reports - %mydate% %mytime%"
    
    echo 🚀 Pushing to GitHub...
    git push
    
    if %errorlevel% equ 0 (
        echo ✅ Successfully updated GitHub repository!
    ) else (
        echo ❌ Failed to push to GitHub
        echo 💡 You may need to pull first or check your authentication
    )
) else (
    echo ℹ️  No changes to commit
)

echo ========================================
echo Update process completed
echo ========================================
pause

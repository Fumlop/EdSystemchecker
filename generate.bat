@echo off
echo Starting PowerPlay Analysis Pipeline
echo =====================================
cd /d d:\Apps\EdSystemChecker

echo.
echo [1/5] Downloading fresh data (with cleanup)...
if exist "html\power-controlled-5.html" if exist "html\power-exploited-5.html" (
    echo → Found existing files, cleaning up and downloading fresh data...
    python python\download.py
) else (
    echo → No existing files found, downloading fresh data...
    python python\download.py
)
if errorlevel 1 (
    echo ❌ Download failed
    pause
    exit /b 1
)

echo.
echo [2/5] Extracting system data...
python python\extract.py
if errorlevel 1 (
    echo ❌ Extraction failed
    pause
    exit /b 1
)

echo.
echo [3/5] Generating stronghold report...
python python\create_stronghold_md.py
if errorlevel 1 (
    echo ❌ Stronghold report failed
    pause
    exit /b 1
)

echo.
echo [4/5] Generating exploited report...
python python\create_exploited_md.py
if errorlevel 1 (
    echo ❌ Exploited report failed
    pause
    exit /b 1
)

echo.
echo [5/6] Generating fortified report...
python python\create_fortified_md.py
if errorlevel 1 (
    echo ❌ Fortified report failed
    pause
    exit /b 1
)

echo.
echo [6/6] Generating README...
python python\genreadme.py
if errorlevel 1 (
    echo ❌ README generation failed
    pause
    exit /b 1
)

echo.
echo ✅ Pipeline complete! All reports generated.
echo.
echo Generated files:
echo   • json\stronghold_systems.json
echo   • json\exploited_systems.json
echo   • json\fortified_systems.json
echo   • stronghold_status.md
echo   • exploited_status.md
echo   • fortified_status.md
echo   • README.md
echo.
pause

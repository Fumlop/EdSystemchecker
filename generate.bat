@echo off
echo Starting PowerPlay Analysis Pipeline
echo =====================================
cd /d d:\Apps\EdSystemChecker

echo.
echo [1/7] Downloading HTML data...
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
echo [2/7] Extracting system data...
python python\extract.py
if errorlevel 1 (
    echo ❌ Extraction failed
    pause
    exit /b 1
)

echo.
echo [3/7] Generating stronghold report...
python python\create_stronghold_md.py
if errorlevel 1 (
    echo ❌ Stronghold report failed
    pause
    exit /b 1
)

echo.
echo [4/7] Generating exploited report...
python python\create_exploited_md.py
if errorlevel 1 (
    echo ❌ Exploited report failed
    pause
    exit /b 1
)

echo.
echo [5/7] Generating fortified report...
python python\create_fortified_md.py
if errorlevel 1 (
    echo ❌ Fortified report failed
    pause
    exit /b 1
)

echo.
echo [6/7] Generating contested systems report...
python python\create_contested_md.py
if errorlevel 1 (
    echo ❌ Contested systems report failed
    pause
    exit /b 1
)

echo.
echo [7/7] Generating README...
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
echo   • json\contested_systems.json
echo   • stronghold_status.md
echo   • exploited_status.md
echo   • fortified_status.md
echo   • contested_status.md
echo   • README.md
echo.
pause

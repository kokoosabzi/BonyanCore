# فایل bat را با محتوای کامل ایجاد کن
@"
@echo off
chcp 65001 >nul
echo ============================================================
echo Bonyan Core - Full File Generator
echo Creating all files...
echo ============================================================

REM Create folders
mkdir app 2>nul
mkdir app\core 2>nul
mkdir app\models 2>nul
mkdir app\schemas 2>nul
mkdir app\services 2>nul
mkdir app\routers 2>nul
mkdir app\templates 2>nul
mkdir app\static 2>nul
mkdir app\utils 2>nul
mkdir migrations 2>nul
mkdir migrations\versions 2>nul
mkdir docs 2>nul
mkdir imports 2>nul
mkdir exports 2>nul
mkdir uploads 2>nul
mkdir tests 2>nul

echo.
echo All folders created!
echo.
pause
"@ | Out-File -FilePath create_all_files.bat -Encoding ASCII
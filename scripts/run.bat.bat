@echo off
chcp 65001 >nul
echo 🚀 Ejecutando TikTok-Control-Panel (modo desarrollo)...
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instala Python 3.8+
    pause
    exit /b
)

python app/main_monitor.py

echo.
echo ⚠️ Cierra esta ventana cuando termines.
pause
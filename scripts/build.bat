@echo off
chcp 65001 >nul
echo 🏗️ Compilando TikTok-Control-Panel v7.0...
echo.

:: Instalar PyInstaller si no está
pip install pyinstaller --quiet

:: Compilar sin consola
pyinstaller ^
--onefile ^
--windowed ^
--name "TikTok-Control-Panel" ^
--distpath "." ^
--workpath "build_temp" ^
--clean ^
app/main_monitor.py

echo.
echo ✅ ¡Listo! Ejecutable creado: TikTok-Control-Panel.exe
echo    - Sin ventana negra
echo    - Todo integrado
pause
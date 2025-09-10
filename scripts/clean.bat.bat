@echo off
chcp 65001 >nul
echo 🧹 Limpiando archivos temporales...
echo.

if exist "build_temp" (
    rmdir /s /q "build_temp"
    echo ✅ Carpeta build_temp eliminada
)

if exist "__pycache__" (
    rmdir /s /q "__pycache__"
    echo ✅ Carpeta __pycache__ eliminada
)

if exist "*.spec" (
    del "*.spec"
    echo ✅ Archivo .spec eliminado
)

echo.
echo 💡 Usa este script antes de compilar para evitar errores.
pause
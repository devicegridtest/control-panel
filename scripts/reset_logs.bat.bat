
@echo off
chcp 65001 >nul
echo 🗑️ Reiniciando logs...
echo.

set LOG_FILE=output\actividad.log

if exist "%LOG_FILE%" (
    echo # Log reiniciado el %date% %time% > "%LOG_FILE%"
    echo ✅ Archivo de log reiniciado
) else (
    echo # Log creado el %date% %time% > "%LOG_FILE%"
    echo ✅ Archivo de log creado
)

echo.
echo 📄 Puedes verlo en: %cd%\%LOG_FILE%
pause
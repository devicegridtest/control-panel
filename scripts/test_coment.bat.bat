@echo off
chcp 65001 >nul
echo 🧪 Prueba de Comentarios
echo.

set /p serial="📌 Serial (Enter=primero): "

if "%serial%"=="" (
    for /f "skip=1 tokens=1" %%d in ('adb devices ^| findstr /i "device"') do (
        set serial=%%d
        goto :start_test
    )
) else (
    goto :start_test
)

:start_test
if "%serial%"=="" (
    echo ❌ No hay dispositivos
    pause
    exit /b 1
)

echo 📱: %serial%
adb -s %serial% shell am start -n com.zhiliaoapp.musically/.MainActivity
timeout /t 5 >nul
adb -s %serial% shell input tap 651 773
timeout /t 2 >nul
adb -s %serial% shell input tap 285 1275
timeout /t 1 >nul
adb -s %serial% shell input text "Excelente video"
timeout /t 1 >nul
adb -s %serial% shell input keyevent KEYCODE_ENTER
echo ✅ Comentario enviado
pause
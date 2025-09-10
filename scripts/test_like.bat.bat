@echo off
chcp 65001 >nul
echo 🧪 Prueba de Like (doble tap) en todos los dispositivos...
echo.

for /f "skip=1 tokens=1" %%d in ('adb devices ^| findstr /i "device"') do (
    if not "%%d"=="" (
        echo 📱 Dispositivo: %%d
        echo ❤️  Doble tap (like)...
        adb -s %%d shell input tap 720 833
        timeout /t 0.1 >nul
        adb -s %%d shell input tap 720 833
        echo ↕️  Deslizando...
        adb -s %%d shell input touchscreen swipe 580 941 580 54
        echo.
    )
)

echo ✅ Prueba de like completada.
pause
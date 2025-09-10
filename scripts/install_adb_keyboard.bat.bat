@echo off
chcp 65001 >nul
echo 📥 Instalando AdbKeyboard en todos los dispositivos...
echo.

:: Verificar que el APK exista
if not exist "app\extra\AdbKeyboard.apk" (
    echo ❌ No se encontró el archivo: app\extra\AdbKeyboard.apk
    echo 💡 Asegúrate de descargarlo y colocarlo en esa carpeta.
    echo.
    echo 📥 Descárgalo desde:
    echo    https://github.com/senzhk/ADBKeyBoard/releases/download/v1.1/AdbKeyboard.apk
    echo.
    pause
    exit /b 1
)

:: Instalar en cada dispositivo
for /f "skip=1 tokens=1" %%d in ('adb devices ^| findstr /i "device" ^| findstr /v "offline"') do (
    if not "%%d"=="" (
        echo 📱 Dispositivo: %%d
        echo 📦 Instalando AdbKeyboard...
        adb -s %%d install "app\extra\AdbKeyboard.apk"
        if %errorlevel% equ 0 (
            echo ✅ Listo en %%d
        ) else (
            echo ⚠️ Error en %%d (puede ya estar instalado)
        )
        echo.
    )
)

echo 💡 Actívalo en cada dispositivo:
echo    Ajustes → Sistema → Idiomas y entrada → Teclado → Teclado virtual → AdbKeyboard
echo.
pause
@echo off
chcp 65001 >nul

echo 🛑 MATEMOS TODAS LAS ACCIONES DE LOS DISPOSITIVOS...
echo ====================================================

:: 1. Matar ADB (detiene todos los comandos: tap, swipe, text, etc)
echo 🚫 Cerrando ADB...
taskkill /f /im adb.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ ADB terminado
) else (
    echo ⚠️  ADB ya estaba cerrado o no se encontró
)

:: 2. Matar scrcpy
echo 🖥️ Cerrando scrcpy...
taskkill /f /im scrcpy.exe >nul 2>&1
taskkill /f /im cmd.exe /fi "WINDOWTITLE eq scrcpy*" >nul 2>&1
echo ✅ Ventanas de scrcpy cerradas

:: 3. Opcional: Reiniciar ADB server (limpia conexiones)
echo 🔄 Reiniciando servidor ADB...
adb start-server
adb kill-server
adb start-server
echo ✅ Servidor ADB reiniciado

:: 4. Verificar dispositivos
echo 📱 Dispositivos conectados:
adb devices

echo.
echo 💡 Todos los bots, taps, comentarios y scrolls han sido detenidos.
echo    Puedes reiniciar tu app de forma segura.
echo.
pause
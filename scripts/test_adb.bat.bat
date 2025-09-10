@echo off
chcp 65001 >nul
echo 🧰 Diagnóstico ADB
echo =================
echo.

:: Ver dispositivos
echo 📱 Dispositivos conectados:
adb devices -l
echo.

:: Probar cada dispositivo
for /f "skip=1 tokens=1" %%d in ('adb devices ^| findstr /i "device" ^| findstr /v "offline"') do (
    if not "%%d"=="" (
        echo 🔄 Probando %%d...
        adb -s %%d shell getprop ro.product.model
        adb -s %%d shell getprop ro.serialno
        echo ✅ Conexión OK
        echo.
    )
)

:: Verificar ADB
echo 🛠️ Estado de ADB:
adb version
echo.

echo 💡 Si todo está OK, puedes usar el panel sin problemas.
pause
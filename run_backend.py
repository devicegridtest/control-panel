# run_backend.py
"""
Servidor FastAPI para el Panel de Control TikTok v8.0 PRO
Conexión REAL con dispositivos Android mediante ADB
"""

import os
import subprocess
import threading
import time
import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from typing import Dict, Any
import uvicorn

# === CONFIGURACIÓN DE SEGURIDAD ===
security = HTTPBasic()

# Usuarios permitidos (en producción, usa .env o base de datos)
USERS = {
    "admin": "devicegrid2025"  # Cambia esta contraseña
}

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(credentials.username, "admin")
    correct_pass = secrets.compare_digest(credentials.password, USERS["admin"])
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=401,
            detail="Acceso denegado. Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# === ESTADO GLOBAL DEL SISTEMA ===
system_status = {
    "devices": [],
    "bots": {
        "likes": 0,
        "comments": 0,
        "auto_replicate": False
    },
    "last_update": time.strftime("%H:%M:%S")
}

# Ruta al script de control
MAIN_MONITOR_SCRIPT = "app/main_monitor.py"

# Directorio de subidas
UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# === FUNCIÓN REAL DE MONITOREO CON ADB ===
def get_adb_devices():
    """Ejecuta 'adb devices' y devuelve una lista de dispositivos conectados"""
    try:
        # Ejecutar comando adb
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Error al ejecutar ADB: {result.stderr}")
            return []

        # Parsear salida
        lines = result.stdout.strip().splitlines()
        devices = []
        for line in lines[1:]:  # Ignorar encabezado
            if "\t" in line:
                device_id, status = line.split("\t")
                if status == "device":
                    devices.append(device_id)
                else:
                    print(f"⚠️ Dispositivo {device_id} en estado: {status}")
        return devices

    except FileNotFoundError:
        print("❌ ADB no está instalado o no está en el PATH")
        return []
    except Exception as e:
        print(f"❌ Error inesperado al ejecutar ADB: {e}")
        return []

def real_device_monitor():
    """Monitorea dispositivos ADB en tiempo real"""
    print("🔍 Iniciando monitoreo de dispositivos ADB...")
    while True:
        try:
            # Obtener dispositivos reales
            devices = get_adb_devices()
            system_status["devices"] = devices
            system_status["last_update"] = time.strftime("%H:%M:%S")
            print(f"✅ Dispositivos detectados: {devices}")
        except Exception as e:
            print(f"❌ Error en monitoreo ADB: {e}")
            system_status["devices"] = []
        
        time.sleep(5)  # Actualizar cada 5 segundos

# Iniciar monitoreo en segundo plano
threading.Thread(target=real_device_monitor, daemon=True).start()

# === INICIALIZAR FASTAPI ===
app = FastAPI(
    title="DeviceGrid API",
    description="Backend para el Panel de Control TikTok v8.0 PRO",
    version="1.0.0"
)

# Permitir CORS (solo para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia a dominio específico en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ENDPOINTS DE LA API ===

@app.get("/api/status")
def get_status(user: str = Depends(authenticate)) -> Dict[str, Any]:
    """Obtiene el estado actual del sistema (dispositivos, bots, etc.)"""
    return system_status

@app.post("/api/start")
def start_control_panel(user: str = Depends(authenticate)) -> Dict[str, str]:
    """Inicia el panel de control en segundo plano"""
    def run_monitor():
        try:
            subprocess.run([os.sys.executable, MAIN_MONITOR_SCRIPT], check=True)
        except Exception as e:
            print(f"❌ Error al iniciar el panel: {e}")

    thread = threading.Thread(target=run_monitor, daemon=True)
    thread.start()
    return {"status": "started", "message": "Panel de control iniciado"}

@app.post("/api/command/{command}")
def send_command(command: str, user: str = Depends(authenticate)) -> Dict[str, str]:
    """Envía comandos al panel de control (futuro: integración con main_monitor.py)"""
    valid_commands = ["refresh", "start_likes", "start_comments", "stop_all"]
    
    if command not in valid_commands:
        raise HTTPException(status_code=400, detail="Comando no soportado")

    # Aquí podrías enviar señales al main_monitor.py
    if command == "refresh":
        system_status["devices"] = get_adb_devices()  # Forzar actualización
    elif command == "start_likes":
        system_status["bots"]["likes"] += 1
    elif command == "start_comments":
        system_status["bots"]["comments"] += 1
    elif command == "stop_all":
        system_status["bots"] = {"likes": 0, "comments": 0, "auto_replicate": False}

    return {"status": "success", "command": command, "message": f"Comando '{command}' ejecutado"}

@app.post("/api/upload/template")
def upload_template(file: UploadFile = File(...), user: str = Depends(authenticate)):
    """Sube una plantilla de imagen"""
    file_path = os.path.join(UPLOAD_DIR, f"template_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return {"message": "Plantilla subida exitosamente", "path": file_path}

@app.post("/api/upload/video")
def upload_video(file: UploadFile = File(...), user: str = Depends(authenticate)):
    """Sube un video para usar en pruebas"""
    file_path = os.path.join(UPLOAD_DIR, f"video_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return {"message": "Video subido exitosamente", "path": file_path}

@app.get("/api/health")
def health_check():
    """Endpoint para verificar que el servidor está activo"""
    return {"status": "healthy", "timestamp": time.time()}

# === EJECUCIÓN ===
if __name__ == "__main__":
    print("🚀 Iniciando servidor DeviceGrid en http://localhost:8000")
    print("🔐 Acceso: usuario=admin, contraseña=devicegrid2025")
    print("📱 Asegúrate de tener 'adb' instalado y dispositivos conectados")
    uvicorn.run("run_backend:app", host="0.0.0.0", port=8000, reload=False)
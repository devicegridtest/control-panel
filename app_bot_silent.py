# app/bot_silent.py - Versión silenciosa (sin ventana)
import subprocess
import threading
import random
import time
import sys

# Configuración
ADB = "adb"
TIKTOK_PKG = "com.zhiliaoapp.musically"
SCROLL_INTERVAL = 35
COMMENT_INTERVAL = 20

COMMENTS = [
    "¡Excelente video!", "Muy buen contenido 💯", "¡Me encanta! 🔥",
    "¿Qué modelo usas?", "Sube más videos 🙌", "¡Increíble edición!",
    "Gracias por compartir ❤️", "Wow, viral seguro 🚀",
    "Buenos likes 👍", "Suscribete a mi canal!"
]

def run_adb(cmd):
    try:
        return subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True, timeout=10).stdout
    except:
        return None

def get_devices():
    result = run_adb("devices")
    if not result: return []
    return [l.split()[0] for l in result.splitlines()[1:] if "device" in l and not l.startswith("*")]

def open_tiktok(serial):
    run_adb(f"-s {serial} shell monkey -p {TIKTOK_PKG} -c android.intent.category.LAUNCHER 1")
    time.sleep(3)

def force_landscape(serial):
    run_adb(f"-s {serial} shell settings put system user_rotation 1")
    run_adb(f"-s {serial} shell settings put system accelerometer_rotation 0")

def bot_loop(serial):
    print(f"[{serial}] Bot iniciado: scroll cada {SCROLL_INTERVAL}s, comentario cada {COMMENT_INTERVAL}s")
    last_scroll = time.time()
    last_comment = time.time()

    while True:
        now = time.time()

        if now - last_scroll >= SCROLL_INTERVAL:
            run_adb(f"-s {serial} shell input touchscreen swipe 500 1200 500 300")
            print(f"[{serial}] ↕️ Deslizado")
            last_scroll = now

        if now - last_comment >= COMMENT_INTERVAL:
            run_adb(f"-s {serial} shell input tap 900 1300")
            time.sleep(1)
            comment = random.choice(COMMENTS)
            run_adb(f"-s {serial} shell input text '{comment}'")
            run_adb(f"-s {serial} shell input keyevent KEYCODE_ENTER")
            print(f"[{serial}] 💬 Comentó: {comment}")
            last_comment = now

        time.sleep(1)

def main():
    print("🚀 Iniciando bot silencioso para TikTok...")
    print("🔍 Buscando dispositivos ADB...")

    while True:
        devices = get_devices()
        print(f"✅ {len(devices)} dispositivos conectados: {devices}")

        for serial in devices:
            if serial not in [t.name for t in threading.enumerate()]:
                threading.Thread(target=bot_loop, args=(serial,), name=serial, daemon=True).start()

        time.sleep(10)  # Reescanea cada 10 segundos

if __name__ == "__main__":
    main()
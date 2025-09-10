# capture_template_enhanced.py - Captura Inteligente de Plantillas (Auto-Detección + Variaciones)
import cv2
import numpy as np
import os
import time
import mss
from PIL import Image
import argparse

# === CONFIGURACIÓN ===
OUTPUT_DIR = "templates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Resolución típica de TikTok (vertical)
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1280

# Zona aproximada de botones (ajustar si es necesario)
LIKE_REGION = (680, 780, 60, 100)    # (x, y, width, height) cerca del corazón
COMMENT_REGION = (640, 770, 60, 100) # cerca del ícono de comentario

# Aumento de robustez
VARIATIONS = [
    {"alpha": 1.0, "beta": 0},   # Original
    {"alpha": 1.2, "beta": 10},  # Más brillante
    {"alpha": 0.8, "beta": -10}, # Más oscuro
    {"alpha": 1.0, "beta": 0}    # Escala (se hace después)
]

def adjust_brightness_contrast(image, alpha=1.0, beta=0):
    """Ajusta brillo (beta) y contraste (alpha)"""
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def capture_screen():
    """Captura la pantalla completa usando mss"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Monitor principal
        img = sct.grab(monitor)
        frame = np.array(img)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

def find_window_region():
    """Busca la ventana de scrcpy o asume posición (ajustable)"""
    print("🔍 Buscando ventana de scrcpy... (asegúrate de tenerla abierta)")
    time.sleep(1)
    screen = capture_screen()
    h, w = screen.shape[:2]
    
    # Suponemos que scrcpy está centrado (ajusta si está en esquina)
    x = (w - SCREEN_WIDTH) // 2
    y = (h - SCREEN_HEIGHT) // 2
    x = max(0, x)
    y = max(0, y)
    
    return x, y

def extract_region(screen, win_x, win_y, roi_x, roi_y, w, h):
    """Extrae región ajustada a la ventana de scrcpy"""
    abs_x = win_x + roi_x
    abs_y = win_y + roi_y
    abs_x = max(0, abs_x)
    abs_y = max(0, abs_y)
    return screen[abs_y:abs_y+h, abs_x:abs_x+w]

def auto_capture_button(button_type="like"):
    """Captura automática del botón cuando aparece"""
    print(f"\n🤖 Modo automático: detectando botón de {button_type}...")
    print("👉 Abre TikTok y reproduce un video. Mantén el botón visible.")

    # Obtener posición de ventana
    win_x, win_y = find_window_region()
    print(f"📍 Ventana detectada en ({win_x}, {win_y})")

    roi = LIKE_REGION if button_type == "like" else COMMENT_REGION
    template_name = f"template_{button_type}.png"
    variations = []

    captured = False
    start_time = time.time()

    while not captured and (time.time() - start_time) < 30:  # Máx 30 segundos
        screen = capture_screen()
        region = extract_region(screen, win_x, win_y, *roi)

        # Convertir a escala de grises
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detección por bordes (para botones con contorno)
        edges = cv2.Canny(blur, 50, 150)

        # Contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = w / h if h != 0 else 0

            # Filtro: tamaño y proporción de botón
            if 800 < area < 15000 and 0.8 < aspect < 1.5:
                print(f"✅ Posible botón detectado: área={area}, relación={aspect:.2f}")
                detail = region[y:y+h, x:x+w]
                if detail.size == 0:
                    continue

                # Guardar variaciones
                for i, var in enumerate(VARIATIONS):
                    enhanced = adjust_brightness_contrast(detail, var["alpha"], var["beta"])
                    if i == 3:
                        # Escala: 90% y 110%
                        h_small, w_small = int(h*0.9), int(w*0.9)
                        small = cv2.resize(detail, (w_small, h_small))
                        variations.append((adjust_brightness_contrast(small, 1.0, 0), f"{button_type}_scale_small"))
                        
                        h_large, w_large = int(h*1.1), int(w*1.1)
                        large = cv2.resize(detail, (w_large, h_large))
                        variations.append((adjust_brightness_contrast(large, 1.0, 0), f"{button_type}_scale_large"))
                    else:
                        variations.append((enhanced, f"{button_type}_v{i}"))

                captured = True
                break

        if not captured:
            print("⏳ Buscando botón...", end="\r")
            time.sleep(1)

    if not captured:
        print("\n❌ No se detectó el botón. Intenta manualmente o acércate más.")
        return

    # Guardar todas las variaciones
    saved_files = []
    for i, (img, suffix) in enumerate(variations):
        if "scale" in suffix:
            name = f"template_{suffix}.png"
        else:
            name = f"template_{button_type}_{i}.png"
        path = os.path.join(OUTPUT_DIR, name)
        cv2.imwrite(path, img)
        saved_files.append(name)

    print(f"\n🎉 ¡Captura automática exitosa!")
    print(f"💾 Guardado en: {OUTPUT_DIR}/")
    for f in saved_files:
        img = cv2.imread(os.path.join(OUTPUT_DIR, f))
        if img is not None:
            print(f"   ✅ {f} → {img.shape[1]}x{img.shape[0]} px")
    print(f"\n📌 Usa 'template_{button_type}.png' como principal, los demás son backups.")


def manual_capture():
    """Captura manual con selección de ROI"""
    print("\n🎯 Modo manual: selecciona el área del botón")
    screen = capture_screen()
    win_x, win_y = find_window_region()

    cv2.namedWindow("🎯 Selecciona el botón", cv2.WINDOW_NORMAL)
    roi = cv2.selectROI("🎯 Selecciona el botón", screen, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("🎯 Selecciona el botón")

    if roi[2] == 0 or roi[3] == 0:
        print("❌ No se seleccionó ningún área.")
        return

    x, y, w, h = roi
    cropped = screen[y:y+h, x:x+w]

    name = input("Nombre del botón (ej: like, comment): ").strip()
    if not name:
        name = "custom"

    # Guardar variaciones
    for i, var in enumerate(VARIATIONS):
        enhanced = adjust_brightness_contrast(cropped, var["alpha"], var["beta"])
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"template_{name}_v{i}.png"), enhanced)

    # Escalas
    small = cv2.resize(cropped, (int(w*0.9), int(h*0.9)))
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"template_{name}_scale_small.png"), small)
    large = cv2.resize(cropped, (int(w*1.1), int(w*1.1)))
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"template_{name}_scale_large.png"), large)

    print(f"✅ {len(VARIATIONS) + 2} variantes guardadas para 'template_{name}'")


if __name__ == "__main__":
    print("==========================================")
    print("  🎯 CAPTURADOR INTELIGENTE DE PLANTILLAS")
    print("==========================================")
    print("Este script detecta automáticamente los botones de TikTok")
    print("y genera múltiples variantes para mejor detección.")

    mode = input("\n¿Modo? (1) Automático, (2) Manual: ").strip()

    if mode == "1":
        btn = input("¿Qué botón? (1) Like, (2) Comentario: ").strip()
        button_type = "like" if btn == "1" else "comment" if btn == "2" else "custom"
        auto_capture_button(button_type)
    elif mode == "2":
        manual_capture()
    else:
        print("❌ Opción no válida.")
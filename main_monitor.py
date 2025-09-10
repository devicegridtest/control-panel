# app/main_monitor.py - Panel de Control TikTok v8.0 PRO (Con Partículas Animadas + Control Maestro)
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import random
import time
import csv
import os
import cv2
import numpy as np

# === CONFIGURACIÓN ===
ADB = "adb"
SCRCPY = "scrcpy"
TIKTOK_PKG = "com.zhiliaoapp.musically"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Configuración de ventana
WINDOW_WIDTH = 185
WINDOW_HEIGHT = 370
MARGIN = 5
MAX_COLS = 10

# Comentarios personalizados
COMMENTS = [
    "Excelente video", "uy buen contenido 💯", "Me encanta! 🔥",
    "Qué modelo usas?", "Sube más videos 🙌", "Increíble edición!",
    "Gracias por compartir ❤️", "esto es viral seguro 🚀",
    "nice video ❤️", "very cool ❤️", "incredible 🚀",
    "aquí nos quedamos xd", "pero que ven mis ojos xd", "me gusta lo que veo"
]

# Paleta Neón
NEON_GREEN = "#00FF00"
NEON_CYAN = "#00FFFF"
NEON_PINK = "#FF00FF"
NEON_RED = "#FF0000"
NEON_BLUE = "#33CCFF"
NEON_ORANGE = "#FF5E00"
NEON_PURPLE = "#CC00FF"
NEON_YELLOW = "#FFFF00"
NEON_LIME = "#99FF00"

# Colores modo oscuro
BG_DARK = "#121212"
FG_LIGHT = "#FFFFFF"
FG_GRAY = "#BBBBBB"

class Particle:
    def __init__(self, canvas, x, y, color, size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.color = color
        self.size = size
        self.id = canvas.create_oval(
            x, y, x + size, y + size,
            fill=color, outline="", stipple="gray50"
        )

    def move(self):
        self.x += self.vx
        self.y += self.vy
        if not (0 < self.x < self.canvas.winfo_width()):
            self.vx *= -1
        if not (0 < self.y < self.canvas.winfo_height()):
            self.vy *= -1
        self.canvas.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)

class TikTokControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Panel de Control TikTok v8.0 PRO")
        self.root.geometry("1400x750")
        self.root.configure(bg=BG_DARK)

        # === FONDO CON PARTÍCULAS ===
        self.canvas = tk.Canvas(root, bg=BG_DARK, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.particles = []
        self.create_particles(300)
        self.animate_particles()

        # Aplicar estilo oscuro
        self.setup_dark_style()

        # Fuentes
        self.button_font = ("Segoe UI", 10, "bold")
        self.header_font = ("Arial", 18, "bold")
        self.label_font = ("Arial", 11)
        self.console_font = ("Consolas", 10)

        self.devices = []
        self.bots = {}
        self.master_process = None
        self.monitoring = False

        self.create_widgets()
        self.start_monitor()
        self.start_pulse_animation()

    def setup_dark_style(self):
        """Configura el estilo oscuro con ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=BG_DARK)
        style.configure("TLabel", background=BG_DARK, foreground=FG_LIGHT)
        style.configure("TButton", background=BG_DARK, foreground=FG_LIGHT)
        style.map("TButton", background=[('active', '#222222')])
        style.configure("Treeview", background="#1E1E1E", foreground=FG_LIGHT, fieldbackground=BG_DARK)
        style.map('Treeview', background=[('selected', NEON_BLUE)], foreground=[('selected', 'black')])
        style.configure("TCombobox", fieldbackground=BG_DARK, background=BG_DARK, foreground=FG_LIGHT)

    def create_particles(self, count):
        """Crea partículas en posiciones aleatorias"""
        for _ in range(count):
            x = random.randint(1, self.root.winfo_width())
            y = random.randint(0, self.root.winfo_height())
            color = random.choice([NEON_GREEN, NEON_CYAN, NEON_PINK, NEON_BLUE, NEON_YELLOW, NEON_PURPLE])
            size = random.randint(1, 8)
            p = Particle(self.canvas, x, y, color, size)
            self.particles.append(p)

    def animate_particles(self):
        """Animación suave de partículas"""
        for p in self.particles:
            try:
                p.move()
            except tk.TclError:
                return
        self.root.after(50, self.animate_particles)

    def create_widgets(self):
        # Header (sobre el canvas)
        tk.Label(self.root, text="🎮 Panel de Control TikTok v8.0 PRO", font=self.header_font,
                 bg=BG_DARK, fg=NEON_CYAN).pack(pady=10)
        tk.Label(self.root, text="Control total: interacción, comentarios, visualización",
                 fg=FG_GRAY, font=self.label_font, bg=BG_DARK).pack()

        # === BOTONES PRINCIPALES ===
        btn_frame = tk.Frame(self.root, bg=BG_DARK)
        btn_frame.pack(pady=10)

        self.btn_refresh = tk.Button(btn_frame, text="🔄 Refrescar", command=self.refresh,
                                     bg=NEON_GREEN, fg="#000000", width=14, font=self.button_font,
                                     highlightthickness=2, highlightbackground="#33ff33")
        self.btn_refresh.grid(row=0, column=0, padx=6, pady=4)

        self.btn_open = tk.Button(btn_frame, text="📱 Abrir TikTok", command=self.open_tiktok,
                                  bg=NEON_CYAN, fg="#000000", width=14, font=self.button_font,
                                  highlightthickness=2, highlightbackground="#33ffff")
        self.btn_open.grid(row=0, column=1, padx=6, pady=4)

        self.btn_landscape = tk.Button(btn_frame, text="🔁 Horizontal", command=self.landscape,
                                       bg=NEON_PINK, fg="#000000", width=14, font=self.button_font,
                                       highlightthickness=2, highlightbackground="#ff33ff")
        self.btn_landscape.grid(row=0, column=2, padx=6, pady=4)

        self.btn_close = tk.Button(btn_frame, text="🛑 Cerrar TikTok", command=self.close_tiktok,
                                   bg=NEON_RED, fg="#FFFFFF", width=14, font=self.button_font,
                                   highlightthickness=2, highlightbackground="#ff3333")
        self.btn_close.grid(row=0, column=3, padx=6, pady=4)

        # === CONTROL MASIVO ===
        massive_frame = tk.Frame(self.root, bg=BG_DARK)
        massive_frame.pack(pady=10)

        self.btn_mass_like = tk.Button(massive_frame, text="❤️ Like Masivo (Todos)", command=self.mass_like,
                                       bg=NEON_PURPLE, fg="#FFFFFF", width=18, font=self.button_font,
                                       highlightthickness=2, highlightbackground="#e633ff")
        self.btn_mass_like.grid(row=0, column=0, padx=10, pady=4)

        self.btn_mass_comment = tk.Button(massive_frame, text="💬 Comentar Todos", command=self.mass_comment,
                                          bg=NEON_BLUE, fg="#000000", width=18, font=self.button_font,
                                          highlightthickness=2, highlightbackground="#66e0ff")
        self.btn_mass_comment.grid(row=0, column=1, padx=10, pady=4)

        # === VISUALIZACIÓN ===
        vis_frame = tk.Frame(self.root, bg=BG_DARK)
        vis_frame.pack(pady=10)

        self.btn_show = tk.Button(vis_frame, text="▶️ Mostrar Pantallas", command=self.open_scrcpy_windows,
                                  bg=NEON_BLUE, fg="#000000", width=18, font=self.button_font,
                                  highlightthickness=2, highlightbackground="#66e0ff")
        self.btn_show.grid(row=0, column=0, padx=6, pady=4)

        self.btn_hide = tk.Button(vis_frame, text="⏹️ Cerrar Pantallas", command=self.close_scrcpy_windows,
                                  bg=NEON_ORANGE, fg="#FFFFFF", width=18, font=self.button_font,
                                  highlightthickness=2, highlightbackground="#ff8a33")
        self.btn_hide.grid(row=0, column=1, padx=6, pady=4)

        self.btn_likes = tk.Button(vis_frame, text="❤️ Iniciar Interacción", command=self.start_interaction,
                                   bg=NEON_PURPLE, fg="#FFFFFF", width=18, font=self.button_font,
                                   highlightthickness=2, highlightbackground="#e633ff")
        self.btn_likes.grid(row=0, column=2, padx=6, pady=4)

        self.btn_comments = tk.Button(vis_frame, text="💬 Iniciar Comentarios", command=self.toggle_comments,
                                      bg=NEON_BLUE, fg="#000000", width=18, font=self.button_font,
                                      highlightthickness=2, highlightbackground="#66e0ff")
        self.btn_comments.grid(row=0, column=3, padx=6, pady=4)

        tk.Button(vis_frame, text="🛑 Cerrar Todas las Apps", command=self.close_all_apps,
                  bg="#FF3300", fg="#FFFFFF", width=18, font=self.button_font,
                  highlightthickness=2, highlightbackground="#ff5533").grid(row=0, column=4, padx=6, pady=4)

        tk.Button(vis_frame, text="🔍 Ver Apps Instaladas", command=self.show_installed_apps,
                  bg="#00CCCC", fg="#FFFFFF", width=18, font=self.button_font,
                  highlightthickness=2, highlightbackground="#33e6e6").grid(row=0, column=5, padx=6, pady=4)

        # === CONTROL MAESTRO AUTOMÁTICO ===
        self.btn_auto = tk.Button(vis_frame, text="🤖 Control Maestro (Auto)", command=self.toggle_auto_replicate,
                                  bg=NEON_GREEN, fg="#000000", width=18, font=self.button_font,
                                  highlightthickness=2, highlightbackground="#33ff33")
        self.btn_auto.grid(row=0, column=6, padx=6, pady=4)

        # === CAPTURAR PLANTILLAS ===
        self.btn_capture = tk.Button(vis_frame, text="📸 Capturar Plantilla", command=self.capture_template_gui,
                                     bg=NEON_YELLOW, fg="#000000", width=18, font=self.button_font,
                                     highlightthickness=2, highlightbackground="#ffff33")
        self.btn_capture.grid(row=0, column=7, padx=6, pady=4)

        # === TEST ===
        test_frame = tk.Frame(self.root, bg=BG_DARK)
        test_frame.pack(pady=10)

        tk.Button(test_frame, text="📄 Ver Log", command=self.ver_log,
                  bg=NEON_YELLOW, fg="#000000", width=18, font=self.button_font,
                  highlightthickness=2, highlightbackground="#ffff33").grid(row=0, column=0, padx=6, pady=4)

        tk.Button(test_frame, text="🧹 Limpiar Log", command=self.limpiar_log,
                  bg=NEON_LIME, fg="#000000", width=18, font=self.button_font,
                  highlightthickness=2, highlightbackground="#ccff33").grid(row=0, column=1, padx=6, pady=4)

        tk.Button(test_frame, text="🧪 Probar ADB", command=self.probar_adb,
                  bg="#00FF99", fg="#000000", width=18, font=self.button_font,
                  highlightthickness=2, highlightbackground="#33ffaa").grid(row=0, column=2, padx=6, pady=4)

        tk.Button(test_frame, text="✅ Test: Like", command=self.test_like,
                  bg="#FF66CC", fg="#000000", width=18, font=self.button_font,
                  highlightthickness=2, highlightbackground="#ff99dd").grid(row=0, column=3, padx=6, pady=4)

        # === LISTAS ===
        tk.Label(self.root, text="🔌 Dispositivos conectados:", font=("Arial", 11, "bold"),
                 bg=BG_DARK, fg=NEON_CYAN).pack(anchor="w", padx=20, pady=(10, 5))
        self.listbox = tk.Listbox(self.root, height=8, font=self.console_font, bg="#1E1E1E", fg="#0f0", bd=0, highlightthickness=0)
        self.listbox.pack(fill="x", padx=20)

        tk.Label(self.root, text="📊 Actividad en curso:", font=("Arial", 10, "bold"),
                 bg=BG_DARK, fg=NEON_GREEN).pack(anchor="w", padx=20, pady=(10, 5))
        self.status = tk.Text(self.root, height=6, bg="#1E1E1E", fg="#0f0", font=self.console_font, bd=0)
        self.status.pack(fill="x", padx=20)

        tk.Label(self.root, text="📋 Consola de actividad:", font=("Arial", 10, "bold"),
                 bg=BG_DARK, fg=NEON_YELLOW).pack(anchor="w", padx=20, pady=(10, 5))
        self.logs = scrolledtext.ScrolledText(self.root, height=14, bg="#111", fg="#0f0",
                                              insertbackground="white", font=self.console_font, bd=0)
        self.logs.pack(fill="both", expand=True, padx=20, pady=5)

    def start_pulse_animation(self):
        """Animación de pulso neón en botones clave"""
        def pulse():
            color = random.choice([NEON_GREEN, "#00CC00", "#009900", NEON_PURPLE])
            buttons = [self.btn_mass_like, self.btn_likes]
            for btn in buttons:
                try:
                    btn.config(bg=color)
                except:
                    pass
            self.root.after(800, lambda: [btn.config(bg=NEON_PURPLE) for btn in buttons])
            self.root.after(1600, pulse)
        pulse()

    def log(self, msg):
        self.logs.config(state="normal")
        self.logs.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.logs.see("end")
        self.logs.config(state="disabled")

        log_file = os.path.join(OUTPUT_DIR, "actividad.log")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        except Exception as e:
            print(f"Error al guardar log: {e}")

    def run_adb(self, cmd):
        try:
            result = subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout if result.returncode == 0 else None
        except Exception as e:
            self.log(f"⚠️ ADB Error: {str(e)}")
            return None

    def run_scrcpy(self, cmd):
        try:
            subprocess.Popen(["cmd", "/c"] + cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            self.log(f"⚠️ scrcpy Error: {str(e)}")

    def refresh(self):
        result = self.run_adb("devices")
        if not result: return
        lines = [l.strip() for l in result.splitlines()[1:] if "device" in l]
        self.devices = [l.split()[0] for l in lines]
        self.listbox.delete(0, "end")
        for d in self.devices:
            self.listbox.insert("end", d)
            self.ensure_screen_on(d)
        self.log(f"✅ {len(self.devices)} dispositivos detectados")

    def ensure_screen_on(self, serial):
        result = self.run_adb(f"-s {serial} shell dumpsys power | grep 'mScreenOn='")
        if result and "false" in result:
            self.run_adb(f"-s {serial} shell input keyevent KEYCODE_WAKEUP")
            self.run_adb(f"-s {serial} shell input swipe 500 1000 500 200")
            self.log(f"💡 {serial} → Pantalla encendida")

    def open_tiktok(self):
        for d in self.devices:
            threading.Thread(target=self._open, args=(d,), daemon=True).start()

    def _open(self, serial):
        self.run_adb(f"-s {serial} shell monkey -p {TIKTOK_PKG} -c android.intent.category.LAUNCHER 1")
        self.log(f"📱 {serial} → TikTok abierto")
        time.sleep(2)

    def landscape(self):
        for d in self.devices:
            threading.Thread(target=self._rotate, args=(d,), daemon=True).start()

    def _rotate(self, serial):
        self.run_adb(f"-s {serial} shell settings put system user_rotation 1")
        self.run_adb(f"-s {serial} shell settings put system accelerometer_rotation 0")
        self.log(f"🔁 {serial} → Horizontal activado")

    def close_tiktok(self):
        for d in self.devices:
            threading.Thread(target=self._close, args=(d,), daemon=True).start()

    def _close(self, serial):
        self.run_adb(f"-s {serial} shell am force-stop {TIKTOK_PKG}")
        self.log(f"🛑 {serial} → TikTok cerrado")

    def close_all_apps(self):
        if not self.devices:
            self.log("⚠️ No hay dispositivos conectados.")
            return

        self.log("🛑 Cerrando TODAS las apps (método fuerte)...")
        for serial in self.devices:
            threading.Thread(target=self._force_close_all_apps, args=(serial,), daemon=True).start()

    def _force_close_all_apps(self, serial):
        try:
            self.run_adb(f"-s {serial} shell input keyevent KEYCODE_APP_SWITCH")
            time.sleep(2.5)
            self.run_adb(f"-s {serial} shell input swipe 900 500 100 500")
            self.log(f"🧹 {serial} → Apps cerradas (multitarea)")
            time.sleep(3)

            apps_to_kill = [
                "com.zhiliaoapp.musically",
                "com.google.android.youtube",
                "com.instagram.android",
                "com.whatsapp",
                "com.facebook.katana",
                "com.accurast.attested.executor.sbs.canary"
            ]
            for pkg in apps_to_kill:
                self.run_adb(f"-s {serial} shell am force-stop {pkg}")
            self.log(f"✅ {serial} → Apps comunes cerradas")
        except Exception as e:
            self.log(f"❌ {serial} → Error: {str(e)}")

    def open_scrcpy_windows(self):
        if not self.devices:
            self.log("❌ No hay dispositivos para mostrar.")
            return

        self.log("🖥️ Abriendo ventanas de scrcpy...")
        pos_x = 0
        pos_y = 40
        col = 0

        for serial in self.devices:
            title = f"scrcpy-{serial}"
            cmd = [
                SCRCPY,
                "--serial", serial,
                "--window-title", title,
                "--window-width", str(WINDOW_WIDTH),
                "--window-height", str(WINDOW_HEIGHT),
                "--window-x", str(pos_x),
                "--window-y", str(pos_y),
                "--window-borderless",
                "--always-on-top",
                "--no-control"
            ]
            self.run_scrcpy(cmd)
            self.log(f"▶️ {serial} → Ventana abierta")
            time.sleep(1.2)
            self.minimize_window(title)
            col += 1
            pos_x = WINDOW_WIDTH * col + MARGIN * col
            if col >= MAX_COLS:
                col = 0
                pos_x = 0
                pos_y += WINDOW_HEIGHT + MARGIN

        self.log("✅ Todas las ventanas han sido abiertas y minimizadas.")

    def minimize_window(self, title):
        try:
            ps_script = f'''
            $title = '{title}'
            $proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like "*$title*" }} | Select-Object -First 1
            if ($proc) {{
                $sig = '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);'
                $type = Add-Type -MemberDefinition $sig -Name 'WinApi' -Namespace 'Win32' -PassThru
                $type::ShowWindow($proc.MainWindowHandle, 6)
            }}
            '''
            subprocess.run(['powershell', '-Command', ps_script], shell=True, capture_output=True)
        except:
            pass

    def close_scrcpy_windows(self):
        self.log("⏹️ Cerrando scrcpy.exe...")
        try:
            subprocess.run("taskkill /f /im scrcpy.exe", shell=True)
            subprocess.run('taskkill /f /im cmd.exe /fi "WINDOWTITLE eq scrcpy*"', shell=True)
            self.log("✅ scrcpy cerrado.")
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")

    # === CONTROL MASIVO ===
    def mass_like(self):
        if not self.devices:
            self.log("⚠️ No hay dispositivos.")
            return
        self.log("❤️ Iniciando LIKE MASIVO...")
        for serial in self.devices:
            threading.Thread(target=self._single_like, args=(serial,), daemon=True).start()

    def _single_like(self, serial):
        self.run_adb(f"-s {serial} shell input tap 655 703")
        time.sleep(0.1)
        self.run_adb(f"-s {serial} shell input tap 659 783")
        self.log(f"❤️ {serial} → Like masivo aplicado")

    def mass_comment(self):
        if not self.devices:
            return
        self.log("💬 Iniciando comentarios masivos...")
        for serial in self.devices:
            threading.Thread(target=self._single_comment, args=(serial,), daemon=True).start()

    def _single_comment(self, serial):
        comment = random.choice(COMMENTS)
        self.run_adb(f"-s {serial} shell input tap 142 1250")
        time.sleep(2)
        self.run_adb(f"-s {serial} shell input tap 285 1275")
        time.sleep(1)
        self.run_adb(f"-s {serial} shell ime enable com.android.adbkeyboard/.AdbIME")
        self.run_adb(f"-s {serial} shell ime set com.android.adbkeyboard/.AdbIME")
        self.run_adb(f'-s {serial} shell am broadcast -a ADB_INPUT_TEXT --es msg "{comment}"')
        time.sleep(0.5)
        self.run_adb(f"-s {serial} shell input keyevent KEYCODE_ENTER")
        self.log(f"💬 {serial} → {comment}")

    # === INTERACCIÓN ===
    def start_interaction(self):
        if self.is_interaction_running():
            self.stop_interaction()
            self.btn_likes.config(text="❤️ Iniciar Interacción")
            return

        for d in self.devices:
            if d not in self.bots:
                self.bots[d] = {}
            if 'interaction' not in self.bots[d]:
                stop_event = threading.Event()
                thread = threading.Thread(target=self.interaction_loop, args=(d, stop_event), daemon=True)
                thread.start()
                self.bots[d]['interaction'] = (thread, stop_event)
                self.log(f"🟢 {d} → Interacción iniciada")
        self.update_status()
        self.btn_likes.config(text="🛑 Detener Interacción")
        self.log("✅ Bots de interacción iniciados.")

    def stop_interaction(self):
        stopped = 0
        for d, bot in self.bots.items():
            if 'interaction' in bot:
                thread, event = bot['interaction']
                event.set()
                del bot['interaction']
                stopped += 1
        self.update_status()
        self.log(f"✅ {stopped} bots detenidos.")

    def is_interaction_running(self):
        return any('interaction' in bot for bot in self.bots.values())

    def interaction_loop(self, serial, stop_event):
        while not stop_event.is_set():
            x, y = 655, 703
            self.run_adb(f"-s {serial} shell input tap {x} {y}")
            time.sleep(0.1)
            self.run_adb(f"-s {serial} shell input tap {x} {y}")
            self.log(f"❤️ {serial} → Like")

            wait = 3 + random.randint(0, 7)
            for _ in range(wait):
                if stop_event.is_set():
                    return
                time.sleep(1)

            self.run_adb(f"-s {serial} shell input touchscreen swipe 708 707 708 54")
            self.log(f"↕️ {serial} → Deslizado")

            for _ in range(50 + random.randint(0, 9)):
                if stop_event.is_set():
                    return
                time.sleep(1)

    def toggle_comments(self):
        if self.is_comments_running():
            self.stop_comments()
            self.btn_comments.config(text="💬 Iniciar Comentarios")
        else:
            self.start_comments()
            self.btn_comments.config(text="🛑 Detener Comentarios")

    def start_comments(self):
        for d in self.devices:
            if d not in self.bots:
                self.bots[d] = {}
            if 'comment' not in self.bots[d]:
                stop_event = threading.Event()
                thread = threading.Thread(target=self.comment_loop, args=(d, stop_event), daemon=True)
                thread.start()
                self.bots[d]['comment'] = (thread, stop_event)
                self.log(f"🟢 {d} → Comentarios iniciados")
        self.update_status()

    def comment_loop(self, serial, stop_event):
        while not stop_event.is_set():
            comment = random.choice(COMMENTS)
            self.run_adb(f"-s {serial} shell input tap 651 773")
            time.sleep(2)
            self.run_adb(f"-s {serial} shell input tap 285 1275")
            time.sleep(1)
            self.run_adb(f"-s {serial} shell ime enable com.android.adbkeyboard/.AdbIME")
            self.run_adb(f"-s {serial} shell ime set com.android.adbkeyboard/.AdbIME")
            self.run_adb(f'-s {serial} shell am broadcast -a ADB_INPUT_TEXT --es msg "{comment}"')
            time.sleep(0.5)
            self.run_adb(f"-s {serial} shell input keyevent KEYCODE_ENTER")
            self.log(f"💬 {serial} → {comment}")
            time.sleep(20 + random.randint(0, 5))

    def stop_comments(self):
        stopped = 0
        for d, bot in self.bots.items():
            if 'comment' in bot:
                thread, event = bot['comment']
                event.set()
                del bot['comment']
                stopped += 1
        self.update_status()
        self.log(f"✅ {stopped} bots detenidos.")

    def is_comments_running(self):
        return any('comment' in bot for bot in self.bots.values())

    def update_status(self):
        self.status.config(state="normal")
        self.status.delete(1.0, "end")
        active = 0
        for serial, bot in self.bots.items():
            if 'interaction' in bot:
                self.status.insert("end", f"🟢 {serial} → ❤️ Like + ↕️ Scroll\n")
                active += 1
            if 'comment' in bot:
                self.status.insert("end", f"🟢 {serial} → 💬 Comentarios\n")
                active += 1
        if active == 0:
            self.status.insert("end", "⚪ Ningún bot activo\n")
        self.status.config(state="disabled")

    def show_installed_apps(self):
        if not self.devices:
            messagebox.showwarning("Advertencia", "No hay dispositivos conectados.")
            return

        self.log("🔍 Obteniendo apps instaladas...")
        all_packages = {}
        threads = []
        completed = 0
        lock = threading.Lock()

        def get_packages(serial):
            nonlocal completed
            result = self.run_adb(f"-s {serial} shell pm list packages -3")
            with lock:
                if result:
                    pkgs = [line.replace("package:", "").strip() for line in result.strip().splitlines() if line.startswith("package:")]
                    all_packages[serial] = sorted(pkgs)
                    self.log(f"✅ {serial} → {len(pkgs)} apps obtenidas")
                completed += 1

        for serial in self.devices:
            t = threading.Thread(target=get_packages, args=(serial,), daemon=True)
            t.start()
            threads.append(t)

        def check_completion():
            nonlocal completed
            if completed < len(self.devices):
                self.root.after(200, check_completion)
            else:
                if not all_packages:
                    messagebox.showerror("Error", "No se pudieron obtener apps")
                    return
                self.log("✅ Todas las apps obtenidas")
                self.open_packages_window(all_packages)

        check_completion()

    def open_packages_window(self, all_packages):
        win = tk.Toplevel(self.root)
        win.title("📦 Apps Instaladas")
        win.geometry("800x600")
        win.transient(self.root)
        win.grab_set()
        win.configure(bg=BG_DARK)

        tk.Label(win, text="📦 Apps Instaladas por Dispositivo", font=("Arial", 12, "bold"),
                 bg=BG_DARK, fg=NEON_CYAN).pack(pady=5)

        device_frame = tk.Frame(win, bg=BG_DARK)
        device_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(device_frame, text="Dispositivo:", bg=BG_DARK, fg=FG_LIGHT).pack(side="left")
        selected_device = tk.StringVar()
        device_combo = ttk.Combobox(device_frame, textvariable=selected_device, state="readonly", width=30)
        device_combo['values'] = list(all_packages.keys())
        if device_combo['values']:
            device_combo.current(0)
        device_combo.pack(side="left", padx=5)

        search_frame = tk.Frame(win, bg=BG_DARK)
        search_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(search_frame, text="Buscar:", bg=BG_DARK, fg=FG_LIGHT).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=5)

        list_frame = tk.Frame(win)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        listbox = tk.Listbox(list_frame, height=15, font=self.console_font, bg="#1E1E1E", fg="#0f0")
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame = tk.Frame(win, bg=BG_DARK)
        btn_frame.pack(pady=10)

        copy_btn = tk.Button(btn_frame, text="📋 Copiar Paquete", bg="#FF9800", fg="white", width=20, state="disabled", font=self.button_font)
        copy_btn.pack(side="left", padx=5)

        open_btn = tk.Button(btn_frame, text="▶️ Abrir App", bg="#2196F3", fg="white", width=15, state="disabled", font=self.button_font)
        open_btn.pack(side="left", padx=5)

        export_btn = tk.Button(btn_frame, text="📤 Exportar a CSV", bg="#4CAF50", fg="white", width=15, font=self.button_font)
        export_btn.pack(side="left", padx=5)

        close_btn = tk.Button(btn_frame, text="Cerrar", command=win.destroy, bg="#9E9E9E", fg="white", width=10, font=self.button_font)
        close_btn.pack(side="left", padx=5)

        packages = []
        def update_list():
            listbox.delete(0, "end")
            serial = selected_device.get()
            if serial in all_packages:
                search = search_var.get().lower()
                packages.clear()
                for pkg in all_packages[serial]:
                    if search in pkg.lower():
                        listbox.insert("end", pkg)
                        packages.append(pkg)

        device_combo.bind("<<ComboboxSelected>>", lambda e: update_list())
        search_var.trace_add("write", lambda *args: update_list())
        update_list()

        def on_select(event):
            try:
                selected = listbox.get(listbox.curselection())
                copy_btn.config(state="normal")
                open_btn.config(state="normal")
            except:
                pass

        def copy_package():
            try:
                selected = listbox.get(listbox.curselection())
                self.root.clipboard_clear()
                self.root.clipboard_append(selected)
                self.log(f"📋 Copiado: {selected}")
                messagebox.showinfo("Copiado", f"✅ {selected}\nCopiado al portapapeles")
            except:
                pass

        def open_app():
            try:
                selected = listbox.get(listbox.curselection())
                serial = selected_device.get()
                self.run_adb(f"-s {serial} shell monkey -p {selected} -c android.intent.category.LAUNCHER 1")
                self.log(f"📱 {serial} → Abriendo: {selected}")
                messagebox.showinfo("Éxito", f"✅ {selected}\nAbierto en {serial}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir: {str(e)}")

        def export_csv():
            file_path = filedialog.asksaveasfilename(
                initialdir=OUTPUT_DIR,
                initialfile="apps_instaladas.csv",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if not file_path:
                return
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Dispositivo", "Package Name"])
                    for serial, pkgs in all_packages.items():
                        for pkg in pkgs:
                            writer.writerow([serial, pkg])
                self.log(f"✅ Exportado a: {file_path}")
                messagebox.showinfo("Exportado", f"✅ Lista exportada a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

        copy_btn.config(command=copy_package)
        open_btn.config(command=open_app)
        export_btn.config(command=export_csv)
        listbox.bind("<<ListboxSelect>>", on_select)

    def ver_log(self):
        log_file = os.path.join(OUTPUT_DIR, "actividad.log")
        if not os.path.exists(log_file):
            messagebox.showinfo("Info", "Aún no hay registros.")
            return
        try:
            os.startfile(log_file)
        except:
            messagebox.showerror("Error", "No se pudo abrir el archivo.")

    def limpiar_log(self):
        log_file = os.path.join(OUTPUT_DIR, "actividad.log")
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"# Log limpiado el {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.log("🧹 Log limpiado")
            messagebox.showinfo("Éxito", "✅ Log limpiado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo limpiar: {str(e)}")

    def probar_adb(self):
        if not self.devices:
            messagebox.showwarning("Advertencia", "No hay dispositivos conectados.")
            return

        serial = self.devices[0]
        self.log(f"🧪 Probando ADB con {serial}...")
        result = self.run_adb(f"-s {serial} shell getprop ro.product.model")
        if result:
            model = result.strip()
            self.log(f"✅ {serial} → Modelo: {model}")
            messagebox.showinfo("Éxito", f"✅ Dispositivo detectado:\n{serial}\nModelo: {model}")
        else:
            self.log(f"❌ {serial} → Error de conexión ADB")
            messagebox.showerror("Error", f"❌ No se pudo conectar con {serial}")

    def test_like(self):
        if not self.devices:
            messagebox.showwarning("Advertencia", "No hay dispositivos conectados.")
            return

        self.log("✅ Iniciando prueba de like en todos los dispositivos...")
        for serial in self.devices:
            threading.Thread(target=self._test_like_single, args=(serial,), daemon=True).start()

    def _test_like_single(self, serial):
        self.log(f"✅ Test: Dando like en {serial}...")
        self.run_adb(f"-s {serial} shell am start -n com.zhiliaoapp.musically/.MainActivity")
        time.sleep(3)
        self.run_adb(f"-s {serial} shell input tap 672 670")
        time.sleep(0.1)
        self.run_adb(f"-s {serial} shell input tap 672 670")
        self.log(f"❤️ {serial} → Like de prueba (doble tap)")
        messagebox.showinfo("Test Like", f"✅ Like enviado en {serial}")

    def start_monitor(self):
        self.refresh()
        self.root.after(2000, self.start_monitor)

    # === CONTROL MAESTRO: Un dispositivo controla a todos ===
    def replicate_last_action(self):
        """Repite la última acción (like + scroll) en todos los dispositivos"""
        if not self.devices:
            self.log("⚠️ No hay dispositivos.")
            return

        self.log("🔁 Replicando última acción en todos los dispositivos...")
        for serial in self.devices:
            threading.Thread(target=self._replicate_single, args=(serial,), daemon=True).start()

    def _replicate_single(self, serial):
        # 1. Doble tap (like)
        self.run_adb(f"-s {serial} shell input tap 720 833")
        time.sleep(0.1)
        self.run_adb(f"-s {serial} shell input tap 720 833")
        # 2. Scroll
        self.run_adb(f"-s {serial} shell input touchscreen swipe 708 707 708 54")
        self.log(f"✅ {serial} → Acción replicada")

    # === CONTROL MAESTRO AUTOMÁTICO ===
    def toggle_auto_replicate(self):
        if self.monitoring:
            self.stop_auto_replicate()
        else:
            self.start_auto_replicate()

    def start_auto_replicate(self):
        if not self.devices:
            messagebox.showwarning("Advertencia", "No hay dispositivos.")
            return
        master = self.devices[0]
        self.log(f"🤖 Iniciando monitoreo automático en {master}")
        self.btn_auto.config(text="🛑 Detener Control Maestro", bg=NEON_RED)
        self.monitoring = True
        threading.Thread(target=self.monitor_master_device, args=(master,), daemon=True).start()

    def stop_auto_replicate(self):
        self.monitoring = False
        if self.master_process:
            self.master_process.terminate()
        self.btn_auto.config(text="🤖 Control Maestro (Auto)", bg=NEON_GREEN)
        self.log("🛑 Control maestro detenido")

    def monitor_master_device(self, master):
        template_like = cv2.imread(os.path.join(TEMPLATES_DIR, "template_like.png"), 0)
        template_comment = cv2.imread(os.path.join(TEMPLATES_DIR, "template_comment.png"), 0)
        if template_like is None or template_comment is None:
            self.log("❌ No se encontraron las plantillas. Usa '📸 Capturar Plantilla'")
            self.stop_auto_replicate()
            return

        cmd = [SCRCPY, "--serial", master, "--max-fps", "10", "--crop", "720:1280:0:0", "--no-control", "--no-window"]
        self.master_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        while self.monitoring:
            try:
                ret, frame = self.grab_frame(self.master_process.stdout)
                if not ret: continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detectar LIKE
                res = cv2.matchTemplate(gray, template_like, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > 0.8:
                    self.log("❤️ Like detectado → Replicando en todos...")
                    self.replicate_last_action()

                # Detectar COMENTARIO
                res = cv2.matchTemplate(gray, template_comment, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > 0.8:
                    self.log("💬 Comentario detectado → Replicando en todos...")
                    self.mass_comment()

                time.sleep(0.5)
            except Exception as e:
                self.log(f"❌ Error en monitoreo: {str(e)}")
                break
        self.master_process = None

    def grab_frame(self, pipe):
        data = b''
        while len(data) < 4:
            chunk = pipe.read(4 - len(data))
            if not chunk: return False, None
            data += chunk
        frame_size = int.from_bytes(data, 'little')
        data = b''
        while len(data) < frame_size:
            chunk = pipe.read(frame_size - len(data))
            if not chunk: return False, None
            data += chunk
        np_frame = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
        return True, frame

    # === CAPTURAR PLANTILLAS DESDE GUI ===
    def capture_template_gui(self):
        if not self.devices:
            messagebox.showwarning("Advertencia", "Conecta al menos un dispositivo.")
            return

        win = tk.Toplevel(self.root)
        win.title("📸 Capturar Plantilla")
        win.geometry("400x300")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="📸 Capturar Plantilla", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(win, text="Asegúrate de tener scrcpy abierto y el botón visible.").pack(pady=5)

        def capture(mode):
            win.destroy()
            self._capture_template(mode)

        tk.Button(win, text="❤️ Botón de Like", command=lambda: capture("like"),
                  bg=NEON_PURPLE, fg="white", width=20).pack(pady=5)
        tk.Button(win, text="💬 Botón de Comentario", command=lambda: capture("comment"),
                  bg=NEON_BLUE, fg="black", width=20).pack(pady=5)
        tk.Button(win, text="❌ Cancelar", command=win.destroy,
                  bg="#9E9E9E", fg="white", width=20).pack(pady=10)

    def _capture_template(self, button_type):
        try:
            import mss
            self.log(f"📸 Iniciando captura de plantilla: {button_type}")

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            roi = cv2.selectROI("Selecciona el botón", frame, fromCenter=False, showCrosshair=True)
            cv2.destroyWindow("Selecciona el botón")

            if roi[2] == 0 or roi[3] == 0:
                self.log("❌ Captura cancelada.")
                return

            x, y, w, h = roi
            cropped = frame[y:y+h, x:x+w]
            path = os.path.join(TEMPLATES_DIR, f"template_{button_type}.png")
            cv2.imwrite(path, cropped)
            self.log(f"✅ Plantilla guardada: {path}")
        except ImportError:
            self.log("❌ Instala 'mss' con: pip install mss pillow opencv-python")
        except Exception as e:
            self.log(f"❌ Error al capturar: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokControlPanel(root)
    root.mainloop()
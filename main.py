# main.py - Punto de entrada para Render
import os
import sys

# Añade la carpeta 'app' al path
sys.path.append('app')

# Importa y ejecuta tu panel
if __name__ == "__main__":
    try:
        from main_monitor import TikTokControlPanel
        import tkinter as tk
        # ⚠️ Render no tiene GUI, este código fallará
        root = tk.Tk()
        app = TikTokControlPanel(root)
        root.mainloop()
    except Exception as e:
        print(f"❌ Este script requiere una interfaz gráfica. No se puede ejecutar en Render: {e}")
        print("💡 Render no soporta aplicaciones de escritorio con Tkinter.")
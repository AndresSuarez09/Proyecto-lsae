# ui_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime, timedelta
from auth_siigo import obtener_token_siigo
from query_facturas import consultar_facturas_siigo
from main import resolver_clientes, generar_excel
from siigoScript.Detrack.main_detrack import main as flujo_detrack
import requests

# Paleta corporativa Lubrisol
COLOR_VERDE = "#006633"
COLOR_VERDE_HOVER = "#00994d"
COLOR_BLANCO = "#FFFFFF"
COLOR_GRIS_OSCURO = "#333333"

token = obtener_token_siigo()

# ----------------------------
# Funciones de acciones
# ----------------------------
def mostrar_facturas_en_log(facturas, fecha_texto=""):
    if not facturas:
        log_text.insert(tk.END, f"🚫 No se encontraron facturas {fecha_texto}\n", "error")
        return
    log_text.insert(tk.END, f"📦 Total encontradas {fecha_texto}: {len(facturas)}\n", "info")
    for f in facturas[:10]:
        numero = f.get("number")
        fecha = f.get("date")
        cliente = f.get("customer", {}).get("name", "N/A")
        fv_name = f.get("name") or (f"FV-{numero}" if numero else "FV-?")
        log_text.insert(tk.END, f"   • {fv_name} | Fecha: {fecha} | Cliente: {cliente}\n", "success")
    if len(facturas) > 10:
        log_text.insert(tk.END, f"   ... y {len(facturas)-10} más\n", "info")

def consultar_por_fecha():
    fecha = fecha_entry.get().strip()
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Formato inválido. Use YYYY-MM-DD.")
        return
    facturas = consultar_facturas_siigo(token, fecha)
    mostrar_facturas_en_log(facturas, f"del {fecha}")
    clientes = resolver_clientes(token, facturas)
    generar_excel(facturas, clientes)

def consultar_hoy():
    hoy_local = datetime.now()
    hoy_utc = hoy_local + timedelta(hours=5)  # Ajuste Colombia UTC-5
    fecha = hoy_utc.strftime("%Y-%m-%d")
    facturas = consultar_facturas_siigo(token, fecha)
    mostrar_facturas_en_log(facturas, f"de hoy ({fecha})")
    clientes = resolver_clientes(token, facturas)
    generar_excel(facturas, clientes)

def consultar_factura():
    fv = factura_entry.get().strip()
    if not fv:
        messagebox.showerror("Error", "Debe ingresar número de factura.")
        return
    url = "https://api.siigo.com/v1/invoices"
    headers = {"Authorization": token, "Content-Type": "application/json", "Partner-Id": "Lubrisol"}
    for campo in ["name", "number", "document_id"]:
        response = requests.get(url, headers=headers, params={campo: fv})
        data = response.json().get("results", [])
        if data:
            mostrar_facturas_en_log(data, f"puntual {fv}")
            clientes = resolver_clientes(token, data)
            generar_excel(data, clientes)
            return
    log_text.insert(tk.END, f"🚫 No se encontró la factura {fv}\n", "error")

def generar_excel_y_detrack():
    hoy_local = datetime.now()
    hoy_utc = hoy_local + timedelta(hours=5)
    fecha = hoy_utc.strftime("%Y-%m-%d")
    facturas = consultar_facturas_siigo(token, fecha)
    mostrar_facturas_en_log(facturas, f"de hoy ({fecha})")
    clientes = resolver_clientes(token, facturas)
    generar_excel(facturas, clientes)
    flujo_detrack()

def generar_excel_sin_detrack():
    hoy_local = datetime.now()
    hoy_utc = hoy_local + timedelta(hours=5)
    fecha = hoy_utc.strftime("%Y-%m-%d")
    facturas = consultar_facturas_siigo(token, fecha)
    mostrar_facturas_en_log(facturas, f"de hoy ({fecha})")
    clientes = resolver_clientes(token, facturas)
    generar_excel(facturas, clientes)

def subir_detrack():
    flujo_detrack()
    log_text.insert(tk.END, "✅ Órdenes enviadas desde último Excel\n", "success")

# ----------------------------
# Ventana principal
# ----------------------------
root = tk.Tk()
root.title("Integración Siigo → Detrack - Lubrisol")
root.geometry("900x600")
root.configure(bg=COLOR_BLANCO)

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Segoe UI", 11, "bold"),
                padding=10,
                relief="flat",
                borderwidth=0,
                background=COLOR_VERDE,
                foreground="white")
style.map("TButton",
          background=[("active", COLOR_VERDE_HOVER)],
          foreground=[("active", "white")])

# ----------------------------
# Header corporativo
# ----------------------------
header = tk.Frame(root, bg=COLOR_VERDE, height=80)
header.pack(fill="x")

try:
    logo_img = Image.open("logo_lubrisol.png").resize((150, 70))
    logo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(header, image=logo, bg=COLOR_VERDE)
    logo_label.image = logo
    logo_label.pack(side="left", padx=20, pady=5)
except Exception:
    logo_label = tk.Label(header, text="Lubrisol de Colombia", fg=COLOR_BLANCO, bg=COLOR_VERDE, font=("Segoe UI", 18, "bold"))
    logo_label.pack(side="left", padx=20, pady=5)

title_label = tk.Label(header,
                       text="Integración Siigo → Detrack",
                       fg=COLOR_BLANCO, bg=COLOR_VERDE,
                       font=("Segoe UI", 20, "bold"))
title_label.pack(side="left", padx=20)

# ----------------------------
# Notebook (pestañas)
# ----------------------------
container = tk.Frame(root, bg=COLOR_BLANCO)
container.pack(expand=True, fill="both", padx=12, pady=12)

notebook = ttk.Notebook(container)
notebook.pack(expand=True, fill="both")

# Pestaña Siigo con fondo corporativo
frame_siigo = tk.Frame(notebook, bg=COLOR_BLANCO, width=860, height=300)
frame_siigo.pack_propagate(False)
notebook.add(frame_siigo, text="Consultas Siigo")

try:
    bg_img_siigo = Image.open("lubrisol_background.png").resize((860, 300))
    bg_photo_siigo = ImageTk.PhotoImage(bg_img_siigo)
    bg_label_siigo = tk.Label(frame_siigo, image=bg_photo_siigo)
    bg_label_siigo.image = bg_photo_siigo
    bg_label_siigo.place(x=0, y=0, relwidth=1, relheight=1)
except Exception:
    pass

ttk.Label(frame_siigo, text="Fecha (YYYY-MM-DD):").pack(pady=(12, 4))
fecha_entry = ttk.Entry(frame_siigo)
fecha_entry.pack(pady=4)
ttk.Button(frame_siigo, text="Consultar por fecha", command=consultar_por_fecha).pack(pady=6)
ttk.Button(frame_siigo, text="Consultar facturas de hoy", command=consultar_hoy).pack(pady=6)

ttk.Label(frame_siigo, text="Número de factura (FV):").pack(pady=(12, 4))
factura_entry = ttk.Entry(frame_siigo)
factura_entry.pack(pady=4)
ttk.Button(frame_siigo, text="Consultar factura puntual", command=consultar_factura).pack(pady=6)

# Pestaña Detrack con fondo corporativo
frame_detrack = tk.Frame(notebook, bg=COLOR_BLANCO, width=860, height=300)
frame_detrack.pack_propagate(False)
notebook.add(frame_detrack, text="Acciones Detrack")

try:
    bg_img_detrack = Image.open("lubrisol_background.png").resize((860, 300))
    bg_photo_detrack = ImageTk.PhotoImage(bg_img_detrack)
    bg_label_detrack = tk.Label(frame_detrack, image=bg_photo_detrack)
    bg_label_detrack.image = bg_photo_detrack
    bg_label_detrack.place(x=0, y=0, relwidth=1, relheight=1)
except Exception:
    pass

ttk.Button(frame_detrack, text="Generar Excel sin subir", command=generar_excel_sin_detrack).pack(pady=8)
ttk.Button(frame_detrack, text="Generar Excel y subir", command=generar_excel_y_detrack).pack(pady=8)
ttk.Button(frame_detrack, text="Subir último Excel a Detrack", command=subir_detrack).pack(pady=8)

# ----------------------------
# Área de log con título restaurado
# ----------------------------
ttk.Label(root, text="Registro de acciones", font=("Segoe UI", 12, "bold")).pack(padx=12, anchor="w")

log_frame = tk.Frame(root, bg=COLOR_BLANCO)
log_frame.pack(fill="x", padx=12, pady=(0, 12))

log_text = tk.Text(log_frame, height=12, bg="#ffffff", fg=COLOR_GRIS_OSCURO,
                   font=("Consolas", 10), relief="flat")
log_text.pack(fill="x", padx=12, pady=12)

# Tags de color para mensajes
log_text.tag_config("info", foreground="blue")
log_text.tag_config("success", foreground="green")
log_text.tag_config("error", foreground="red")

# ----------------------------
# Footer con botón de salida
# ----------------------------
footer = tk.Frame(root, bg=COLOR_BLANCO)
footer.pack(fill="x", padx=12, pady=(0, 12))
salir_btn = ttk.Button(footer, text="Salir", command=root.quit)
salir_btn.pack(side="right")

# ----------------------------
# Lanzar la aplicación
# ----------------------------
root.mainloop()

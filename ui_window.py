# ui_window.py
import config
import webview
import os  # manejo de rutas
import requests  # llamadas HTTP a APIs
import webbrowser  # abrir enlaces en navegador
import tkinter as tk
from tkinter import ttk
from tkinterweb import HtmlFrame  # navegador embebido
from datetime import datetime, timedelta  # fechas y tiempos
import tkinter as tk  # base de la interfaz
from tkinter import simpledialog, ttk, messagebox  # diálogos y widgets
import pandas as pd  # manejo de datos y Excel
from PIL import Image, ImageTk  # imágenes en la interfaz
from auth_siigo import obtener_token_siigo  # token Siigo
from query_facturas import consultar_facturas_siigo  # consulta facturas
from main import resolver_clientes  # resolver clientes
from excel_generator import generar_excel  # generar Excel
from siigoScript.Detrack.excel_detrack import generar_excel_detrack # generar Excel Detrack
from siigoScript.Detrack.main_detrack import main as flujo_detrack  # flujo principal Detrack
from siigoScript.Detrack import payload_builder_form, uploader_detrack  # construcción y subida de payloads
from siigoScript.Detrack import consultas_detrack, consulta_puntual_detrack  # consultas a Detrack

# Paleta corporativa Lubrisol
COLOR_VERDE = "#006633"
COLOR_VERDE_HOVER = "#00994d"
COLOR_BLANCO = "#FFFFFF"
COLOR_GRIS_OSCURO = "#333333"

token = obtener_token_siigo()

# ----------------------------
# Funciones de acciones Siigo
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
    generar_excel(facturas, token, clientes)

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
# ----------------------------
# Funciones de acciones Detrack
# ----------------------------

def generar_excel_y_detrack():
    hoy_local = datetime.now()
    hoy_utc = hoy_local + timedelta(hours=5)
    fecha = hoy_utc.strftime("%Y-%m-%d")

    # Consultar facturas en Siigo
    facturas = consultar_facturas_siigo(token, fecha)
    if not facturas:
        messagebox.showinfo("Sin facturas", f"No se encontraron facturas en Siigo para {fecha}")
        return

    mostrar_facturas_en_log(facturas, f"de hoy ({fecha})")

    # Resolver clientes
    clientes = resolver_clientes(token, facturas)

    # ✅ Generar Excel con estética rojo/negro (Siigo → Detrack)
    ruta_excel = generar_excel(facturas, token, clientes)
    if ruta_excel:
        log_text.insert(tk.END, f"✅ Excel generado: {ruta_excel}\n", "success")

    # ✅ Subir a Detrack
    flujo_detrack()
    log_text.insert(tk.END, "✅ Órdenes enviadas a Detrack\n", "success")


def generar_excel_sin_detrack():
    hoy_local = datetime.now()
    hoy_utc = hoy_local + timedelta(hours=5)
    fecha = hoy_utc.strftime("%Y-%m-%d")

    # Consultar facturas en Siigo
    facturas = consultar_facturas_siigo(token, fecha)
    if not facturas:
        messagebox.showinfo("Sin facturas", f"No se encontraron facturas en Siigo para {fecha}")
        return

    mostrar_facturas_en_log(facturas, f"de hoy ({fecha})")

    # Resolver clientes
    clientes = resolver_clientes(token, facturas)

    # ✅ Generar Excel con estética rojo/negro (Siigo → Detrack)
    ruta_excel = generar_excel(facturas, token, clientes)
    if ruta_excel:
        log_text.insert(tk.END, f"✅ Excel generado (sin subir): {ruta_excel}\n", "success")

    # ❌ No se sube a Detrack aquí, solo se genera el archivo


def subir_detrack():
    # ✅ Usa el último Excel generado y lo sube a Detrack
    flujo_detrack()
    log_text.insert(tk.END, "✅ Órdenes enviadas desde último Excel\n", "success")
# ----------------------------
# Formulario para crear Job en Detrack
# ----------------------------
def abrir_formulario_job():
    form = tk.Toplevel()
    form.title("Crear nuevo Job en Detrack")

    # POD DETAILS
    tk.Label(form, text="POD Details", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(10,5))
    tk.Label(form, text="Tracking Status:").grid(row=1, column=0, sticky="w")
    tk.Button(form, text="Out for Delivery").grid(row=1, column=1, sticky="w")

    tk.Label(form, text="Job Status:").grid(row=2, column=0, sticky="w")
    combo_job_status = ttk.Combobox(form, values=["Info received", "In progress", "On Hold", "Return"])
    combo_job_status.grid(row=2, column=1)

    # JOB DETAILS
    tk.Label(form, text="Job Details", font=("Segoe UI", 12, "bold")).grid(row=3, column=0, columnspan=2, pady=(10,5))
    tk.Label(form, text="Detrack No.:").grid(row=4, column=0, sticky="w")
    entry_detrack_no = tk.Entry(form)
    entry_detrack_no.grid(row=4, column=1)

    tk.Label(form, text="Detrack Job Type:").grid(row=5, column=0, sticky="w")
    tk.Label(form, text="Delivery").grid(row=5, column=1, sticky="w")

    tk.Label(form, text="Assign to:").grid(row=6, column=0, sticky="w")
    combo_assign = ttk.Combobox(form, values=["ANDRES", "JOHN G", "Principal"])
    combo_assign.grid(row=6, column=1)

    tk.Label(form, text="D.O. No.:").grid(row=7, column=0, sticky="w")
    entry_do_no = tk.Entry(form)
    entry_do_no.grid(row=7, column=1)

    tk.Label(form, text="Date:").grid(row=8, column=0, sticky="w")
    entry_date = tk.Entry(form)
    entry_date.grid(row=8, column=1)

    tk.Label(form, text="Address:").grid(row=9, column=0, sticky="w")
    entry_address = tk.Entry(form)
    entry_address.grid(row=9, column=1)
    tk.Label(form, text="Company name:").grid(row=10, column=0, sticky="w")
    entry_company = tk.Entry(form)
    entry_company.grid(row=10, column=1)

    tk.Label(form, text="Deliver to:").grid(row=11, column=0, sticky="w")
    entry_deliver_to = tk.Entry(form)
    entry_deliver_to.grid(row=11, column=1)

    tk.Label(form, text="Phone No.:").grid(row=12, column=0, sticky="w")
    entry_phone = tk.Entry(form)
    entry_phone.grid(row=12, column=1)

    tk.Label(form, text="Invoice No.:").grid(row=13, column=0, sticky="w")
    entry_invoice_no = tk.Entry(form)
    entry_invoice_no.grid(row=13, column=1)

    tk.Label(form, text="Invoice amount:").grid(row=14, column=0, sticky="w")
    entry_invoice_amount = tk.Entry(form)
    entry_invoice_amount.grid(row=14, column=1)

    tk.Label(form, text="Payment mode:").grid(row=15, column=0, sticky="w")
    combo_payment = ttk.Combobox(form, values=["Credit card", "Cash", "COD"])
    combo_payment.grid(row=15, column=1)

    tk.Label(form, text="Payment amount:").grid(row=16, column=0, sticky="w")
    entry_payment_amount = tk.Entry(form)
    entry_payment_amount.grid(row=16, column=1)

    tk.Label(form, text="Order No.:").grid(row=17, column=0, sticky="w")
    entry_order_no = tk.Entry(form)
    entry_order_no.grid(row=17, column=1)

    tk.Label(form, text="Instructions:").grid(row=18, column=0, sticky="w")
    entry_instructions = tk.Entry(form)
    entry_instructions.grid(row=18, column=1)

    tk.Label(form, text="Pieces:").grid(row=19, column=0, sticky="w")
    entry_pieces = tk.Entry(form)
    entry_pieces.grid(row=19, column=1)

    tk.Label(form, text="Job owner:").grid(row=20, column=0, sticky="w")
    entry_job_owner = tk.Entry(form)
    entry_job_owner.grid(row=20, column=1)

    tk.Label(form, text="Carrier:").grid(row=21, column=0, sticky="w")
    entry_carrier = tk.Entry(form)
    entry_carrier.grid(row=21, column=1)

    tk.Label(form, text="Identification No.:").grid(row=22, column=0, sticky="w")
    entry_id_no = tk.Entry(form)
    entry_id_no.grid(row=22, column=1)
    # ITEM DETAILS
    tk.Label(form, text="Item Details", font=("Segoe UI", 12, "bold")).grid(row=23, column=0, columnspan=2, pady=(10,5))
    tk.Label(form, text="SKU:").grid(row=24, column=0, sticky="w")
    entry_sku = tk.Entry(form)
    entry_sku.grid(row=24, column=1)

    tk.Label(form, text="Item Description:").grid(row=25, column=0, sticky="w")
    entry_item_desc = tk.Entry(form)
    entry_item_desc.grid(row=25, column=1)

    tk.Label(form, text="Quantity:").grid(row=26, column=0, sticky="w")
    entry_quantity = tk.Entry(form)
    entry_quantity.grid(row=26, column=1)

    tk.Label(form, text="Comments:").grid(row=27, column=0, sticky="w")
    entry_comments = tk.Entry(form)
    entry_comments.grid(row=27, column=1)

    tk.Label(form, text="Reject quantity:").grid(row=28, column=0, sticky="w")
    entry_reject_qty = tk.Entry(form)
    entry_reject_qty.grid(row=28, column=1)

    tk.Label(form, text="Item reject Reason:").grid(row=29, column=0, sticky="w")
    combo_reject_reason = ttk.Combobox(form, values=[
        "Pedido incorrecto", "Cantidad incorrecta", "Producto defectuoso",
        "Envase dañado", "Mal rotulado", "Producto no requerido"
    ])
    combo_reject_reason.grid(row=29, column=1)

    # Función para crear Job
    def crear_job():
        datos = {
            "job_status": combo_job_status.get(),
            "assign_to": combo_assign.get(),
            "do_number": entry_do_no.get(),
            "date": entry_date.get(),
            "address": entry_address.get(),
            "company_name": entry_company.get(),
            "deliver_to": entry_deliver_to.get(),
            "phone_number": entry_phone.get(),
            "invoice_number": entry_invoice_no.get(),
            "invoice_amount": entry_invoice_amount.get(),
            "payment_mode": combo_payment.get(),
            "payment_amount": entry_payment_amount.get(),
            "order_number": entry_order_no.get(),
            "instructions": entry_instructions.get(),
            "pieces": entry_pieces.get(),
            "job_owner": entry_job_owner.get(),
            "carrier": entry_carrier.get(),
            "identification_number": entry_id_no.get(),
            "sku": entry_sku.get(),
            "item_description": entry_item_desc.get(),
            "quantity": entry_quantity.get(),
            "comments": entry_comments.get(),
            "reject_quantity": entry_reject_qty.get(),
            "reject_reason": combo_reject_reason.get()
        }

        payload = payload_builder_form.build_payload(datos)
        try:
            resultado = uploader_detrack.upload_job(payload)
            if resultado:
                messagebox.showinfo("Éxito", "Job creado en Detrack")
            else:
                messagebox.showerror("Error", "No se pudo crear el Job en Detrack")
        except Exception as e:
            messagebox.showerror("Error", f"Excepción: {e}")

    # Botón final
    tk.Button(form, text="Crear Job", command=crear_job).grid(row=30, column=0, columnspan=2, pady=10)
# -------------------------------
# Consultar por fecha Detrack
# -------------------------------
def consultar_por_fecha_detrack():
    fecha = fecha_entry_detrack.get().strip()
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Formato inválido. Use YYYY-MM-DD.")
        return

    ordenes = consultas_detrack.consultar_por_fecha(fecha)
    if ordenes is None:
        messagebox.showerror("Error", "No se pudieron consultar órdenes en Detrack")
        return

    log_text.insert(tk.END, f"📦 Órdenes encontradas en Detrack {fecha}: {len(ordenes)}\n", "info")
    for job in ordenes[:10]:
        log_text.insert(
            tk.END,
            f"   • {job.get('do_number')} | Estado: {job.get('status')} | Cliente: {job.get('deliver_to_collect_from')}\n",
            "success"
        )
    if len(ordenes) > 10:
        log_text.insert(tk.END, f"   ... y {len(ordenes)-10} más\n", "info")

    # ✅ Generar Excel con las órdenes consultadas
    from siigoScript.Detrack.excel_detrack import generar_excel_detrack
    ruta_excel = generar_excel_detrack(ordenes)
    if ruta_excel:
        log_text.insert(tk.END, f"✅ Excel generado: {ruta_excel}\n", "success")
# Consultar por rango de fecha Detrack
def consultar_por_rango():
    fecha_inicio = simpledialog.askstring("Fecha inicio", "Ingrese fecha inicio (YYYY-MM-DD):")
    fecha_fin = simpledialog.askstring("Fecha fin", "Ingrese fecha fin (YYYY-MM-DD):")

    if not fecha_inicio or not fecha_fin:
        messagebox.showinfo("Rango inválido", "Debe ingresar ambas fechas")
        return

    url = f"https://app.detrack.com/api/v2/jobs?start_date={fecha_inicio}&end_date={fecha_fin}"
    headers = {"X-API-KEY": "7a09cb54a6c46023f37205e3e0adbbb9c8a985fa825cf42a"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        ordenes = response.json()

        data = ordenes.get("data", [])

        if not data:
            messagebox.showinfo("Sin resultados", "No hay órdenes en ese rango de fechas")
            return

        # ✅ Usar tu generador de Excel Detrack
        ruta_salida = generar_excel_detrack(data)

        messagebox.showinfo("Consulta realizada", f"✅ Excel generado: {ruta_salida}")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al consultar Detrack:\n{e}")

# -------------------------------
# Consultar puntual Detrack
# -------------------------------
def consultar_puntual_detrack():
    numero = entry_do_number_detrack.get().strip()
    if not numero:
        messagebox.showerror("Error", "Debe ingresar un DO Number")
        return

    orden = consulta_puntual_detrack.consultar_por_numero(numero)
    if orden:
        log_text.insert(
            tk.END,
            f"🔎 Orden encontrada: {orden.get('do_number')} | Estado: {orden.get('status')} | Cliente: {orden.get('deliver_to_collect_from')}\n",
            "success"
        )

        # ✅ Generar Excel con la orden puntual
        from siigoScript.Detrack.excel_detrack import generar_excel_detrack
        ruta_excel = generar_excel_detrack([orden])  # pasamos lista con un solo elemento
        if ruta_excel:
            log_text.insert(tk.END, f"✅ Excel generado: {ruta_excel}\n", "success")

    else:
        messagebox.showerror("Error", f"No se encontró la orden {numero} en Detrack")

#portal empleados lubrisol
def abrir_portal_empleados():
    webbrowser.open("https://lubrisolae.web.app")

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

# Campo para ingresar la fecha en Detrack + botón
ttk.Label(frame_detrack, text="Fecha (YYYY-MM-DD):").pack(pady=(12, 4))
fecha_entry_detrack = ttk.Entry(frame_detrack)
fecha_entry_detrack.pack(pady=4)
ttk.Button(frame_detrack, text="Consultar por fecha", command=consultar_por_fecha_detrack).pack(pady=8)

# Campo para ingresar el DO Number puntual en Detrack + botón
ttk.Label(frame_detrack, text="Número de DO (Detrack):").pack(pady=(12, 4))
entry_do_number_detrack = ttk.Entry(frame_detrack)
entry_do_number_detrack.pack(pady=4)
ttk.Button(frame_detrack, text="Consultar orden puntual", command=consultar_puntual_detrack).pack(pady=8)

# Botones generales de acciones Detrack
ttk.Button(frame_detrack, text="Generar Excel sin subir", command=generar_excel_sin_detrack).pack(pady=8)
ttk.Button(frame_detrack, text="Generar Excel y subir", command=generar_excel_y_detrack).pack(pady=8)
ttk.Button(frame_detrack, text="Subir último Excel a Detrack", command=subir_detrack).pack(pady=8)
ttk.Button(frame_detrack, text="Crear nueva Orden/Job", command=lambda: abrir_formulario_job()).pack(pady=8)
ttk.Button(frame_detrack, text="Consultar por rango de fechas", command=consultar_por_rango).pack(pady=8)

# -----------------------------------------------------------------------------
# Pestaña Portal Empleados (PyWebview con barra de navegación)
# -----------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import webview

frame_empleados = tk.Frame(notebook, bg=COLOR_BLANCO, width=860, height=600)
frame_empleados.pack_propagate(False)
notebook.add(frame_empleados, text="Portal Empleados")

# Variables de control
current_url = tk.StringVar(value="https://lubrisolae.web.app")
browser_window = None

# Funciones de navegación
def abrir_portal():
    global browser_window
    # Crear ventana PyWebview con el portal
    browser_window = webview.create_window("Portal Empleados - Lubrisol", current_url.get())
    webview.start()

def cargar_url():
    if browser_window:
        browser_window.load_url(current_url.get())

def ir_atras():
    if browser_window:
        browser_window.evaluate_js("history.back()")

def ir_adelante():
    if browser_window:
        browser_window.evaluate_js("history.forward()")

def recargar():
    if browser_window:
        browser_window.reload()

# Barra de navegación
nav_frame = tk.Frame(frame_empleados, bg=COLOR_BLANCO)
nav_frame.pack(fill="x", pady=5)

btn_atras = ttk.Button(nav_frame, text="⬅ Atrás", command=ir_atras)
btn_atras.pack(side="left", padx=5)

btn_adelante = ttk.Button(nav_frame, text="➡ Adelante", command=ir_adelante)
btn_adelante.pack(side="left", padx=5)

btn_recargar = ttk.Button(nav_frame, text="🔄 Recargar", command=recargar)
btn_recargar.pack(side="left", padx=5)

entry_url = ttk.Entry(nav_frame, textvariable=current_url, width=60)
entry_url.pack(side="left", padx=5)

btn_ir = ttk.Button(nav_frame, text="Ir", command=cargar_url)
btn_ir.pack(side="left", padx=5)

# Botón para abrir el portal
ttk.Button(frame_empleados, text="Abrir portal completo",
           command=abrir_portal).pack(pady=20)

 #----------------------------
 # Opcional: logo corporativo
 #----------------------------
try:
     logo_img_emp = Image.open("logo_lubrisol.png").resize((120, 60))
     logo_photo_emp = ImageTk.PhotoImage(logo_img_emp)
     tk.Label(frame_empleados, image=logo_photo_emp, bg=COLOR_BLANCO).pack(pady=10)
except Exception:
     ttk.Label(frame_empleados, text="Lubrisol de Colombia",
               font=("Segoe UI", 12, "bold")).pack(pady=10)

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

# main.py

import os
import time
import io
import re
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auth_siigo import obtener_token_siigo
import config
from excel_generator import generar_excel
from query_facturas import consultar_facturas_siigo, consultar_factura_por_numero, consultar_facturas_rango_siigo

# Imports Detrack
from siigoScript.Detrack.main_detrack import main as flujo_detrack
from siigoScript.Detrack.excel_detrack import generar_excel_detrack
from siigoScript.Detrack.consultas_detrack import consultar_por_fecha as consultar_detrack_fecha
from siigoScript.Detrack.consulta_puntual_detrack import consultar_por_numero as consultar_detrack_numero
from siigoScript.Detrack.payload_builder_form import build_payload as build_payload_form
from siigoScript.Detrack.uploader_detrack import upload_job

app = FastAPI(title="Integración Siigo → Detrack - Lubrisol")

os.makedirs("static", exist_ok=True)
os.makedirs("resultados", exist_ok=True)
os.makedirs("salida", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/resultados", StaticFiles(directory="resultados"), name="resultados")
app.mount("/salida", StaticFiles(directory="salida"), name="salida")

@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def login_page():
    with open("templates/login.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/logout")
def logout():
    return RedirectResponse(url="/login")

class LoginData(BaseModel):
    username: str
    password: str

def load_users():
    with open("data/users.json", "r") as f:
        return json.load(f)

@app.post("/login")
def login(data: LoginData):
    users = load_users()
    if data.username in users and users[data.username] == data.password:
        return {"status": "ok", "message": "Login exitoso"}
    return {"status": "error", "message": "Credenciales inválidas"}

def resolver_clientes(token, facturas):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }
    claves = set()
    for f in facturas:
        customer = f.get("customer", {}) if isinstance(f, dict) else {}
        cid = customer.get("id")
        nit = customer.get("identification")
        if cid: claves.add(("id", cid))
        elif nit: claves.add(("identification", nit))

    clientes_resueltos = {}
    for tipo, valor in claves:
        try:
            url = f"https://api.siigo.com/v1/customers/{valor}" if tipo == "id" else f"https://api.siigo.com/v1/customers?identification={valor}"
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                clientes_resueltos[valor] = "SIN NOMBRE"
                continue
            data = resp.json()
            if isinstance(data, dict) and "results" in data and data["results"]: cliente_data = data["results"][0]
            elif isinstance(data, list) and data: cliente_data = data[0]
            elif isinstance(data, dict): cliente_data = data
            else: cliente_data = {}
            nombre_raw = cliente_data.get("name")
            if isinstance(nombre_raw, list): nombre = " ".join(nombre_raw).replace("S.A.", "").strip()
            elif isinstance(nombre_raw, str): nombre = nombre_raw.replace("S.A.", "").strip()
            else: nombre = (cliente_data.get("commercial_name") or "SIN NOMBRE").strip()
            clientes_resueltos[valor] = nombre or "SIN NOMBRE"
        except Exception:
            clientes_resueltos[valor] = "SIN NOMBRE"
    return clientes_resueltos

def preparar_datos_tabla(facturas, clientes, limite=100):
    datos = []
    for fac in facturas[:limite]:
        numero = fac.get("name", fac.get("number", "N/A"))
        id_cliente = fac.get("customer", {}).get("id", "")
        nombre_cliente = clientes.get(id_cliente, fac.get("customer", {}).get("identification", "Consumidor"))
        valor = fac.get("total", 0)
        datos.append({"numero": str(numero), "cliente": str(nombre_cliente), "valor": f"${valor:,.2f}", "estado": "Procesada"})
    return datos

@app.get("/consultar_facturas_fecha")
def consultar_facturas_fecha(fecha: str = Query(...)):
    token = obtener_token_siigo()
    facturas = consultar_facturas_siigo(token, fecha)
    clientes = resolver_clientes(token, facturas)
    datos_tabla = preparar_datos_tabla(facturas, clientes)
    ruta_excel = generar_excel(facturas, token, clientes)
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "total": len(facturas), "datos_tabla": datos_tabla}

@app.get("/consultar_facturas_rango")
def consultar_facturas_rango(fecha_inicio: str = Query(...), fecha_fin: str = Query(...)):
    token = obtener_token_siigo()
    facturas = consultar_facturas_rango_siigo(token, fecha_inicio, fecha_fin)
    clientes = resolver_clientes(token, facturas)
    datos_tabla = preparar_datos_tabla(facturas, clientes)
    ruta_excel = generar_excel(facturas, token, clientes)
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "total": len(facturas), "datos_tabla": datos_tabla}

@app.get("/consultar_facturas_hoy")
def consultar_facturas_hoy():
    token = obtener_token_siigo()
    fecha = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d")
    facturas = consultar_facturas_siigo(token, fecha)
    clientes = resolver_clientes(token, facturas)
    datos_tabla = preparar_datos_tabla(facturas, clientes)
    ruta_excel = generar_excel(facturas, token, clientes)
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "total": len(facturas), "datos_tabla": datos_tabla}

@app.get("/consultar_factura_puntual")
def consultar_factura_puntual(numero: str):
    token = obtener_token_siigo()
    facturas = consultar_factura_por_numero(token, numero)
    clientes = resolver_clientes(token, facturas)
    datos_tabla = preparar_datos_tabla(facturas, clientes)
    ruta_excel = generar_excel(facturas, token, clientes)
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "total": len(facturas), "datos_tabla": datos_tabla}

def preparar_datos_tabla_detrack(ordenes, limite=100):
    datos = []
    if not ordenes: return datos
    for ord in ordenes[:limite]:
        if not isinstance(ord, dict): continue
        numero = ord.get("do_number", ord.get("DO Number", ord.get("Tracking No", "N/A")))
        cliente = ord.get("deliver_to_collect_from", ord.get("Deliver To / Collect From", ord.get("Customer", "N/A")))
        estado = ord.get("primary_job_status", ord.get("Status", "N/A"))
        datos.append({"numero": str(numero), "cliente": str(cliente), "estado": str(estado).capitalize()})
    return datos

@app.get("/generar_excel_y_detrack")
def generar_excel_y_detrack():
    token = obtener_token_siigo()
    fecha = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d")
    facturas = consultar_facturas_siigo(token, fecha)
    clientes = resolver_clientes(token, facturas)
    ruta_excel = generar_excel(facturas, token, clientes)
    flujo_detrack()
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "mensaje": "Órdenes enviadas a Detrack"}

@app.get("/generar_excel_sin_detrack")
def generar_excel_sin_detrack():
    token = obtener_token_siigo()
    fecha = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d")
    facturas = consultar_facturas_siigo(token, fecha)
    clientes = resolver_clientes(token, facturas)
    ruta_excel = generar_excel(facturas, token, clientes)
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "mensaje": "Excel generado sin subir"}

@app.get("/subir_detrack")
def subir_detrack():
    flujo_detrack()
    return {"status": "ok", "mensaje": "Órdenes enviadas desde último Excel"}

@app.get("/consultar_detrack_fecha")
def consultar_detrack_por_fecha(fecha: str):
    ordenes = consultar_detrack_fecha(fecha)
    ruta_excel = generar_excel_detrack(ordenes)
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "total": len(ordenes) if ordenes else 0, "datos_tabla": preparar_datos_tabla_detrack(ordenes)}

@app.get("/consultar_detrack_puntual")
def consultar_detrack_puntual(numero: str):
    orden = consultar_detrack_numero(numero)
    ruta_excel = generar_excel_detrack([orden]) if orden else None
    return {"status": "ok" if orden else "error", "archivo": f"/resultados/{ruta_excel}" if ruta_excel else None, "datos_tabla": preparar_datos_tabla_detrack([orden]), "total": 1 if orden else 0}

@app.post("/crear_job_detrack")
async def crear_job_detrack(request: Request):
    datos = await request.json()
    fecha = datos.get("date", "")
    if "/" in fecha:
        try: dia, mes, anio = fecha.split("/"); fecha = f"{anio}-{mes}-{dia}"
        except: pass

    items_formateados = [{"sku": i.get("sku", ""), "description": i.get("description", ""), "quantity": i.get("quantity", 1)} for i in datos.get("items", [])]

    job_data = {
        "type": "Collection", "primary_job_status": "dispatched", "open_to_marketplace": False,
        "assign_to": datos.get("assign_to", ""), "do_number": datos.get("do_number", ""), 
        "date": fecha, "start_date": fecha, "address": datos.get("address", ""), 
        "company_name": datos.get("company_name", ""), "deliver_to_collect_from": datos.get("deliver_to", ""), 
        "phone_number": datos.get("phone", ""), "invoice_number": datos.get("invoice_no", ""),
        "payment_mode": datos.get("payment_mode", ""), "order_number": datos.get("order_no", ""),
        "instructions": datos.get("instructions", ""), "job_owner": datos.get("job_owner", ""),
        "carrier": datos.get("carrier", ""), "identification_number": datos.get("identification_no", ""),
        "items": items_formateados
    }

    if datos.get("invoice_amount"): job_data["invoice_amount"] = float(datos.get("invoice_amount"))
    if datos.get("payment_amount"): job_data["payment_amount"] = float(datos.get("payment_amount"))
    if datos.get("pieces"): job_data["pieces"] = int(datos.get("pieces"))

    resultado = upload_job({"data": job_data})
    return {"status": "ok" if resultado else "error", "resultado": resultado}

# 🚀 ENDPOINT REIMPORTACIÓN DE EXCEL EDITADO
@app.post("/subir_excel_editado")
async def subir_excel_editado(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        if df.empty:
            return JSONResponse(status_code=400, content={"status": "error", "mensaje": "El archivo Excel está vacío."})
        
        col_be = None
        for col in ["BE", "DO Number", "D.O. No.", "FV"]:
            if col in df.columns:
                col_be = col
                break
        
        if not col_be:
            return JSONResponse(status_code=400, content={"status": "error", "mensaje": "No se encontró columna BE o DO Number en el Excel."})

        grupos = df.groupby(col_be)
        procesados = 0
        errores = 0

        for be_val, grupo in grupos:
            if pd.isna(be_val) or not str(be_val).strip(): continue

            primera = grupo.iloc[0]
            be_str = str(be_val).strip()

            if not be_str.startswith("BE"):
                solo_num = re.sub(r'\D', '', be_str)
                be_str = f"BE00{solo_num}" if solo_num else be_str

            fecha_val = primera.get("Fecha", "")
            if isinstance(fecha_val, datetime): fecha_str = fecha_val.strftime("%Y-%m-%d")
            else: fecha_str = str(fecha_val).split("T")[0] if fecha_val else ""

            address_val = str(primera.get("address", primera.get("Dirección", "")))
            company_val = str(primera.get("company_name", primera.get("Cliente", "")))
            deliver_val = str(primera.get("deliver_to_collect_from", company_val))
            phone_val = str(primera.get("Teléfono", primera.get("Phone", "")))

            items = []
            total_pieces = 0
            for _, fila in grupo.iterrows():
                cant = fila.get("Cantidad", 1)
                try: cant_int = int(cant) if not pd.isna(cant) else 1
                except: cant_int = 1

                sku_val = str(fila.get("Código producto", fila.get("SKU", "")))
                desc_val = str(fila.get("Productos", fila.get("Descripción", "Lubricante")))

                items.append({
                    "sku": "" if sku_val == "nan" else sku_val,
                    "description": "" if desc_val == "nan" else desc_val,
                    "quantity": cant_int
                })
                total_pieces += cant_int

            job_data = {
                "type": "Collection",
                "do_number": be_str,
                "date": fecha_str,
                "address": "" if address_val == "nan" else address_val,
                "company_name": "" if company_val == "nan" else company_val,
                "deliver_to_collect_from": "" if deliver_val == "nan" else deliver_val,
                "phone_number": "" if phone_val == "nan" else phone_val,
                "pieces": total_pieces,
                "items": items
            }

            if upload_job({"data": job_data}): procesados += 1
            else: errores += 1

        return {"status": "ok", "mensaje": f"Órdenes procesadas en Detrack: {procesados}. Errores: {errores}"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "mensaje": f"Error procesando el archivo: {str(e)}"})

@app.get("/portal_empleados", response_class=HTMLResponse)
def portal_empleados(): return """<iframe src="https://lubrisolae.web.app" style="width:100%; height:80vh; border:none;"></iframe>"""

@app.get("/listar_resultados")
def listar_resultados(): return {"archivos": os.listdir("resultados")}

@app.get("/listar_salida")
def listar_salida(): return {"archivos": os.listdir("salida")}
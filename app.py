from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import os

# Imports Siigo
from auth_siigo import obtener_token_siigo
from query_facturas import consultar_facturas_siigo, consultar_factura_por_numero, consultar_facturas_rango_siigo
from main import resolver_clientes
from excel_generator import generar_excel

# Imports Detrack
from siigoScript.Detrack.main_detrack import main as flujo_detrack
from siigoScript.Detrack.excel_detrack import generar_excel_detrack
from siigoScript.Detrack.consultas_detrack import consultar_por_fecha as consultar_detrack_fecha
from siigoScript.Detrack.consulta_puntual_detrack import consultar_por_numero as consultar_detrack_numero
from siigoScript.Detrack.payload_builder_form import build_payload as build_payload_form
from siigoScript.Detrack.uploader_detrack import upload_job

app = FastAPI(title="Integración Siigo → Detrack - Lubrisol")

# ----------------------------
# Servir frontend
# ----------------------------
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

# ----------------------------
# Login básico con JSON
# ----------------------------
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

# ----------------------------
# Endpoints Siigo
# ----------------------------
def preparar_datos_tabla(facturas, clientes, limite=100):
    datos = []
    for fac in facturas[:limite]:
        numero = fac.get("name", "N/A")
        id_cliente = fac.get("customer", {}).get("id", "")
        nombre_cliente = clientes.get(id_cliente, fac.get("customer", {}).get("identification", "Consumidor"))
        valor = fac.get("total", 0)
        datos.append({
            "numero": numero,
            "cliente": str(nombre_cliente),
            "valor": f"${valor:,.2f}",
            "estado": "Procesada"
        })
    return datos

@app.get("/consultar_facturas_fecha")
def consultar_facturas_fecha(fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD")):
    token = obtener_token_siigo()
    facturas = consultar_facturas_siigo(token, fecha)
    clientes = resolver_clientes(token, facturas)
    
    # 1. Datos primero
    datos_tabla = preparar_datos_tabla(facturas, clientes)
    # 2. Excel después
    ruta_excel = generar_excel(facturas, token, clientes)
    
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "total": len(facturas), "datos_tabla": datos_tabla}

@app.get("/consultar_facturas_rango")
def consultar_facturas_rango(
    fecha_inicio: str = Query(..., description="Fecha inicial YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="Fecha final YYYY-MM-DD")
):
    token = obtener_token_siigo()
    facturas = consultar_facturas_rango_siigo(token, fecha_inicio, fecha_fin)
    clientes = resolver_clientes(token, facturas)
    
    datos_tabla = preparar_datos_tabla(facturas, clientes)
    ruta_excel = generar_excel(facturas, token, clientes)
    
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "total": len(facturas), "datos_tabla": datos_tabla}

@app.get("/consultar_facturas_hoy")
def consultar_facturas_hoy():
    token = obtener_token_siigo()
    hoy_utc = datetime.now() + timedelta(hours=5)
    fecha = hoy_utc.strftime("%Y-%m-%d")
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

# ----------------------------
# Endpoints Detrack
# ----------------------------
@app.get("/generar_excel_y_detrack")
def generar_excel_y_detrack():
    token = obtener_token_siigo()
    hoy_utc = datetime.now() + timedelta(hours=5)
    fecha = hoy_utc.strftime("%Y-%m-%d")
    facturas = consultar_facturas_siigo(token, fecha)
    clientes = resolver_clientes(token, facturas)
    ruta_excel = generar_excel(facturas, token, clientes)
    flujo_detrack()
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "mensaje": "Órdenes enviadas a Detrack"}

@app.get("/generar_excel_sin_detrack")
def generar_excel_sin_detrack():
    token = obtener_token_siigo()
    hoy_utc = datetime.now() + timedelta(hours=5)
    fecha = hoy_utc.strftime("%Y-%m-%d")
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
    return {"status": "ok", "archivo": f"/resultados/{ruta_excel}", "total": len(ordenes)}

@app.get("/consultar_detrack_puntual")
def consultar_detrack_puntual(numero: str):
    orden = consultar_detrack_numero(numero)
    ruta_excel = generar_excel_detrack([orden]) if orden else None
    return {"status": "ok" if orden else "error", "archivo": f"/resultados/{ruta_excel}" if ruta_excel else None, "orden": orden}

@app.post("/crear_job_detrack")
async def crear_job_detrack(request: Request):
    datos = await request.json()
    fecha = datos.get("date")
    if "/" in fecha:
        dia, mes, anio = fecha.split("/")
        fecha = f"{anio}-{mes}-{dia}"

    items_texto = datos.get("items", "")
    items = [{"description": items_texto, "quantity": 1}] if items_texto else []

    payload = {
        "data": {
            "type": "Delivery", "primary_job_status": "dispatched", "open_to_marketplace": False,
            "do_number": datos.get("do_number"), "attempt": 1, "date": fecha, "start_date": fecha,
            "address": datos.get("address"), "deliver_to_collect_from": datos.get("customer"), "items": items
        }
    }
    resultado = upload_job(payload)
    return {"status": "ok" if resultado else "error", "resultado": resultado}

# ----------------------------
# Portal empleados & Archivos
# ----------------------------
@app.get("/portal_empleados", response_class=HTMLResponse)
def portal_empleados():
    return """<iframe src="https://lubrisolae.web.app" style="width:100%; height:80vh; border:none;"></iframe>"""

@app.get("/listar_resultados")
def listar_resultados(): return {"archivos": os.listdir("resultados")}

@app.get("/listar_salida")
def listar_salida(): return {"archivos": os.listdir("salida")}
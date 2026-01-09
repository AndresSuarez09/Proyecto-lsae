# excel_generator.py
import config
import os
import pandas as pd
import requests
import time
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill

clientes_cache = {}
consultas_realizadas = 0

# 🔧 Resolver cliente por identificación
def resolver_cliente_por_identificacion(identificacion, token, clientes_resueltos=None):
    global consultas_realizadas

    if not identificacion or not identificacion.strip() or identificacion == "222222222222":
        return f"ID: {identificacion}", None

    if clientes_resueltos and identificacion in clientes_resueltos:
        nombre = clientes_resueltos[identificacion]
        clientes_cache[identificacion] = (nombre, identificacion)
        return nombre, identificacion

    if identificacion in clientes_cache:
        return clientes_cache[identificacion]

    if consultas_realizadas >= 95:
        time.sleep(60)
        consultas_realizadas = 0

    url = f"https://api.siigo.com/v1/customers?identification={identificacion}"
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }

    try:
        response = requests.get(url, headers=headers)
        consultas_realizadas += 1
        data = response.json()

        if isinstance(data, dict) and "results" in data and isinstance(data["results"], list) and data["results"]:
            cliente = data["results"][0]
            nombre_raw = cliente.get("name")
            nombre = " ".join(nombre_raw) if isinstance(nombre_raw, list) else nombre_raw
            nit = cliente.get("identification", identificacion)
            if nombre:
                clientes_cache[identificacion] = (nombre, nit)
                return nombre, nit

        clientes_cache[identificacion] = (f"ID: {identificacion}", None)
        return f"ID: {identificacion}", None

    except Exception:
        clientes_cache[identificacion] = (f"ID: {identificacion}", None)
        return f"ID: {identificacion}", None

# 🔧 Obtener diccionario de vendedores
def obtener_diccionario_vendedores(token):
    url = "https://api.siigo.com/v1/users"
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        vendedores = {}
        for usuario in data.get("results", data):
            seller_id = usuario.get("id")
            nombre = f"{usuario.get('first_name', '')} {usuario.get('last_name', '')}".strip()
            vendedores[seller_id] = {
                "nombre": nombre,
                "email": usuario.get("email", ""),
                "identification": usuario.get("identification", "")
            }
        return vendedores
    except Exception:
        return {}

# ✅ Generar Excel con columnas FV y BE
def generar_excel(facturas, token, clientes_resueltos=None):
    if not facturas:
        print("⚠️ No hay facturas para generar el Excel.")
        return None

    vendedores_diccionario = obtener_diccionario_vendedores(token)

    os.makedirs(config.CARPETA_SALIDA, exist_ok=True)
    base_name = config.NOMBRE_ARCHIVO_EXCEL
    ruta_archivo = os.path.join(config.CARPETA_SALIDA, base_name)

    # 🔒 Lógica incremental: si existe, crear facturas_lubrisol(1).xlsx, (2), etc.
    if os.path.exists(ruta_archivo):
        nombre, ext = os.path.splitext(base_name)
        contador = 1
        while True:
            nuevo_nombre = f"{nombre}({contador}){ext}"
            ruta_archivo = os.path.join(config.CARPETA_SALIDA, nuevo_nombre)
            if not os.path.exists(ruta_archivo):
                break
            contador += 1

    print(f"📁 Generando archivo Excel en: {ruta_archivo}")

    registros = []
    for f in facturas:
        if isinstance(f, dict):
            productos = []
            codigos = []

            for item in f.get("items", []):
                if isinstance(item, dict):
                    nombre = item.get("description", "Sin nombre")
                    cantidad = item.get("quantity", 0)
                    precio = item.get("price", 0)
                    total = item.get("total", 0)
                    productos.append(f"{nombre} ({cantidad} x {precio:,}) = {total:,}")
                    codigos.append(str(item.get("code", "")))

            cliente_obj = f.get("customer", {})
            cliente_identificacion = cliente_obj.get("identification")
            cliente_nombre, cliente_identificacion = resolver_cliente_por_identificacion(
                cliente_identificacion, token, clientes_resueltos
            )

            vendedor_id = f.get("seller")
            vendedor_info = vendedores_diccionario.get(vendedor_id, {})
            vendedor_nombre = vendedor_info.get("nombre", f"ID: {vendedor_id}")
            email_vendedor = vendedor_info.get("email", "")
            id_vendedor = vendedor_info.get("identification", "")

            numero_fv = f.get("number")
            numero_be = numero_fv.replace("FV", "BE") if numero_fv else None

            registros.append({
                "Número FV": numero_fv,
                "Número BE": numero_be,
                "Fecha": f.get("date"),
                "Cliente": cliente_nombre,
                "Identificación": cliente_identificacion,
                "Vendedor": vendedor_nombre,
                "Total": f.get("total"),
                "Saldo": f.get("balance"),
                "Productos": "; ".join(productos),
                "Email vendedor": email_vendedor,
                "ID vendedor": id_vendedor,
                "Código producto": "; ".join(codigos)
            })

    columnas_ordenadas = [
        "Número FV", "Número BE", "Fecha", "Cliente", "Identificación", "Vendedor",
        "Total", "Saldo", "Productos", "Email vendedor", "ID vendedor", "Código producto"
    ]

    df = pd.DataFrame(registros)
    df = df[columnas_ordenadas]
    df.to_excel(ruta_archivo, index=False)

    wb = load_workbook(ruta_archivo)
    ws = wb.active

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")

    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    for row in ws.iter_rows(min_row=2, min_col=1, max_col=len(columnas_ordenadas)):
        for cell in row:
            if cell.column_letter in ["G", "H"]:  # Total y Saldo
                cell.number_format = '"$"#,##0.00'

    wb.save(ruta_archivo)
    print("✅ Archivo Excel generado con columnas FV y BE.")
    return ruta_archivo

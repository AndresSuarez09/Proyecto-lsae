# main.py

import os
import time
import requests
import pandas as pd
from auth_siigo import obtener_token_siigo
import config

def consultar_facturas(token):
    print("🔗 Conectando con Siigo API para listar facturas...")

    url = "https://api.siigo.com/v1/invoices"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }
    params = {
        "created_start": config.CREATED_START,
        "created_end": config.CREATED_END,
        "page_size": config.PAGE_SIZE,
        "page": 1
    }

    todas = []
    while True:
        print(f"📄 Consultando página {params['page']} ({config.CREATED_START} → {config.CREATED_END})...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Blindaje: la respuesta puede ser dict con "results" o una lista directa
        if isinstance(data, dict):
            items = data.get("results", [])
        elif isinstance(data, list):
            items = data
        else:
            items = []

        if not items:
            print("🚫 No se encontraron más facturas.")
            break

        todas.extend(items)
        print(f"✅ {len(items)} facturas agregadas. Acumulado: {len(todas)}")

        # Si la respuesta es menor al tamaño de página, ya no hay más
        if len(items) < params["page_size"]:
            print("📉 Última página detectada por tamaño de respuesta.")
            break

        params["page"] += 1
        time.sleep(0.2)  # Evitar throttling

    print(f"📦 Total acumulado: {len(todas)} facturas.")
    return todas

def resolver_clientes(token, facturas):
    print("🔍 Resolviendo nombres de clientes en Siigo...")

    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }

    # Construir conjunto de claves únicas (id o identificación)
    claves = set()
    for f in facturas:
        customer = f.get("customer", {}) if isinstance(f, dict) else {}
        cid = customer.get("id")
        nit = customer.get("identification")
        if cid:
            claves.add(("id", cid))
        elif nit:
            claves.add(("identification", nit))

    clientes_resueltos = {}
    for tipo, valor in claves:
        try:
            if tipo == "id":
                url = f"https://api.siigo.com/v1/customers/{valor}"
            else:
                url = f"https://api.siigo.com/v1/customers?identification={valor}"

            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                print(f"⚠️ Error {resp.status_code} consultando cliente {tipo}:{valor}: {resp.text}")
                clientes_resueltos[valor] = "SIN NOMBRE"
                continue

            data = resp.json()

            # Normalizar cliente_data según formato de respuesta
            if isinstance(data, dict) and "results" in data and data["results"]:
                cliente_data = data["results"][0]
            elif isinstance(data, list) and data:
                cliente_data = data[0]
            elif isinstance(data, dict):
                cliente_data = data
            else:
                cliente_data = {}

            # Extraer nombre con respaldo a commercial_name
            nombre_raw = cliente_data.get("name")
            if isinstance(nombre_raw, list):
                nombre = " ".join(nombre_raw).replace("S.A.", "").strip()
            elif isinstance(nombre_raw, str):
                nombre = nombre_raw.replace("S.A.", "").strip()
            else:
                nombre = (cliente_data.get("commercial_name") or "SIN NOMBRE").strip()

            clientes_resueltos[valor] = nombre or "SIN NOMBRE"
            print(f"✅ Cliente resuelto: {tipo}:{valor} → {clientes_resueltos[valor]}")

        except Exception as e:
            print(f"⚠️ Excepción al consultar cliente {tipo}:{valor}: {e}")
            clientes_resueltos[valor] = "SIN NOMBRE"

    print(f"📊 Total clientes resueltos: {len(clientes_resueltos)}")
    return clientes_resueltos

def generar_excel(facturas, clientes):
    os.makedirs(config.CARPETA_SALIDA, exist_ok=True)
    ruta_excel = os.path.join(config.CARPETA_SALIDA, config.NOMBRE_ARCHIVO_EXCEL)

    registros = []
    for factura in facturas:
        customer = factura.get("customer", {}) if isinstance(factura, dict) else {}
        clave_cliente = customer.get("id") or customer.get("identification")
        cliente_nombre = clientes.get(clave_cliente, "SIN NOMBRE")

        # Productos como lista segura
        items = factura.get("items", []) if isinstance(factura, dict) else []
        productos = ", ".join([i.get("description", "") for i in items if isinstance(i, dict)])

        registros.append({
            "FV": factura.get("number"),
            "BE": f"BE{factura.get('number')}",
            "Cliente": cliente_nombre,
            "Fecha": factura.get("date"),
            "Total": factura.get("total"),
            "Productos": productos
        })

    df = pd.DataFrame(registros)
    df.to_excel(ruta_excel, index=False)
    print(f"📁 Generado archivo Excel en: {ruta_excel}")

def main():
    print("🚀 Iniciando flujo de consulta y generación de Excel...")
    try:
        token = obtener_token_siigo()
        facturas = consultar_facturas(token)
        print(f"📦 Total de facturas recibidas: {len(facturas)}")

        clientes = resolver_clientes(token, facturas)
        generar_excel(facturas, clientes)

    except Exception as e:
        print(f"❌ Error inesperado durante el proceso: {str(e)}")

if __name__ == "__main__":
    main()

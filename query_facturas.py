# query_facturas.py
import config
import requests
import time

def consultar_facturas_siigo(token, fecha=None):
    """
    Consulta facturas en Siigo para un día específico usando fecha de creación completa (UTC).
    """
    print("🔗 Conectando con Siigo API para listar facturas...")
    url = "https://api.siigo.com/v1/invoices"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }

    todas_las_facturas = []
    pagina_actual = 1
    fecha_inicio = f"{fecha}T00:00:00Z"
    fecha_fin = f"{fecha}T23:59:59Z"

    while True:
        print(f"📄 Consultando página {pagina_actual} para {fecha}...")
        params = {
            "created_start": fecha_inicio,
            "created_end": fecha_fin,
            "page_size": config.PAGE_SIZE,
            "page": pagina_actual
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            raw = response.json()
            data = raw.get("results", [])

            if not data:
                print("🚫 No se encontraron más facturas.")
                break

            todas_las_facturas.extend(data)
            print(f"✅ Página {pagina_actual}: {len(data)} facturas agregadas.")

            pagination = raw.get("pagination", {})
            if pagina_actual >= pagination.get("total_pages", 1):
                break

            pagina_actual += 1
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la consulta: {e}")
            break

    print(f"📦 Total acumulado: {len(todas_las_facturas)} facturas.")
    return todas_las_facturas


def consultar_factura_por_numero(token, numero_factura: str):
    """
    Consulta una factura específica en Siigo con filtro estricto.
    """
    print(f"🔗 Consultando factura {numero_factura} en Siigo...")
    url = "https://api.siigo.com/v1/invoices"
    headers = {"Authorization": token, "Content-Type": "application/json", "Partner-Id": "Lubrisol"}
    
    for param_key in ["name", "document_number"]:
        params = {param_key: numero_factura}
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json().get("results", [])
                if data:
                    # 🛠️ FILTRO ESTRICTO: Solo nos quedamos con la factura que contiene el número exacto
                    facturas_exactas = [f for f in data if numero_factura in str(f.get("name", ""))]
                    if facturas_exactas:
                        print("✅ Factura encontrada de forma exacta.")
                        return facturas_exactas
        except Exception:
            continue

    print("🚫 No se encontró la factura.")
    return []


def consultar_facturas_rango_siigo(token, fecha_inicio_str, fecha_fin_str):
    """
    Consulta facturas en Siigo para un rango de fechas específico.
    """
    print(f"🔗 Conectando con Siigo API para listar facturas del {fecha_inicio_str} al {fecha_fin_str}...")
    url = "https://api.siigo.com/v1/invoices"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }

    todas_las_facturas = []
    pagina_actual = 1

    while True:
        print(f"📄 Consultando página {pagina_actual} (rango {fecha_inicio_str} a {fecha_fin_str})...")
        params = {
            "date_start": fecha_inicio_str,
            "date_end": fecha_fin_str,
            "page_size": config.PAGE_SIZE,
            "page": pagina_actual
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            raw = response.json()
            data = raw.get("results", [])

            if not data:
                print("🚫 No se encontraron más facturas en este rango.")
                break

            todas_las_facturas.extend(data)
            print(f"✅ Página {pagina_actual}: {len(data)} facturas agregadas.")

            if len(data) < config.PAGE_SIZE:
                print("📉 Última página alcanzada.")
                break

            pagina_actual += 1
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la consulta por rango: {e}")
            break

    print(f"📦 Total acumulado en rango: {len(todas_las_facturas)} facturas.")
    return todas_las_facturas
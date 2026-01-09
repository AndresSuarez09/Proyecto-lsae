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

    # Formato completo de fecha con hora UTC
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
    Consulta una factura específica en Siigo por su número (ej. FV-003-457).
    """
    print(f"🔗 Consultando factura {numero_factura} en Siigo...")

    url = "https://api.siigo.com/v1/invoices"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }
    params = {"name": numero_factura}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        raw = response.json()
        data = raw.get("results", [])

        if data:
            print("✅ Factura encontrada.")
            return data
        else:
            print("🚫 No se encontró la factura.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al consultar factura {numero_factura}: {e}")
        return []

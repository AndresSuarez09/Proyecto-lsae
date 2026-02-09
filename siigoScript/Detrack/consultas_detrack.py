# consultas_detrack.py
import requests
from siigoScript.Detrack.config_detrack import DETRACK_URL, HEADERS

def consultar_por_fecha(fecha):
    """
    Consulta órdenes en Detrack para una fecha específica (YYYY-MM-DD).
    Retorna lista de órdenes o None si hay error.
    """
    url = f"{DETRACK_URL}?date={fecha}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"🚫 Excepción al consultar: {e}")
        return None

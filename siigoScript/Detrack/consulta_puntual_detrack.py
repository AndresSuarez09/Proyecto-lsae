# consulta_puntual_detrack.py
import requests
from siigoScript.Detrack.config_detrack import DETRACK_URL, HEADERS

def consultar_por_numero(do_number):
    """
    Consulta una orden puntual en Detrack por su DO Number.
    Retorna la orden o None si no existe.
    """
    url = f"{DETRACK_URL}?do_number={do_number}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json().get("data", [])
            return data[0] if data else None
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"🚫 Excepción al consultar: {e}")
        return None

# consulta_puntual_detrack.py
import requests
from siigoScript.Detrack.config_detrack import DETRACK_URL, HEADERS

def consultar_por_numero(do_number):
    """
    Consulta una orden puntual en Detrack por su DO Number con filtro estricto.
    """
    # 🛠️ Si digitas solo números (ej "9152"), agregamos el prefijo "BE00" automáticamente
    if do_number.isdigit():
        do_number = f"BE00{do_number}"
        
    url = f"{DETRACK_URL}?do_number={do_number}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json().get("data", [])
            # 🛠️ FILTRO ESTRICTO: Buscar la orden exacta en la respuesta
            for job in data:
                if job.get("do_number") == do_number:
                    return job
        return None
    except Exception as e:
        print(f"🚫 Excepción al consultar en Detrack: {e}")
        return None
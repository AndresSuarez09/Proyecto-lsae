#uploader_detrack.py
import requests
import os
import pandas as pd
from datetime import datetime

# ✅ Import correcto desde el paquete siigoScript.Detrack
from siigoScript.Detrack.config_detrack import DETRACK_URL, HEADERS

TRAZABILIDAD_FILE = "salida/registro_cambios.xlsx"

def registrar_trazabilidad(payload, resultado):
    """
    Registra cada envío en un Excel de trazabilidad.
    """
    os.makedirs("salida", exist_ok=True)

    # Extraer datos relevantes
    do_number = payload["data"].get("do_number")
    cliente = payload["data"].get("address")
    fecha = payload["data"].get("date")
    estado = resultado.get("status") if resultado else "Error"
    detrack_number = resultado.get("detrack_number") if resultado else None
    tracking_link = resultado.get("tracking_link") if resultado else None
    observaciones = "✅ Orden creada" if resultado else "❌ Error en envío"

    nuevo_registro = {
        "Número BE": do_number,
        "Cliente": cliente,
        "Fecha": fecha,
        "Estado": estado,
        "Detrack #": detrack_number,
        "Tracking Link": tracking_link,
        "Observaciones": observaciones,
        "Registrado en": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Si el archivo existe, lo cargamos y agregamos fila
    if os.path.exists(TRAZABILIDAD_FILE):
        df = pd.read_excel(TRAZABILIDAD_FILE)
        df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    else:
        df = pd.DataFrame([nuevo_registro])

    df.to_excel(TRAZABILIDAD_FILE, index=False)
    print(f"📊 Registro actualizado en {TRAZABILIDAD_FILE}")


def enviar_orden(payload):
    """
    Envía la orden a Detrack usando el endpoint oficial.
    Muestra trazabilidad en consola y registra en Excel.
    """
    try:
        response = requests.post(DETRACK_URL, json=payload, headers=HEADERS)
        if response.status_code == 201:
            data = response.json()["data"]
            print(f"\n✅ Orden creada exitosamente:")
            print(f"   DO Number     : {data['do_number']}")
            print(f"   Detrack #     : {data['detrack_number']}")
            print(f"   Estado        : {data['status']}")
            print(f"   Tracking Link : {data['tracking_link']}")

            # Registrar en Excel
            registrar_trazabilidad(payload, data)
            return data
        else:
            print(f"\n❌ Error {response.status_code}: {response.text}")
            registrar_trazabilidad(payload, None)
            return None
    except Exception as e:
        print(f"\n🚫 Excepción al enviar la orden: {str(e)}")
        registrar_trazabilidad(payload, None)
        return None
# Alias para compatibilidad con el formulario manual
def upload_job(payload):
    return enviar_orden(payload)

# main_detrack.py

import os
import glob
import pandas as pd

# ✅ Imports dentro del paquete siigoScript.Detrack
from siigoScript.Detrack.payload_builder_detrack import build_payload
from siigoScript.Detrack.uploader_detrack import enviar_orden
from siigoScript.Detrack import config_detrack as config   # configuración específica de Detrack

def obtener_ultimo_excel():
    """
    Busca el último archivo Excel generado en la carpeta de resultados.
    Si hay versiones incrementales (facturas_lubrisol(1).xlsx, etc.),
    selecciona el más reciente.
    """
    carpeta = config.CARPETA_SALIDA
    patron = os.path.join(carpeta, "facturas_lubrisol*.xlsx")
    archivos = glob.glob(patron)
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún Excel en {carpeta}")
    archivos.sort(key=os.path.getmtime, reverse=True)
    return archivos[0]


def main():
    print("🚀 Iniciando flujo de integración Siigo → Detrack...")

    # Leer el último Excel generado por Siigo
    ruta_excel = obtener_ultimo_excel()
    print(f"📂 Usando archivo Excel: {ruta_excel}")
    df = pd.read_excel(ruta_excel)

    for _, row in df.iterrows():
        datos = {
            "do_number": row["BE"],                     # Número de orden logística
            "date": row["Fecha"],                       # Fecha de la factura
            "address": row["Cliente"],                  # Nombre del cliente
            "deliver_to_collect_from": row["Cliente"],  # También usamos Cliente aquí
            "phone": row["FV"],                         # Usamos FV como identificación
            "items": row["Productos"]                   # Lista de productos
        }

        payload = build_payload(datos)
        enviar_orden(payload)

    print("✅ Flujo finalizado. Órdenes enviadas a Detrack.")


if __name__ == "__main__":
    main()

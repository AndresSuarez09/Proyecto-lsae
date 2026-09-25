# main_detrack.py

import os
import glob
import pandas as pd

from siigoScript.Detrack.payload_builder_detrack import build_payload
from siigoScript.Detrack.uploader_detrack import enviar_orden
from siigoScript.Detrack import config_detrack as config

def obtener_ultimo_excel():
    carpeta = config.CARPETA_SALIDA
    patron = os.path.join(carpeta, "facturas_lubrisol*.xlsx")
    archivos = glob.glob(patron)
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún Excel en {carpeta}")
    archivos.sort(key=os.path.getmtime, reverse=True)
    return archivos[0]

def main():
    print("🚀 Iniciando flujo de integración Siigo → Detrack...")
    ruta_excel = obtener_ultimo_excel()
    print(f"📂 Usando archivo Excel: {ruta_excel}")
    
    df = pd.read_excel(ruta_excel)
    df.columns = df.columns.str.strip()
    print("Columnas detectadas:", df.columns.tolist())

    if "FV" not in df.columns:
        print("❌ Error: No se encontró la columna 'FV' en el Excel.")
        return

    # Agrupar las filas por número de factura para unificar los ítems
    facturas_agrupadas = df.groupby("FV", dropna=False)

    for fv, grupo in facturas_agrupadas:
        if pd.isna(fv) or str(fv).strip() == "":
            continue

        primera_fila = grupo.iloc[0]
        
        do_number = primera_fila.get("BE")
        if pd.isna(do_number) or str(do_number).strip() == "":
            do_number = f"BE-{fv}"
        
        # Construir la lista dinámica de productos para esta factura
        items_list = []
        for _, fila in grupo.iterrows():
            producto = str(fila.get("Productos", "")).strip()
            if producto and producto.lower() != "nan" and producto != "Sin productos":
                cantidad_cruda = fila.get("Cantidad", 1)
                try:
                    cantidad = int(float(cantidad_cruda)) if pd.notna(cantidad_cruda) else 1
                except ValueError:
                    cantidad = 1
                    
                items_list.append({
                    "description": producto,
                    "quantity": cantidad
                })
        
        # Respaldo por si la factura no tiene productos registrados
        if not items_list:
            items_list.append({"description": "Sin descripción", "quantity": 1})

        # Armar el paquete de datos unificado
        datos = {
            "do_number": str(do_number).strip(),
            "date": str(primera_fila.get("Fecha", "")).split()[0] if pd.notna(primera_fila.get("Fecha")) else "",
            "address": str(primera_fila.get("address", "")) if pd.notna(primera_fila.get("address")) else "",
            "deliver_to_collect_from": str(primera_fila.get("company_name", "")) if pd.notna(primera_fila.get("company_name")) else "",
            "phone_number": str(fv).strip(),
            "items": items_list
        }

        print(f"DEBUG DATOS ({fv}):", datos)
        payload = build_payload(datos)
        print(f"DEBUG PAYLOAD ({fv}):", payload)
        enviar_orden(payload)

    print("✅ Flujo finalizado. Órdenes enviadas a Detrack.")

if __name__ == "__main__":
    main()
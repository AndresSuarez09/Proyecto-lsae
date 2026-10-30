# payload_builder_detrack.py

def build_payload(data):
    """
    Construye el payload para crear una orden en Detrack.
    El resultado está anidado bajo la clave 'data', como exige la API v2.
    """
    print("DEBUG DATA:", data)

    payload = {
        "data": {
            "type": "Collection",                                      # ✅ Ajuste: Cambiado de Delivery a Collection
            "do_number": data["do_number"],
            "date": data.get("date"),
            "address": data.get("address"),                            # Dirección física
            "company_name": data.get("company_name"),                  # Nombre de la compañía
            "deliver_to_collect_from": data.get("deliver_to_collect_from"), 
            "phone_number": data.get("phone_number"),                  # Teléfono real
            "pieces": data.get("pieces"),                              # Sumatoria de piezas
            "items": data.get("items", [])                             # Ítems con SKU
        }
    }

    print("DEBUG PAYLOAD:", payload)
    return payload
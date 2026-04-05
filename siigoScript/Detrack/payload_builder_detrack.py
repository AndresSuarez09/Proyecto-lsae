# payload_builder_detrack.py

def build_payload(data):
    """
    Construye el payload para crear una orden en Detrack.
    El resultado está anidado bajo la clave 'data', como exige la API v2.
    Los campos se transforman desde el Excel de Siigo al formato requerido.
    """

    print("DEBUG DATA:", data)

    payload = {
        "data": {
            "type": "Delivery",
            "do_number": data["do_number"],
            "date": data.get("date"),
            "address": data.get("address"),                          # ✅ Dirección física
            "deliver_to_collect_from": data.get("deliver_to_collect_from"),          # ✅ Nombre del cliente/empresa
            "phone_number": data.get("phone"),
            "items": [
                {
                    "description": data.get("items"),
                    "quantity": 1
                }
            ]
        }
    }

    print("DEBUG PAYLOAD:", payload)
    return payload
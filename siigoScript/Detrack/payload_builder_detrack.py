# payload_builder_detrack.py

def build_payload(data):
    """
    Construye el payload para crear una orden en Detrack.
    El resultado está anidado bajo la clave 'data', como exige la API v2.
    Los campos se transforman desde el Excel de Siigo al formato requerido.
    """
    return {
        "data": {
            "type": "Delivery",                          # Tipo de orden
            "do_number": data["do_number"],              # Número BE (transformado desde FV)
            "date": data.get("date"),                    # Fecha de la factura
            "address": data.get("address"),              # Dirección / Cliente
            "deliver_to_collect_from": data.get("address"),  # Nombre del cliente (usamos mismo campo)
            "phone_number": data.get("phone"),           # Identificación / Teléfono
            "items": [
                {
                    "description": data.get("items"),    # Productos concatenados del Excel
                    "quantity": 1                        # Se envía como un ítem descriptivo
                }
            ]
        }
    }

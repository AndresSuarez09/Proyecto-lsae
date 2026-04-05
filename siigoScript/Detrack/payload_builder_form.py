# payload_builder_form.py

def build_payload(data):
    """
    Construye el payload para crear una orden en Detrack
    a partir de los datos ingresados manualmente en el formulario.
    """
    return {
        "data": {
            "type": "Delivery",
            "do_number": data.get("do_number"),
            "date": data.get("date"),
            "address": data.get("address"),                        # Dirección física
            "deliver_to_collect_from": data.get("deliver_to_collect_from"),   # ✅ Nombre del cliente/empresa
            "phone_number": data.get("phone_number"),
            "invoice_number": data.get("invoice_number"),
            "invoice_amount": data.get("invoice_amount"),
            "payment_mode": data.get("payment_mode"),
            "payment_amount": data.get("payment_amount"),
            "order_number": data.get("order_number"),
            "instructions": data.get("instructions"),
            "pieces": data.get("pieces"),
            "job_owner": data.get("job_owner"),
            "carrier": data.get("carrier"),
            "identification_number": data.get("identification_number"),
            "status": data.get("job_status"),
            "assign_to": data.get("assign_to"),
            "items": [
                {
                    "sku": data.get("sku"),
                    "description": data.get("item_description"),
                    "quantity": data.get("quantity"),
                    "comments": data.get("comments"),
                    "reject_quantity": data.get("reject_quantity"),
                    "reject_reason": data.get("reject_reason")
                }
            ]
        }
    }
# input_console_detrack.py

def capturar_datos():
    """
    Solicita al usuario los datos mínimos necesarios para crear una orden en Detrack.
    """
    print("\n📝 Ingreso de datos para nueva orden:")
    return {
        "do_number": input("🔢 Número de orden (do_number): ").strip(),
        "date": input("📅 Fecha (YYYY-MM-DD): ").strip(),
        "address": input("📍 Dirección de entrega: ").strip(),
        "deliver_to": input("👤 Nombre del destinatario: ").strip(),
        "phone": input("📞 Teléfono de contacto: ").strip()
    }

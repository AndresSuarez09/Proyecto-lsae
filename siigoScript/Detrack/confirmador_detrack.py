# confirmador_detrack.py

def confirmar(datos):
    """
    Muestra los datos ingresados y solicita confirmación antes de enviar la orden.
    """
    print("\n📋 Resumen de datos ingresados:")
    for clave, valor in datos.items():
        print(f" - {clave}: {valor}")
    
    respuesta = input("\n¿Confirmar envío a Detrack? (s/n): ").strip().lower()
    return respuesta == "s"

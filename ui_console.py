# ui_console.py
from datetime import datetime
from auth_siigo import obtener_token_siigo
from query_facturas import consultar_facturas_siigo, consultar_factura_por_numero
from main import resolver_clientes, generar_excel
from siigoScript.Detrack.main_detrack import main as flujo_detrack

def mostrar_menu():
    print("\n=== Menú de integración Siigo → Detrack ===")
    print("1. Consultar facturas por fecha")
    print("2. Consultar todas las facturas del día actual")
    print("3. Consultar una factura específica (FV)")
    print("4. Generar Excel sin subir a Detrack")
    print("5. Generar Excel y subir a Detrack")
    print("6. Subir a Detrack desde el último Excel generado")
    print("0. Salir")

def validar_formato_fecha(fecha_str: str) -> bool:
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def preguntar_subida_detrack():
    subir = input("¿Desea subir a Detrack? (s/n): ").strip().lower()
    if subir == "s":
        print("▶ Enviando órdenes a Detrack...")
        flujo_detrack()
    else:
        print("ℹ Se omite subida a Detrack.")

def ejecutar_opcion(opcion: str, token: str):
    if opcion == "1":
        fecha = input("Ingrese la fecha (YYYY-MM-DD): ").strip()
        if not validar_formato_fecha(fecha):
            print("❌ Formato de fecha inválido. Use YYYY-MM-DD.")
            return
        print(f"▶ Consultando facturas del {fecha}...")
        facturas = consultar_facturas_siigo(token, created_start=fecha, created_end=fecha)
        clientes = resolver_clientes(token, facturas)
        generar_excel(facturas, clientes)
        preguntar_subida_detrack()

    elif opcion == "2":
        hoy = datetime.now().strftime("%Y-%m-%d")
        print(f"▶ Consultando todas las facturas del día {hoy}...")
        facturas = consultar_facturas_siigo(token, created_start=hoy, created_end=hoy)
        clientes = resolver_clientes(token, facturas)
        generar_excel(facturas, clientes)
        print("✅ Excel generado para el día actual.")

    elif opcion == "3":
        fv = input("Ingrese el número exacto de la factura (FV): ").strip()
        if not fv:
            print("❌ Número de factura requerido.")
            return
        facturas = consultar_factura_por_numero(token, fv)
        if not facturas:
            print("🚫 No se encontró la factura indicada.")
            return
        clientes = resolver_clientes(token, facturas)
        generar_excel(facturas, clientes)
        preguntar_subida_detrack()

    elif opcion == "4":
        print("▶ Generando Excel sin subir a Detrack...")
        facturas = consultar_facturas_siigo(token)
        clientes = resolver_clientes(token, facturas)
        generar_excel(facturas, clientes)
        print("✅ Excel generado. Se omite subida a Detrack.")

    elif opcion == "5":
        print("▶ Generando Excel y subiendo a Detrack...")
        facturas = consultar_facturas_siigo(token)
        clientes = resolver_clientes(token, facturas)
        generar_excel(facturas, clientes)
        flujo_detrack()

    elif opcion == "6":
        print("▶ Subiendo órdenes a Detrack desde el último Excel generado...")
        flujo_detrack()

    elif opcion == "0":
        print("👋 Saliendo del sistema...")
        exit()
    else:
        print("❌ Opción inválida.")

def main():
    print("🔐 Generando token JWT desde Siigo...")
    token = obtener_token_siigo()  # se genera una sola vez
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        ejecutar_opcion(opcion, token)

if __name__ == "__main__":
    main()

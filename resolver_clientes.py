# resolver_clientes.py

import requests

def construir_diccionario_clientes(facturas, token):
    """
    Construye un diccionario con los nombres de clientes registrados en Siigo.
    - Si la factura trae customer.id → consulta /v1/customers/{id}
    - Si solo trae customer.identification → consulta /v1/customers?identification={nit}
    Aplica validación robusta para evitar errores con valores int, None o listas.
    """

    clientes_resueltos = {}

    for f in facturas:
        cliente = f.get("customer", {})
        cliente_id = cliente.get("id")
        identificacion = cliente.get("identification")

        # Evitar consultas duplicadas
        clave = cliente_id or identificacion
        if not clave or clave in clientes_resueltos:
            continue

        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Partner-Id": "Lubrisol"
        }

        try:
            # Selección de endpoint según lo disponible
            if cliente_id:
                url = f"https://api.siigo.com/v1/customers/{cliente_id}"
            else:
                url = f"https://api.siigo.com/v1/customers?identification={identificacion}"

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                # Manejo de respuesta: puede ser dict con "results", lista o dict directo
                if isinstance(data, dict) and "results" in data and data["results"]:
                    cliente_data = data["results"][0]
                elif isinstance(data, list) and data:
                    cliente_data = data[0]
                elif isinstance(data, dict):
                    cliente_data = data
                else:
                    cliente_data = {}

                # Normalización del nombre
                nombre_raw = cliente_data.get("name")
                if isinstance(nombre_raw, list):
                    nombre = " ".join(nombre_raw).replace("S.A.", "").strip()
                elif isinstance(nombre_raw, str):
                    nombre = nombre_raw.replace("S.A.", "").strip()
                else:
                    nombre = cliente_data.get("commercial_name", "SIN NOMBRE")

                clientes_resueltos[clave] = nombre
                print(f"✅ Cliente resuelto: {clave} → {nombre}")

            else:
                print(f"⚠️ Error {response.status_code} al consultar cliente {clave}: {response.text}")
                clientes_resueltos[clave] = "SIN NOMBRE"

        except Exception as e:
            print(f"⚠️ Excepción al consultar cliente {clave}: {e}")
            clientes_resueltos[clave] = "SIN NOMBRE"

    print(f"📊 Total clientes resueltos: {len(clientes_resueltos)}")
    return clientes_resueltos

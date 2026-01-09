# config_detrack.py

# Endpoint oficial de Detrack para crear órdenes
DETRACK_URL = "https://app.detrack.com/api/v2/dn/jobs"

# Headers con autenticación
HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": "7a09cb54a6c46023f37205e3e0adbbb9c8a985fa825cf42a"
}

# Carpeta donde se guardan los Excels generados por Siigo
# Ajusta el nombre si tu script principal guarda en otra ruta
CARPETA_SALIDA = "resultados"

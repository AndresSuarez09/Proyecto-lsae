# 🧾 Script de Consulta de Facturas - Lubrisol

Este script permite consultar facturas desde Siigo y generar un archivo Excel profesional con los resultados.

---

## 📁 Archivos incluidos

- `main.py`: Ejecuta el flujo completo
- `config.py`: Edita credenciales y filtros
- `query_facturas.py`: Conexión con Siigo API
- `excel_generator.py`: Genera el archivo Excel

---

## 🔐 Configuración

1. Abre `config.py`
2. Reemplaza el valor de `SIIGO_ACCESS_KEY` con tu token JWT válido de Siigo
3. Ajusta las fechas y estado de factura si lo deseas

```python
SIIGO_ACCESS_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Token JWT real
FECHA_INICIO = "2025-08-01"
FECHA_FIN = "2025-08-31"
ESTADO_FACTURA = "open"

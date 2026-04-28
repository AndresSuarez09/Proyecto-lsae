# app.py

from fastapi import FastAPI

# Inicializamos la aplicación FastAPI
app = FastAPI()

# Ruta principal que muestra un mensaje simple
@app.get("/")
def root():
    return {"message": "Backend Lubrisol activo"}

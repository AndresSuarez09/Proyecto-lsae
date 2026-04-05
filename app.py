# app.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Inicializamos la aplicación FastAPI
app = FastAPI()

# Indicamos dónde están las plantillas HTML
templates = Jinja2Templates(directory="templates")

# Ruta principal que muestra la interfaz
@app.get("/", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .api.routes import auth, empresas, insumos, servicios, paquetes, auditoria, caja, demo, ventas, importacion, usuarios

app = FastAPI(title="INV DOC — Guiar Salud IPS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(empresas.router)
app.include_router(insumos.router)
app.include_router(servicios.router)
app.include_router(paquetes.router)
app.include_router(auditoria.router)
app.include_router(caja.router)
app.include_router(demo.router)
app.include_router(ventas.router)
app.include_router(importacion.router)
app.include_router(usuarios.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Frontend compilado (solo en produccion, cuando la imagen incluye /app/static) ---
# En desarrollo local el frontend corre en su propio contenedor nginx y este bloque no aplica.
_static_dir = settings.STATIC_DIR
if os.path.isdir(_static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(_static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def servir_spa(full_path: str):
        """Devuelve el archivo estatico si existe; si no, index.html para que React Router resuelva la ruta."""
        candidato = os.path.join(_static_dir, full_path)
        if full_path and os.path.isfile(candidato):
            return FileResponse(candidato)
        return FileResponse(os.path.join(_static_dir, "index.html"))

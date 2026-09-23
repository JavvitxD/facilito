from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from datetime import date
import uuid

from ...database import get_db
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user
from ...audit import registrar
from ...importacion import exportar_inventario, analizar, aplicar

router = APIRouter(tags=["importacion"])

TIPO_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MAX_BYTES = 5 * 1024 * 1024


def check_espacio_access(espacio_id: uuid.UUID, current_user: Usuario, db: Session) -> Espacio:
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if current_user.rol != "superadmin" and current_user.empresa_id != espacio.empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return espacio


async def _leer_archivo(archivo: UploadFile) -> bytes:
    if not archivo.filename or not archivo.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=422, detail="El archivo debe ser un Excel (.xlsx)")
    contenido = await archivo.read()
    if len(contenido) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera los 5 MB")
    if not contenido:
        raise HTTPException(status_code=422, detail="El archivo está vacío")
    return contenido


@router.get("/espacios/{espacio_id}/inventario/exportar")
def exportar(
    espacio_id: uuid.UUID,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Descarga el inventario en Excel para trabajarlo sin conexion."""
    espacio = check_espacio_access(espacio_id, current_user, db)
    contenido = exportar_inventario(db, espacio_id, espacio.nombre)
    nombre = f"inventario_{date.today().isoformat()}.xlsx"
    return Response(
        content=contenido,
        media_type=TIPO_EXCEL,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.post("/espacios/{espacio_id}/inventario/analizar")
async def analizar_archivo(
    espacio_id: uuid.UUID,
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Describe que haria la importacion. No modifica nada."""
    check_espacio_access(espacio_id, current_user, db)
    contenido = await _leer_archivo(archivo)
    try:
        return analizar(db, espacio_id, contenido)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/espacios/{espacio_id}/inventario/importar")
async def importar_archivo(
    espacio_id: uuid.UUID,
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aplica el archivo. La interfaz muestra el analisis antes de llegar aqui."""
    check_espacio_access(espacio_id, current_user, db)
    contenido = await _leer_archivo(archivo)
    try:
        resultado = aplicar(db, espacio_id, contenido, current_user.email)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    registrar(
        db, espacio_id, current_user, "importacion", archivo.filename or "Excel", "crear",
        f"Importación desde Excel: {resultado['creados']} productos creados, "
        f"{resultado['actualizados']} actualizados",
    )
    db.commit()
    return resultado

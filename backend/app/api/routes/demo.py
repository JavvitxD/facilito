from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuario import Usuario
from ...auth import get_current_user
from ...demo import restaurar, EMAIL_DEMO

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/es-demo")
def es_demo(current_user: Usuario = Depends(get_current_user)):
    """Permite a la interfaz mostrar el boton de restaurar solo en la cuenta demo."""
    return {"es_demo": current_user.email == EMAIL_DEMO}


@router.post("/restaurar")
def restaurar_demo(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve el ambiente de demostracion a su estado original.

    Solo la propia cuenta demo puede invocarlo. La restriccion es por email, no
    por rol ni por empresa, para que ninguna cuenta real pueda perder datos por
    un error de configuracion.
    """
    if current_user.email != EMAIL_DEMO:
        raise HTTPException(
            status_code=403,
            detail="Solo la cuenta de demostración puede restaurarse",
        )

    espacio = restaurar(db)
    return {
        "mensaje": "Ambiente de demostración restaurado",
        "espacio_id": str(espacio.id),
    }

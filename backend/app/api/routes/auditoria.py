from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from ...database import get_db
from ...models.audit_log import AuditLog
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user

router = APIRouter(tags=["auditoria"])


def check_espacio_access(espacio_id: uuid.UUID, current_user: Usuario, db: Session):
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if current_user.rol != "superadmin" and current_user.empresa_id != espacio.empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return espacio


@router.get("/espacios/{espacio_id}/auditoria")
def get_auditoria(
    espacio_id: uuid.UUID,
    entidad: Optional[str] = Query(None),
    accion: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)

    q = db.query(AuditLog).filter(AuditLog.espacio_id == espacio_id)
    if entidad:
        q = q.filter(AuditLog.entidad == entidad)
    if accion:
        q = q.filter(AuditLog.accion == accion)

    total = q.count()
    logs = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "registros": [
            {
                "id": str(log.id),
                "usuario_email": log.usuario_email,
                "entidad": log.entidad,
                "entidad_nombre": log.entidad_nombre,
                "accion": log.accion,
                "descripcion": log.descripcion,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }

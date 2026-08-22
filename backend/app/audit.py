import uuid
from sqlalchemy.orm import Session
from .models.audit_log import AuditLog
from .models.usuario import Usuario


def registrar(
    db: Session,
    espacio_id: uuid.UUID,
    usuario: Usuario,
    entidad: str,
    entidad_nombre: str,
    accion: str,
    descripcion: str,
) -> None:
    log = AuditLog(
        espacio_id=espacio_id,
        usuario_email=usuario.email,
        entidad=entidad,
        entidad_nombre=entidad_nombre,
        accion=accion,
        descripcion=descripcion,
    )
    db.add(log)

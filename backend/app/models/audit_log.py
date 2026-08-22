import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    usuario_email = Column(String, nullable=True)
    entidad = Column(String, nullable=False)   # insumo | precio | proveedor | servicio | paquete
    entidad_nombre = Column(String, nullable=True)
    accion = Column(String, nullable=False)    # crear | editar | eliminar
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

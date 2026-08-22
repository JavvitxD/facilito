import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Paquete(Base):
    __tablename__ = "paquetes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)

    espacio = relationship("Espacio", back_populates="paquetes")
    servicios = relationship("PaqueteServicio", back_populates="paquete", cascade="all, delete-orphan")


class PaqueteServicio(Base):
    __tablename__ = "paquete_servicios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paquete_id = Column(UUID(as_uuid=True), ForeignKey("paquetes.id"), nullable=False)
    servicio_id = Column(UUID(as_uuid=True), ForeignKey("servicios.id"), nullable=False)

    paquete = relationship("Paquete", back_populates="servicios")
    servicio = relationship("Servicio")

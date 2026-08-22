import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Espacio(Base):
    __tablename__ = "espacios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    especialidad = Column(String)
    activo = Column(Boolean, default=True)

    empresa = relationship("Empresa", back_populates="espacios")
    proveedores = relationship("Proveedor", back_populates="espacio")
    insumos = relationship("Insumo", back_populates="espacio")
    servicios = relationship("Servicio", back_populates="espacio")
    paquetes = relationship("Paquete", back_populates="espacio")

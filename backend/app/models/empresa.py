import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    nit = Column(String)
    ciudad = Column(String)
    # 'salud' (IPS: insumos, servicios, paquetes) o 'comercio' (distribuidora:
    # productos, combos, promociones). Solo cambia como se nombran las cosas.
    tipo_negocio = Column(String, nullable=False, default="salud")
    activa = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuarios = relationship("Usuario", back_populates="empresa")
    espacios = relationship("Espacio", back_populates="empresa")

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    precio_mercado_referencia = Column(Numeric(12, 2))
    url_referencia_precio = Column(String)
    margen_ganancia_pct = Column(Numeric(5, 2), default=30)
    activo = Column(Boolean, default=True)

    espacio = relationship("Espacio", back_populates="servicios")
    insumos = relationship("ServicioInsumo", back_populates="servicio", cascade="all, delete-orphan")

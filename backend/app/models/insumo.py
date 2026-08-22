import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Insumo(Base):
    __tablename__ = "insumos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    nombre = Column(String, nullable=False)
    categoria = Column(String)  # 'medico' | 'medicamento' | 'aseo'
    unidad_medida = Column(String)
    invima = Column(String)
    stock_actual = Column(Numeric(12, 4), default=0)
    stock_minimo = Column(Numeric(12, 4), default=0)
    activo = Column(Boolean, default=True)

    espacio = relationship("Espacio", back_populates="insumos")
    precios = relationship("PrecioInsumo", back_populates="insumo", cascade="all, delete-orphan")
    servicios = relationship("ServicioInsumo", back_populates="insumo")

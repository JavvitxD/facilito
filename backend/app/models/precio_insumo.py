import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class PrecioInsumo(Base):
    __tablename__ = "precios_insumo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    insumo_id = Column(UUID(as_uuid=True), ForeignKey("insumos.id"), nullable=False)
    proveedor_id = Column(UUID(as_uuid=True), ForeignKey("proveedores.id"), nullable=False)
    precio_presentacion = Column(Numeric(12, 2), nullable=False)
    unidades_por_presentacion = Column(Integer)
    descripcion_presentacion = Column(String)
    fuente_url = Column(String)
    fecha_precio = Column(Date)
    activo = Column(Boolean, default=True)

    insumo = relationship("Insumo", back_populates="precios")
    proveedor = relationship("Proveedor", back_populates="precios")

    @property
    def precio_unitario(self):
        if self.unidades_por_presentacion and self.unidades_por_presentacion > 0:
            return float(self.precio_presentacion) / self.unidades_por_presentacion
        return float(self.precio_presentacion)

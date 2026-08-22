import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    nombre = Column(String, nullable=False)

    espacio = relationship("Espacio", back_populates="proveedores")
    precios = relationship("PrecioInsumo", back_populates="proveedor")

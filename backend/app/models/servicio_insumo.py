import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class ServicioInsumo(Base):
    __tablename__ = "servicio_insumos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    servicio_id = Column(UUID(as_uuid=True), ForeignKey("servicios.id"), nullable=False)
    insumo_id = Column(UUID(as_uuid=True), ForeignKey("insumos.id"), nullable=False)
    cantidad = Column(Numeric(12, 4), nullable=False)
    notas = Column(String)

    servicio = relationship("Servicio", back_populates="insumos")
    insumo = relationship("Insumo", back_populates="servicios")

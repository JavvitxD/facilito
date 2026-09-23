import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class Venta(Base):
    """Una venta es un hecho: no se edita ni se borra.

    Para deshacerla se anula, lo que devuelve el stock y revierte el ingreso de
    caja, dejando constancia del motivo. Los importes quedan congelados aunque
    los precios del catalogo cambien despues.
    """

    __tablename__ = "ventas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    cliente = Column(String)
    notas = Column(Text)

    estado_pago = Column(String, nullable=False, default="pagado")  # 'pagado' | 'pendiente'
    fecha_pago = Column(Date)

    total = Column(Numeric(14, 2), nullable=False, default=0)
    costo_total = Column(Numeric(14, 2), nullable=False, default=0)

    anulada = Column(Boolean, default=False, nullable=False)
    motivo_anulacion = Column(Text)

    usuario_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("VentaItem", back_populates="venta", cascade="all, delete-orphan")


class VentaItem(Base):
    """Linea de una venta: un producto suelto o un combo.

    Guarda el nombre, el costo y el precio sugerido tal como estaban al vender,
    de modo que la venta siga siendo legible si el catalogo cambia. La diferencia
    entre 'precio_unitario' y 'precio_sugerido' es la que delata un cobro fuera
    de lista.
    """

    __tablename__ = "venta_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venta_id = Column(UUID(as_uuid=True), ForeignKey("ventas.id"), nullable=False)

    insumo_id = Column(UUID(as_uuid=True), ForeignKey("insumos.id"))
    servicio_id = Column(UUID(as_uuid=True), ForeignKey("servicios.id"))

    descripcion = Column(String, nullable=False)
    cantidad = Column(Numeric(12, 4), nullable=False)
    precio_unitario = Column(Numeric(14, 2), nullable=False)
    precio_sugerido = Column(Numeric(14, 2))
    costo_unitario = Column(Numeric(14, 2), default=0)
    subtotal = Column(Numeric(14, 2), nullable=False)

    venta = relationship("Venta", back_populates="items")

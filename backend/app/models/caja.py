import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base


class MovimientoCaja(Base):
    """Movimiento de efectivo. Es un hecho contable: nunca se edita ni se borra.

    Para deshacer un movimiento se marca 'anulado' y se registra el motivo, de modo
    que el historico conserve tanto el movimiento original como su anulacion.
    """

    __tablename__ = "movimientos_caja"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    tipo = Column(String, nullable=False)       # 'ingreso' | 'egreso'
    categoria = Column(String, nullable=False)  # 'venta' | 'prestamo' | 'abono' | 'compra' | 'gasto' | 'ajuste' | 'otro'
    concepto = Column(String, nullable=False)
    monto = Column(Numeric(14, 2), nullable=False)

    # Enlace al registro que lo origino (prestamo, abono, venta...), si lo hubo.
    referencia_tipo = Column(String)
    referencia_id = Column(UUID(as_uuid=True))

    anulado = Column(Boolean, default=False, nullable=False)
    motivo_anulacion = Column(Text)

    usuario_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Prestamo(Base):
    """Dinero prestado que esta pendiente de cobro."""

    __tablename__ = "prestamos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    deudor = Column(String, nullable=False)
    concepto = Column(String)
    monto = Column(Numeric(14, 2), nullable=False)
    notas = Column(Text)
    activo = Column(Boolean, default=True, nullable=False)
    usuario_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    abonos = relationship("AbonoPrestamo", back_populates="prestamo", cascade="all, delete-orphan")


class AbonoPrestamo(Base):
    """Pago parcial o total recibido contra un prestamo."""

    __tablename__ = "abonos_prestamo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prestamo_id = Column(UUID(as_uuid=True), ForeignKey("prestamos.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    monto = Column(Numeric(14, 2), nullable=False)
    notas = Column(Text)
    usuario_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    prestamo = relationship("Prestamo", back_populates="abonos")


class ArqueoCaja(Base):
    """Conteo fisico del efectivo en un momento dado.

    Guarda el saldo teorico calculado en ese instante junto al efectivo realmente
    contado. La diferencia entre ambos es la senal de descuadre: se registra, no
    se corrige sola.
    """

    __tablename__ = "arqueos_caja"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    espacio_id = Column(UUID(as_uuid=True), ForeignKey("espacios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    efectivo_contado = Column(Numeric(14, 2), nullable=False)
    saldo_teorico = Column(Numeric(14, 2), nullable=False)
    diferencia = Column(Numeric(14, 2), nullable=False)
    notas = Column(Text)
    usuario_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

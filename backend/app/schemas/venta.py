from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import uuid


class VentaItemCreate(BaseModel):
    # Se envia insumo_id (producto suelto) o servicio_id (combo), no ambos.
    insumo_id: Optional[uuid.UUID] = None
    servicio_id: Optional[uuid.UUID] = None
    cantidad: Decimal
    # Precio realmente cobrado. Si viene vacio se usa el sugerido.
    precio_unitario: Optional[Decimal] = None


class VentaCreate(BaseModel):
    fecha: date
    cliente: Optional[str] = None
    notas: Optional[str] = None
    estado_pago: str = "pagado"        # 'pagado' | 'pendiente'
    items: List[VentaItemCreate]


class VentaAnular(BaseModel):
    motivo: str


class RegistrarPago(BaseModel):
    fecha_pago: date


class VentaItemOut(BaseModel):
    id: uuid.UUID
    insumo_id: Optional[uuid.UUID] = None
    servicio_id: Optional[uuid.UUID] = None
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    precio_sugerido: Optional[Decimal] = None
    costo_unitario: Optional[Decimal] = None
    subtotal: Decimal

    class Config:
        from_attributes = True


class AlertaVenta(BaseModel):
    tipo: str        # 'precio_fuera_de_lista' | 'stock_insuficiente' | 'pago_vencido'
    severidad: str
    mensaje: str


class VentaOut(BaseModel):
    id: uuid.UUID
    fecha: date
    cliente: Optional[str] = None
    notas: Optional[str] = None
    estado_pago: str
    fecha_pago: Optional[date] = None
    total: Decimal
    costo_total: Decimal
    utilidad: Decimal
    anulada: bool
    motivo_anulacion: Optional[str] = None
    usuario_email: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[VentaItemOut] = []
    alertas: List[AlertaVenta] = []


class ResumenVentas(BaseModel):
    total_vendido: Decimal
    total_costo: Decimal
    utilidad: Decimal
    margen_pct: Optional[float] = None
    cantidad_ventas: int
    por_cobrar: Decimal
    ventas_pendientes: int
    ventas_con_alertas: int

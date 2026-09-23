from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import uuid


# --- Movimientos ---

class MovimientoCreate(BaseModel):
    fecha: date
    tipo: str            # 'ingreso' | 'egreso'
    categoria: str       # 'venta' | 'prestamo' | 'abono' | 'compra' | 'gasto' | 'ajuste' | 'otro'
    concepto: str
    monto: Decimal


class MovimientoAnular(BaseModel):
    motivo: str


class MovimientoOut(BaseModel):
    id: uuid.UUID
    fecha: date
    tipo: str
    categoria: str
    concepto: str
    monto: Decimal
    referencia_tipo: Optional[str] = None
    referencia_id: Optional[uuid.UUID] = None
    anulado: bool
    motivo_anulacion: Optional[str] = None
    usuario_email: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Prestamos ---

class PrestamoCreate(BaseModel):
    fecha: date
    deudor: str
    concepto: Optional[str] = None
    monto: Decimal
    notas: Optional[str] = None
    # Si es True se registra tambien el egreso de caja correspondiente.
    afecta_caja: bool = True


class PrestamoUpdate(BaseModel):
    deudor: Optional[str] = None
    concepto: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[bool] = None


class AbonoCreate(BaseModel):
    fecha: date
    monto: Decimal
    notas: Optional[str] = None
    afecta_caja: bool = True


class AbonoOut(BaseModel):
    id: uuid.UUID
    fecha: date
    monto: Decimal
    notas: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PrestamoOut(BaseModel):
    id: uuid.UUID
    fecha: date
    deudor: str
    concepto: Optional[str] = None
    monto: Decimal
    notas: Optional[str] = None
    activo: bool
    total_abonado: Decimal
    saldo: Decimal
    abonos: List[AbonoOut] = []
    created_at: Optional[datetime] = None


# --- Arqueo ---

class ArqueoCreate(BaseModel):
    fecha: date
    efectivo_contado: Decimal
    notas: Optional[str] = None


class ArqueoOut(BaseModel):
    id: uuid.UUID
    fecha: date
    efectivo_contado: Decimal
    saldo_teorico: Decimal
    diferencia: Decimal
    notas: Optional[str] = None
    usuario_email: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Resumen ---

class AlertaCaja(BaseModel):
    tipo: str        # 'descuadre' | 'prestamo_sin_abonos' | 'saldo_negativo'
    severidad: str   # 'alta' | 'media' | 'baja'
    mensaje: str
    detalle: Optional[str] = None


class ResumenCaja(BaseModel):
    total_ingresos: Decimal
    total_egresos: Decimal
    saldo_teorico: Decimal
    total_prestado: Decimal
    total_abonado: Decimal
    saldo_por_cobrar: Decimal
    ultimo_arqueo: Optional[ArqueoOut] = None
    alertas: List[AlertaCaja] = []

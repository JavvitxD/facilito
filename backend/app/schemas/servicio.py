from pydantic import BaseModel
from typing import Optional, List
import uuid
from decimal import Decimal


class ServicioInsumoCreate(BaseModel):
    insumo_id: uuid.UUID
    cantidad: Decimal
    notas: Optional[str] = None


class ServicioInsumoOut(BaseModel):
    id: uuid.UUID
    insumo_id: uuid.UUID
    insumo_nombre: Optional[str] = None
    cantidad: Decimal
    notas: Optional[str] = None
    costo_unitario: Optional[float] = None
    costo_total: Optional[float] = None

    class Config:
        from_attributes = True


class ServicioCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_mercado_referencia: Optional[Decimal] = None
    url_referencia_precio: Optional[str] = None
    margen_ganancia_pct: Optional[Decimal] = Decimal("30")
    insumos: Optional[List[ServicioInsumoCreate]] = []


class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_mercado_referencia: Optional[Decimal] = None
    url_referencia_precio: Optional[str] = None
    margen_ganancia_pct: Optional[Decimal] = None
    activo: Optional[bool] = None
    insumos: Optional[List[ServicioInsumoCreate]] = None


class ServicioOut(BaseModel):
    id: uuid.UUID
    espacio_id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None
    precio_mercado_referencia: Optional[Decimal] = None
    url_referencia_precio: Optional[str] = None
    margen_ganancia_pct: Optional[Decimal] = None
    activo: bool
    insumos: List[ServicioInsumoOut] = []

    class Config:
        from_attributes = True


class CostoServicioOut(BaseModel):
    servicio_id: uuid.UUID
    nombre: str
    costo_insumos: float
    margen_ganancia_pct: float
    precio_sugerido: float
    precio_mercado_referencia: Optional[float] = None
    margen_real_pct: Optional[float] = None
    insumos: List[ServicioInsumoOut] = []

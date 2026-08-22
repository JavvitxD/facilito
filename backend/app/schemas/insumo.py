from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import date
from decimal import Decimal


class PrecioInsumoCreate(BaseModel):
    proveedor_id: uuid.UUID
    precio_presentacion: Decimal
    unidades_por_presentacion: Optional[int] = None
    descripcion_presentacion: Optional[str] = None
    fuente_url: Optional[str] = None
    fecha_precio: Optional[date] = None


class PrecioInsumoOut(BaseModel):
    id: uuid.UUID
    proveedor_id: uuid.UUID
    proveedor_nombre: Optional[str] = None
    precio_presentacion: Decimal
    unidades_por_presentacion: Optional[int] = None
    precio_unitario: Optional[float] = None
    descripcion_presentacion: Optional[str] = None
    fuente_url: Optional[str] = None
    fecha_precio: Optional[date] = None
    activo: bool

    class Config:
        from_attributes = True


class InsumoCreate(BaseModel):
    nombre: str
    categoria: Optional[str] = None
    unidad_medida: Optional[str] = None
    invima: Optional[str] = None
    stock_actual: Optional[Decimal] = Decimal("0")
    stock_minimo: Optional[Decimal] = Decimal("0")
    precios: Optional[List[PrecioInsumoCreate]] = []


class InsumoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    unidad_medida: Optional[str] = None
    invima: Optional[str] = None
    stock_actual: Optional[Decimal] = None
    stock_minimo: Optional[Decimal] = None
    activo: Optional[bool] = None


class InsumoOut(BaseModel):
    id: uuid.UUID
    espacio_id: uuid.UUID
    nombre: str
    categoria: Optional[str] = None
    unidad_medida: Optional[str] = None
    invima: Optional[str] = None
    stock_actual: Optional[Decimal] = None
    stock_minimo: Optional[Decimal] = None
    activo: bool
    alerta_stock: bool = False
    precio_minimo: Optional[float] = None
    precios: List[PrecioInsumoOut] = []

    class Config:
        from_attributes = True


class PrecioInsumoUpdate(BaseModel):
    precio_presentacion: Optional[Decimal] = None
    unidades_por_presentacion: Optional[int] = None
    descripcion_presentacion: Optional[str] = None
    fecha_precio: Optional[date] = None


class ProveedorCreate(BaseModel):
    nombre: str


class ProveedorUpdate(BaseModel):
    nombre: str


class ProveedorOut(BaseModel):
    id: uuid.UUID
    nombre: str

    class Config:
        from_attributes = True

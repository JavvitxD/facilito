from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


class EmpresaCreate(BaseModel):
    nombre: str
    nit: Optional[str] = None
    ciudad: Optional[str] = None
    tipo_negocio: str = "salud"   # 'salud' | 'comercio'


class EmpresaUpdate(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    ciudad: Optional[str] = None
    tipo_negocio: Optional[str] = None
    activa: Optional[bool] = None


class EmpresaOut(BaseModel):
    id: uuid.UUID
    nombre: str
    nit: Optional[str] = None
    ciudad: Optional[str] = None
    tipo_negocio: str = "salud"
    activa: bool
    creado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class EspacioCreate(BaseModel):
    nombre: str
    especialidad: Optional[str] = None


class EspacioOut(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID
    nombre: str
    especialidad: Optional[str] = None
    activo: bool
    # Se repite aqui para que la interfaz sepa como nombrar las secciones sin
    # tener que consultar la empresa por separado.
    tipo_negocio: str = "salud"

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


class EmpresaCreate(BaseModel):
    nombre: str
    nit: Optional[str] = None
    ciudad: Optional[str] = None


class EmpresaOut(BaseModel):
    id: uuid.UUID
    nombre: str
    nit: Optional[str] = None
    ciudad: Optional[str] = None
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

    class Config:
        from_attributes = True

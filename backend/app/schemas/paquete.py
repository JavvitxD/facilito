from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class PaqueteServicioItem(BaseModel):
    servicio_id: UUID


class PaqueteCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    servicios: List[PaqueteServicioItem] = []


class PaqueteUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    servicios: Optional[List[PaqueteServicioItem]] = None


class ServicioResumenOut(BaseModel):
    id: UUID
    nombre: str
    costo_insumos: float

    class Config:
        from_attributes = True


class PaqueteOut(BaseModel):
    id: UUID
    espacio_id: UUID
    nombre: str
    descripcion: Optional[str]
    activo: bool
    servicios: List[ServicioResumenOut]
    costo_total: float

    class Config:
        from_attributes = True

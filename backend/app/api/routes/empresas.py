from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from ...database import get_db
from ...models.empresa import Empresa
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user, require_superadmin
from ...schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut, EspacioCreate, EspacioOut

router = APIRouter(prefix="/empresas", tags=["empresas"])


@router.get("", response_model=List[EmpresaOut])
def list_empresas(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.rol == "superadmin":
        return db.query(Empresa).filter(Empresa.activa == True).all()
    if current_user.empresa_id:
        return db.query(Empresa).filter(Empresa.id == current_user.empresa_id).all()
    return []


@router.post("", response_model=EmpresaOut)
def create_empresa(data: EmpresaCreate, _: Usuario = Depends(require_superadmin), db: Session = Depends(get_db)):
    empresa = Empresa(**data.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa


@router.put("/{empresa_id}", response_model=EmpresaOut)
def update_empresa(empresa_id: uuid.UUID, data: EmpresaUpdate, _: Usuario = Depends(require_superadmin), db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    cambios = data.model_dump(exclude_unset=True)
    if "tipo_negocio" in cambios and cambios["tipo_negocio"] not in ("salud", "comercio"):
        raise HTTPException(status_code=422, detail="El tipo de negocio debe ser 'salud' o 'comercio'")
    for campo, valor in cambios.items():
        setattr(empresa, campo, valor)
    db.commit()
    db.refresh(empresa)
    return empresa


@router.get("/{empresa_id}/espacios", response_model=List[EspacioOut])
def list_espacios(empresa_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.rol != "superadmin" and current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    espacios = db.query(Espacio).filter(Espacio.empresa_id == empresa_id, Espacio.activo == True).all()
    # El tipo se copia en cada espacio para que la interfaz no tenga que pedir
    # la empresa aparte solo para saber como nombrar las secciones.
    return [
        {
            "id": e.id, "empresa_id": e.empresa_id, "nombre": e.nombre,
            "especialidad": e.especialidad, "activo": e.activo,
            "tipo_negocio": empresa.tipo_negocio,
        }
        for e in espacios
    ]


@router.post("/{empresa_id}/espacios", response_model=EspacioOut)
def create_espacio(empresa_id: uuid.UUID, data: EspacioCreate, _: Usuario = Depends(require_superadmin), db: Session = Depends(get_db)):
    espacio = Espacio(empresa_id=empresa_id, **data.model_dump())
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio

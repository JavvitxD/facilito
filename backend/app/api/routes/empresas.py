from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from ...database import get_db
from ...models.empresa import Empresa
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user, require_superadmin
from ...schemas.empresa import EmpresaCreate, EmpresaOut, EspacioCreate, EspacioOut

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


@router.get("/{empresa_id}/espacios", response_model=List[EspacioOut])
def list_espacios(empresa_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.rol != "superadmin" and current_user.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return db.query(Espacio).filter(Espacio.empresa_id == empresa_id, Espacio.activo == True).all()


@router.post("/{empresa_id}/espacios", response_model=EspacioOut)
def create_espacio(empresa_id: uuid.UUID, data: EspacioCreate, _: Usuario = Depends(require_superadmin), db: Session = Depends(get_db)):
    espacio = Espacio(empresa_id=empresa_id, **data.model_dump())
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio

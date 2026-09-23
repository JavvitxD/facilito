from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import secrets
import uuid

from ...database import get_db
from ...models.usuario import Usuario
from ...models.empresa import Empresa
from ...auth import get_current_user, require_superadmin, hash_password
from ...schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioOut, PasswordRestablecida,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

MIN_PASSWORD = 8

# Sin caracteres que se confundan al dictarla por telefono (O/0, l/1, I).
ALFABETO_TEMPORAL = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generar_password_temporal(longitud: int = 10) -> str:
    return "".join(secrets.choice(ALFABETO_TEMPORAL) for _ in range(longitud))


def armar_salida(usuario: Usuario) -> dict:
    return {
        "id": usuario.id,
        "email": usuario.email,
        "rol": usuario.rol,
        "empresa_id": usuario.empresa_id,
        "empresa_nombre": usuario.empresa.nombre if usuario.empresa else None,
        "activo": usuario.activo,
        "debe_cambiar_password": bool(usuario.debe_cambiar_password),
    }


@router.get("", response_model=List[UsuarioOut])
def listar_usuarios(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """El superadmin ve todos; una cuenta empresa ve solo los de su empresa."""
    q = db.query(Usuario)
    if current_user.rol != "superadmin":
        if not current_user.empresa_id:
            return []
        q = q.filter(Usuario.empresa_id == current_user.empresa_id)
    return [armar_salida(u) for u in q.order_by(Usuario.email).all()]


@router.post("", response_model=UsuarioOut)
def crear_usuario(
    data: UsuarioCreate,
    _: Usuario = Depends(require_superadmin),
    db: Session = Depends(get_db),
):
    if data.rol not in ("superadmin", "empresa"):
        raise HTTPException(status_code=422, detail="El rol debe ser 'superadmin' o 'empresa'")
    if len(data.password) < MIN_PASSWORD:
        raise HTTPException(
            status_code=422,
            detail=f"La contraseña debe tener al menos {MIN_PASSWORD} caracteres",
        )
    if data.rol == "empresa" and not data.empresa_id:
        raise HTTPException(status_code=422, detail="Un usuario de empresa debe tener una empresa asignada")

    correo = str(data.email).strip().lower()
    if db.query(Usuario).filter(Usuario.email == correo).first():
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese correo")

    if data.empresa_id and not db.query(Empresa).filter(Empresa.id == data.empresa_id).first():
        raise HTTPException(status_code=404, detail="La empresa no existe")

    usuario = Usuario(
        email=correo,
        password_hash=hash_password(data.password),
        rol=data.rol,
        empresa_id=data.empresa_id if data.rol == "empresa" else None,
        activo=True,
        debe_cambiar_password=data.debe_cambiar_password,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return armar_salida(usuario)


@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: uuid.UUID,
    data: UsuarioUpdate,
    current_user: Usuario = Depends(require_superadmin),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cambios = data.model_dump(exclude_unset=True)

    if "activo" in cambios and cambios["activo"] is False and usuario.id == current_user.id:
        raise HTTPException(status_code=409, detail="No puedes desactivar tu propia cuenta")

    if "rol" in cambios:
        if cambios["rol"] not in ("superadmin", "empresa"):
            raise HTTPException(status_code=422, detail="El rol debe ser 'superadmin' o 'empresa'")
        if usuario.id == current_user.id and cambios["rol"] != "superadmin":
            raise HTTPException(status_code=409, detail="No puedes quitarte a ti mismo el rol de superadmin")

    if "email" in cambios:
        correo = str(cambios["email"]).strip().lower()
        existente = db.query(Usuario).filter(Usuario.email == correo, Usuario.id != usuario_id).first()
        if existente:
            raise HTTPException(status_code=409, detail="Ya existe un usuario con ese correo")
        cambios["email"] = correo

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return armar_salida(usuario)


@router.post("/{usuario_id}/restablecer-password", response_model=PasswordRestablecida)
def restablecer_password(
    usuario_id: uuid.UUID,
    _: Usuario = Depends(require_superadmin),
    db: Session = Depends(get_db),
):
    """Genera una contrasena temporal para alguien que perdio la suya.

    Se devuelve una sola vez, para entregarsela a la persona. Queda marcada como
    temporal: al entrar, la aplicacion le exige elegir una propia, de modo que
    ni el administrador conserve una clave con la que pueda entrar despues.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    temporal = generar_password_temporal()
    usuario.password_hash = hash_password(temporal)
    usuario.debe_cambiar_password = True
    db.commit()

    return PasswordRestablecida(
        usuario_id=usuario.id,
        email=usuario.email,
        password_temporal=temporal,
    )

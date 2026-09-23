from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str
    rol: str = "empresa"              # 'superadmin' | 'empresa'
    empresa_id: Optional[uuid.UUID] = None
    # Si es True, la persona debe elegir una contrasena propia al entrar.
    debe_cambiar_password: bool = True


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    empresa_id: Optional[uuid.UUID] = None
    activo: Optional[bool] = None


class UsuarioOut(BaseModel):
    id: uuid.UUID
    email: str
    rol: str
    empresa_id: Optional[uuid.UUID] = None
    empresa_nombre: Optional[str] = None
    activo: bool
    debe_cambiar_password: bool = False

    class Config:
        from_attributes = True


class PasswordRestablecida(BaseModel):
    """La contrasena temporal se devuelve una sola vez, al generarla."""
    usuario_id: uuid.UUID
    email: str
    password_temporal: str

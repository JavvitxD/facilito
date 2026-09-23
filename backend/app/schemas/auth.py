from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    rol: str
    empresa_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

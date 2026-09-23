from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ...database import get_db
from ...models.usuario import Usuario
from ...auth import verify_password, hash_password, create_access_token, get_current_user
from ...schemas.auth import Token, UserOut, CambiarPasswordRequest

# Longitud minima exigida a una contrasena nueva.
MIN_PASSWORD = 8

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == form_data.username, Usuario.activo == True).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@router.post("/cambiar-password", response_model=Token)
def cambiar_password(
    data: CambiarPasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cambia la contrasena del usuario autenticado.

    Exige la contrasena actual para que un token robado no baste para tomar la
    cuenta. Devuelve un token nuevo para que la sesion siga viva tras el cambio.
    """
    if not verify_password(data.password_actual, current_user.password_hash):
        raise HTTPException(status_code=401, detail="La contraseña actual no es correcta")

    nueva = data.password_nueva
    if len(nueva) < MIN_PASSWORD:
        raise HTTPException(
            status_code=422,
            detail=f"La contraseña nueva debe tener al menos {MIN_PASSWORD} caracteres",
        )
    if nueva == data.password_actual:
        raise HTTPException(status_code=422, detail="La contraseña nueva debe ser distinta de la actual")

    current_user.password_hash = hash_password(nueva)
    # Ya eligio una propia: deja de ser temporal.
    current_user.debe_cambiar_password = False
    db.commit()

    token = create_access_token({"sub": str(current_user.id)})
    return {"access_token": token, "token_type": "bearer"}

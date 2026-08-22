from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from ...database import get_db
from ...models.paquete import Paquete, PaqueteServicio
from ...models.servicio import Servicio
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user
from ...schemas.paquete import PaqueteCreate, PaqueteOut, PaqueteUpdate
from ...audit import registrar

router = APIRouter(tags=["paquetes"])


def check_espacio_access(espacio_id: uuid.UUID, current_user: Usuario, db: Session):
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if current_user.rol != "superadmin" and current_user.empresa_id != espacio.empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return espacio


def get_costo_servicio(servicio: Servicio) -> float:
    total = 0.0
    for si in servicio.insumos:
        precios = [p for p in si.insumo.precios if p.activo]
        if precios:
            precio_min = min(p.precio_unitario for p in precios)
            total += precio_min * float(si.cantidad)
    return total


def build_paquete_out(paquete: Paquete) -> dict:
    servicios_out = []
    costo_total = 0.0
    for ps in paquete.servicios:
        srv = ps.servicio
        if srv and srv.activo:
            costo = get_costo_servicio(srv)
            costo_total += costo
            servicios_out.append({
                "id": srv.id,
                "nombre": srv.nombre,
                "costo_insumos": costo,
            })
    return {
        "id": paquete.id,
        "espacio_id": paquete.espacio_id,
        "nombre": paquete.nombre,
        "descripcion": paquete.descripcion,
        "activo": paquete.activo,
        "servicios": servicios_out,
        "costo_total": costo_total,
    }


@router.get("/espacios/{espacio_id}/paquetes", response_model=List[PaqueteOut])
def list_paquetes(espacio_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    paquetes = db.query(Paquete).filter(Paquete.espacio_id == espacio_id, Paquete.activo == True).all()
    return [build_paquete_out(p) for p in paquetes]


@router.post("/espacios/{espacio_id}/paquetes", response_model=PaqueteOut)
def create_paquete(espacio_id: uuid.UUID, data: PaqueteCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    paquete = Paquete(espacio_id=espacio_id, nombre=data.nombre, descripcion=data.descripcion)
    db.add(paquete)
    db.flush()
    for item in data.servicios:
        srv = db.query(Servicio).filter(Servicio.id == item.servicio_id, Servicio.espacio_id == espacio_id).first()
        if srv:
            ps = PaqueteServicio(paquete_id=paquete.id, servicio_id=srv.id)
            db.add(ps)
    registrar(db, espacio_id, current_user, "paquete", data.nombre, "crear",
              f"Paquete creado: {data.nombre} ({len(data.servicios)} servicios)")
    db.commit()
    db.refresh(paquete)
    return build_paquete_out(paquete)


@router.get("/paquetes/{paquete_id}", response_model=PaqueteOut)
def get_paquete(paquete_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    paquete = db.query(Paquete).filter(Paquete.id == paquete_id).first()
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    check_espacio_access(paquete.espacio_id, current_user, db)
    return build_paquete_out(paquete)


@router.put("/paquetes/{paquete_id}", response_model=PaqueteOut)
def update_paquete(paquete_id: uuid.UUID, data: PaqueteUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    paquete = db.query(Paquete).filter(Paquete.id == paquete_id).first()
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    check_espacio_access(paquete.espacio_id, current_user, db)

    if data.nombre is not None:
        paquete.nombre = data.nombre
    if data.descripcion is not None:
        paquete.descripcion = data.descripcion
    if data.activo is not None:
        paquete.activo = data.activo

    if data.servicios is not None:
        for ps in paquete.servicios:
            db.delete(ps)
        db.flush()
        for item in data.servicios:
            srv = db.query(Servicio).filter(Servicio.id == item.servicio_id, Servicio.espacio_id == paquete.espacio_id).first()
            if srv:
                ps = PaqueteServicio(paquete_id=paquete.id, servicio_id=srv.id)
                db.add(ps)

    accion = "eliminar" if data.activo is False else "editar"
    desc = f"Paquete {'eliminado' if accion == 'eliminar' else 'actualizado'}: {paquete.nombre}"
    registrar(db, paquete.espacio_id, current_user, "paquete", paquete.nombre, accion, desc)
    db.commit()
    db.refresh(paquete)
    return build_paquete_out(paquete)


@router.delete("/paquetes/{paquete_id}")
def delete_paquete(paquete_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    paquete = db.query(Paquete).filter(Paquete.id == paquete_id).first()
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    check_espacio_access(paquete.espacio_id, current_user, db)
    paquete.activo = False
    db.commit()
    return {"ok": True}

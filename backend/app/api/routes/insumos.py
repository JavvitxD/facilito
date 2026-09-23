from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from ...database import get_db
from ...models.insumo import Insumo
from ...models.precio_insumo import PrecioInsumo
from ...models.proveedor import Proveedor
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user
from ...schemas.insumo import InsumoCreate, InsumoOut, InsumoUpdate, PrecioInsumoCreate, PrecioInsumoOut, PrecioInsumoUpdate, ProveedorCreate, ProveedorOut, ProveedorUpdate
from ...audit import registrar

router = APIRouter(tags=["insumos"])


def check_espacio_access(espacio_id: uuid.UUID, current_user: Usuario, db: Session):
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if current_user.rol != "superadmin" and current_user.empresa_id != espacio.empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return espacio


def build_insumo_out(insumo: Insumo) -> dict:
    precios = [p for p in insumo.precios if p.activo]
    precio_minimo = min((p.precio_unitario for p in precios), default=None)
    alerta_stock = (
        insumo.stock_minimo is not None
        and insumo.stock_actual is not None
        and float(insumo.stock_actual) < float(insumo.stock_minimo)
    )
    precios_out = []
    for p in precios:
        precios_out.append({
            "id": p.id,
            "proveedor_id": p.proveedor_id,
            "proveedor_nombre": p.proveedor.nombre if p.proveedor else None,
            "precio_presentacion": p.precio_presentacion,
            "unidades_por_presentacion": p.unidades_por_presentacion,
            "precio_unitario": p.precio_unitario,
            "descripcion_presentacion": p.descripcion_presentacion,
            "fuente_url": p.fuente_url,
            "fecha_precio": p.fecha_precio,
            "activo": p.activo,
        })
    return {
        "id": insumo.id,
        "espacio_id": insumo.espacio_id,
        "nombre": insumo.nombre,
        "categoria": insumo.categoria,
        "unidad_medida": insumo.unidad_medida,
        "invima": insumo.invima,
        "stock_actual": insumo.stock_actual,
        "stock_minimo": insumo.stock_minimo,
        "activo": insumo.activo,
        "alerta_stock": alerta_stock,
        "precio_minimo": precio_minimo,
        "precio_venta": insumo.precio_venta,
        "precios": precios_out,
    }


def _precio_out(precio: PrecioInsumo) -> dict:
    return {
        "id": precio.id,
        "proveedor_id": precio.proveedor_id,
        "proveedor_nombre": precio.proveedor.nombre if precio.proveedor else None,
        "precio_presentacion": precio.precio_presentacion,
        "unidades_por_presentacion": precio.unidades_por_presentacion,
        "precio_unitario": precio.precio_unitario,
        "descripcion_presentacion": precio.descripcion_presentacion,
        "fuente_url": precio.fuente_url,
        "fecha_precio": precio.fecha_precio,
        "activo": precio.activo,
    }


@router.get("/espacios/{espacio_id}/insumos", response_model=List[InsumoOut])
def list_insumos(espacio_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    insumos = db.query(Insumo).filter(Insumo.espacio_id == espacio_id, Insumo.activo == True).all()
    return [build_insumo_out(i) for i in insumos]


@router.post("/espacios/{espacio_id}/insumos", response_model=InsumoOut)
def create_insumo(espacio_id: uuid.UUID, data: InsumoCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    precios_data = data.precios or []
    insumo_data = data.model_dump(exclude={"precios"})
    insumo = Insumo(espacio_id=espacio_id, **insumo_data)
    db.add(insumo)
    db.flush()
    for p in precios_data:
        precio = PrecioInsumo(insumo_id=insumo.id, **p.model_dump())
        db.add(precio)
    registrar(db, espacio_id, current_user, "insumo", data.nombre, "crear",
              f"Insumo creado: {data.nombre}")
    db.commit()
    db.refresh(insumo)
    return build_insumo_out(insumo)


@router.get("/insumos/{insumo_id}", response_model=InsumoOut)
def get_insumo(insumo_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    check_espacio_access(insumo.espacio_id, current_user, db)
    return build_insumo_out(insumo)


@router.put("/insumos/{insumo_id}", response_model=InsumoOut)
def update_insumo(insumo_id: uuid.UUID, data: InsumoUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    check_espacio_access(insumo.espacio_id, current_user, db)

    cambios = data.model_dump(exclude_none=True)
    descripciones = []
    if "stock_actual" in cambios:
        descripciones.append(f"Stock: {float(insumo.stock_actual or 0):.0f} → {float(cambios['stock_actual']):.0f} {insumo.unidad_medida or ''}")
    if "nombre" in cambios:
        descripciones.append(f"Nombre: {insumo.nombre} → {cambios['nombre']}")
    if "stock_minimo" in cambios:
        descripciones.append(f"Stock mínimo: {float(insumo.stock_minimo or 0):.0f} → {float(cambios['stock_minimo']):.0f}")
    otros = [k for k in cambios if k not in ("stock_actual", "nombre", "stock_minimo", "activo")]
    if otros:
        descripciones.append(f"Campos actualizados: {', '.join(otros)}")

    for field, value in cambios.items():
        setattr(insumo, field, value)

    accion = "eliminar" if cambios.get("activo") is False else "editar"
    desc = "; ".join(descripciones) if descripciones else f"Insumo {'eliminado' if accion == 'eliminar' else 'actualizado'}: {insumo.nombre}"
    registrar(db, insumo.espacio_id, current_user, "insumo", insumo.nombre, accion, desc)
    db.commit()
    db.refresh(insumo)
    return build_insumo_out(insumo)


@router.delete("/insumos/{insumo_id}")
def delete_insumo(insumo_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    check_espacio_access(insumo.espacio_id, current_user, db)
    insumo.activo = False
    registrar(db, insumo.espacio_id, current_user, "insumo", insumo.nombre, "eliminar",
              f"Insumo eliminado: {insumo.nombre}")
    db.commit()
    return {"ok": True}


@router.post("/insumos/{insumo_id}/precios", response_model=PrecioInsumoOut)
def add_precio(insumo_id: uuid.UUID, data: PrecioInsumoCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    check_espacio_access(insumo.espacio_id, current_user, db)
    precio = PrecioInsumo(insumo_id=insumo_id, **data.model_dump())
    db.add(precio)
    db.flush()
    prov_nombre = precio.proveedor.nombre if precio.proveedor else str(data.proveedor_id)
    registrar(db, insumo.espacio_id, current_user, "precio", insumo.nombre, "crear",
              f"Precio agregado en {insumo.nombre} — Proveedor: {prov_nombre}, ${float(data.precio_presentacion):,.0f}")
    db.commit()
    db.refresh(precio)
    return _precio_out(precio)


@router.get("/espacios/{espacio_id}/proveedores", response_model=List[ProveedorOut])
def list_proveedores(espacio_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    return db.query(Proveedor).filter(Proveedor.espacio_id == espacio_id).all()


@router.post("/espacios/{espacio_id}/proveedores", response_model=ProveedorOut)
def create_proveedor(espacio_id: uuid.UUID, data: ProveedorCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    proveedor = Proveedor(espacio_id=espacio_id, **data.model_dump())
    db.add(proveedor)
    registrar(db, espacio_id, current_user, "proveedor", data.nombre, "crear",
              f"Proveedor creado: {data.nombre}")
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.get("/espacios/{espacio_id}/alertas-stock", response_model=List[InsumoOut])
def alertas_stock(espacio_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    insumos = db.query(Insumo).filter(Insumo.espacio_id == espacio_id, Insumo.activo == True).all()
    alertas = [build_insumo_out(i) for i in insumos if float(i.stock_actual or 0) < float(i.stock_minimo or 0)]
    return alertas


@router.put("/precios/{precio_id}", response_model=PrecioInsumoOut)
def update_precio(precio_id: uuid.UUID, data: PrecioInsumoUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    precio = db.query(PrecioInsumo).filter(PrecioInsumo.id == precio_id).first()
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    check_espacio_access(precio.insumo.espacio_id, current_user, db)

    cambios = data.model_dump(exclude_none=True)
    descripciones = []
    if "precio_presentacion" in cambios:
        descripciones.append(f"${float(precio.precio_presentacion):,.0f} → ${float(cambios['precio_presentacion']):,.0f}")
    if "unidades_por_presentacion" in cambios:
        descripciones.append(f"Unidades: {precio.unidades_por_presentacion} → {cambios['unidades_por_presentacion']}")

    for field, value in cambios.items():
        setattr(precio, field, value)

    prov_nombre = precio.proveedor.nombre if precio.proveedor else "?"
    desc = f"Precio de {prov_nombre} en {precio.insumo.nombre} actualizado"
    if descripciones:
        desc += ": " + "; ".join(descripciones)
    registrar(db, precio.insumo.espacio_id, current_user, "precio", precio.insumo.nombre, "editar", desc)
    db.commit()
    db.refresh(precio)
    return _precio_out(precio)


@router.delete("/precios/{precio_id}")
def delete_precio(precio_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    precio = db.query(PrecioInsumo).filter(PrecioInsumo.id == precio_id).first()
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    check_espacio_access(precio.insumo.espacio_id, current_user, db)
    prov_nombre = precio.proveedor.nombre if precio.proveedor else "?"
    insumo_nombre = precio.insumo.nombre
    espacio_id = precio.insumo.espacio_id
    precio.activo = False
    registrar(db, espacio_id, current_user, "precio", insumo_nombre, "eliminar",
              f"Precio de {prov_nombre} eliminado en {insumo_nombre}")
    db.commit()
    return {"ok": True}


@router.put("/proveedores/{proveedor_id}", response_model=ProveedorOut)
def update_proveedor(proveedor_id: uuid.UUID, data: ProveedorUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    check_espacio_access(proveedor.espacio_id, current_user, db)
    nombre_anterior = proveedor.nombre
    proveedor.nombre = data.nombre
    registrar(db, proveedor.espacio_id, current_user, "proveedor", data.nombre, "editar",
              f"Proveedor renombrado: {nombre_anterior} → {data.nombre}")
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.delete("/proveedores/{proveedor_id}")
def delete_proveedor(proveedor_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    check_espacio_access(proveedor.espacio_id, current_user, db)
    nombre = proveedor.nombre
    espacio_id = proveedor.espacio_id
    db.delete(proveedor)
    registrar(db, espacio_id, current_user, "proveedor", nombre, "eliminar",
              f"Proveedor eliminado: {nombre}")
    db.commit()
    return {"ok": True}

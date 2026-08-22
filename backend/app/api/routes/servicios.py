from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
import uuid
from ...database import get_db
from ...models.servicio import Servicio
from ...models.servicio_insumo import ServicioInsumo
from ...models.insumo import Insumo
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user
from ...schemas.servicio import ServicioCreate, ServicioOut, ServicioUpdate, CostoServicioOut
from ...audit import registrar

router = APIRouter(tags=["servicios"])


def check_espacio_access(espacio_id: uuid.UUID, current_user: Usuario, db: Session):
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if current_user.rol != "superadmin" and current_user.empresa_id != espacio.empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return espacio


def get_precio_minimo(insumo: Insumo) -> float:
    precios_activos = [p for p in insumo.precios if p.activo]
    if not precios_activos:
        return 0.0
    return min(p.precio_unitario for p in precios_activos)


def build_servicio_out(servicio: Servicio, db: Session) -> dict:
    insumos_out = []
    for si in servicio.insumos:
        insumo = si.insumo
        costo_unit = get_precio_minimo(insumo)
        costo_total = costo_unit * float(si.cantidad)
        insumos_out.append({
            "id": si.id,
            "insumo_id": si.insumo_id,
            "insumo_nombre": insumo.nombre if insumo else None,
            "cantidad": si.cantidad,
            "notas": si.notas,
            "costo_unitario": costo_unit,
            "costo_total": costo_total,
        })
    return {
        "id": servicio.id,
        "espacio_id": servicio.espacio_id,
        "nombre": servicio.nombre,
        "descripcion": servicio.descripcion,
        "precio_mercado_referencia": servicio.precio_mercado_referencia,
        "url_referencia_precio": servicio.url_referencia_precio,
        "margen_ganancia_pct": servicio.margen_ganancia_pct,
        "activo": servicio.activo,
        "insumos": insumos_out,
    }


@router.get("/espacios/{espacio_id}/servicios", response_model=List[ServicioOut])
def list_servicios(espacio_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    servicios = db.query(Servicio).filter(Servicio.espacio_id == espacio_id, Servicio.activo == True).all()
    return [build_servicio_out(s, db) for s in servicios]


@router.post("/espacios/{espacio_id}/servicios", response_model=ServicioOut)
def create_servicio(espacio_id: uuid.UUID, data: ServicioCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    insumos_data = data.insumos or []
    servicio_data = data.model_dump(exclude={"insumos"})
    servicio = Servicio(espacio_id=espacio_id, **servicio_data)
    db.add(servicio)
    db.flush()
    for item in insumos_data:
        si = ServicioInsumo(servicio_id=servicio.id, **item.model_dump())
        db.add(si)
    registrar(db, espacio_id, current_user, "servicio", data.nombre, "crear",
              f"Servicio creado: {data.nombre} ({len(insumos_data)} insumos)")
    db.commit()
    db.refresh(servicio)
    return build_servicio_out(servicio, db)


@router.get("/servicios/{servicio_id}", response_model=ServicioOut)
def get_servicio(servicio_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    check_espacio_access(servicio.espacio_id, current_user, db)
    return build_servicio_out(servicio, db)


@router.put("/servicios/{servicio_id}", response_model=ServicioOut)
def update_servicio(servicio_id: uuid.UUID, data: ServicioUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    check_espacio_access(servicio.espacio_id, current_user, db)

    insumos_data = data.insumos
    update_fields = data.model_dump(exclude={"insumos"}, exclude_none=True)
    for field, value in update_fields.items():
        setattr(servicio, field, value)

    if insumos_data is not None:
        db.query(ServicioInsumo).filter(ServicioInsumo.servicio_id == servicio.id).delete(synchronize_session="fetch")
        db.flush()
        for item in insumos_data:
            si = ServicioInsumo(servicio_id=servicio.id, **item.model_dump())
            db.add(si)

    accion = "eliminar" if update_fields.get("activo") is False else "editar"
    desc = f"Servicio {'eliminado' if accion == 'eliminar' else 'actualizado'}: {servicio.nombre}"
    if insumos_data is not None and accion != "eliminar":
        desc += f" ({len(insumos_data)} insumos)"
    registrar(db, servicio.espacio_id, current_user, "servicio", servicio.nombre, accion, desc)
    db.commit()
    db.refresh(servicio)
    return build_servicio_out(servicio, db)


@router.get("/servicios/{servicio_id}/costo", response_model=CostoServicioOut)
def costo_servicio(servicio_id: uuid.UUID, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    check_espacio_access(servicio.espacio_id, current_user, db)

    insumos_out = []
    costo_total = 0.0
    for si in servicio.insumos:
        insumo = si.insumo
        costo_unit = get_precio_minimo(insumo)
        costo_item = costo_unit * float(si.cantidad)
        costo_total += costo_item
        insumos_out.append({
            "id": si.id,
            "insumo_id": si.insumo_id,
            "insumo_nombre": insumo.nombre if insumo else None,
            "cantidad": si.cantidad,
            "notas": si.notas,
            "costo_unitario": costo_unit,
            "costo_total": costo_item,
        })

    margen = float(servicio.margen_ganancia_pct or 30)
    precio_sugerido = costo_total * (1 + margen / 100)
    precio_mercado = float(servicio.precio_mercado_referencia) if servicio.precio_mercado_referencia else None
    margen_real = ((precio_mercado - costo_total) / costo_total * 100) if precio_mercado and costo_total > 0 else None

    return {
        "servicio_id": servicio.id,
        "nombre": servicio.nombre,
        "costo_insumos": costo_total,
        "margen_ganancia_pct": margen,
        "precio_sugerido": precio_sugerido,
        "precio_mercado_referencia": precio_mercado,
        "margen_real_pct": margen_real,
        "insumos": insumos_out,
    }


@router.get("/espacios/{espacio_id}/reporte-costos")
def reporte_costos(espacio_id: uuid.UUID, formato: str = "json", current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    check_espacio_access(espacio_id, current_user, db)
    servicios = db.query(Servicio).filter(Servicio.espacio_id == espacio_id, Servicio.activo == True).all()

    reporte = []
    for servicio in servicios:
        costo_total = 0.0
        for si in servicio.insumos:
            costo_unit = get_precio_minimo(si.insumo)
            costo_total += costo_unit * float(si.cantidad)
        margen = float(servicio.margen_ganancia_pct or 30)
        precio_sugerido = costo_total * (1 + margen / 100)
        reporte.append({
            "nombre": servicio.nombre,
            "costo_insumos": round(costo_total, 2),
            "margen_pct": margen,
            "precio_sugerido": round(precio_sugerido, 2),
            "precio_mercado": float(servicio.precio_mercado_referencia) if servicio.precio_mercado_referencia else None,
        })

    if formato == "excel":
        import openpyxl
        from io import BytesIO
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte de Costos"
        headers = ["Servicio", "Costo Insumos (COP)", "Margen %", "Precio Sugerido (COP)", "Precio Mercado (COP)"]
        ws.append(headers)
        for row in reporte:
            ws.append([row["nombre"], row["costo_insumos"], row["margen_pct"], row["precio_sugerido"], row["precio_mercado"]])
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return Response(
            content=buf.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=reporte_costos.xlsx"},
        )

    return reporte

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal
import uuid

from ...database import get_db
from ...models.venta import Venta, VentaItem
from ...models.insumo import Insumo
from ...models.servicio import Servicio
from ...models.caja import MovimientoCaja
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user
from ...audit import registrar
from ...schemas.venta import (
    VentaCreate, VentaAnular, RegistrarPago, VentaOut, AlertaVenta, ResumenVentas,
)

router = APIRouter(tags=["ventas"])

CERO = Decimal("0")

# Margen que se sugiere cuando un producto no tiene precio de venta propio.
MARGEN_POR_DEFECTO = Decimal("40")

# Una venta a credito pasado este plazo se marca como cobro vencido.
DIAS_PAGO_VENCIDO = 30

# Diferencia que se tolera antes de considerar que se cobro fuera de lista.
TOLERANCIA_PRECIO = Decimal("1")


def check_espacio_access(espacio_id: uuid.UUID, current_user: Usuario, db: Session) -> Espacio:
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if current_user.rol != "superadmin" and current_user.empresa_id != espacio.empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return espacio


def costo_insumo(insumo: Insumo) -> Decimal:
    """Costo unitario: el menor precio activo entre los proveedores."""
    activos = [p for p in insumo.precios if p.activo]
    if not activos:
        return CERO
    return Decimal(str(min(p.precio_unitario for p in activos)))


def precio_sugerido_insumo(insumo: Insumo) -> Decimal:
    if insumo.precio_venta is not None:
        return Decimal(str(insumo.precio_venta))
    return (costo_insumo(insumo) * (1 + MARGEN_POR_DEFECTO / 100)).quantize(Decimal("1"))


def costo_servicio(servicio: Servicio) -> Decimal:
    return sum(
        (costo_insumo(si.insumo) * Decimal(str(si.cantidad)) for si in servicio.insumos),
        CERO,
    )


def precio_sugerido_servicio(servicio: Servicio) -> Decimal:
    margen = Decimal(str(servicio.margen_ganancia_pct or MARGEN_POR_DEFECTO))
    return (costo_servicio(servicio) * (1 + margen / 100)).quantize(Decimal("1"))


def calcular_alertas(venta: Venta) -> List[AlertaVenta]:
    """Senala lo que no encaja. Nunca corrige el dato: la venta queda como ocurrio."""
    alertas: List[AlertaVenta] = []

    for item in venta.items:
        if item.precio_sugerido is None:
            continue
        cobrado = Decimal(str(item.precio_unitario))
        sugerido = Decimal(str(item.precio_sugerido))
        diferencia = cobrado - sugerido
        if abs(diferencia) > TOLERANCIA_PRECIO:
            sentido = "por encima" if diferencia > 0 else "por debajo"
            alertas.append(AlertaVenta(
                tipo="precio_fuera_de_lista",
                severidad="media" if diferencia > 0 else "alta",
                mensaje=(
                    f"{item.descripcion}: se cobro ${cobrado:,.0f} y la lista dice "
                    f"${sugerido:,.0f} ({sentido} por ${abs(diferencia):,.0f})"
                ),
            ))

    if not venta.anulada and venta.estado_pago == "pendiente":
        dias = (date.today() - venta.fecha).days
        if dias > DIAS_PAGO_VENCIDO:
            alertas.append(AlertaVenta(
                tipo="pago_vencido",
                severidad="alta",
                mensaje=f"Sin pagar desde hace {dias} dias",
            ))

    return alertas


def armar_venta_out(venta: Venta) -> dict:
    total = Decimal(str(venta.total))
    costo = Decimal(str(venta.costo_total))
    return {
        "id": venta.id,
        "fecha": venta.fecha,
        "cliente": venta.cliente,
        "notas": venta.notas,
        "estado_pago": venta.estado_pago,
        "fecha_pago": venta.fecha_pago,
        "total": total,
        "costo_total": costo,
        "utilidad": total - costo,
        "anulada": venta.anulada,
        "motivo_anulacion": venta.motivo_anulacion,
        "usuario_email": venta.usuario_email,
        "created_at": venta.created_at,
        "items": venta.items,
        "alertas": calcular_alertas(venta),
    }


def mover_stock(db: Session, item: VentaItem, signo: int) -> None:
    """Descuenta (signo -1) o devuelve (signo +1) el stock que la linea consume."""
    if item.insumo_id:
        insumo = db.query(Insumo).filter(Insumo.id == item.insumo_id).first()
        if insumo:
            insumo.stock_actual = Decimal(str(insumo.stock_actual or 0)) + signo * Decimal(str(item.cantidad))
    elif item.servicio_id:
        servicio = db.query(Servicio).filter(Servicio.id == item.servicio_id).first()
        if servicio:
            for componente in servicio.insumos:
                consumo = Decimal(str(componente.cantidad)) * Decimal(str(item.cantidad))
                componente.insumo.stock_actual = (
                    Decimal(str(componente.insumo.stock_actual or 0)) + signo * consumo
                )


# ---------------------------------------------------------------- consultas

@router.get("/espacios/{espacio_id}/ventas", response_model=List[VentaOut])
def listar_ventas(
    espacio_id: uuid.UUID,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    estado_pago: Optional[str] = None,
    incluir_anuladas: bool = True,
    limit: int = Query(200, le=1000),
    offset: int = 0,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)
    q = db.query(Venta).filter(Venta.espacio_id == espacio_id)
    if desde:
        q = q.filter(Venta.fecha >= desde)
    if hasta:
        q = q.filter(Venta.fecha <= hasta)
    if estado_pago:
        q = q.filter(Venta.estado_pago == estado_pago)
    if not incluir_anuladas:
        q = q.filter(Venta.anulada == False)
    ventas = (
        q.order_by(Venta.fecha.desc(), Venta.created_at.desc())
        .offset(offset).limit(limit).all()
    )
    return [armar_venta_out(v) for v in ventas]


@router.get("/espacios/{espacio_id}/ventas/resumen", response_model=ResumenVentas)
def resumen_ventas(
    espacio_id: uuid.UUID,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)
    ventas = db.query(Venta).filter(
        Venta.espacio_id == espacio_id, Venta.anulada == False
    ).all()

    total = sum((Decimal(str(v.total)) for v in ventas), CERO)
    costo = sum((Decimal(str(v.costo_total)) for v in ventas), CERO)
    pendientes = [v for v in ventas if v.estado_pago == "pendiente"]
    utilidad = total - costo

    return ResumenVentas(
        total_vendido=total,
        total_costo=costo,
        utilidad=utilidad,
        margen_pct=float(utilidad / total * 100) if total > 0 else None,
        cantidad_ventas=len(ventas),
        por_cobrar=sum((Decimal(str(v.total)) for v in pendientes), CERO),
        ventas_pendientes=len(pendientes),
        ventas_con_alertas=sum(1 for v in ventas if calcular_alertas(v)),
    )


# ---------------------------------------------------------------- registro

@router.post("/espacios/{espacio_id}/ventas", response_model=VentaOut)
def crear_venta(
    espacio_id: uuid.UUID,
    data: VentaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registra una venta: descuenta stock y, si esta pagada, suma el ingreso a caja.

    Se permite vender por encima del stock disponible y a un precio distinto al de
    lista. Ambas cosas quedan senaladas, no bloqueadas: el registro debe poder
    reflejar lo que de verdad paso en el mostrador.
    """
    check_espacio_access(espacio_id, current_user, db)
    if data.estado_pago not in ("pagado", "pendiente"):
        raise HTTPException(status_code=422, detail="El estado de pago debe ser 'pagado' o 'pendiente'")
    if not data.items:
        raise HTTPException(status_code=422, detail="La venta debe tener al menos un producto")

    venta = Venta(
        espacio_id=espacio_id,
        fecha=data.fecha,
        cliente=data.cliente,
        notas=data.notas,
        estado_pago=data.estado_pago,
        fecha_pago=data.fecha if data.estado_pago == "pagado" else None,
        usuario_email=current_user.email,
        total=CERO,
        costo_total=CERO,
    )
    db.add(venta)
    db.flush()

    total = CERO
    costo_total = CERO
    sin_stock: List[str] = []

    for entrada in data.items:
        if entrada.cantidad <= 0:
            raise HTTPException(status_code=422, detail="La cantidad debe ser mayor que cero")
        if bool(entrada.insumo_id) == bool(entrada.servicio_id):
            raise HTTPException(status_code=422, detail="Cada linea debe ser un producto o un combo, no ambos")

        if entrada.insumo_id:
            insumo = db.query(Insumo).filter(Insumo.id == entrada.insumo_id).first()
            if not insumo or insumo.espacio_id != espacio_id:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            descripcion = insumo.nombre
            costo_unit = costo_insumo(insumo)
            sugerido = precio_sugerido_insumo(insumo)
            disponible = Decimal(str(insumo.stock_actual or 0))
            if disponible < entrada.cantidad:
                sin_stock.append(f"{insumo.nombre} (habia {disponible:g}, se vendieron {entrada.cantidad:g})")
        else:
            servicio = db.query(Servicio).filter(Servicio.id == entrada.servicio_id).first()
            if not servicio or servicio.espacio_id != espacio_id:
                raise HTTPException(status_code=404, detail="Combo no encontrado")
            descripcion = servicio.nombre
            costo_unit = costo_servicio(servicio)
            sugerido = precio_sugerido_servicio(servicio)

        precio = entrada.precio_unitario if entrada.precio_unitario is not None else sugerido
        if precio < 0:
            raise HTTPException(status_code=422, detail="El precio no puede ser negativo")

        subtotal = (precio * entrada.cantidad).quantize(Decimal("0.01"))
        item = VentaItem(
            venta_id=venta.id,
            insumo_id=entrada.insumo_id,
            servicio_id=entrada.servicio_id,
            descripcion=descripcion,
            cantidad=entrada.cantidad,
            precio_unitario=precio,
            precio_sugerido=sugerido,
            costo_unitario=costo_unit,
            subtotal=subtotal,
        )
        db.add(item)
        db.flush()
        mover_stock(db, item, -1)

        total += subtotal
        costo_total += (costo_unit * entrada.cantidad).quantize(Decimal("0.01"))

    venta.total = total
    venta.costo_total = costo_total

    if data.estado_pago == "pagado":
        db.add(MovimientoCaja(
            espacio_id=espacio_id,
            fecha=data.fecha,
            tipo="ingreso",
            categoria="venta",
            concepto=f"Venta{' a ' + data.cliente if data.cliente else ''}",
            monto=total,
            referencia_tipo="venta",
            referencia_id=venta.id,
            usuario_email=current_user.email,
        ))

    detalle = (
        f"Venta de ${total:,.0f} ({len(data.items)} lineas)"
        f"{' a ' + data.cliente if data.cliente else ''}, {data.estado_pago}"
    )
    if sin_stock:
        detalle += ". Se vendio sin stock suficiente: " + "; ".join(sin_stock)
    registrar(db, espacio_id, current_user, "venta", data.cliente or "Venta", "crear", detalle)

    db.commit()
    db.refresh(venta)
    return armar_venta_out(venta)


@router.post("/ventas/{venta_id}/anular", response_model=VentaOut)
def anular_venta(
    venta_id: uuid.UUID,
    data: VentaAnular,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Anula una venta: devuelve el stock y revierte el ingreso, sin borrar nada."""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    check_espacio_access(venta.espacio_id, current_user, db)
    if venta.anulada:
        raise HTTPException(status_code=409, detail="La venta ya estaba anulada")

    for item in venta.items:
        mover_stock(db, item, +1)

    movimiento = db.query(MovimientoCaja).filter(
        MovimientoCaja.referencia_tipo == "venta",
        MovimientoCaja.referencia_id == venta.id,
        MovimientoCaja.anulado == False,
    ).first()
    if movimiento:
        movimiento.anulado = True
        movimiento.motivo_anulacion = f"Venta anulada: {data.motivo}"

    venta.anulada = True
    venta.motivo_anulacion = data.motivo

    registrar(
        db, venta.espacio_id, current_user, "venta", venta.cliente or "Venta", "anular",
        f"Se anulo la venta de ${Decimal(str(venta.total)):,.0f} del {venta.fecha}. "
        f"Se devolvio el stock. Motivo: {data.motivo}",
    )
    db.commit()
    db.refresh(venta)
    return armar_venta_out(venta)


@router.post("/ventas/{venta_id}/registrar-pago", response_model=VentaOut)
def registrar_pago(
    venta_id: uuid.UUID,
    data: RegistrarPago,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marca como pagada una venta a credito y suma el ingreso a caja."""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    check_espacio_access(venta.espacio_id, current_user, db)
    if venta.anulada:
        raise HTTPException(status_code=409, detail="La venta esta anulada")
    if venta.estado_pago == "pagado":
        raise HTTPException(status_code=409, detail="La venta ya estaba pagada")

    venta.estado_pago = "pagado"
    venta.fecha_pago = data.fecha_pago

    db.add(MovimientoCaja(
        espacio_id=venta.espacio_id,
        fecha=data.fecha_pago,
        tipo="ingreso",
        categoria="venta",
        concepto=f"Pago de venta{' de ' + venta.cliente if venta.cliente else ''} del {venta.fecha}",
        monto=Decimal(str(venta.total)),
        referencia_tipo="venta",
        referencia_id=venta.id,
        usuario_email=current_user.email,
    ))

    registrar(
        db, venta.espacio_id, current_user, "venta", venta.cliente or "Venta", "editar",
        f"Se registro el pago de ${Decimal(str(venta.total)):,.0f} "
        f"por la venta del {venta.fecha}",
    )
    db.commit()
    db.refresh(venta)
    return armar_venta_out(venta)

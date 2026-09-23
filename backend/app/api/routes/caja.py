from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal
import uuid

from ...database import get_db
from ...models.caja import MovimientoCaja, Prestamo, AbonoPrestamo, ArqueoCaja
from ...models.espacio import Espacio
from ...models.usuario import Usuario
from ...auth import get_current_user
from ...audit import registrar
from ...schemas.caja import (
    MovimientoCreate, MovimientoAnular, MovimientoOut,
    PrestamoCreate, PrestamoUpdate, PrestamoOut, AbonoCreate,
    ArqueoCreate, ArqueoOut,
    ResumenCaja, AlertaCaja,
)

router = APIRouter(tags=["caja"])

CERO = Decimal("0")

# Un prestamo sin ningun abono pasado este plazo se marca como alerta.
DIAS_PRESTAMO_SIN_ABONO = 30


def check_espacio_access(espacio_id: uuid.UUID, current_user: Usuario, db: Session) -> Espacio:
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    if current_user.rol != "superadmin" and current_user.empresa_id != espacio.empresa_id:
        raise HTTPException(status_code=403, detail="Sin acceso")
    return espacio


def calcular_saldo_teorico(db: Session, espacio_id: uuid.UUID) -> Decimal:
    """Ingresos menos egresos, ignorando los movimientos anulados."""
    filas = (
        db.query(MovimientoCaja.tipo, func.coalesce(func.sum(MovimientoCaja.monto), 0))
        .filter(MovimientoCaja.espacio_id == espacio_id, MovimientoCaja.anulado == False)
        .group_by(MovimientoCaja.tipo)
        .all()
    )
    totales = {tipo: Decimal(str(total)) for tipo, total in filas}
    return totales.get("ingreso", CERO) - totales.get("egreso", CERO)


def armar_prestamo_out(prestamo: Prestamo) -> dict:
    total_abonado = sum((Decimal(str(a.monto)) for a in prestamo.abonos), CERO)
    monto = Decimal(str(prestamo.monto))
    return {
        "id": prestamo.id,
        "fecha": prestamo.fecha,
        "deudor": prestamo.deudor,
        "concepto": prestamo.concepto,
        "monto": monto,
        "notas": prestamo.notas,
        "activo": prestamo.activo,
        "total_abonado": total_abonado,
        "saldo": monto - total_abonado,
        "abonos": sorted(prestamo.abonos, key=lambda a: a.fecha),
        "created_at": prestamo.created_at,
    }


# ---------------------------------------------------------------- resumen

@router.get("/espacios/{espacio_id}/caja/resumen", response_model=ResumenCaja)
def resumen_caja(
    espacio_id: uuid.UUID,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)

    filas = (
        db.query(MovimientoCaja.tipo, func.coalesce(func.sum(MovimientoCaja.monto), 0))
        .filter(MovimientoCaja.espacio_id == espacio_id, MovimientoCaja.anulado == False)
        .group_by(MovimientoCaja.tipo)
        .all()
    )
    totales = {tipo: Decimal(str(total)) for tipo, total in filas}
    ingresos = totales.get("ingreso", CERO)
    egresos = totales.get("egreso", CERO)
    saldo_teorico = ingresos - egresos

    prestamos = (
        db.query(Prestamo)
        .filter(Prestamo.espacio_id == espacio_id, Prestamo.activo == True)
        .all()
    )
    total_prestado = sum((Decimal(str(p.monto)) for p in prestamos), CERO)
    total_abonado = sum(
        (Decimal(str(a.monto)) for p in prestamos for a in p.abonos), CERO
    )

    ultimo_arqueo = (
        db.query(ArqueoCaja)
        .filter(ArqueoCaja.espacio_id == espacio_id)
        .order_by(ArqueoCaja.fecha.desc(), ArqueoCaja.created_at.desc())
        .first()
    )

    # --- Alertas: se senalan, no se corrigen ---
    alertas: List[AlertaCaja] = []

    if ultimo_arqueo and Decimal(str(ultimo_arqueo.diferencia)) != CERO:
        dif = Decimal(str(ultimo_arqueo.diferencia))
        sobra = dif > CERO
        alertas.append(AlertaCaja(
            tipo="descuadre",
            severidad="alta",
            mensaje=f"El ultimo arqueo no cuadra: {'sobran' if sobra else 'faltan'} ${abs(dif):,.0f}",
            detalle=(
                f"Arqueo del {ultimo_arqueo.fecha}: se contaron ${Decimal(str(ultimo_arqueo.efectivo_contado)):,.0f} "
                f"frente a ${Decimal(str(ultimo_arqueo.saldo_teorico)):,.0f} esperados."
            ),
        ))

    if saldo_teorico < CERO:
        alertas.append(AlertaCaja(
            tipo="saldo_negativo",
            severidad="alta",
            mensaje=f"El saldo de caja es negativo: ${saldo_teorico:,.0f}",
            detalle="Hay mas egresos que ingresos registrados. Puede faltar registrar ingresos.",
        ))

    limite = date.today() - timedelta(days=DIAS_PRESTAMO_SIN_ABONO)
    for p in prestamos:
        saldo = Decimal(str(p.monto)) - sum((Decimal(str(a.monto)) for a in p.abonos), CERO)
        if saldo > CERO and not p.abonos and p.fecha <= limite:
            dias = (date.today() - p.fecha).days
            alertas.append(AlertaCaja(
                tipo="prestamo_sin_abonos",
                severidad="media",
                mensaje=f"{p.deudor} no ha abonado nada en {dias} dias",
                detalle=f"Prestamo del {p.fecha} por ${Decimal(str(p.monto)):,.0f}. Saldo pendiente: ${saldo:,.0f}.",
            ))

    return ResumenCaja(
        total_ingresos=ingresos,
        total_egresos=egresos,
        saldo_teorico=saldo_teorico,
        total_prestado=total_prestado,
        total_abonado=total_abonado,
        saldo_por_cobrar=total_prestado - total_abonado,
        ultimo_arqueo=ultimo_arqueo,
        alertas=alertas,
    )


# ---------------------------------------------------------------- movimientos

@router.get("/espacios/{espacio_id}/caja/movimientos", response_model=List[MovimientoOut])
def listar_movimientos(
    espacio_id: uuid.UUID,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    tipo: Optional[str] = None,
    categoria: Optional[str] = None,
    incluir_anulados: bool = True,
    limit: int = Query(200, le=1000),
    offset: int = 0,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)
    q = db.query(MovimientoCaja).filter(MovimientoCaja.espacio_id == espacio_id)
    if desde:
        q = q.filter(MovimientoCaja.fecha >= desde)
    if hasta:
        q = q.filter(MovimientoCaja.fecha <= hasta)
    if tipo:
        q = q.filter(MovimientoCaja.tipo == tipo)
    if categoria:
        q = q.filter(MovimientoCaja.categoria == categoria)
    if not incluir_anulados:
        q = q.filter(MovimientoCaja.anulado == False)
    return (
        q.order_by(MovimientoCaja.fecha.desc(), MovimientoCaja.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post("/espacios/{espacio_id}/caja/movimientos", response_model=MovimientoOut)
def crear_movimiento(
    espacio_id: uuid.UUID,
    data: MovimientoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)
    if data.tipo not in ("ingreso", "egreso"):
        raise HTTPException(status_code=422, detail="El tipo debe ser 'ingreso' o 'egreso'")
    if data.monto <= 0:
        raise HTTPException(status_code=422, detail="El monto debe ser mayor que cero")

    mov = MovimientoCaja(
        espacio_id=espacio_id,
        usuario_email=current_user.email,
        **data.model_dump(),
    )
    db.add(mov)
    registrar(
        db, espacio_id, current_user, "caja", data.concepto, "crear",
        f"{data.tipo.capitalize()} de ${data.monto:,.0f} ({data.categoria}) el {data.fecha}",
    )
    db.commit()
    db.refresh(mov)
    return mov


@router.post("/caja/movimientos/{movimiento_id}/anular", response_model=MovimientoOut)
def anular_movimiento(
    movimiento_id: uuid.UUID,
    data: MovimientoAnular,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Anula un movimiento sin borrarlo: el hecho original queda en el historico."""
    mov = db.query(MovimientoCaja).filter(MovimientoCaja.id == movimiento_id).first()
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    check_espacio_access(mov.espacio_id, current_user, db)
    if mov.anulado:
        raise HTTPException(status_code=409, detail="El movimiento ya estaba anulado")

    mov.anulado = True
    mov.motivo_anulacion = data.motivo
    registrar(
        db, mov.espacio_id, current_user, "caja", mov.concepto, "anular",
        f"Se anulo el {mov.tipo} de ${Decimal(str(mov.monto)):,.0f} del {mov.fecha}. Motivo: {data.motivo}",
    )
    db.commit()
    db.refresh(mov)
    return mov


# ---------------------------------------------------------------- prestamos

@router.get("/espacios/{espacio_id}/caja/prestamos", response_model=List[PrestamoOut])
def listar_prestamos(
    espacio_id: uuid.UUID,
    solo_pendientes: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)
    prestamos = (
        db.query(Prestamo)
        .filter(Prestamo.espacio_id == espacio_id, Prestamo.activo == True)
        .order_by(Prestamo.fecha.desc())
        .all()
    )
    salida = [armar_prestamo_out(p) for p in prestamos]
    if solo_pendientes:
        salida = [p for p in salida if p["saldo"] > CERO]
    return salida


@router.post("/espacios/{espacio_id}/caja/prestamos", response_model=PrestamoOut)
def crear_prestamo(
    espacio_id: uuid.UUID,
    data: PrestamoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)
    if data.monto <= 0:
        raise HTTPException(status_code=422, detail="El monto debe ser mayor que cero")

    campos = data.model_dump(exclude={"afecta_caja"})
    prestamo = Prestamo(espacio_id=espacio_id, usuario_email=current_user.email, **campos)
    db.add(prestamo)
    db.flush()

    if data.afecta_caja:
        db.add(MovimientoCaja(
            espacio_id=espacio_id,
            fecha=data.fecha,
            tipo="egreso",
            categoria="prestamo",
            concepto=f"Prestamo a {data.deudor}" + (f" — {data.concepto}" if data.concepto else ""),
            monto=data.monto,
            referencia_tipo="prestamo",
            referencia_id=prestamo.id,
            usuario_email=current_user.email,
        ))

    registrar(
        db, espacio_id, current_user, "prestamo", data.deudor, "crear",
        f"Prestamo de ${data.monto:,.0f} a {data.deudor} el {data.fecha}",
    )
    db.commit()
    db.refresh(prestamo)
    return armar_prestamo_out(prestamo)


@router.put("/caja/prestamos/{prestamo_id}", response_model=PrestamoOut)
def actualizar_prestamo(
    prestamo_id: uuid.UUID,
    data: PrestamoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")
    check_espacio_access(prestamo.espacio_id, current_user, db)

    campos = data.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(prestamo, campo, valor)

    accion = "eliminar" if campos.get("activo") is False else "editar"
    registrar(
        db, prestamo.espacio_id, current_user, "prestamo", prestamo.deudor, accion,
        f"Prestamo {'dado de baja' if accion == 'eliminar' else 'actualizado'}: {prestamo.deudor}",
    )
    db.commit()
    db.refresh(prestamo)
    return armar_prestamo_out(prestamo)


@router.post("/caja/prestamos/{prestamo_id}/abonos", response_model=PrestamoOut)
def registrar_abono(
    prestamo_id: uuid.UUID,
    data: AbonoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")
    check_espacio_access(prestamo.espacio_id, current_user, db)
    if data.monto <= 0:
        raise HTTPException(status_code=422, detail="El monto debe ser mayor que cero")

    abono = AbonoPrestamo(
        prestamo_id=prestamo.id,
        fecha=data.fecha,
        monto=data.monto,
        notas=data.notas,
        usuario_email=current_user.email,
    )
    db.add(abono)
    db.flush()

    if data.afecta_caja:
        db.add(MovimientoCaja(
            espacio_id=prestamo.espacio_id,
            fecha=data.fecha,
            tipo="ingreso",
            categoria="abono",
            concepto=f"Abono de {prestamo.deudor}",
            monto=data.monto,
            referencia_tipo="abono",
            referencia_id=abono.id,
            usuario_email=current_user.email,
        ))

    registrar(
        db, prestamo.espacio_id, current_user, "prestamo", prestamo.deudor, "editar",
        f"Abono de ${data.monto:,.0f} recibido de {prestamo.deudor} el {data.fecha}",
    )
    db.commit()
    db.refresh(prestamo)
    return armar_prestamo_out(prestamo)


# ---------------------------------------------------------------- arqueos

@router.get("/espacios/{espacio_id}/caja/arqueos", response_model=List[ArqueoOut])
def listar_arqueos(
    espacio_id: uuid.UUID,
    limit: int = Query(50, le=200),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_espacio_access(espacio_id, current_user, db)
    return (
        db.query(ArqueoCaja)
        .filter(ArqueoCaja.espacio_id == espacio_id)
        .order_by(ArqueoCaja.fecha.desc(), ArqueoCaja.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/espacios/{espacio_id}/caja/arqueos", response_model=ArqueoOut)
def crear_arqueo(
    espacio_id: uuid.UUID,
    data: ArqueoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registra un conteo fisico de efectivo y deja constancia de la diferencia.

    La diferencia no se corrige automaticamente: queda registrada para que el
    usuario decida si la justifica con un movimiento de ajuste.
    """
    check_espacio_access(espacio_id, current_user, db)

    saldo_teorico = calcular_saldo_teorico(db, espacio_id)
    diferencia = data.efectivo_contado - saldo_teorico

    arqueo = ArqueoCaja(
        espacio_id=espacio_id,
        fecha=data.fecha,
        efectivo_contado=data.efectivo_contado,
        saldo_teorico=saldo_teorico,
        diferencia=diferencia,
        notas=data.notas,
        usuario_email=current_user.email,
    )
    db.add(arqueo)

    if diferencia == CERO:
        detalle = "El conteo cuadra con el saldo esperado."
    elif diferencia > CERO:
        detalle = f"Sobran ${diferencia:,.0f} frente al saldo esperado."
    else:
        detalle = f"Faltan ${abs(diferencia):,.0f} frente al saldo esperado."

    registrar(
        db, espacio_id, current_user, "arqueo", f"Arqueo del {data.fecha}", "crear",
        f"Contado ${data.efectivo_contado:,.0f}, esperado ${saldo_teorico:,.0f}. {detalle}",
    )
    db.commit()
    db.refresh(arqueo)
    return arqueo

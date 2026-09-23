"""Ambiente de demostracion: construccion y restauracion.

Los datos son ficticios a proposito. El catalogo de productos es comercial, pero
deudores y compradores no corresponden a ninguna persona real, porque cualquier
interesado puede entrar a esta cuenta.

Las fechas se calculan hacia atras desde el dia en que se siembra, de modo que al
restaurar la demo vuelve a verse reciente.
"""
import uuid
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from .models.empresa import Empresa
from .models.usuario import Usuario
from .models.espacio import Espacio
from .models.proveedor import Proveedor
from .models.insumo import Insumo
from .models.precio_insumo import PrecioInsumo
from .models.servicio import Servicio
from .models.servicio_insumo import ServicioInsumo
from .models.paquete import Paquete, PaqueteServicio
from .models.audit_log import AuditLog
from .models.caja import MovimientoCaja, Prestamo, AbonoPrestamo, ArqueoCaja
from .models.venta import Venta, VentaItem
from .auth import hash_password

EMAIL_DEMO = "demo@facilito.co"
PASSWORD_DEMO = "demo2026"
EMPRESA_DEMO = "Distribuidora Vital (Demo)"
ESPACIO_DEMO = "Punto de venta (Demo)"

# (nombre, presentacion, stock, stock_minimo, costo, precio_venta, proveedor)
# costo None deja el producto sin precio de compra, para que se vea esa alerta.
PRODUCTOS = [
    ("VitalPro",          "Polvo 300 g",     4, 2, 147000, 294000, "Importadora Andina"),
    ("V-NeuroKafe",       "Polvo 150 g",     6, 3, 105000, 210000, "Importadora Andina"),
    ("VitalAge Collagen", "Polvo 300 g",     3, 2, 122500, 245000, "Naturales del Valle"),
    ("V-Té Detox",        "Caja 20 sobres", 18, 6,  25600,  57000, "Naturales del Valle"),
    ("V-Control",         "60 cápsulas",     5, 3,  70000, 140000, "Importadora Andina"),
    ("V-Itadol",          "60 cápsulas",     1, 3,  70000, 140000, "Importadora Andina"),
    ("V-Daily",           "Polvo 150 g",     4, 2, 175000, 350000, "Distribuidora Central"),
    ("V-FortyFlora",      "60 cápsulas",     2, 3,  70000, 140000, "Naturales del Valle"),
    ("Genius Shake",      "Polvo 400 g",     3, 2, 175000, 350000, "Distribuidora Central"),
    ("V-Omega3",          "60 cápsulas",     7, 3,  84000, 168000, "Naturales del Valle"),
    ("V-Curcumax",        "60 cápsulas",     0, 3,  91000, 182000, "Importadora Andina"),
    ("V-Organex",         "60 cápsulas",     2, 2,   None, 160000, "Distribuidora Central"),
]

# (dias atras, cliente, estado_pago, [(producto, cantidad, precio cobrado o None)])
# Un precio distinto al de lista se conserva tal cual y la aplicacion lo senala.
VENTAS = [
    (26, "Laura Restrepo",  "pagado",    [("VitalPro", 1, None), ("V-Omega3", 1, None)]),
    (19, "Andrés Mejía",    "pagado",    [("V-Té Detox", 4, None)]),
    (12, "Carolina Ossa",   "pagado",    [("V-Daily", 1, 245000)]),
    (38, "Julián Betancur", "pendiente", [("Genius Shake", 1, None)]),
    (3,  "Sara Villa",      "pagado",    [("V-NeuroKafe", 2, None), ("V-Control", 1, None)]),
]

PROVEEDORES = ("Importadora Andina", "Naturales del Valle", "Distribuidora Central")

COMBOS = [
    ("Combo Energía",   "V-NeuroKafe + Genius Shake",        100, [("V-NeuroKafe", 1), ("Genius Shake", 1)]),
    ("Combo Detox",     "V-Té Detox + V-Control",            120, [("V-Té Detox", 2), ("V-Control", 1)]),
    ("Combo Bienestar", "V-Daily + V-Omega3 + V-FortyFlora",  90, [("V-Daily", 1), ("V-Omega3", 1), ("V-FortyFlora", 1)]),
]

# (dias atras, tipo, categoria, concepto, monto)
# Los ingresos por venta no van aqui: los genera cada venta al registrarse.
MOVIMIENTOS = [
    (45, "ingreso", "otro",   "Capital inicial del negocio",  3000000),
    (40, "egreso",  "compra", "Compra de inventario inicial", 2100000),
    (28, "egreso",  "gasto",  "Arriendo del local",            800000),
    (18, "egreso",  "gasto",  "Transporte y domicilios",        95000),
    (11, "egreso",  "compra", "Reposición de V-Omega3",        588000),
    (4,  "egreso",  "gasto",  "Servicios públicos",            140000),
]

DIFERENCIA_ARQUEO = Decimal(-35000)


def obtener_empresa_demo(db: Session) -> Empresa | None:
    usuario = db.query(Usuario).filter(Usuario.email == EMAIL_DEMO).first()
    if not usuario or not usuario.empresa_id:
        return None
    return db.query(Empresa).filter(Empresa.id == usuario.empresa_id).first()


def borrar_datos(db: Session, empresa_id: uuid.UUID) -> None:
    """Vacia el contenido de la empresa demo respetando las llaves foraneas.

    La empresa y el usuario se conservan para que las credenciales no cambien.
    """
    espacios = [e.id for e in db.query(Espacio).filter(Espacio.empresa_id == empresa_id).all()]
    if not espacios:
        return

    ventas = [v.id for v in db.query(Venta).filter(Venta.espacio_id.in_(espacios)).all()]
    if ventas:
        db.query(VentaItem).filter(VentaItem.venta_id.in_(ventas)).delete(synchronize_session=False)
        db.query(Venta).filter(Venta.id.in_(ventas)).delete(synchronize_session=False)

    paquetes = [p.id for p in db.query(Paquete).filter(Paquete.espacio_id.in_(espacios)).all()]
    if paquetes:
        db.query(PaqueteServicio).filter(PaqueteServicio.paquete_id.in_(paquetes)).delete(synchronize_session=False)
        db.query(Paquete).filter(Paquete.id.in_(paquetes)).delete(synchronize_session=False)

    servicios = [s.id for s in db.query(Servicio).filter(Servicio.espacio_id.in_(espacios)).all()]
    if servicios:
        db.query(ServicioInsumo).filter(ServicioInsumo.servicio_id.in_(servicios)).delete(synchronize_session=False)
        db.query(Servicio).filter(Servicio.id.in_(servicios)).delete(synchronize_session=False)

    insumos = [i.id for i in db.query(Insumo).filter(Insumo.espacio_id.in_(espacios)).all()]
    if insumos:
        db.query(PrecioInsumo).filter(PrecioInsumo.insumo_id.in_(insumos)).delete(synchronize_session=False)
        db.query(Insumo).filter(Insumo.id.in_(insumos)).delete(synchronize_session=False)

    prestamos = [p.id for p in db.query(Prestamo).filter(Prestamo.espacio_id.in_(espacios)).all()]
    if prestamos:
        db.query(AbonoPrestamo).filter(AbonoPrestamo.prestamo_id.in_(prestamos)).delete(synchronize_session=False)
        db.query(Prestamo).filter(Prestamo.id.in_(prestamos)).delete(synchronize_session=False)

    db.query(MovimientoCaja).filter(MovimientoCaja.espacio_id.in_(espacios)).delete(synchronize_session=False)
    db.query(ArqueoCaja).filter(ArqueoCaja.espacio_id.in_(espacios)).delete(synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.espacio_id.in_(espacios)).delete(synchronize_session=False)
    db.query(Proveedor).filter(Proveedor.espacio_id.in_(espacios)).delete(synchronize_session=False)
    db.query(Espacio).filter(Espacio.id.in_(espacios)).delete(synchronize_session=False)
    db.flush()


def sembrar(db: Session, empresa: Empresa) -> Espacio:
    """Crea el espacio demo con inventario, combos y caja. Asume que no hay datos."""
    hoy = date.today()

    def hace(dias: int) -> date:
        return hoy - timedelta(days=dias)

    espacio = Espacio(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        nombre=ESPACIO_DEMO,
        especialidad="Productos naturales",
        activo=True,
    )
    db.add(espacio)
    db.flush()

    proveedores = {}
    for nombre in PROVEEDORES:
        p = Proveedor(id=uuid.uuid4(), espacio_id=espacio.id, nombre=nombre)
        db.add(p)
        proveedores[nombre] = p
    db.flush()

    insumos = {}
    for nombre, presentacion, stock, minimo, costo, venta, proveedor in PRODUCTOS:
        ins = Insumo(
            id=uuid.uuid4(),
            espacio_id=espacio.id,
            nombre=nombre,
            categoria="suplemento",
            unidad_medida="unidad",
            stock_actual=Decimal(stock),
            stock_minimo=Decimal(minimo),
            precio_venta=Decimal(venta),
            activo=True,
        )
        db.add(ins)
        db.flush()
        insumos[nombre] = ins
        if costo is not None:
            db.add(PrecioInsumo(
                id=uuid.uuid4(),
                insumo_id=ins.id,
                proveedor_id=proveedores[proveedor].id,
                precio_presentacion=Decimal(costo),
                unidades_por_presentacion=1,
                descripcion_presentacion=presentacion,
                fecha_precio=hace(20),
                activo=True,
            ))

    for nombre, descripcion, margen, componentes in COMBOS:
        srv = Servicio(
            id=uuid.uuid4(),
            espacio_id=espacio.id,
            nombre=nombre,
            descripcion=descripcion,
            margen_ganancia_pct=Decimal(margen),
            activo=True,
        )
        db.add(srv)
        db.flush()
        for producto, cantidad in componentes:
            db.add(ServicioInsumo(
                id=uuid.uuid4(),
                servicio_id=srv.id,
                insumo_id=insumos[producto].id,
                cantidad=Decimal(cantidad),
            ))

    for dias, tipo, categoria, concepto, monto in MOVIMIENTOS:
        db.add(MovimientoCaja(
            id=uuid.uuid4(),
            espacio_id=espacio.id,
            fecha=hace(dias),
            tipo=tipo,
            categoria=categoria,
            concepto=concepto,
            monto=Decimal(monto),
            usuario_email=EMAIL_DEMO,
        ))

    # Ventas: cada una descuenta stock al registrarse en la aplicacion, pero aqui
    # el stock ya viene con el valor final, asi que solo se deja el historico.
    for dias, cliente, estado, lineas in VENTAS:
        fecha = hace(dias)
        venta = Venta(
            id=uuid.uuid4(),
            espacio_id=espacio.id,
            fecha=fecha,
            cliente=cliente,
            estado_pago=estado,
            fecha_pago=fecha if estado == "pagado" else None,
            usuario_email=EMAIL_DEMO,
            total=Decimal(0),
            costo_total=Decimal(0),
        )
        db.add(venta)
        db.flush()

        total = Decimal(0)
        costo_total = Decimal(0)
        for producto, cantidad, cobrado in lineas:
            datos = next(x for x in PRODUCTOS if x[0] == producto)
            costo = Decimal(datos[4] or 0)
            sugerido = Decimal(datos[5])
            precio = Decimal(cobrado) if cobrado is not None else sugerido
            db.add(VentaItem(
                id=uuid.uuid4(),
                venta_id=venta.id,
                insumo_id=insumos[producto].id,
                descripcion=producto,
                cantidad=Decimal(cantidad),
                precio_unitario=precio,
                precio_sugerido=sugerido,
                costo_unitario=costo,
                subtotal=precio * cantidad,
            ))
            total += precio * cantidad
            costo_total += costo * cantidad

        venta.total = total
        venta.costo_total = costo_total

        if estado == "pagado":
            db.add(MovimientoCaja(
                id=uuid.uuid4(), espacio_id=espacio.id, fecha=fecha,
                tipo="ingreso", categoria="venta",
                concepto=f"Venta a {cliente}", monto=total,
                referencia_tipo="venta", referencia_id=venta.id,
                usuario_email=EMAIL_DEMO,
            ))

    # Prestamo vencido: sin abonos desde hace 52 dias, dispara la alerta.
    vencido = Prestamo(
        id=uuid.uuid4(), espacio_id=espacio.id, fecha=hace(52),
        deudor="Mariana Gómez", concepto="Préstamo para compra de mercancía",
        monto=Decimal(400000), activo=True, usuario_email=EMAIL_DEMO,
    )
    db.add(vencido)
    db.flush()
    db.add(MovimientoCaja(
        id=uuid.uuid4(), espacio_id=espacio.id, fecha=hace(52),
        tipo="egreso", categoria="prestamo",
        concepto="Préstamo a Mariana Gómez", monto=Decimal(400000),
        referencia_tipo="prestamo", referencia_id=vencido.id, usuario_email=EMAIL_DEMO,
    ))

    # Prestamo al dia: dos abonos recibidos.
    al_dia = Prestamo(
        id=uuid.uuid4(), espacio_id=espacio.id, fecha=hace(30),
        deudor="Ricardo Peláez", concepto="Adelanto de mercancía a consignación",
        monto=Decimal(600000), activo=True, usuario_email=EMAIL_DEMO,
    )
    db.add(al_dia)
    db.flush()
    db.add(MovimientoCaja(
        id=uuid.uuid4(), espacio_id=espacio.id, fecha=hace(30),
        tipo="egreso", categoria="prestamo",
        concepto="Préstamo a Ricardo Peláez", monto=Decimal(600000),
        referencia_tipo="prestamo", referencia_id=al_dia.id, usuario_email=EMAIL_DEMO,
    ))
    for dias, monto in ((16, 250000), (5, 150000)):
        abono = AbonoPrestamo(
            id=uuid.uuid4(), prestamo_id=al_dia.id, fecha=hace(dias),
            monto=Decimal(monto), usuario_email=EMAIL_DEMO,
        )
        db.add(abono)
        db.flush()
        db.add(MovimientoCaja(
            id=uuid.uuid4(), espacio_id=espacio.id, fecha=hace(dias),
            tipo="ingreso", categoria="abono",
            concepto="Abono de Ricardo Peláez", monto=Decimal(monto),
            referencia_tipo="abono", referencia_id=abono.id, usuario_email=EMAIL_DEMO,
        ))

    # Arqueo con una diferencia deliberada, para mostrar la alerta de descuadre.
    # El saldo se toma de los movimientos ya insertados, no de las constantes.
    db.flush()
    movimientos = db.query(MovimientoCaja).filter(
        MovimientoCaja.espacio_id == espacio.id, MovimientoCaja.anulado == False
    ).all()
    ingresos = sum((Decimal(str(m.monto)) for m in movimientos if m.tipo == "ingreso"), Decimal(0))
    egresos = sum((Decimal(str(m.monto)) for m in movimientos if m.tipo == "egreso"), Decimal(0))
    saldo_teorico = ingresos - egresos
    db.add(ArqueoCaja(
        id=uuid.uuid4(),
        espacio_id=espacio.id,
        fecha=hace(1),
        efectivo_contado=saldo_teorico + DIFERENCIA_ARQUEO,
        saldo_teorico=saldo_teorico,
        diferencia=DIFERENCIA_ARQUEO,
        notas="Conteo de cierre. Falta revisar un recibo de gastos menores.",
        usuario_email=EMAIL_DEMO,
    ))

    return espacio


def crear_si_no_existe(db: Session) -> bool:
    """Siembra la demo la primera vez. Devuelve True si la creo."""
    if db.query(Usuario).filter(Usuario.email == EMAIL_DEMO).first():
        return False

    empresa = Empresa(
        id=uuid.uuid4(),
        nombre=EMPRESA_DEMO,
        nit="900.000.000-0",
        ciudad="Medellín",
        activa=True,
    )
    db.add(empresa)
    db.flush()
    db.add(Usuario(
        id=uuid.uuid4(),
        email=EMAIL_DEMO,
        password_hash=hash_password(PASSWORD_DEMO),
        rol="empresa",
        empresa_id=empresa.id,
    ))
    sembrar(db, empresa)
    db.commit()
    return True


def restaurar(db: Session) -> Espacio:
    """Borra lo que haya en la demo y la vuelve a sembrar desde cero."""
    empresa = obtener_empresa_demo(db)
    if empresa is None:
        raise ValueError("El ambiente de demostración no existe")
    borrar_datos(db, empresa.id)
    espacio = sembrar(db, empresa)
    db.commit()
    return espacio

"""
Ambiente de demostracion: distribuidora de productos naturales.

Crea una empresa aparte con datos ficticios para que cualquier interesado pruebe
la aplicacion sin ver informacion de clientes reales. Los nombres de personas son
inventados a proposito.

Los datos estan armados para que se vean solas las senales que la aplicacion
detecta: stock por debajo del minimo, un producto sin precio, un prestamo sin
abonos vencido y un arqueo que no cuadra.

Es idempotente: si el usuario demo ya existe, no hace nada.
"""
import os
import sys
import uuid
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.espacio import Espacio
from app.models.proveedor import Proveedor
from app.models.insumo import Insumo
from app.models.precio_insumo import PrecioInsumo
from app.models.servicio import Servicio
from app.models.servicio_insumo import ServicioInsumo
from app.models.caja import MovimientoCaja, Prestamo, AbonoPrestamo, ArqueoCaja
from app.auth import hash_password

EMAIL_DEMO = "demo@facilito.co"
PASSWORD_DEMO = "demo2026"

db = SessionLocal()

if db.query(Usuario).filter(Usuario.email == EMAIL_DEMO).first():
    print("Seed demo ya ejecutado, omitiendo.")
    db.close()
    sys.exit(0)

print("Cargando ambiente de demostracion...")

HOY = date.today()


def hace(dias: int) -> date:
    return HOY - timedelta(days=dias)


# ---- EMPRESA Y USUARIO ----
empresa = Empresa(
    id=uuid.uuid4(),
    nombre="Distribuidora Vital (Demo)",
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

espacio = Espacio(
    id=uuid.uuid4(),
    empresa_id=empresa.id,
    nombre="Punto de venta (Demo)",
    especialidad="Productos naturales",
    activo=True,
)
db.add(espacio)
db.flush()

# ---- PROVEEDORES ----
proveedores = {}
for nombre in ("Importadora Andina", "Naturales del Valle", "Distribuidora Central"):
    p = Proveedor(id=uuid.uuid4(), espacio_id=espacio.id, nombre=nombre)
    db.add(p)
    proveedores[nombre] = p
db.flush()

# ---- PRODUCTOS ----
# (nombre, presentacion, stock, stock_minimo, costo, proveedor)
# costo None deja el producto sin precio, para mostrar esa alerta.
PRODUCTOS = [
    ("VitalPro",            "Polvo 300 g",        4,  2, 147000, "Importadora Andina"),
    ("V-NeuroKafe",         "Polvo 150 g",        6,  3, 105000, "Importadora Andina"),
    ("VitalAge Collagen",   "Polvo 300 g",        3,  2, 122500, "Naturales del Valle"),
    ("V-Té Detox",          "Caja 20 sobres",    18,  6,  25600, "Naturales del Valle"),
    ("V-Control",           "60 cápsulas",        5,  3,  70000, "Importadora Andina"),
    ("V-Itadol",            "60 cápsulas",        1,  3,  70000, "Importadora Andina"),
    ("V-Daily",             "Polvo 150 g",        4,  2, 175000, "Distribuidora Central"),
    ("V-FortyFlora",        "60 cápsulas",        2,  3,  70000, "Naturales del Valle"),
    ("Genius Shake",        "Polvo 400 g",        3,  2, 175000, "Distribuidora Central"),
    ("V-Omega3",            "60 cápsulas",        7,  3,  84000, "Naturales del Valle"),
    ("V-Curcumax",          "60 cápsulas",        0,  3,  91000, "Importadora Andina"),
    ("V-Organex",           "60 cápsulas",        2,  2,   None, "Distribuidora Central"),
]

insumos = {}
for nombre, presentacion, stock, minimo, costo, proveedor in PRODUCTOS:
    ins = Insumo(
        id=uuid.uuid4(),
        espacio_id=espacio.id,
        nombre=nombre,
        categoria="suplemento",
        unidad_medida="unidad",
        stock_actual=Decimal(stock),
        stock_minimo=Decimal(minimo),
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

# ---- COMBOS ----
# Muestran como se arma un precio de venta a partir del costo de los productos.
COMBOS = [
    ("Combo Energía",   "V-NeuroKafe + Genius Shake",        100, [("V-NeuroKafe", 1), ("Genius Shake", 1)]),
    ("Combo Detox",     "V-Té Detox + V-Control",            120, [("V-Té Detox", 2), ("V-Control", 1)]),
    ("Combo Bienestar", "V-Daily + V-Omega3 + V-FortyFlora",  90, [("V-Daily", 1), ("V-Omega3", 1), ("V-FortyFlora", 1)]),
]

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

# ---- CAJA ----
# Ingresos y egresos de las ultimas semanas.
MOVIMIENTOS = [
    (45, "ingreso", "otro",   "Capital inicial del negocio",          3000000),
    (40, "egreso",  "compra", "Compra de inventario inicial",         2100000),
    (32, "ingreso", "venta",  "Venta Combo Energía — Laura Restrepo",   560000),
    (28, "egreso",  "gasto",  "Arriendo del local",                     800000),
    (25, "ingreso", "venta",  "Venta VitalPro x2 — Andrés Mejía",       588000),
    (21, "ingreso", "venta",  "Venta V-Té Detox x10 — feria de salud",  512000),
    (18, "egreso",  "gasto",  "Transporte y domicilios",                 95000),
    (14, "ingreso", "venta",  "Venta Combo Detox — Carolina Ossa",      342000),
    (11, "egreso",  "compra", "Reposición de V-Omega3",                 588000),
    (7,  "ingreso", "venta",  "Venta V-Daily — Julián Betancur",        350000),
    (4,  "egreso",  "gasto",  "Servicios públicos",                     140000),
    (2,  "ingreso", "venta",  "Venta Combo Bienestar — Sara Villa",     627000),
]

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

# ---- PRESTAMOS ----
# El primero lleva mas de 30 dias sin ningun abono: dispara la alerta.
prestamo_vencido = Prestamo(
    id=uuid.uuid4(),
    espacio_id=espacio.id,
    fecha=hace(52),
    deudor="Mariana Gómez",
    concepto="Préstamo para compra de mercancía",
    monto=Decimal(400000),
    activo=True,
    usuario_email=EMAIL_DEMO,
)
db.add(prestamo_vencido)
db.flush()
db.add(MovimientoCaja(
    id=uuid.uuid4(), espacio_id=espacio.id, fecha=hace(52),
    tipo="egreso", categoria="prestamo",
    concepto="Préstamo a Mariana Gómez", monto=Decimal(400000),
    referencia_tipo="prestamo", referencia_id=prestamo_vencido.id,
    usuario_email=EMAIL_DEMO,
))

# El segundo va al dia, con dos abonos recibidos.
prestamo_al_dia = Prestamo(
    id=uuid.uuid4(),
    espacio_id=espacio.id,
    fecha=hace(30),
    deudor="Ricardo Peláez",
    concepto="Adelanto de mercancía a consignación",
    monto=Decimal(600000),
    activo=True,
    usuario_email=EMAIL_DEMO,
)
db.add(prestamo_al_dia)
db.flush()
db.add(MovimientoCaja(
    id=uuid.uuid4(), espacio_id=espacio.id, fecha=hace(30),
    tipo="egreso", categoria="prestamo",
    concepto="Préstamo a Ricardo Peláez", monto=Decimal(600000),
    referencia_tipo="prestamo", referencia_id=prestamo_al_dia.id,
    usuario_email=EMAIL_DEMO,
))

for dias, monto in ((16, 250000), (5, 150000)):
    abono = AbonoPrestamo(
        id=uuid.uuid4(),
        prestamo_id=prestamo_al_dia.id,
        fecha=hace(dias),
        monto=Decimal(monto),
        usuario_email=EMAIL_DEMO,
    )
    db.add(abono)
    db.flush()
    db.add(MovimientoCaja(
        id=uuid.uuid4(), espacio_id=espacio.id, fecha=hace(dias),
        tipo="ingreso", categoria="abono",
        concepto="Abono de Ricardo Peláez", monto=Decimal(monto),
        referencia_tipo="abono", referencia_id=abono.id,
        usuario_email=EMAIL_DEMO,
    ))

# ---- ARQUEO ----
# Se deja una diferencia pequena a proposito para mostrar la alerta de descuadre.
ingresos = sum(Decimal(m[4]) for m in MOVIMIENTOS if m[1] == "ingreso") + Decimal(400000)
egresos = sum(Decimal(m[4]) for m in MOVIMIENTOS if m[1] == "egreso") + Decimal(1000000)
saldo_teorico = ingresos - egresos
contado = saldo_teorico - Decimal(35000)

db.add(ArqueoCaja(
    id=uuid.uuid4(),
    espacio_id=espacio.id,
    fecha=hace(1),
    efectivo_contado=contado,
    saldo_teorico=saldo_teorico,
    diferencia=contado - saldo_teorico,
    notas="Conteo de cierre. Falta revisar un recibo de gastos menores.",
    usuario_email=EMAIL_DEMO,
))

db.commit()
db.close()

print(f"Ambiente de demostracion listo: {EMAIL_DEMO} / {PASSWORD_DEMO}")

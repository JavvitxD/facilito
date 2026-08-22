"""
Seed inicial: Guiar Salud IPS — Dra. Estela Quintero
Ejecutar una sola vez después de las migraciones.
"""
import os
import sys
import uuid
from datetime import date

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
from app.auth import hash_password

db = SessionLocal()

# --- Verificar si ya hay datos ---
if db.query(Usuario).first():
    print("Seed ya ejecutado, omitiendo.")
    db.close()
    sys.exit(0)

print("Cargando datos iniciales...")

# ---- EMPRESA ----
empresa = Empresa(
    id=uuid.uuid4(),
    nombre="Guiar Salud IPS",
    nit="900.123.456-7",
    ciudad="Bogotá",
    activa=True,
)
db.add(empresa)
db.flush()

# ---- USUARIOS ----
superadmin = Usuario(
    id=uuid.uuid4(),
    email="admin@invdoc.co",
    password_hash=hash_password("admin2026"),
    rol="superadmin",
    empresa_id=None,
)
empresa_user = Usuario(
    id=uuid.uuid4(),
    email="guiarsalud@invdoc.co",
    password_hash=hash_password("guiar2026"),
    rol="empresa",
    empresa_id=empresa.id,
)
db.add(superadmin)
db.add(empresa_user)
db.flush()

# ---- ESPACIOS ----
espacio_estela = Espacio(
    id=uuid.uuid4(),
    empresa_id=empresa.id,
    nombre="Dra. Stella Quintero",
    especialidad="Medicina Estética",
    activo=True,
)
espacio_mf = Espacio(
    id=uuid.uuid4(),
    empresa_id=empresa.id,
    nombre="Dra. María Fernanda Calderón",
    especialidad="Medicina Estética",
    activo=True,
)
db.add(espacio_estela)
db.add(espacio_mf)
db.flush()

eid = espacio_estela.id

# ---- PROVEEDORES ----
prov_nombres = ["Jaguar", "Gloria", "Dermavan", "Skymedic", "Pricesmart", "D1", "Distribuidor", "Online"]
proveedores = {}
for nombre in prov_nombres:
    p = Proveedor(id=uuid.uuid4(), espacio_id=eid, nombre=nombre)
    db.add(p)
    proveedores[nombre] = p
db.flush()

J = proveedores["Jaguar"]
G = proveedores["Gloria"]
D = proveedores["Dermavan"]
S = proveedores["Skymedic"]
O = proveedores["Online"]

HOY = date(2026, 6, 19)


def insumo(nombre, categoria, unidad, precios_list, stock_actual=0, stock_minimo=0):
    ins = Insumo(
        id=uuid.uuid4(),
        espacio_id=eid,
        nombre=nombre,
        categoria=categoria,
        unidad_medida=unidad,
        stock_actual=stock_actual,
        stock_minimo=stock_minimo,
        activo=True,
    )
    db.add(ins)
    db.flush()
    for prov, precio_pres, uds, desc in precios_list:
        pr = PrecioInsumo(
            id=uuid.uuid4(),
            insumo_id=ins.id,
            proveedor_id=prov.id,
            precio_presentacion=precio_pres,
            unidades_por_presentacion=uds,
            descripcion_presentacion=desc,
            fecha_precio=HOY,
            activo=True,
        )
        db.add(pr)
    db.flush()
    return ins


# ============================================================
# INSUMOS MÉDICOS
# ============================================================
jer1_27 = insumo("Jeringa 1ml 27G 1/2", "medico", "unidad", [
    (J, 25000, 100, "Caja 100 uds"),
    (G, 14200, 100, "Caja 100 uds"),
], stock_minimo=50)

jer3_21 = insumo("Jeringa 3ml 21G x 1/2", "medico", "unidad", [
    (J, 30000, 100, "Caja 100 uds"),
    (G, 18000, 100, "Caja 100 uds"),
], stock_minimo=20)

jer5_21 = insumo("Jeringa 5ml 21G x 1/2", "medico", "unidad", [
    (J, 30000, 100, "Caja 100 uds"),
    (G, 13500, 100, "Caja 100 uds"),
], stock_minimo=10)

jer10_21 = insumo("Jeringa 10ml 21G x 1/2", "medico", "unidad", [
    (G, 20000, 100, "Caja 100 uds"),
], stock_minimo=10)

jer20_21 = insumo("Jeringa 20ml 21G x 1/2", "medico", "unidad", [
    (J, 40000, 100, "Caja 100 uds"),
    (G, 35000, 100, "Caja 100 uds"),
], stock_minimo=10)

aguja18 = insumo("Aguja hipodérmica 18G x 1 1/2", "medico", "unidad", [
    (J, 15000, 100, "Caja 100 uds"),
    (G, 6600, 100, "Caja 100 uds"),
], stock_minimo=50)

aguja21 = insumo("Aguja hipodérmica 21G x 1 1/2", "medico", "unidad", [
    (J, 15000, 100, "Caja 100 uds"),
], stock_minimo=20)

aguja22 = insumo("Aguja hipodérmica 22G x 1 1/2", "medico", "unidad", [
    (G, 6600, 100, "Caja 100 uds"),
], stock_minimo=20)

aguja30 = insumo("Aguja hipodérmica 30G x 1/2", "medico", "unidad", [
    (J, 15000, 100, "Caja 100 uds"),
    (G, 11600, 100, "Caja 100 uds"),
], stock_minimo=10)

gasa = insumo("Gasa hospitalaria tejida", "medico", "unidad", [
    (J, 70000, 1000, "Rollo 100 yardas / 1000 gasas"),
    (G, 47000, 1000, "Rollo 100 yardas / 1000 gasas"),
], stock_minimo=200)

algodon = insumo("Rollo algodón", "medico", "unidad", [
    (J, 19000, 1000, "Rollo / 1000 unidades"),
], stock_minimo=100)

macrogoteo = insumo("Macrogoteo", "medico", "unidad", [
    (J, 1300, 1, "Unidad"),
    (G, 225, 1, "Caja 25 uds — precio por caja"),  # nota: precio total caja
], stock_minimo=5)

cateter24_nipro = insumo("Catéter intravenoso #24G Nipro", "medico", "unidad", [
    (G, 1700, 1, "Unidad"),
    (J, 3400, 1, "Unidad"),
], stock_minimo=10)

cateter24_prec = insumo("Catéter intravenoso #24G Precision", "medico", "unidad", [
    (J, 1800, 1, "Unidad"),
], stock_minimo=5)

aguja_sangre_21 = insumo("Aguja toma de sangre 21G x 1 1/2", "medico", "unidad", [
    (J, 53600, 100, "Caja 100 uds"),
    (G, 18000, 100, "Caja 100 uds"),
], stock_minimo=10)

curas = insumo("Curas redondas", "medico", "unidad", [
    (J, 5000, 100, "Caja 100 uds"),
    (G, 4000, 100, "Caja 100 uds"),
], stock_minimo=20)

especulo = insumo("Espéculo para otoscopio", "medico", "unidad", [
    (J, 38100, 34, "Bolsa 34 uds"),
    (G, 14000, 60, "Bolsa 60 uds"),
], stock_minimo=10)

cloruro100 = insumo("Cloruro de sodio 0.9% 100ml", "medico", "unidad", [
    (J, 3900, 1, "Unidad"),
    (G, 2800, 1, "Unidad"),
], stock_minimo=5)

cloruro250 = insumo("Cloruro de sodio 0.9% 250ml", "medico", "unidad", [
    (J, 4000, 1, "Unidad"),
    (G, 3300, 1, "Unidad"),
], stock_minimo=5)

cloruro500 = insumo("Cloruro de sodio 0.9% 500ml", "medico", "unidad", [
    (G, 3100, 1, "Unidad"),
], stock_minimo=3)

bata = insumo("Bata paciente azul desechable", "aseo", "unidad", [
    (J, 28560, 10, "Bolsa 10 uds"),
], stock_minimo=10)

gorro = insumo("Gorro tipo oruga", "aseo", "unidad", [
    (J, 19000, 100, "Bolsa 100 uds"),
], stock_minimo=50)

guante_latex_s = insumo("Guante tipo látex talla S", "medico", "par", [
    (J, 38000, 100, "Caja 100 pares"),
    (G, 35700, 100, "Caja 100 pares"),
], stock_minimo=20)

guante_nitrilo_s = insumo("Guante tipo nitrilo talla S", "medico", "par", [
    (G, 33300, 100, "Caja 100 pares"),
    (J, 45200, 100, "Caja 100 pares"),
], stock_minimo=20)

tubo_azul = insumo("Tubo tapa azul", "medico", "unidad", [
    (J, 83300, 100, "Caja 100 uds"),
], stock_minimo=5)

tubo_amarilla = insumo("Tubo tapa amarilla", "medico", "unidad", [
    (J, 82100, 100, "Caja 100 uds"),
], stock_minimo=5)

tubo_lila = insumo("Tubo tapa lila", "medico", "unidad", [
    (J, 65400, 100, "Caja 100 uds"),
], stock_minimo=5)

alcohol = insumo("Alcohol al 70% 3600ml", "aseo", "ml", [
    (J, 36000, 3600, "Botella 3600ml — precio por ml"),
], stock_minimo=500)

lidocaina_sin = insumo("Lidocaína 2% sin epinefrina", "medicamento", "ml", [
    (J, 1800, 10, "Ampolla 10ml"),
    (G, 7200, 50, "Ampolla 50ml"),
], stock_minimo=20)

lidocaina_con = insumo("Lidocaína 2% con epinefrina", "medicamento", "ml", [
    (J, 38700, 10, "Ampolla 10ml"),
], stock_minimo=10)

aguja34g = insumo("Aguja 34G x 4mm", "medico", "unidad", [
    (D, 272000, 100, "Caja 100 uds"),
], stock_minimo=10)

# ---- Medicamentos Skymedic ----
skinox = insumo("Skinox (peeling + serum) — cara", "medicamento", "por paciente", [
    (S, 1856100, 25, "Paquete rinde 25 pacientes cara"),
], stock_minimo=1)

skinox_casa = insumo("Skinox tratamiento en casa", "medicamento", "paquete", [
    (S, 396750, 1, "Por paquete"),
], stock_minimo=1)

densify = insumo("Densify II", "medicamento", "jeringa", [
    (S, 405000, 1, "Por jeringa"),
], stock_minimo=1)

colagen_serum = insumo("Colagen deep serum", "medicamento", "por paciente", [
    (S, 368000, 20, "Unidad rinde 20 pacientes"),
], stock_minimo=1)

hyalurox = insumo("Hyalurox deep serum", "medicamento", "por paciente", [
    (S, 368000, 20, "Unidad rinde 20 pacientes"),
], stock_minimo=1)

fotoskinox = insumo("Fotoskinox deep serum", "medicamento", "por paciente", [
    (S, 368000, 20, "Unidad rinde 20 pacientes"),
], stock_minimo=1)

hairox = insumo("Hairox deep serum", "medicamento", "por paciente", [
    (S, 368000, 20, "Unidad rinde 20 pacientes"),
], stock_minimo=1)

meso_ox = insumo("Meso ox (varios tipos)", "medicamento", "ml", [
    (S, 108000, 5, "Caja 5 viales x 5ml — precio por vial"),
], stock_minimo=1)

meso_hydra = insumo("Meso ox hydralight", "medicamento", "ml", [
    (S, 158000, 5, "Caja 5 unidades x 5ml — precio por vial"),
], stock_minimo=1)

exosomas = insumo("Exosomas faciales", "medicamento", "ml", [
    (S, 132000, 1, "Caja 5 unidades — precio por ml"),
], stock_minimo=1)

# ---- Insumos cotizados online ----
prolene_4_0 = insumo("Sutura Prolene 4-0 (Ethicon)", "medico", "unidad", [
    (O, 20000, 1, "Unidad — precio aproximado, cotizar con Jaguar/Gloria"),
], stock_minimo=5)

prolene_2_0 = insumo("Sutura Prolene 2-0 (Ethicon)", "medico", "unidad", [
    (O, 18000, 1, "Unidad — precio aproximado, cotizar con Jaguar/Gloria"),
], stock_minimo=5)

hoja_bisturi = insumo("Hoja de bisturí #15", "medico", "unidad", [
    (O, 50000, 100, "Caja 100 uds — precio aprox."),
], stock_minimo=10)

guante_esteril_m = insumo("Guantes estériles látex quirúrgicos talla M", "medico", "par", [
    (O, 4000, 1, "Por par"),
], stock_minimo=10)

micropore = insumo("Micropore 3M rollo pequeño 12mm x 5m", "medico", "rollo", [
    (O, 4500, 1, "Por rollo"),
], stock_minimo=5)

acetaminofen = insumo("Acetaminofén 500mg tableta", "medicamento", "tableta", [
    (O, 2100, 10, "Blister x10"),
], stock_minimo=20)

panitos = insumo("Pañitos húmedos", "aseo", "unidad", [
    (O, 55, 1, "Por unidad — precio estimado"),
], stock_minimo=50)

# ============================================================
# SERVICIOS — Dra. Estela Quintero
# ============================================================

def servicio(nombre, desc, margen, insumos_list):
    srv = Servicio(
        id=uuid.uuid4(),
        espacio_id=eid,
        nombre=nombre,
        descripcion=desc,
        margen_ganancia_pct=margen,
        activo=True,
    )
    db.add(srv)
    db.flush()
    for ins, cantidad, notas in insumos_list:
        si = ServicioInsumo(
            id=uuid.uuid4(),
            servicio_id=srv.id,
            insumo_id=ins.id,
            cantidad=cantidad,
            notas=notas,
        )
        db.add(si)
    db.flush()
    return srv


servicio(
    "Blefaroplastia",
    "Procedimiento quirúrgico de párpados",
    40,
    [
        (guante_esteril_m, 4, "4 pares"),
        (jer1_27, 1, None),
        (aguja18, 1, None),
        (lidocaina_con, 15, "15ml con epinefrina"),
        (panitos, 10, None),
        (gasa, 15, "15 gasas"),
        (prolene_4_0, 1, None),
        (hoja_bisturi, 1, None),
        (micropore, 0.1667, "1/6 de rollo"),
        (acetaminofen, 2, "2 tabletas postprocedimiento"),
    ],
)

servicio(
    "Lifting de Oreja",
    "Procedimiento estético de oreja — cantidades de algunos insumos pendientes de confirmar",
    40,
    [
        (hoja_bisturi, 1, None),
        (prolene_2_0, 2, None),
        (guante_esteril_m, 4, "4 pares"),
        (jer1_27, 1, None),
        (micropore, 0.1667, "1/6 de rollo — estimado"),
    ],
)

servicio(
    "Lifting de Nariz",
    "Procedimiento estético de nariz — cantidades de algunos insumos pendientes de confirmar",
    40,
    [
        (hoja_bisturi, 1, None),
        (prolene_2_0, 2, None),
        (guante_esteril_m, 4, "4 pares"),
        (jer1_27, 1, None),
        (micropore, 0.1667, "1/6 de rollo — estimado"),
    ],
)

servicio(
    "Colocación de Hilos Extensores",
    "Aplicación de hilos extensores (PDO u otra marca) — tipo/precio de hilos pendiente de confirmar",
    40,
    [
        (guante_esteril_m, 1, "1 par"),
        (jer1_27, 1, None),
        (aguja18, 1, None),
    ],
)

servicio(
    "Aplicación de Botox",
    "Aplicación de toxina botulínica — marca y dosis pendientes de confirmar",
    40,
    [
        (guante_esteril_m, 1, "1 par"),
        (jer1_27, 5, "5 jeringas 1ml"),
    ],
)

db.commit()
print("Seed completado exitosamente.")
print()
print("  Credenciales:")
print("  Superadmin : admin@invdoc.co / admin2026")
print("  Empresa    : guiarsalud@invdoc.co / guiar2026")

db.close()

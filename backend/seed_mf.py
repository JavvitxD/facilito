"""
Seed Dra. María Fernanda Calderón — todos los servicios e insumos del spec.
Ejecutar DESPUÉS de seed.py (requiere que la empresa y el espacio ya existan).
"""
import os
import sys
import uuid
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.espacio import Espacio
from app.models.proveedor import Proveedor
from app.models.insumo import Insumo
from app.models.precio_insumo import PrecioInsumo
from app.models.servicio import Servicio
from app.models.servicio_insumo import ServicioInsumo
from app.models.paquete import Paquete, PaqueteServicio

db = SessionLocal()

espacio_mf = db.query(Espacio).filter(Espacio.nombre.ilike("%María Fernanda%")).first()
if not espacio_mf:
    print("ERROR: No se encontró el espacio de la Dra. María Fernanda. Ejecuta seed.py primero.")
    db.close()
    sys.exit(1)

if db.query(Servicio).filter(Servicio.espacio_id == espacio_mf.id).first():
    print("Seed MF ya ejecutado, omitiendo.")
    db.close()
    sys.exit(0)

print("Cargando datos Dra. María Fernanda Calderón...")

eid = espacio_mf.id
HOY = date(2026, 6, 26)

# ---- PROVEEDORES ----
prov_nombres = ["Jaguar", "Gloria", "Dermavan", "Skymedic", "Tecnovital", "Sesderma", "Mediderma", "Online"]
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
T = proveedores["Tecnovital"]
Se = proveedores["Sesderma"]
M = proveedores["Mediderma"]
O = proveedores["Online"]


def insumo(nombre, categoria, unidad, precios_list, stock_actual=0, stock_minimo=0):
    ins = Insumo(
        id=uuid.uuid4(), espacio_id=eid, nombre=nombre, categoria=categoria,
        unidad_medida=unidad, stock_actual=stock_actual, stock_minimo=stock_minimo, activo=True,
    )
    db.add(ins)
    db.flush()
    for prov, precio_pres, uds, desc in precios_list:
        pr = PrecioInsumo(
            id=uuid.uuid4(), insumo_id=ins.id, proveedor_id=prov.id,
            precio_presentacion=precio_pres, unidades_por_presentacion=uds,
            descripcion_presentacion=desc, fecha_precio=HOY, activo=True,
        )
        db.add(pr)
    db.flush()
    return ins


# ============================================================
# INSUMOS BÁSICOS (consumibles)
# ============================================================
guante_nitrilo = insumo("Guante tipo nitrilo talla S", "medico", "par", [
    (G, 33300, 100, "Caja 100 pares"), (J, 45200, 100, "Caja 100 pares"),
], stock_minimo=50)

gorro = insumo("Gorro tipo oruga", "aseo", "unidad", [
    (J, 19000, 100, "Bolsa 100 uds"),
], stock_minimo=50)

tapabocas = insumo("Tapabocas desechable", "aseo", "unidad", [
    (J, 18000, 100, "Caja 100 uds"),
], stock_minimo=50)

panitos = insumo("Pañitos húmedos", "aseo", "unidad", [
    (O, 55, 1, "Por unidad — precio estimado"),
], stock_minimo=100)

gasas = insumo("Gasa hospitalaria tejida", "medico", "unidad", [
    (J, 70000, 1000, "Rollo 1000 gasas"), (G, 47000, 1000, "Rollo 1000 gasas"),
], stock_minimo=200)

bata = insumo("Bata paciente azul desechable", "aseo", "unidad", [
    (J, 28560, 10, "Bolsa 10 uds"),
], stock_minimo=10)

polainas = insumo("Polainas desechables par", "aseo", "par", [
    (J, 15000, 100, "Bolsa 100 pares"),
], stock_minimo=20)

balaca = insumo("Balaca para cabello", "aseo", "unidad", [
    (O, 300, 1, "Por unidad"),
], stock_minimo=20)

bajalenguas = insumo("Bajalenguas madera", "medico", "unidad", [
    (J, 12000, 100, "Caja 100 uds"),
], stock_minimo=20)

escobillon = insumo("Escobillón estéril", "medico", "unidad", [
    (O, 2500, 1, "Por unidad"),
], stock_minimo=10)

alcohol = insumo("Alcohol al 70%", "aseo", "ml", [
    (J, 36000, 3600, "Botella 3600ml"),
], stock_minimo=500)

micropore = insumo("Micropore 3M rollo 12mm", "medico", "rollo", [
    (O, 4500, 1, "Por rollo"),
], stock_minimo=5)

algodon = insumo("Algodón bola pequeña", "medico", "unidad", [
    (J, 19000, 1000, "Rollo / 1000 uds"),
], stock_minimo=100)

# ============================================================
# INSUMOS MÉDICOS INYECTABLES
# ============================================================
jer1ml = insumo("Jeringa 1ml 27G x 1/2", "medico", "unidad", [
    (J, 25000, 100, "Caja 100 uds"), (G, 14200, 100, "Caja 100 uds"),
], stock_minimo=50)

jer3ml = insumo("Jeringa 3ml 21G x 1/2", "medico", "unidad", [
    (J, 30000, 100, "Caja 100 uds"), (G, 18000, 100, "Caja 100 uds"),
], stock_minimo=30)

jer5ml = insumo("Jeringa 5ml 21G x 1/2", "medico", "unidad", [
    (J, 30000, 100, "Caja 100 uds"), (G, 13500, 100, "Caja 100 uds"),
], stock_minimo=20)

jer10ml = insumo("Jeringa 10ml 21G x 1/2", "medico", "unidad", [
    (G, 20000, 100, "Caja 100 uds"),
], stock_minimo=10)

aguja18g = insumo("Aguja hipodérmica 18G x 1 1/2", "medico", "unidad", [
    (J, 15000, 100, "Caja 100 uds"), (G, 6600, 100, "Caja 100 uds"),
], stock_minimo=20)

aguja30g = insumo("Aguja hipodérmica 30G x 1/2", "medico", "unidad", [
    (J, 15000, 100, "Caja 100 uds"), (G, 11600, 100, "Caja 100 uds"),
], stock_minimo=10)

aguja27g = insumo("Aguja hipodérmica 27G x 1/2", "medico", "unidad", [
    (J, 15000, 100, "Caja 100 uds"),
], stock_minimo=10)

aguja21g = insumo("Aguja hipodérmica 21G x 1/2", "medico", "unidad", [
    (J, 15000, 100, "Caja 100 uds"),
], stock_minimo=10)

aguja34g = insumo("Aguja 34G x 4mm (nanopore/meso)", "medico", "unidad", [
    (D, 272000, 100, "Caja 100 uds"),
], stock_minimo=10)

aguja_nanopore = insumo("Aguja nanopore", "medico", "unidad", [
    (O, 15000, 1, "Por unidad — cotizar proveedor"),
], stock_minimo=5)

llave_3vias = insumo("Llave de 3 vías", "medico", "unidad", [
    (G, 4500, 1, "Por unidad"),
], stock_minimo=5)

canula = insumo("Cánula 25G x 1.5 punta roma", "medico", "unidad", [
    (O, 8500, 1, "Por unidad"),
], stock_minimo=10)

lidocaina_sin = insumo("Lidocaína 2% sin epinefrina", "medicamento", "ml", [
    (J, 1800, 10, "Ampolla 10ml"), (G, 7200, 50, "Ampolla 50ml"),
], stock_minimo=50)

suero_sal_100 = insumo("Cloruro de sodio 0.9% 100ml", "medico", "unidad", [
    (J, 3900, 1, "Unidad"), (G, 2800, 1, "Unidad"),
], stock_minimo=10)

cateter24 = insumo("Catéter intravenoso #24G", "medico", "unidad", [
    (G, 1700, 1, "Unidad"), (J, 3400, 1, "Unidad"),
], stock_minimo=5)

macrogoteo = insumo("Macrogoteo", "medico", "unidad", [
    (J, 1300, 1, "Unidad"), (G, 225, 1, "Unidad"),
], stock_minimo=5)

torniquete = insumo("Torniquete látex", "medico", "unidad", [
    (O, 3500, 1, "Por unidad"),
], stock_minimo=3)

glutaraldehido = insumo("Glutaraldehído 50ml", "medicamento", "ml", [
    (O, 120000, 50, "Frasco 50ml"),
], stock_minimo=50)

kit_citologia = insumo("Kit de citología cervicovaginal", "medico", "kit", [
    (O, 8000, 1, "Por kit"),
], stock_minimo=5)

# ============================================================
# INSUMOS ESPECIALIZADOS — MEDICAMENTOS Y PRODUCTOS ESTÉTICOS
# ============================================================

# Toxina botulínica
botox_100u = insumo("Toxina botulínica Botox® 100U (Allergan)", "medicamento", "unidad", [
    (O, 750000, 100, "Frasco 100U — precio adquisición médica estimado"),
], stock_minimo=1)

neuronox_100u = insumo("Toxina botulínica Neuronox® 100U (Medytox)", "medicamento", "unidad", [
    (O, 450000, 100, "Frasco 100U — precio adquisición médica estimado"),
], stock_minimo=1)

jer_insulina = insumo("Jeringa insulina 30UI x 1/2", "medico", "unidad", [
    (J, 15000, 100, "Caja 100 uds"),
], stock_minimo=20)

# Ácido hialurónico
ah_1ml = insumo("Ácido hialurónico facial 1ml (Restylane/Juvederm/Belotero)", "medicamento", "jeringa", [
    (O, 500000, 1, "Jeringa 1ml — precio adquisición médica estimado Restylane"),
    (O, 650000, 1, "Jeringa 1ml — precio adquisición médica estimado Juvederm"),
], stock_minimo=1)

# Bioestimulador TKN HA3
tkn_ha3 = insumo("Bioestimulador TKN HA3", "medicamento", "jeringa", [
    (T, 380000, 1, "Por jeringa — cotizar con Tecnovital"),
], stock_minimo=1)

# Hidroxiapatita de calcio
hidroxiapatita = insumo("Hidroxiapatita de calcio (Radiesse)", "medicamento", "jeringa", [
    (O, 800000, 1, "Jeringa 1.5ml — precio adquisición médica estimado"),
], stock_minimo=1)

# Hilos
hilos_bioestimulacion = insumo("Paquete hilos de bioestimulación PDO", "medico", "paquete", [
    (O, 350000, 1, "Paquete estándar — cotizar cantidad y tipo"),
], stock_minimo=1)

# Lipólisis
aqualyx = insumo("Aqualyx 8ml (lipólisis enzimática)", "medicamento", "ampolla", [
    (O, 180000, 1, "Frasco 8ml — precio estimado, verificar INVIMA"),
], stock_minimo=2)

# PDRN / Esperma de salmón
pdrn_salmon = insumo("PDRN / Esperma de salmón (1cc)", "medicamento", "cc", [
    (O, 250000, 1, "Por aplicación 1cc — precio estimado"),
], stock_minimo=2)

# Exosomas
exosomas = insumo("Exosomas faciales 1cc", "medicamento", "cc", [
    (S, 132000, 1, "Por cc — precio Skymedic"),
], stock_minimo=2)

# Mesoject gun
mesoject_gun = insumo("Dispositivo facial mesoject gun (pistola meso)", "medico", "uso", [
    (O, 5000, 1, "Costo por uso / descartables"),
], stock_minimo=1)

# Tecnovital
limpiador_tecnovital = insumo("Limpiador facial Tecnovital (por paciente)", "medicamento", "por paciente", [
    (T, 250000, 20, "Frasco rinde 20 pacientes"),
], stock_minimo=1)

mascarilla_tecnovital = insumo("Mascarilla Tecnovital (por paciente)", "medicamento", "por paciente", [
    (T, 300000, 20, "Frasco rinde 20 pacientes"),
], stock_minimo=1)

anestesia_topica = insumo("Anestesia tópica (crema EMLA o similar)", "medicamento", "por paciente", [
    (O, 12000, 1, "Por aplicación"),
], stock_minimo=5)

# Peeling y serum Skymedic
peeling_skymedic = insumo("Peeling Skymedic (por paciente)", "medicamento", "por paciente", [
    (S, 74244, 25, "Paquete 25 pacientes"),
], stock_minimo=1)

serum_skymedic = insumo("Serum Skymedic (por paciente)", "medicamento", "por paciente", [
    (S, 74244, 25, "Paquete 25 pacientes — estimado similar a peeling"),
], stock_minimo=1)

# Peeling Sesderma
peeling_sesderma = insumo("Peeling Sesderma", "medicamento", "por paciente", [
    (Se, 85000, 10, "Frasco rinde ~10 pacientes — cotizar"),
], stock_minimo=1)

# Meso ox
meso_ox = insumo("Meso ox hydralight (ml)", "medicamento", "ml", [
    (S, 31600, 5, "Vial 5ml"),
], stock_minimo=1)

# Vitamina C inyectable
vit_c = insumo("Vitamina C inyectable 1cc", "medicamento", "cc", [
    (O, 8000, 1, "Ampolla 1cc"),
], stock_minimo=5)

mesobasic = insumo("Mesobasic solution 1cc", "medicamento", "cc", [
    (O, 25000, 1, "Por cc — cotizar"),
], stock_minimo=2)

mesoterapia_mediderma = insumo("Mesoterapia Mediderma 3cc", "medicamento", "cc", [
    (M, 45000, 1, "Por cc"),
], stock_minimo=2)

kenacort = insumo("Kenacort (triamcinolona) ampolla", "medicamento", "unidad", [
    (O, 22000, 1, "Por ampolla"),
], stock_minimo=3)

procaina_10cc = insumo("Procaína 1% ampolla 10ml", "medicamento", "ml", [
    (O, 12000, 10, "Ampolla 10ml"),
], stock_minimo=2)

# Radiofrecuencia
crema_rf = insumo("Crema conductora para radiofrecuencia", "medicamento", "por paciente", [
    (O, 15000, 1, "Por aplicación"),
], stock_minimo=5)

toalla_z = insumo("Toalla tipo Z desechable", "aseo", "unidad", [
    (O, 1500, 1, "Por unidad"),
], stock_minimo=10)

# Depilación láser
gel_ultrasonido = insumo("Gel ultrasonido incoloro", "medicamento", "cc", [
    (O, 18000, 1000, "Litro — precio por cc"),
], stock_minimo=200)

gel_post_depilacion = insumo("Gel post-depilación aplicación", "medicamento", "aplicación", [
    (O, 3000, 1, "Por aplicación"),
], stock_minimo=5)

# Alidya
alidya = insumo("Alidya (anticelulítico inyectable)", "medicamento", "ampolla", [
    (O, 240000, 1, "Por vial — precio estimado, verificar INVIMA"),
], stock_minimo=2)

# Escleroterapia
sklerol = insumo("Sklerol 2cc (escleroterapia)", "medicamento", "cc", [
    (O, 80000, 2, "Ampolla 2cc"),
], stock_minimo=4)

# Tricología
meso_ox_hair = insumo("Meso ox Hair 2.5ml", "medicamento", "ml", [
    (S, 108000, 5, "Caja 5 viales x 5ml"),
], stock_minimo=1)

dutasteride = insumo("Dutasteride 1ml (inhibidor hormonal)", "medicamento", "ml", [
    (O, 45000, 1, "Por ampolla 1ml"),
], stock_minimo=2)

exosomas_capilar = insumo("Exosomas capilares 1ml", "medicamento", "ml", [
    (S, 132000, 1, "Por ml"),
], stock_minimo=1)

hr3_sesion = insumo("HR3 fototerapia capilar (sesión 15 min)", "equipo", "sesión", [
    (O, 15000, 1, "Por sesión"),
], stock_minimo=0)

hairox_serum = insumo("Hair ox serum 5cc", "medicamento", "cc", [
    (S, 108000, 5, "Caja 5 viales x 5ml"),
], stock_minimo=1)

tubo_azul = insumo("Tubo tapa azul (PRP)", "medico", "unidad", [
    (J, 83300, 100, "Caja 100 uds"),
], stock_minimo=10)

hisopo = insumo("Hisopo estéril", "medico", "unidad", [
    (O, 500, 1, "Por unidad"),
], stock_minimo=10)

# Sesiones de equipos
fotoage_sesion = insumo("Fotoage LED (sesión 15 min)", "equipo", "sesión", [
    (O, 10000, 1, "Por sesión"),
], stock_minimo=0)

carboxiterapia_sesion = insumo("Carboxiterapia (sesión)", "equipo", "sesión", [
    (O, 25000, 1, "Por sesión"),
], stock_minimo=0)

rf_sesion = insumo("Radiofrecuencia sesión 30 min", "equipo", "sesión", [
    (O, 25000, 1, "Por sesión"),
], stock_minimo=0)

# Oculares (ptosis)
protectores_oculares = insumo("Protectores oculares desechables (par)", "medico", "par", [
    (O, 5000, 1, "Por par"),
], stock_minimo=5)

anestesia_ocular = insumo("Anestesia ocular (proparacaína gotas)", "medicamento", "frasco", [
    (O, 18000, 1, "Frasco 5ml"),
], stock_minimo=2)

gotas_oculares = insumo("Gotas oculares lubricantes", "medicamento", "frasco", [
    (O, 12000, 1, "Frasco"),
], stock_minimo=2)

# Medicina alternativa
agujas_largas_acupuntura = insumo("Paquete agujas largas acupuntura", "medico", "paquete", [
    (O, 15000, 1, "Paquete de agujas"),
], stock_minimo=5)

agujas_pequenas_acupuntura = insumo("Paquete agujas pequeñas acupuntura", "medico", "paquete", [
    (O, 8000, 1, "Paquete de agujas"),
], stock_minimo=5)

ampolla_celulas_madre = insumo("Ampolla células madre / factor de crecimiento", "medicamento", "ampolla", [
    (O, 500000, 1, "Por ampolla — cotizar proveedor especializado"),
], stock_minimo=1)

agua_esteril = insumo("Agua estéril 10cc", "medicamento", "cc", [
    (O, 5000, 10, "Ampolla 10cc"),
], stock_minimo=10)

ah_articular = insumo("Ácido hialurónico articular (Synvisc/similar)", "medicamento", "jeringa", [
    (O, 350000, 1, "Por jeringa — cotizar proveedor"),
], stock_minimo=1)

curas = insumo("Curas adhesivas", "medico", "unidad", [
    (J, 5000, 100, "Caja 100 uds"),
], stock_minimo=10)

punzon = insumo("Punzón para comedones", "medico", "unidad", [
    (O, 15000, 1, "Por unidad — reutilizable, precio esterilización"),
], stock_minimo=1)

brocha = insumo("Brocha/espátula desechable para mascarilla", "medico", "unidad", [
    (O, 800, 1, "Por unidad"),
], stock_minimo=10)

agua_bicarbonatada = insumo("Agua bicarbonatada 5ml", "medicamento", "ml", [
    (O, 3000, 5, "Por preparación 5ml"),
], stock_minimo=5)

# ============================================================
# SERVICIOS — Dra. María Fernanda Calderón
# ============================================================

def servicio(nombre, desc, margen, insumos_list, precio_mercado=None):
    srv = Servicio(
        id=uuid.uuid4(), espacio_id=eid, nombre=nombre, descripcion=desc,
        margen_ganancia_pct=margen, precio_mercado_referencia=precio_mercado, activo=True,
    )
    db.add(srv)
    db.flush()
    for ins, cantidad, notas in insumos_list:
        si = ServicioInsumo(id=uuid.uuid4(), servicio_id=srv.id, insumo_id=ins.id, cantidad=cantidad, notas=notas)
        db.add(si)
    db.flush()
    return srv


# --- Valoración ---
srv_valoracion = servicio(
    "Valoración medicina estética",
    "Diagnóstico estético y capilar integral",
    50,
    [
        (limpiador_tecnovital, 1, "1 paciente limpiador"),
        (panitos, 2, "2 pañitos húmedos"),
    ],
)

# --- Limpieza facial ---
srv_limpieza = servicio(
    "Limpieza facial medicalizada",
    "Limpieza facial profunda médica — 2-3 horas",
    50,
    [
        (guante_nitrilo, 2, "2 pares"),
        (tapabocas, 1, None),
        (gorro, 1, None),
        (panitos, 4, None),
        (gasas, 4, None),
        (agua_bicarbonatada, 5, "5ml"),
        (peeling_skymedic, 1, "1 paciente"),
        (serum_skymedic, 1, "1 paciente"),
        (mascarilla_tecnovital, 1, "1 paciente"),
        (limpiador_tecnovital, 1, "1 paciente"),
        (punzon, 1, None),
        (brocha, 1, None),
        (fotoage_sesion, 1, "15 min"),
    ],
)

# --- Toxina botulínica ---
srv_toxina = servicio(
    "Toxina botulínica (50U)",
    "Eliminación de líneas de expresión — 30 min",
    60,
    [
        (botox_100u, 50, "50 unidades Botox"),
        (jer_insulina, 5, "5 jeringas insulina 30UI"),
        (panitos, 2, None),
        (limpiador_tecnovital, 1, "1 paciente"),
        (balaca, 1, None),
        (guante_nitrilo, 1, "1 par"),
    ],
    precio_mercado=1200000,
)

# --- Ácido hialurónico (1-5 jeringas) ---
insumos_ah_base = [
    (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
    (panitos, 4, None), (limpiador_tecnovital, 1, "1 paciente"),
    (canula, 1, None), (jer1ml, 1, None), (lidocaina_sin, 5, "5ml"),
    (fotoage_sesion, 1, "15 min roja"),
]

def srv_ah(n_jeringas, precio=None):
    return servicio(
        f"Ácido hialurónico facial {n_jeringas} jeringa{'s' if n_jeringas > 1 else ''}",
        f"Relleno y armonización facial — 30-45 min",
        60,
        insumos_ah_base + [(ah_1ml, n_jeringas, f"{n_jeringas} jeringa(s) AH")],
        precio_mercado=precio,
    )

srv_ah1 = srv_ah(1, 1400000)
srv_ah2 = srv_ah(2, 2600000)
srv_ah3 = srv_ah(3, 3600000)
srv_ah4 = srv_ah(4, 4400000)
srv_ah5 = srv_ah(5, 5000000)

# --- Bioestimulador TKN HA3 ---
insumos_tkn_base = [
    (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
    (panitos, 4, None), (limpiador_tecnovital, 1, "1 paciente"),
    (canula, 1, None), (jer1ml, 1, None), (lidocaina_sin, 5, "5ml"),
    (fotoage_sesion, 1, "15 min roja"),
]

def srv_tkn(n):
    return servicio(
        f"Bioestimulador TKN HA3 — {n} jeringa{'s' if n > 1 else ''}",
        f"Rejuvenecimiento con colágeno natural — {'30' if n == 1 else '45'} min",
        55,
        insumos_tkn_base + [(tkn_ha3, n, f"{n} unidad(es) TKN HA3")],
    )

srv_tkn1 = srv_tkn(1)
srv_tkn2 = srv_tkn(2)

# --- Hidroxiapatita de calcio ---
def srv_hidrx(n):
    return servicio(
        f"Hidroxiapatita de calcio {n} jeringa{'s' if n > 1 else ''}",
        f"Rejuvenecimiento con colágeno natural — {'35' if n == 1 else '45'} min",
        55,
        insumos_tkn_base + [(hidroxiapatita, n, f"{n} jeringa(s) hidroxiapatita")],
    )

srv_hidrx1 = srv_hidrx(1)
srv_hidrx2 = srv_hidrx(2)

# --- Hilos tensores ---
srv_hilos = servicio(
    "Hilos tensores faciales/corporales",
    "Efecto lifting sin cirugía — 30-60 min",
    60,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 4, None), (limpiador_tecnovital, 1, "1 paciente"),
        (jer1ml, 1, None), (anestesia_topica, 1, "1 paciente"),
        (hilos_bioestimulacion, 1, "1 paquete hilos"),
    ],
)

# --- Lipopapada Aqualyx ---
insumos_lipo_base = [
    (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
    (panitos, 4, None), (jer1ml, 1, None), (jer5ml, 2, "2 jeringas 5ml"),
    (lidocaina_sin, 5, "5ml"), (alcohol, 10, "10ml"),
    (rf_sesion, 1, "1 sesión radiofrecuencia 30 min"),
    (carboxiterapia_sesion, 1, "1 sesión carboxiterapia"),
]

def srv_lipo(n_amp):
    return servicio(
        f"Lipopapada enzimática {n_amp} ampolla{'s' if n_amp > 1 else ''} Aqualyx",
        f"Reducción de papada sin cirugía — {'30' if n_amp == 1 else '45' if n_amp <= 3 else '60'} min",
        55,
        insumos_lipo_base + [(aqualyx, n_amp, f"{n_amp} ampolla(s) Aqualyx")],
    )

srv_lipo1 = srv_lipo(1)
srv_lipo2 = srv_lipo(2)
srv_lipo3 = srv_lipo(3)
srv_lipo4 = srv_lipo(4)

# --- Esperma de salmón ---
insumos_salmon_base = [
    (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
    (panitos, 4, None), (limpiador_tecnovital, 1, "1 paciente"),
    (jer3ml, 2, "2 jeringas 3ml"), (pdrn_salmon, 1, "1cc esperma de salmón"),
    (aguja18g, 1, "1 aguja 18G"), (llave_3vias, 1, None),
]

srv_salmon_jeringa = servicio(
    "Esperma de salmón con jeringa",
    "Regeneración celular avanzada — 45 min",
    55,
    insumos_salmon_base + [
        (aguja34g, 1, "1 aguja 34G"), (anestesia_topica, 1, "1 paciente"),
        (bajalenguas, 1, None),
    ],
)

srv_salmon_meso = servicio(
    "Esperma de salmón con mesoject gun",
    "Regeneración celular avanzada — 40 min",
    55,
    insumos_salmon_base + [(mesoject_gun, 1, "1 uso mesoject gun"), (bajalenguas, 1, None)],
)

srv_salmon_laser = servicio(
    "Esperma de salmón con láser CO2",
    "Regeneración celular avanzada — 1 hora",
    55,
    insumos_salmon_base + [(suero_sal_100, 1, "100ml solución salina"), (bajalenguas, 1, None)],
)

srv_salmon_nanopore = servicio(
    "Esperma de salmón con nanopore",
    "Regeneración celular avanzada — 35-40 min",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 2, None), (limpiador_tecnovital, 1, "1 paciente"),
        (jer3ml, 2, "2 jeringas 3ml"), (pdrn_salmon, 1, "1cc esperma de salmón"),
        (aguja18g, 1, None), (llave_3vias, 1, None),
        (aguja_nanopore, 1, "1 aguja nanopore"), (peeling_sesderma, 1, "1 paciente"),
        (gasas, 2, "2 gasas"),
    ],
)

# --- Exosomas faciales ---
def srv_exo(modo, minutos, insumos_extra):
    return servicio(
        f"Exosomas faciales con {modo}",
        f"Rejuvenecimiento celular facial — {minutos}",
        55,
        [
            (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
            (panitos, 4, None), (limpiador_tecnovital, 1, "1 paciente"),
            (jer3ml, 2, "2 jeringas 3ml"), (exosomas, 1, "1cc exosomas"),
            (aguja18g, 1, None), (llave_3vias, 1, None),
        ] + insumos_extra,
    )

srv_exo_jer = srv_exo("jeringa", "35 min", [(aguja34g, 1, "1 aguja 34G"), (anestesia_topica, 1, None), (bajalenguas, 1, None)])
srv_exo_meso = srv_exo("mesoject gun", "45 min", [(mesoject_gun, 1, None), (bajalenguas, 1, None)])
srv_exo_laser = srv_exo("láser CO2", "1 hora", [(suero_sal_100, 1, "100ml solución salina"), (bajalenguas, 1, None)])
srv_exo_nano = servicio(
    "Exosomas faciales con nanopore",
    "Rejuvenecimiento celular facial — 1 hora",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 2, None), (limpiador_tecnovital, 1, "1 paciente"),
        (jer3ml, 2, "2 jeringas 3ml"), (exosomas, 1, "1cc exosomas"),
        (aguja18g, 1, None), (llave_3vias, 1, None),
        (aguja_nanopore, 1, None), (peeling_sesderma, 1, None), (gasas, 2, None),
    ],
)

# --- Peeling ---
srv_peeling = servicio(
    "Peeling facial/corporal",
    "Renovación profunda de la piel — 30 min",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 2, None), (limpiador_tecnovital, 1, "1 paciente"),
        (gasas, 6, "6 gasas"), (peeling_skymedic, 1, "1 paciente"),
        (serum_skymedic, 1, "1 paciente"), (fotoage_sesion, 1, "15 min"),
    ],
)

# --- Mesoterapia periocular ---
srv_meso_periocular = servicio(
    "Mesoterapia periocular",
    "Rejuvenecimiento de ojeras — 40 min",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 2, None), (limpiador_tecnovital, 1, "1 paciente"),
        (meso_ox, 1, "1 ampolla Hydralight o meso Skymedic"),
    ],
)

# --- Cicatrices ---
insumos_cicatrices_base = [
    (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
    (panitos, 2, None), (limpiador_tecnovital, 1, "1 paciente"),
    (jer1ml, 1, None), (fotoage_sesion, 1, "15 min"),
]

srv_cicatriz_kenacort = servicio(
    "Tratamiento cicatrices Kenacort",
    "Corrección y mejora de cicatrices — 30 min",
    55,
    insumos_cicatrices_base + [(kenacort, 1, "1 ampolla kenacort"), (aguja30g, 1, "1 aguja 30G x 1/2")],
)

srv_cicatriz_procaina = servicio(
    "Tratamiento cicatrices Procaína",
    "Corrección y mejora de cicatrices — 30 min",
    55,
    insumos_cicatrices_base + [(procaina_10cc, 5, "5cc procaína"), (aguja30g, 1, "1 aguja 30G x 1/2")],
)

# --- Nanopore ---
srv_nanopore = servicio(
    "Nanopore",
    "Bioestimulación facial con microcanales — 1 hora",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 2, None), (limpiador_tecnovital, 1, "1 paciente"),
        (gasas, 4, "4 gasas"), (peeling_sesderma, 1, "1 paciente"),
        (jer3ml, 1, None), (aguja_nanopore, 1, "1 aguja nanopore"),
        (vit_c, 1, "1cc vitamina C"), (mesobasic, 1, "1cc mesobasic solution"),
        (mesoterapia_mediderma, 3, "3cc mesoterapia Mediderma"),
        (fotoage_sesion, 1, "15 min"),
    ],
)

# --- Láser CO2 retiro lesiones ---
def srv_laser_lesiones(rango, n_panitos, n_lidocaina, n_anestesia, precio=None):
    return servicio(
        f"Láser CO2 retiro lesiones {rango}",
        f"Eliminación de lesiones de la piel",
        55,
        [
            (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
            (panitos, n_panitos, None), (limpiador_tecnovital, 1, "1 paciente"),
            (bata, 1, None), (polainas, 1, "1 par"),
            (jer1ml, 1, None), (lidocaina_sin, n_lidocaina, f"{n_lidocaina}ml"),
            (anestesia_topica, n_anestesia, f"{n_anestesia} paciente(s)"),
            (fotoage_sesion, 1, "15 min"),
            (bajalenguas, 1, None), (escobillon, 2, "2 escobillones"),
        ],
        precio_mercado=precio,
    )

srv_laser_l1 = srv_laser_lesiones("0-10", 4, 5, 1, 600000)
srv_laser_l2 = srv_laser_lesiones("11-20", 4, 5, 1, 900000)
srv_laser_l3 = srv_laser_lesiones("21-30", 6, 10, 2, 1200000)
srv_laser_l4 = srv_laser_lesiones("31-50", 6, 10, 2, 1600000)

# --- Láser CO2 rejuvenecimiento ---
srv_laser_rejuv = servicio(
    "Láser CO2 rejuvenecimiento facial/corporal",
    "Rejuvenecimiento láser avanzado — 1 hora",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 4, None), (limpiador_tecnovital, 1, "1 paciente"),
        (bata, 1, None), (polainas, 1, "1 par"),
        (jer1ml, 1, None), (lidocaina_sin, 5, "5ml"),
        (anestesia_topica, 1, "1 paciente"),
        (fotoage_sesion, 1, "15 min"),
        (bajalenguas, 1, None), (escobillon, 2, "2 escobillones"),
    ],
    precio_mercado=1800000,
)

srv_laser_intimo = servicio(
    "Láser CO2 rejuvenecimiento íntimo",
    "Rejuvenecimiento íntimo femenino — 45 min",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 4, None), (bata, 1, None), (polainas, 1, "1 par"),
        (anestesia_topica, 1, "1 paciente"),
        (glutaraldehido, 50, "50ml glutaraldehído"),
    ],
)

# --- Protocolo Exoscar ---
srv_exoscar = servicio(
    "Protocolo Exoscar cicatrices",
    "Corrección láser de cicatrices — 1 hora",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 5, None), (limpiador_tecnovital, 1, "1 paciente"),
        (bata, 1, None), (polainas, 1, "1 par"),
        (jer1ml, 1, None), (lidocaina_sin, 5, "5ml"),
        (anestesia_topica, 1, "1 paciente"), (canula, 1, None),
        (exosomas, 1, "1cc exosomas"), (carboxiterapia_sesion, 1, "1 aplicación"),
        (fotoage_sesion, 1, "15 min"),
        (bajalenguas, 1, None), (escobillon, 2, "2 escobillones"),
    ],
)

# --- Radiofrecuencia ---
srv_radiofrecuencia = servicio(
    "Radiofrecuencia monopolar facial/corporal",
    "Reafirmación y tensado de la piel — 30-60 min",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 5, None), (limpiador_tecnovital, 1, "facial"),
        (bata, 1, None), (polainas, 1, "1 par"),
        (crema_rf, 1, "1 paciente crema RF"), (alcohol, 5, "5cc"),
        (toalla_z, 2, "2 toallas tipo Z"),
    ],
)

# --- Carboxiterapia ---
srv_carboxiterapia = servicio(
    "Carboxiterapia facial/corporal",
    "Oxigenación y regeneración — 15 min",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 2, None), (bata, 1, None), (polainas, 1, "1 par"),
        (aguja27g, 1, "1 aguja 27G x 1/2"), (alcohol, 5, "5cc"),
    ],
)

# --- Depilación láser ---
srv_depilacion = servicio(
    "Depilación láser diodo 808nm",
    "Depilación láser permanente — Variable",
    60,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 2, None), (bata, 1, None),
        (gel_ultrasonido, 10, "10cc gel ultrasonido"),
        (gel_post_depilacion, 2, "2 aplicaciones"),
        (toalla_z, 2, "2 toallas tipo Z"), (alcohol, 5, "5cc"),
    ],
)

# --- Manejo celulitis Alidya ---
insumos_alidya_base = [
    (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
    (panitos, 4, None), (jer1ml, 1, None), (jer5ml, 2, "2 jeringas 5ml"),
    (lidocaina_sin, 5, "5ml"), (alcohol, 10, "10ml"),
]

def srv_alidya(n_amp):
    return servicio(
        f"Manejo celulitis {n_amp} ampolla{'s' if n_amp > 1 else ''} Alidya",
        f"Tratamiento anticelulitis — {'30' if n_amp == 1 else '45' if n_amp <= 3 else '60'} min",
        55,
        insumos_alidya_base + [(alidya, n_amp, f"{n_amp} ampolla(s) Alidya")],
    )

srv_alidya1 = srv_alidya(1)
srv_alidya2 = srv_alidya(2)
srv_alidya3 = srv_alidya(3)
srv_alidya4 = srv_alidya(4)

# --- Ptosis palpebral ---
srv_ptosis = servicio(
    "Manejo ptosis palpebral",
    "Rejuvenecimiento de párpados — 45 min",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 4, None), (limpiador_tecnovital, 1, "1 paciente"),
        (bata, 1, None), (polainas, 1, "1 par"),
        (jer1ml, 1, None), (lidocaina_sin, 5, "5ml"),
        (anestesia_topica, 1, "1 paciente"),
        (fotoage_sesion, 1, "15 min"),
        (bajalenguas, 1, None), (escobillon, 2, "2 escobillones"),
        (glutaraldehido, 20, "20cc glutaraldehído"),
        (protectores_oculares, 1, "1 par"),
        (anestesia_ocular, 1, "1 aplicación"),
        (gotas_oculares, 1, "1 aplicación"),
    ],
)

# ---- CIRUGÍA VASCULAR ----
srv_consulta_vascular = servicio(
    "Consulta externa cirugía vascular",
    "Valoración vascular especializada",
    70,
    [(guante_nitrilo, 1, "1 par"), (panitos, 2, None)],
)

insumos_escleroterapia_base = [
    (guante_nitrilo, 1, "1 par"), (tapabocas, 1, None),
    (panitos, 2, None), (bata, 1, None), (jer3ml, 1, None),
    (micropore, 0.05, "Micropore"), (algodon, 20, "20 algodones"),
]

def srv_escleroterapia(n_amp):
    return servicio(
        f"Escleroterapia {n_amp} ampolla{'s' if n_amp > 1 else ''}",
        f"Eliminación de arañitas vasculares — {'30' if n_amp == 1 else '45' if n_amp <= 3 else '60'} min",
        60,
        insumos_escleroterapia_base + [
            (sklerol, n_amp * 2, f"{n_amp * 2}cc Sklerol"),
            (suero_sal_100, n_amp, f"{n_amp}x10cc solución salina"),
        ],
    )

srv_escle1 = srv_escleroterapia(1)
srv_escle2 = srv_escleroterapia(2)
srv_escle3 = srv_escleroterapia(3)
srv_escle4 = srv_escleroterapia(4)

# ---- GINECOLOGÍA ----
srv_consulta_gineco = servicio(
    "Consulta externa ginecología",
    "Consulta ginecológica integral",
    70,
    [(guante_nitrilo, 1, "1 par"), (panitos, 2, None)],
)

srv_citologia = servicio(
    "Citología",
    "Citología para prevención cervical — 15 min",
    60,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 4, None), (bata, 1, None), (polainas, 1, "1 par"),
        (kit_citologia, 1, "1 kit"),
    ],
)

srv_laser_vaginal = servicio(
    "Láser CO2 rejuvenecimiento vaginal",
    "Rejuvenecimiento vaginal láser",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 4, None), (bata, 1, None), (polainas, 1, "1 par"),
        (anestesia_topica, 1, "1 paciente"),
        (glutaraldehido, 50, "50ml glutaraldehído"),
    ],
)

srv_laser_incontinencia = servicio(
    "Láser CO2 incontinencia urinaria",
    "Tratamiento láser para escapes de orina — 45 min",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (gorro, 1, None), (tapabocas, 1, None),
        (panitos, 4, None), (bata, 1, None), (polainas, 1, "1 par"),
        (anestesia_topica, 1, "1 paciente"),
        (glutaraldehido, 50, "50ml glutaraldehído"),
    ],
)

# ---- MEDICINA ALTERNATIVA ----
srv_consulta_alt = servicio(
    "Consulta medicina alternativa",
    "Bienestar integral y terapias complementarias — 1.5 horas",
    70,
    [(guante_nitrilo, 1, "1 par"), (panitos, 2, None)],
)

srv_consulta_funcional = servicio(
    "Consulta medicina funcional",
    "Medicina funcional personalizada — 1.5 horas",
    70,
    [(guante_nitrilo, 1, "1 par"), (panitos, 2, None)],
)

srv_terapia_neural = servicio(
    "Terapia neural",
    "Regulación del sistema nervioso",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (tapabocas, 1, None), (panitos, 4, None),
        (jer3ml, 1, None), (aguja30g, 2, "2 agujas 30G x 1/2"),
        (procaina_10cc, 10, "10cc procaína"), (alcohol, 10, "10cc"),
    ],
)

srv_acupuntura = servicio(
    "Acupuntura",
    "Equilibrio energético y alivio del dolor",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (tapabocas, 1, None), (panitos, 4, None),
        (bata, 1, None), (agujas_largas_acupuntura, 4, "4 paquetes agujas largas"),
        (agujas_pequenas_acupuntura, 2, "2 paquetes agujas pequeñas"),
        (alcohol, 10, "10cc"),
    ],
)

srv_sueroterapia = servicio(
    "Sueroterapia dirigida",
    "Vitaminas y revitalización intravenosa",
    55,
    [
        (suero_sal_100, 1, "100-500cc según indicación"), (cateter24, 1, "catéter #24"),
        (macrogoteo, 1, None), (micropore, 0.1, "Micropore"),
        (algodon, 2, "2 algodones"), (alcohol, 5, "5cc"),
        (torniquete, 1, None), (jer5ml, 1, "jeringa 5 o 10ml"),
    ],
)

srv_bioestim_articular = servicio(
    "Bioestimulación articular ácido hialurónico",
    "Lubricación y bienestar articular",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (tapabocas, 1, None), (gasas, 4, "4 gasas"),
        (bata, 1, None), (aguja21g, 1, "1 aguja 21G x 1/2"),
        (alcohol, 10, "10cc"), (curas, 1, "1-2 curitas"),
        (ah_articular, 1, "1 ácido hialurónico articular"),
    ],
)

srv_celulas_madre = servicio(
    "Células madre",
    "Medicina regenerativa avanzada",
    60,
    [
        (guante_nitrilo, 1, "1 par"), (tapabocas, 1, None),
        (jer10ml, 1, "1 jeringa 10ml"), (curas, 1, None),
        (algodon, 2, "2 algodones"), (alcohol, 2, "2cc"),
        (agua_esteril, 10, "10cc agua estéril"), (ampolla_celulas_madre, 1, "1 ampolla"),
    ],
)

srv_obesidad_1m = servicio(
    "Tratamiento obesidad seguimiento 1 mes",
    "Control médico del peso — 1 mes",
    70,
    [(guante_nitrilo, 1, "1 par"), (panitos, 2, None)],
)

srv_obesidad_2m = servicio(
    "Tratamiento obesidad seguimiento 2 meses",
    "Control médico del peso — 2 meses",
    70,
    [(guante_nitrilo, 1, "1 par"), (panitos, 2, None)],
)

# ---- PSICOLOGÍA ----
srv_valoracion_psi = servicio(
    "Valoración psicológica primera vez",
    "Evaluación psicológica inicial — 1 hora",
    80,
    [],
)

srv_consulta_psi = servicio(
    "Consulta de seguimiento psicológica",
    "Acompañamiento psicológico continuo — 1 hora",
    80,
    [],
)

# ---- TRICOLOGÍA ----
srv_valoracion_trico = servicio(
    "Valoración tricología",
    "Diagnóstico especializado del cabello — 30 min",
    60,
    [
        (guante_nitrilo, 1, "1 par"), (tapabocas, 1, None),
        (panitos, 4, None), (limpiador_tecnovital, 1, "1 paciente"),
    ],
)

insumos_meso_capilar_base = [
    (guante_nitrilo, 1, "1 par"), (tapabocas, 1, None), (panitos, 4, None),
    (jer3ml, 1, None), (tubo_azul, 4, "4 tubos azules"),
    (anestesia_topica, 1, "1 paciente anestesia tópica líquida"),
    (hisopo, 2, "2 hisopos"), (alcohol, 10, "10ml"),
    (hr3_sesion, 1, "HR3 15 minutos"), (hairox_serum, 5, "Hair ox serum 5cc"),
]

srv_meso_capilar_multi = servicio(
    "Mesoterapia capilar multivitamínicos",
    "Nutrición y fortalecimiento capilar",
    55,
    insumos_meso_capilar_base + [
        (meso_ox_hair, 2.5, "2.5ml meso ox hair"), (aguja34g, 1, "1 aguja 34G"),
    ],
)

srv_meso_capilar_hormonal = servicio(
    "Mesoterapia capilar inhibidor hormonal",
    "Control de caída capilar hormonal",
    55,
    insumos_meso_capilar_base + [
        (dutasteride, 1, "1ml dutasteride"), (aguja34g, 1, "1 aguja 34G"),
    ],
)

srv_exo_capilar = servicio(
    "Exosomas capilares",
    "Regeneración capilar avanzada",
    55,
    insumos_meso_capilar_base + [
        (exosomas_capilar, 1, "1ml exosomas capilares"), (aguja34g, 1, "1 aguja 34G"),
    ],
)

srv_prp_capilar = servicio(
    "Plasma rico en plaquetas capilar (PRP)",
    "Bioestimulación para crecimiento capilar",
    55,
    [
        (guante_nitrilo, 1, "1 par"), (tapabocas, 1, None), (panitos, 4, None),
        (jer3ml, 1, None), (tubo_azul, 4, "4 tubos azules"),
        (anestesia_topica, 1, "1 paciente anestesia tópica líquida"),
        (hisopo, 2, "2 hisopos"), (alcohol, 10, "10ml"),
        (hr3_sesion, 1, "HR3 15 minutos"), (hairox_serum, 5, "Hair ox serum 5cc"),
    ],
)

# ============================================================
# PAQUETES PREDEFINIDOS
# ============================================================

def paquete(nombre, desc, servs_list):
    pak = Paquete(id=uuid.uuid4(), espacio_id=eid, nombre=nombre, descripcion=desc, activo=True)
    db.add(pak)
    db.flush()
    for srv in servs_list:
        ps = PaqueteServicio(id=uuid.uuid4(), paquete_id=pak.id, servicio_id=srv.id)
        db.add(ps)
    db.flush()
    return pak


paquete(
    "Glow Reset",
    "Limpieza facial + Peeling + Nanopore + Exosomas + LED",
    [srv_limpieza, srv_peeling, srv_nanopore, srv_exo_jer, srv_radiofrecuencia],
)

paquete(
    "Skin Reboot 360",
    "Peeling medio + Nanopore + PRP capilar + Exosomas + Fototerapia",
    [srv_peeling, srv_nanopore, srv_prp_capilar, srv_exo_jer],
)

paquete(
    "Bye Wrinkles Premium",
    "Toxina botulínica 50U + Mesoterapia periocular",
    [srv_toxina, srv_meso_periocular],
)

paquete(
    "Regeneración Total",
    "Toxina 50U + AH 4 jeringas + Bioestimulador + Nanopore + Exosomas",
    [srv_toxina, srv_ah4, srv_tkn1, srv_nanopore, srv_exo_jer],
)

paquete(
    "Skin Prevent",
    "Mesoterapia periocular + Peeling",
    [srv_meso_periocular, srv_peeling],
)

paquete(
    "Hand Glow",
    "Peeling + Nanopore + Exosomas + Fototerapia",
    [srv_peeling, srv_nanopore, srv_exo_jer],
)

paquete(
    "Hand Rejuvenation Pro",
    "Radiofrecuencia + Nanopore + PRP + Fototerapia",
    [srv_radiofrecuencia, srv_nanopore, srv_prp_capilar],
)

paquete(
    "Hand Age Reverse",
    "Láser CO2 + Exosomas + Bioestimulador + Radiofrecuencia + Mesoterapia periocular",
    [srv_laser_rejuv, srv_exo_jer, srv_tkn1, srv_radiofrecuencia, srv_meso_periocular],
)

paquete(
    "Hand Tone Correct",
    "Peeling + Láser CO2 0-10 lesiones + Mesoterapia periocular",
    [srv_peeling, srv_laser_l1, srv_meso_periocular],
)

db.commit()
print("Seed MF completado exitosamente.")
print(f"  Espacio: {espacio_mf.nombre}")
db.close()

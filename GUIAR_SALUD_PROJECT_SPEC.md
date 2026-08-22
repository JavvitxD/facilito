# SPEC: Facilito - Sistema de Inventario
## Plataforma de Gestión de Inventarios y Costos Médicos
**Cliente inicial:** Guiar Salud IPS  
**Versión:** 2.0 — Basada en documento Dra. María Fernanda Calderón  
**Fecha:** Junio 2026

---

## 1. CONTEXTO Y ARQUITECTURA

### Stack Tecnológico
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + Alembic
- **Frontend:** React 18 + Vite + Tailwind CSS + TypeScript
- **Base de datos:** PostgreSQL
- **Contenedor:** Docker + Docker Compose
- **Auth:** JWT con roles

### Estructura de Roles
```
Superadmin (Javier)
  └── Empresa: Guiar Salud IPS
        ├── Espacio: Dra. Estela Quintero
        └── Espacio: Dra. María Fernanda Calderón
```

### Modelo de Servicios
- **Servicio individual:** cada procedimiento con sus insumos y costo calculado
- **Paquete:** agrupación de servicios individuales que el médico arma libremente
- El sistema calcula el costo tanto por servicio individual como por paquete completo

---

## 2. ESPECIALIDADES Y SERVICIOS

### 2.1 Medicina Estética (Dra. María Fernanda Calderón)

| Servicio | Nombre Comercial | Duración |
|---|---|---|
| Valoración medicina estética | Diagnóstico estético y capilar integral | - |
| Limpieza facial medicalizada | Limpieza facial profunda médica | 2-3 horas |
| Toxina botulínica | Eliminación de líneas de expresión | 30 min |
| Ácido hialurónico facial 1 jeringa | Relleno y armonización facial | 30-45 min |
| Ácido hialurónico facial 2 jeringas | Relleno y armonización facial | 30-45 min |
| Ácido hialurónico facial 3 jeringas | Relleno y armonización facial | 30-45 min |
| Ácido hialurónico facial 4 jeringas | Relleno y armonización facial | 30-45 min |
| Ácido hialurónico facial 5 jeringas | Relleno y armonización facial | 30-45 min |
| Bioestimulador TKN HA3 - 1 jeringa | Rejuvenecimiento con colágeno natural | 30 min |
| Bioestimulador TKN HA3 - 2 jeringas | Rejuvenecimiento con colágeno natural | 45 min |
| Hidroxiapatita de calcio 1 jeringa | Rejuvenecimiento con colágeno natural | 35 min |
| Hidroxiapatita de calcio 2 jeringas | Rejuvenecimiento con colágeno natural | 45 min |
| Hilos tensores faciales/corporales | Efecto lifting sin cirugía | 30-60 min |
| Lipopapada enzimática 1 ampolla Aqualyx | Reducción de papada sin cirugía | 30 min |
| Lipopapada enzimática 2 ampollas Aqualyx | Reducción de papada sin cirugía | 45 min |
| Lipopapada enzimática 3 ampollas Aqualyx | Reducción de papada sin cirugía | 45 min |
| Lipopapada enzimática 4 ampollas Aqualyx | Reducción de papada sin cirugía | 1 hora |
| Esperma de salmón con jeringa | Regeneración celular avanzada | 45 min |
| Esperma de salmón con mesoject gun | Regeneración celular avanzada | 40 min |
| Esperma de salmón con láser CO2 | Regeneración celular avanzada | 1 hora |
| Esperma de salmón con nanopore | Regeneración celular avanzada | 35-40 min |
| Exosomas faciales con jeringa | Rejuvenecimiento celular facial | 35 min |
| Exosomas faciales con mesoject gun | Rejuvenecimiento celular facial | 45 min |
| Exosomas faciales con láser CO2 | Rejuvenecimiento celular facial | 1 hora |
| Exosomas faciales con nanopore | Rejuvenecimiento celular facial | 1 hora |
| Peeling facial/corporal | Renovación profunda de la piel | 30 min |
| Mesoterapia periocular | Rejuvenecimiento de ojeras | 40 min |
| Tratamiento cicatrices kenacort | Corrección y mejora de cicatrices | 30 min |
| Tratamiento cicatrices procaína | Corrección y mejora de cicatrices | 30 min |
| Nanopore | Bioestimulación facial con microcanales | 1 hora |
| Láser CO2 retiro lesiones 0-10 | Eliminación de lesiones de la piel | 35 min |
| Láser CO2 retiro lesiones 11-20 | Eliminación de lesiones de la piel | 45 min |
| Láser CO2 retiro lesiones 21-30 | Eliminación de lesiones de la piel | 1 hora |
| Láser CO2 retiro lesiones 31-50 | Eliminación de lesiones de la piel | 2 horas |
| Láser CO2 rejuvenecimiento facial/corporal | Rejuvenecimiento láser avanzado | 1 hora |
| Láser CO2 rejuvenecimiento íntimo | Rejuvenecimiento íntimo femenino | 45 min |
| Protocolo Exoscar cicatrices | Corrección láser de cicatrices | 1 hora |
| Radiofrecuencia monopolar facial/corporal | Reafirmación y tensado de la piel | 30-60 min |
| Carboxiterapia facial/corporal | Oxigenación y regeneración | 15 min |
| Depilación láser diodo 808nm | Depilación láser permanente | Variable |
| Manejo celulitis 1 ampolla Alidya | Tratamiento anticelulitis | 30 min |
| Manejo celulitis 2 ampollas Alidya | Tratamiento anticelulitis | 45 min |
| Manejo celulitis 3 ampollas Alidya | Tratamiento anticelulitis | 45 min |
| Manejo celulitis 4 ampollas Alidya | Tratamiento anticelulitis | 1 hora |
| Manejo ptosis palpebral | Rejuvenecimiento de párpados | 45 min |

### 2.2 Cirugía Vascular
| Servicio | Nombre Comercial | Duración |
|---|---|---|
| Consulta externa | Valoración vascular especializada | - |
| Escleroterapia 1 ampolla | Eliminación de arañitas vasculares | 30 min |
| Escleroterapia 2 ampollas | Eliminación de arañitas vasculares | 45 min |
| Escleroterapia 3 ampollas | Eliminación de arañitas vasculares | 45 min |
| Escleroterapia 4 ampollas | Eliminación de arañitas vasculares | 1 hora |

### 2.3 Ginecología
| Servicio | Nombre Comercial | Duración |
|---|---|---|
| Consulta externa | Consulta ginecológica integral | - |
| Citología | Citología para prevención cervical | 15 min |
| Láser CO2 rejuvenecimiento vaginal | Rejuvenecimiento vaginal láser | - |
| Láser CO2 incontinencia urinaria | Tratamiento láser para escapes de orina | 45 min |

### 2.4 Medicina Alternativa
| Servicio | Nombre Comercial | Duración |
|---|---|---|
| Consulta medicina alternativa | Bienestar integral y terapias complementarias | 1.5 horas |
| Consulta medicina funcional | Medicina funcional personalizada | 1.5 horas |
| Terapia neural | Regulación del sistema nervioso | - |
| Acupuntura | Equilibrio energético y alivio del dolor | - |
| Sueroterapia dirigida | Vitaminas y revitalización intravenosa | - |
| Bioestimulación articular ácido hialurónico | Lubricación y bienestar articular | - |
| Células madre | Medicina regenerativa avanzada | - |
| Tratamiento obesidad seguimiento 1 mes | Control médico del peso | - |
| Tratamiento obesidad seguimiento 2 meses | Control médico del peso | - |

### 2.5 Psicología
| Servicio | Nombre Comercial | Duración |
|---|---|---|
| Valoración primera vez | Evaluación psicológica inicial | 1 hora |
| Consulta de seguimiento | Acompañamiento psicológico continuo | 1 hora |

### 2.6 Tricología
| Servicio | Nombre Comercial | Duración |
|---|---|---|
| Valoración tricología | Diagnóstico especializado del cabello | 30 min |
| Mesoterapia capilar multivitamínicos | Nutrición y fortalecimiento capilar | - |
| Mesoterapia inhibidor hormonal | Control de caída capilar hormonal | - |
| Exosomas capilares | Regeneración capilar avanzada | - |
| Plasma rico en plaquetas capilar | Bioestimulación para crecimiento capilar | - |
| Trasplante capilar | - | - |

### 2.7 Protocolos / Paquetes Predefinidos
| Paquete | Servicios que lo componen |
|---|---|
| Glow Reset | Limpieza facial + Peeling + Microagujas + PDRN/Exosomas + LED |
| Skin Reboot 360 | Peeling medio + Microneedling + PRP + PDRN + Fototerapia |
| Bye Wrinkles Premium | Toxina botulínica 50U + Meso ox hidralight |
| Regeneración Total | Toxina 50U + AH 4 jeringas + Bioestimulador + Láser/Microagujas + Exosomas |
| Skin Prevent | Mesoject gun + Meso ox hidralight |
| Hand Glow | Peeling + Microneedling + PDRN/Exosomas + Fototerapia |
| Hand Rejuvenation Pro | Radiofrecuencia + Nanopore + Meso ox white + PRP + Fototerapia |
| Hand Age Reverse | Láser CO2 + PRP + Exosomas + Bioestimulador + PDRN + RF + Mesoterapia |
| Hand Tone Correct | Peeling despigmentante + Láser/IPL + Mesoterapia despigmentante |

---

## 3. INSUMOS POR SERVICIO

### MEDICINA ESTÉTICA

#### Valoración de medicina estética y tricología
- 1 limpiador facial
- 2 pañitos húmedos

#### Limpieza facial medicalizada
- 2 pares guantes nitrilo o látex
- 1 tapabocas
- 1 gorro tipo oruga
- 4 pañitos húmedos
- 4 gasas
- 5ml agua bicarbonatada
- 1 paciente peeling Skymedic
- 1 paciente serum Skymedic
- 1 paciente mascarilla Tecnovital
- 1 paciente limpiador Tecnovital
- 1 punzón
- 1 brocha o espátula
- Fotoage 15 minutos

#### Toxina botulínica
- 50 unidades toxina botulínica
- 5 jeringas insulina 30UI
- 2 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 1 balaca
- 1 par guantes nitrilo o látex

#### Ácido hialurónico facial (base — varía solo en cantidad de AH)
- 1 par guantes nitrilo o látex
- 1 gorro tipo oruga
- 1 tapabocas
- 4 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 1 cánula
- 1 jeringa 1ml
- 5ml lidocaína sin epinefrina
- N jeringas de AH (1 a 5 según variante)
- Fotoage roja 15 minutos

#### Bioestimulador TKN HA3 (base — varía en cantidad)
- 1 par guantes nitrilo o látex
- 1 gorro tipo oruga, 1 tapabocas
- 4 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 1 cánula, 1 jeringa 1ml
- 5ml lidocaína sin epinefrina
- N unidades TKN HA3
- Fotoage roja 15 minutos

#### Hidroxiapatita de calcio (base)
- Iguales a TKN HA3, reemplazando con N jeringas de hidroxiapatita

#### Hilos tensores faciales/corporales
- 1 par guantes nitrilo o látex
- 1 gorro tipo oruga, 1 tapabocas
- 4 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 1 jeringa 1ml
- 1 paciente anestesia tópica
- 1 paquete hilos de bioestimulación

#### Lipopapada enzimática Aqualyx (base — varía en ampollas)
- 1 par guantes nitrilo o látex
- 1 gorro tipo oruga, 1 tapabocas
- 4 pañitos húmedos
- 1 jeringa 1ml + 2 jeringas 5ml
- 5ml lidocaína sin epinefrina
- N ampollas Aqualyx
- 10ml alcohol
- 1 sesión radiofrecuencia 30 min
- 1 sesión carboxiterapia

#### Esperma de salmón — con jeringa
- 1 par guantes nitrilo o látex
- 1 gorro tipo oruga, 1 tapabocas
- 4 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 2 jeringas 3ml
- 1cc esperma de salmón
- 1 aguja 18G
- 1 llave 3 vías
- 1 aguja 34G
- 1 paciente anestesia tópica
- 1 bajalenguas

#### Esperma de salmón — con mesoject gun
- (igual al anterior, reemplaza aguja 34G + anestesia tópica por 1 dispositivo facial mesoject gun)

#### Esperma de salmón — con láser CO2
- (igual base, reemplaza aguja 34G y anestesia tópica por 1 solución salina 100ml)

#### Esperma de salmón — nanopore
- 1 par guantes nitrilo o látex
- 1 gorro tipo oruga, 1 tapabocas
- 2 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 2 jeringas 3ml, 1cc esperma de salmón
- 1 aguja 18G, 1 llave 3 vías
- 1 aguja nanopore
- 1 peeling Sesderma
- 2 gasas

#### Exosomas faciales (misma estructura que esperma de salmón, reemplazando producto)

#### Peeling facial/corporal
- 1 par guantes nitrilo o látex
- 1 gorro tipo oruga, 1 tapabocas
- 2 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 6 gasas
- 1 paciente peeling Skymedic
- 1 paciente serum Skymedic
- Fotoage 15 minutos

#### Mesoterapia periocular
- 1 par guantes, 1 gorro, 1 tapabocas
- 2 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 1 ampolla Hydralight o mesoterapia Skymedic

#### Tratamiento cicatrices — Kenacort
- 1 par guantes, 1 gorro, 1 tapabocas
- 2 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 1 jeringa 1ml, 1 ampolla kenacort
- 1 aguja 30G x ½
- Fotoage 15 minutos

#### Tratamiento cicatrices — Procaína
- (igual, reemplaza kenacort por 5cc procaína)

#### Nanopore
- 1 par guantes, 1 gorro, 1 tapabocas
- 2 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 4 gasas, 1 peeling Sesderma
- 1 jeringa 3ml, 1 aguja nanopore
- 1cc vitamina C, 1cc mesobasic solution
- 3cc mesoterapia Mediderma
- Fotoage 15 minutos

#### Láser CO2 retiro lesiones (base — varía pañitos y anestesia según rango)
- 1 par guantes, 1 gorro, 1 tapabocas
- N pañitos húmedos (4-6 según variante)
- 1 paciente limpiador Tecnovital
- 1 bata paciente, 1 par polainas
- 1 jeringa 1ml
- N cc lidocaína sin epinefrina (5-10ml)
- N pacientes anestesia tópica
- Fotoage 15 minutos
- 1 bajalenguas, 2 escobillones

#### Láser CO2 rejuvenecimiento facial/corporal
- (igual a láser lesiones base con 5cc lidocaína, 1 anestesia tópica)

#### Láser CO2 rejuvenecimiento íntimo
- 1 par guantes, 1 gorro, 1 tapabocas
- 4 pañitos húmedos
- 1 bata paciente, 1 par polainas
- 1 paciente anestesia tópica
- 50ml glutaraldehído

#### Protocolo Exoscar
- 1 par guantes, 1 gorro, 1 tapabocas
- 5 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 1 bata paciente, 1 par polainas
- 1 jeringa 1ml, 5cc lidocaína sin epinefrina
- 1 paciente anestesia tópica
- 1 cánula, 1cc exosomas
- 1 aplicación carboxiterapia
- Fotoage 15 minutos
- 1 bajalenguas, 2 escobillones

#### Radiofrecuencia monopolar
- 1 par guantes, 1 gorro, 1 tapabocas
- 5 pañitos húmedos
- 1 paciente limpiador Tecnovital (si es facial)
- 1 bata paciente, 1 par polainas
- 1 crema radiofrecuencia
- 5cc alcohol
- 2 toallas tipo Z

#### Carboxiterapia
- 1 par guantes, 1 gorro, 1 tapabocas
- 2 pañitos húmedos
- 1 bata paciente, 1 par polainas
- 1 aguja 27G x ½
- 5cc alcohol

#### Depilación láser diodo 808nm
- 1 par guantes, 1 gorro, 1 tapabocas
- 2 pañitos húmedos
- 1 bata paciente
- 10cc gel ultrasonido incoloro
- 2 aplicaciones gel post depilación
- 2 toallas tipo Z
- 5cc alcohol

#### Manejo celulitis Alidya (base — varía en ampollas)
- 1 par guantes, 1 gorro, 1 tapabocas
- 4 pañitos húmedos
- 1 jeringa 1ml + 2 jeringas 5ml
- 5ml lidocaína sin epinefrina
- N ampollas Alidya
- 10ml alcohol

#### Manejo ptosis palpebral
- 1 par guantes, 1 gorro, 1 tapabocas
- 4 pañitos húmedos
- 1 paciente limpiador Tecnovital
- 1 bata paciente, 1 par polainas
- 1 jeringa 1ml, 5cc lidocaína sin epinefrina
- 1 paciente anestesia tópica
- Fotoage 15 minutos
- 1 bajalenguas, 2 escobillones
- 20cc glutaraldehído
- 1 par protectores oculares
- 1 anestesia ocular
- 1 gotas oculares

### CIRUGÍA VASCULAR

#### Escleroterapia (base — varía en ampollas Sklerol y solución salina)
- 1 par guantes nitrilo o látex
- 1 tapabocas
- 2 pañitos húmedos
- 1 bata paciente
- 1 jeringa 3ml
- Micropore
- 20 algodones pequeños
- N x 2cc Sklerol (2cc por ampolla)
- N x 10cc solución salina

### GINECOLOGÍA

#### Citología
- 1 par guantes, 1 gorro, 1 tapabocas
- 4 pañitos húmedos
- 1 bata paciente, 1 par polainas
- 1 kit de citología

#### Láser CO2 incontinencia urinaria
- 1 par guantes, 1 gorro, 1 tapabocas
- 4 pañitos húmedos
- 1 bata paciente, 1 par polainas
- 1 paciente anestesia tópica
- 50ml glutaraldehído

### MEDICINA ALTERNATIVA

#### Terapia neural
- 1 par guantes, 1 tapabocas
- 4 pañitos húmedos
- 1 jeringa 3ml
- 2 agujas 30G x ½
- 10cc procaína
- 10cc alcohol

#### Acupuntura
- 1 par guantes, 1 tapabocas
- 4 pañitos húmedos
- 1 bata paciente
- 4 paquetes agujas largas
- 2 paquetes agujas pequeñas
- 10cc alcohol

#### Sueroterapia dirigida
- Solución salina 100cc / 250cc / 500cc (según indicación)
- 1 catéter #24
- 1 macrogoteo
- Micropore
- 2 algodones
- 5cc alcohol
- 1 torniquete
- 1 jeringa 5ml o 10ml

#### Bioestimulación articular ácido hialurónico
- 1 par guantes, 1 tapabocas
- 4 gasas
- 1 bata paciente
- 1 aguja 21G x ½
- 10cc alcohol
- 1-2 curitas
- 1 ácido hialurónico articular

#### Células madre
- 1 par guantes, 1 tapabocas
- 1 jeringa 10ml
- 1 curita, 2 algodones
- 2cc alcohol
- 10cc agua estéril
- 1 ampolla

### TRICOLOGÍA

#### Mesoterapia capilar / Mesoterapia inhibidor hormonal / Exosomas capilares
- 1 par guantes, 1 tapabocas
- 4 pañitos húmedos
- 1 jeringa 3ml
- 4 tubos azules
- 1 paciente anestesia tópica líquida
- 2 hisopos
- Producto activo (2.5ml meso ox hair / 1ml dutasteride / 1ml exosomas)
- 10ml alcohol
- HR3 15 minutos
- Hair ox serum 5cc
- 1 aguja 34G (meso y exosomas)

#### Plasma rico en plaquetas capilar
- (igual a mesoterapia pero sin producto activo inyectable — usa PRP del paciente)

---

## 4. PRECIOS DE INSUMOS — INVESTIGACIÓN ONLINE 2026

### 4.1 Insumos del archivo Excel (Jaguar / Gloria — precios ya confirmados)

| Insumo | Precio unitario | Proveedor |
|---|---|---|
| Jeringa 1ml 27G | $142 | Gloria |
| Jeringa 1ml 27G | $250 | Jaguar |
| Jeringa 3ml 21G | $180 | Gloria |
| Jeringa 3ml 21G | $300 | Jaguar |
| Jeringa 5ml 21G | $135 | Gloria |
| Jeringa 5ml 21G | $300 | Jaguar |
| Jeringa 10ml 21G | $200 | Gloria |
| Jeringa 20ml 21G | $350 | Gloria |
| Aguja 18G x 1½ | $66 | Gloria |
| Aguja 18G x 1½ | $150 | Jaguar |
| Aguja 21G x 1½ | $150 | Jaguar |
| Aguja 22G x 1½ | $66 | Gloria |
| Aguja 30G x ½ | $116 | Gloria |
| Aguja 30G x ½ | $150 | Jaguar |
| Aguja 34G x 4mm | $2.720 | Dermavan |
| Gasa hospitalaria (unidad) | $47 | Gloria |
| Gasa hospitalaria (unidad) | $70 | Jaguar |
| Algodón (unidad) | $19 | Jaguar |
| Macrogoteo | $225 | Gloria |
| Macrogoteo | $1.300 | Jaguar |
| Catéter #24G Nipro | $1.700 | Gloria |
| Catéter #24G Precision | $1.800 | Jaguar |
| Cloruro sodio 0.9% 100ml | $2.800 | Gloria |
| Cloruro sodio 0.9% 250ml | $3.300 | Gloria |
| Cloruro sodio 0.9% 500ml | $3.100 | Gloria |
| Bata paciente desechable | $2.856 | Jaguar |
| Gorro tipo oruga | $190 | Jaguar |
| Guante látex talla S | $357-380/par | Gloria/Jaguar |
| Guante nitrilo talla S | $333-452/par | Gloria/Jaguar |
| Lidocaína 2% sin epinefrina | $144/ml | Gloria (50ml) |
| Lidocaína 2% sin epinefrina | $180/ml | Jaguar (10ml) |
| Lidocaína 2% con epinefrina | $3.870/ml | Jaguar |
| Alcohol 70% | $10/ml | Jaguar |

### 4.2 Insumos Especializados — Investigación Online 2026

| Insumo | Precio Estimado COP | Opción 1 | Opción 2 | Opción 3 |
|---|---|---|---|---|
| **Toxina botulínica 50U** (Botox/Dysport/Neuronox) | $400.000 – $700.000/frasco 100U → ~$200.000–$350.000 por 50U | Allergan (Botox) — cadena distribuidores INVIMA | Dysport (Ipsen/Galderma) — distribuidores autorizados | Neuronox — mejor costo-beneficio según mercado CO |
| **Ácido hialurónico facial 1ml** | $250.000 – $500.000/jeringa (precio de adquisición médica, no de clínica) | Juvederm (Allergan) | Restylane (Galderma) | Belotero (Merz) |
| **Aqualyx 8ml** | $150.000 – $250.000/ampolla (estimado importación) | MedEuroStore mayorista | AestheticPharma distribuidores | Cotizar distribuidor Colombia directo |
| **Alidya** | $200.000 – $350.000/ampolla (estimado) | Marllor Biomedical distribuidores | AestheticPharma | Cotizar distribuidor Colombia |
| **Sklerol (escleroterapia)** | $80.000 – $150.000/ampolla (estimado) | Distribuidores médicos Bogotá | Hospiclinic Colombia | Cotizar Jaguar/Gloria |
| **Kenacort (triamcinolona)** | $15.000 – $30.000/ampolla | Cruz Verde Colombia | Droguería La Rebaja | Jaguar/Gloria |
| **Procaína 1%** | $8.000 – $15.000/ampolla 10ml | Cruz Verde Colombia | Hospiclinic Colombia | Droguería La Rebaja |
| **Sutura Prolene 4-0** | $18.000 – $25.000/unidad | Hospiclinic Colombia (hospiclinicsas.com) | clicks-up.com | Jaguar/Gloria (cotizar) |
| **Sutura Prolene 2-0** | $16.000 – $22.000/unidad | Hospiclinic Colombia | clicks-up.com | Jaguar/Gloria (cotizar) |
| **Hoja bisturí #15** | $500/unidad (caja 100=$50.000) | Cimex Colombia (cimexcolombiasas.com) | Hospiclinic Colombia | Jaguar/Gloria |
| **Guantes estériles látex M** | $3.500 – $4.500/par | PYP Vida (pypvida.com) | Jaguar/Gloria (cotizar talla M) | MercadoLibre Colombia |
| **Micropore 3M rollo 12mm** | $3.500 – $5.000/rollo | Cruz Verde Colombia | Cafam Colombia | Farmalisto |
| **Acetaminofén 500mg** | $210/tableta | Centro Dermatológico Gov. | Cruz Verde Colombia | Cafam Colombia |
| **Gel ultrasonido incoloro** | $15.000 – $25.000/litro | Distribuidoras médicas Bogotá | MercadoLibre Colombia | Jaguar/Gloria |
| **Kit de citología** | $5.000 – $12.000/kit | Distribuidoras médicas | Hospiclinic Colombia | Jaguar/Gloria |
| **Glutaraldehído 50ml** | $8.000 – $15.000/frasco | Distribuidoras médicas | Cruz Verde Colombia | Jaguar/Gloria |
| **Peeling Skymedic (por paciente)** | $74.244/paquete 25 pacientes = $2.970/paciente | Skymedic directo | (ver hoja Medicamento Excel) | — |
| **Serum Skymedic (por paciente)** | Ver hoja Medicamento Excel | Skymedic directo | — | — |
| **Meso ox (por ml)** | $21.600/ml | Skymedic directo | — | — |
| **Exosomas faciales (por ml)** | $132.000/ml | Skymedic directo | — | — |
| **TKN HA3 bioestimulador** | A cotizar | Distribuidores Tecnovital | — | — |
| **Anestesia tópica (por paciente)** | $8.000 – $15.000/paciente | Distribuidoras médicas | Cruz Verde Colombia | Jaguar/Gloria |

> ⚠️ **ADVERTENCIA IMPORTANTE:** Los precios de productos como toxina botulínica, ácido hialurónico, Aqualyx y Alidya son precios de adquisición estimados para uso médico profesional. NO son precios al paciente. La mayoría de estos productos requieren distribuidor autorizado con registro INVIMA vigente en Colombia. Se recomienda cotizar directamente con distribuidores autorizados antes de fijar precios base.

---

## 5. SERVICIOS DRA. ESTELA QUINTERO (datos previos — mantener)

### Blefaroplastia
| Insumo | Cantidad | Precio Unit. | Total |
|---|---|---|---|
| Guantes estériles látex M | 4 pares | $4.000 | $16.000 |
| Jeringa 1ml 27G | 1 | $142 | $142 |
| Aguja 18G | 1 | $66 | $66 |
| Lidocaína 2% con epinefrina | 15ml | $3.870/ml | $58.050 |
| Pañitos húmedos | 10 | $55 | $550 |
| Gasa hospitalaria | 15 | $47 | $705 |
| Sutura Prolene 4-0 | 1 | $20.000 | $20.000 |
| Hoja bisturí #15 | 1 | $500 | $500 |
| Micropore 1/6 rollo | ~1/6 | $750 | $750 |
| Acetaminofén 500mg | 2 tab | $210 | $420 |
| **TOTAL** | | | **~$97.183** |

### Pendientes Dra. Estela
- Lifting de oreja: cantidades de gasas, pañitos, lidocaína, algodón
- Lifting de nariz: cantidades de gasas, pañitos, lidocaína
- Hilos extensores: tipo/marca/precio de hilos
- Botox: marca y dosis exacta

---

## 6. MODELO DE DATOS

```sql
CREATE TABLE empresas (id UUID PRIMARY KEY, nombre VARCHAR, nit VARCHAR, ciudad VARCHAR, activa BOOLEAN);
CREATE TABLE usuarios (id UUID PRIMARY KEY, email VARCHAR UNIQUE, password_hash VARCHAR, rol VARCHAR, empresa_id UUID REFERENCES empresas(id));
CREATE TABLE espacios (id UUID PRIMARY KEY, empresa_id UUID REFERENCES empresas(id), nombre VARCHAR, especialidad VARCHAR);
CREATE TABLE proveedores (id UUID PRIMARY KEY, espacio_id UUID REFERENCES espacios(id), nombre VARCHAR, url_referencia VARCHAR);
CREATE TABLE insumos (id UUID PRIMARY KEY, espacio_id UUID REFERENCES espacios(id), nombre VARCHAR, categoria VARCHAR, unidad_medida VARCHAR, stock_actual DECIMAL, stock_minimo DECIMAL);
CREATE TABLE precios_insumo (id UUID PRIMARY KEY, insumo_id UUID REFERENCES insumos(id), proveedor_id UUID REFERENCES proveedores(id), precio_unitario DECIMAL, precio_presentacion DECIMAL, unidades_por_presentacion INTEGER, descripcion_presentacion VARCHAR, fuente_url VARCHAR, fecha_precio DATE);
CREATE TABLE servicios (id UUID PRIMARY KEY, espacio_id UUID REFERENCES espacios(id), nombre VARCHAR, nombre_comercial VARCHAR, descripcion TEXT, duracion_minutos INTEGER, categoria VARCHAR, precio_mercado_referencia DECIMAL, margen_ganancia_pct DECIMAL DEFAULT 30);
CREATE TABLE servicio_insumos (id UUID PRIMARY KEY, servicio_id UUID REFERENCES servicios(id), insumo_id UUID REFERENCES insumos(id), cantidad DECIMAL, notas VARCHAR);
CREATE TABLE paquetes (id UUID PRIMARY KEY, espacio_id UUID REFERENCES espacios(id), nombre VARCHAR, descripcion TEXT, activo BOOLEAN DEFAULT true);
CREATE TABLE paquete_servicios (id UUID PRIMARY KEY, paquete_id UUID REFERENCES paquetes(id), servicio_id UUID REFERENCES servicios(id));
```

---

## 7. FASES DE DESARROLLO

### Fase 1 — MVP
- Autenticación JWT con roles
- CRUD insumos con precios por proveedor
- CRUD servicios con cálculo automático de costos
- Gestión de paquetes (agrupar servicios)
- Datos iniciales Dra. Estela + Dra. María Fernanda precargados
- UI responsiva

### Fase 2
- Alertas de stock bajo
- Comparador de proveedores
- Módulo reportes y exportación Excel/PDF
- Historial de precios

### Fase 3
- Onboarding nuevos clientes (multi-tenant)
- Panel superadmin completo
- Análisis de tendencias de costos

---

## 8. TABLA DE PRECIOS — INSUMOS ESPECIALIZADOS CON 3 OPCIONES DE COMPRA

> ⚠️ Todos los precios son estimados de adquisición para uso médico profesional. NO son precios al paciente final. Se recomienda cotizar directamente con cada proveedor antes de fijar precios base.

---

### TOXINA BOTULÍNICA
El médico selecciona la marca. Las 3 marcas con registro INVIMA vigente en Colombia son:

| Marca | Fabricante | Presentación | Precio estimado adquisición | INVIMA | Dónde comprar en Colombia |
|---|---|---|---|---|---|
| **Botox** | Allergan (AbbVie) | Frasco 100U | ~$24.000–$32.000 COP/unidad (precio médico estimado basado en $4–8 USD/unidad) | ✅ Vigente | Allergan Colombia, distribuidores autorizados — no venta libre |
| **Dysport** | Galderma/Ipsen | Ampolla 500U | ~$15.000–$20.000 COP/unidad equivalente (requiere 2.5–3x más unidades que Botox) | ✅ Vigente | Locatel Colombia (distribuye Dysport 500UI), distribuidores Galderma |
| **Xeomin** | Merz | Frasco 100U | ~$20.000–$28.000 COP/unidad | ✅ Vigente | Depósito de Drogas Boyacá (DDB) — INVIMA 2015M-0016054, distribuidores Merz Colombia |

**Nota conversión:** 1 unidad Botox = 1 unidad Neuronox = 2.5–3 unidades Dysport. Para 50U de efecto: usar 50U Botox/Xeomin ó ~125–150U Dysport.

**Costo por procedimiento (50U de efecto):**
- Botox: ~$1.200.000 – $1.600.000 COP (adquisición)
- Dysport: ~$900.000 – $1.200.000 COP (adquisición, requiere más unidades)
- Xeomin: ~$1.000.000 – $1.400.000 COP (adquisición)

---

### ÁCIDO HIALURÓNICO FACIAL (por jeringa 1ml)
Todas las siguientes marcas tienen registro INVIMA vigente en Colombia:

| Marca | Fabricante | Posicionamiento | Precio estimado adquisición médica | INVIMA Colombia | Contacto/Distribuidor |
|---|---|---|---|---|---|
| **Juvederm** (línea completa) | Allergan (AbbVie) | Premium | $1.800.000 – $3.200.000/ml precio clínica; precio adquisición médica estimado $600.000–$900.000/jeringa | ✅ Vigente | Allergan Colombia — distribución oficial |
| **Restylane** (línea completa) | Galderma | Premium | $1.600.000 – $2.800.000/ml precio clínica; precio adquisición médica estimado $500.000–$800.000/jeringa | ✅ Vigente | Galderma Colombia; aprobación FDA e INVIMA |
| **Belotero** (línea completa) | Merz | Medio-Premium | $1.400.000 – $2.400.000/ml precio clínica; precio adquisición médica estimado $400.000–$700.000/jeringa | ✅ Vigente | Merz Colombia — distribución oficial |
| **Teosyal / RHA** | Teoxane | Premium | $1.800.000 – $3.000.000/ml precio clínica | ✅ Vigente | Distribuidores Teoxane Colombia |

**Líneas específicas por zona:**
- Labios: Juvederm Volbella / Restylane Kysse / Belotero Balance
- Pómulos/estructura: Juvederm Voluma / Restylane Lyft / Belotero Volume
- Surcos/arrugas medias: Juvederm Ultra / Restylane Defyne / Belotero Intense
- Hidratación/skinbooster: Juvederm Volite / Restylane Skinbooster

> ⚠️ Precios por debajo de $800.000/ml son señal de alerta: pueden indicar falsificación o dilución. Exigir siempre jeringa sellada con lote visible antes de aplicar.

---

### AQUALYX (lipólisis inyectable)

| Opción | Proveedor | Presentación | Precio estimado | Registro | URL |
|---|---|---|---|---|---|
| **Opción 1** | AestheticPharma (distribuidor Marllor oficial) | 1 frasco 8ml | €45–65 EUR (~$200.000–$290.000 COP) | CE 0373 — ⚠️ Verificar INVIMA Colombia | aestheticpharma.com |
| **Opción 2** | MedEuroStore (mayorista internacional) | Caja 10 frascos x 8ml | Precio mayorista — cotizar | CE 0373 | medeurostore.com |
| **Opción 3** | Distribuidor Colombia directo | 1 frasco | Cotizar directamente | Verificar INVIMA | Jaguar/Gloria/Hospiclinic — cotizar |

> ⚠️ **IMPORTANTE:** Aqualyx es un dispositivo médico italiano (marca CE 0373). Para uso legal en Colombia se requiere verificar registro INVIMA vigente. Recomendamos solicitar certificado INVIMA al proveedor antes de comprar.

---

### ALIDYA (anticelulítico inyectable)

| Opción | Proveedor | Presentación | Precio estimado | Registro | URL |
|---|---|---|---|---|---|
| **Opción 1** | AestheticPharma (distribuidor Marllor oficial) | 1 set (vial + disolvente) | €55–75 EUR (~$245.000–$335.000 COP) | CE 0373 | aestheticpharma.com |
| **Opción 2** | MedEuroStore (mayorista) | Caja 5 sets | Precio mayorista — cotizar | CE 0373 | medeurostore.com |
| **Opción 3** | Distribuidor Colombia directo | 1 ampolla | Cotizar directamente | Verificar INVIMA | Jaguar/Gloria/Hospiclinic — cotizar |

> ⚠️ Igual que Aqualyx: verificar registro INVIMA antes de comprar. Ambos son del mismo fabricante (Marllor Biomedical, Italia).

---

### RESUMEN COMPARATIVO — PRODUCTOS ESPECIALIZADOS

| Producto | Precio adquisición estimado (COP) | ¿INVIMA Colombia? | Recomendación |
|---|---|---|---|
| Botox 100U (Allergan) | ~$2.400.000–$3.200.000/frasco | ✅ | Opción premium, más conocida |
| Dysport 500U (Galderma) | ~$1.800.000–$2.500.000/ampolla | ✅ | Precio/unidad aparenta ser menor pero requiere más |
| Xeomin 100U (Merz) | ~$2.000.000–$2.800.000/frasco | ✅ | Menor inmunogenicidad documentada |
| AH Juvederm 1ml (Allergan) | ~$600.000–$900.000/jeringa | ✅ | Premium, mayor duración |
| AH Restylane 1ml (Galderma) | ~$500.000–$800.000/jeringa | ✅ | Relación calidad-precio sólida |
| AH Belotero 1ml (Merz) | ~$400.000–$700.000/jeringa | ✅ | Buena integración piel, más económico |
| Aqualyx 8ml (Marllor) | ~$200.000–$290.000/ampolla | ⚠️ Verificar | Verificar INVIMA Colombia |
| Alidya set (Marllor) | ~$245.000–$335.000/set | ⚠️ Verificar | Verificar INVIMA Colombia |


---

## 8. INVESTIGACIÓN DE PRECIOS — PRODUCTOS ESPECIALIZADOS CON 3 OPCIONES

> **Nota crítica:** Se diferencia entre **precio de adquisición** (lo que paga el consultorio al distribuidor) y **precio de referencia al paciente** (lo que cobra el mercado). El sistema debe manejar ambos valores para calcular márgenes correctamente.

---

### 8.1 TOXINA BOTULÍNICA — 3 Opciones con INVIMA Colombia

| | **Opción 1: Botox® (Allergan/AbbVie)** | **Opción 2: Dysport® (Ipsen/Galderma)** | **Opción 3: Neuronox® (Medytox)** |
|---|---|---|---|
| **INVIMA** | ✅ Registrado INVIMA Colombia | ✅ Registrado INVIMA Colombia | ✅ Registrado INVIMA Colombia |
| **Presentación** | 100 unidades/vial | 300 unidades/vial | 100 unidades/vial |
| **Precio adquisición (estimado)** | $600.000 – $900.000/vial 100U | $500.000 – $750.000/vial 300U | $350.000 – $550.000/vial 100U |
| **Precio unitario** | $6.000 – $9.000/unidad | $1.667 – $2.500/unidad (necesita 2.5-3x más uds) | $3.500 – $5.500/unidad |
| **Costo 50U para procedimiento** | $300.000 – $450.000 | $300.000 – $450.000 (equivalente) | $175.000 – $275.000 |
| **Posicionamiento** | Premium — marca original | Premium — difusión amplia | Mejor costo-beneficio |
| **Mejor para** | Precisión, zonas delicadas | Frente completa, zonas extensas | Pacientes frecuentes, consultorios con alto volumen |
| **Duración efecto** | 3-4 meses | 3-4 meses | Hasta 7 meses (reportado) |
| **Distribuidor Colombia** | Allergan Colombia S.A. — distribuidores autorizados | Galderma Colombia — distribuidores autorizados | Distribuidores autorizados Medytox Colombia |
| **Precio referencia mercado** | $900.000 – $1.800.000/sesión facial | $900.000 – $1.800.000/sesión (equivalente) | $800.000 – $1.500.000/sesión |
| **Fuente** | dermatologiabogota.com, doctoralia.co | dratatianaleal.com | dratatianaleal.com, ewah-derm.com |

> ⚠️ **Nota conversión Dysport:** 1 unidad Botox/Neuronox ≈ 2.5–3 unidades Dysport para efecto equivalente. El procedimiento de 50U Botox equivale a ~125-150U Dysport.

---

### 8.2 ÁCIDO HIALURÓNICO FACIAL — 4 Marcas con INVIMA Colombia

| | **Juvéderm® (Allergan/AbbVie)** | **Restylane® (Galderma)** | **Belotero® (Merz)** | **Teosyal® / RHA (Teoxane)** |
|---|---|---|---|---|
| **INVIMA** | ✅ Registrado INVIMA | ✅ Registrado INVIMA | ✅ Registrado INVIMA | ✅ Registrado INVIMA |
| **Posicionamiento** | Premium | Premium | Medio-Premium | Premium |
| **Precio adquisición estimado/ml** | $500.000 – $800.000/ml | $450.000 – $700.000/ml | $350.000 – $600.000/ml | $500.000 – $750.000/ml |
| **Precio mercado/ml (a paciente)** | $1.800.000 – $3.200.000/ml | $1.600.000 – $2.800.000/ml | $1.400.000 – $2.400.000/ml | $1.800.000 – $3.000.000/ml |
| **Tecnología** | Vycross (reticulación avanzada) | NASHA / XpresHAn | CPM (matriz polidensificada) | RHA (baja reticulación) |
| **Duración** | 9-24 meses según línea | 6-18 meses según línea | 6-18 meses según línea | 9-18 meses |
| **Mejor para** | Volumen, pómulos, mentón | Labios, surcos, naturalidad | Ojeras, líneas finas, integración | Dinamismo facial |
| **Distribuidor Colombia** | Allergan Colombia S.A. | Galderma Colombia | Merz Colombia | Distribuidores Teoxane CO |
| **Fuente** | monreal.com.co, aestheticbyluisdevoz.com | monreal.com.co | draduarte.com | aestheticbyluisdevoz.com |

**Rangos de precio al paciente por densidad (todas las marcas con INVIMA):**

| Tipo de producto | Precio mercado/ml (COP) |
|---|---|
| Skinbooster / ultraligero | $1.000.000 – $1.800.000 |
| Labios / líneas finas | $1.200.000 – $2.200.000 |
| Ojeras (específico) | $1.500.000 – $2.400.000 |
| Surcos medios | $1.400.000 – $2.400.000 |
| Pómulos / mentón (denso) | $1.800.000 – $2.800.000 |
| Mandíbula / rinomodelación | $2.000.000 – $3.200.000 |

> 🚩 **Alerta INVIMA:** Precios por debajo de $800.000/ml son señal de producto falsificado, diluido o sin registro. No se recomienda comprar ácido hialurónico sin verificar registro INVIMA vigente.

---

### 8.3 AQUALYX — 3 Opciones de Adquisición

| | **Opción 1: Distribuidor directo Marllor** | **Opción 2: MedEuroStore (mayorista)** | **Opción 3: AestheticPharma** |
|---|---|---|---|
| **INVIMA Colombia** | ⚠️ Verificar vigencia registro | ⚠️ Verificar vigencia registro | ⚠️ Verificar vigencia registro |
| **Presentación** | 10 viales x 8ml | 10 viales x 8ml | 1 vial x 8ml (también x10) |
| **Precio estimado/vial** | $150.000 – $200.000 | $120.000 – $180.000 | $160.000 – $220.000 |
| **Precio paquete x10** | $1.500.000 – $2.000.000 | $1.200.000 – $1.800.000 | $1.600.000 – $2.200.000 |
| **Web** | Marllor Biomedical (contacto directo) | medeurostore.com/es/aqualyx | aestheticpharma.com |
| **Precio mercado al paciente** | $400.000 – $700.000/sesión 1 ampolla | — | — |
| **Fuente** | aestheticpharma.com, medeurostore.com | medeurostore.com | aestheticpharma.com |

> ⚠️ **IMPORTANTE:** Aqualyx es un dispositivo médico de Clase III que requiere registro INVIMA vigente en Colombia para su importación y uso legal. Se recomienda verificar el número de registro antes de adquirir. Contactar a Marllor Biomedical o a un distribuidor autorizado en Colombia.

---

### 8.4 ALIDYA (Tratamiento Celulitis) — 3 Opciones

| | **Opción 1: Marllor Biomedical directo** | **Opción 2: AestheticPharma** | **Opción 3: MedEuroStore** |
|---|---|---|---|
| **INVIMA Colombia** | ⚠️ Verificar registro | ⚠️ Verificar registro | ⚠️ Verificar registro |
| **Presentación** | Caja x 10 viales | Por vial | Caja x 10 viales |
| **Precio estimado/vial** | $180.000 – $280.000 | $200.000 – $320.000 | $160.000 – $260.000 |
| **Precio paquete x10** | $1.800.000 – $2.800.000 | — | $1.600.000 – $2.600.000 |
| **Web** | Marllor Biomedical (fabricante) | aestheticpharma.com | medeurostore.com |
| **Precio mercado al paciente** | $500.000 – $900.000/sesión | — | — |
| **Fuente** | aestheticpharma.com | aestheticpharma.com | medeurostore.com |

---

### 8.5 SKLEROL (Escleroterapia) — 3 Opciones

| | **Opción 1: Hospiclinic Colombia** | **Opción 2: Distribuidores médicos Bogotá** | **Opción 3: Jaguar / Gloria (cotizar)** |
|---|---|---|---|
| **INVIMA Colombia** | ✅ Verificar con proveedor | ✅ Verificar con proveedor | ✅ Verificar con proveedor |
| **Presentación** | Ampolla 2cc | Ampolla 2cc | Ampolla 2cc |
| **Precio estimado/ampolla** | $60.000 – $100.000 | $70.000 – $120.000 | A cotizar |
| **Web/Contacto** | hospiclinicsas.com | Distribuidoras médicas Bogotá | Contacto Jaguar/Gloria directo |
| **Precio mercado al paciente** | $400.000 – $800.000/sesión | — | — |
| **Fuente** | hospiclinicsas.com | Estimado mercado | — |

---

## 9. RESUMEN — CÓMO IMPLEMENTAR EN EL SISTEMA

El sistema **Facilito** debe manejar los productos especializados así:

```
Insumo: "Toxina Botulínica"
  ├── Opción A: Botox® (Allergan) — $6.000-9.000/unidad — INVIMA ✅
  ├── Opción B: Dysport® (Galderma) — $1.667-2.500/unidad — INVIMA ✅
  └── Opción C: Neuronox® (Medytox) — $3.500-5.500/unidad — INVIMA ✅
  → El médico selecciona cuál usa → el sistema calcula el costo con esa opción

Insumo: "Ácido Hialurónico 1ml"
  ├── Opción A: Juvéderm® — $500.000-800.000/ml — INVIMA ✅
  ├── Opción B: Restylane® — $450.000-700.000/ml — INVIMA ✅
  ├── Opción C: Belotero® — $350.000-600.000/ml — INVIMA ✅
  └── Opción D: Teosyal® — $500.000-750.000/ml — INVIMA ✅
  → El médico selecciona cuál usa → el sistema calcula el costo

Insumo: "Aqualyx"
  ├── Opción A: Marllor directo — $150.000-200.000/vial
  ├── Opción B: MedEuroStore — $120.000-180.000/vial
  └── Opción C: AestheticPharma — $160.000-220.000/vial
  → ⚠️ Requiere verificación INVIMA antes de compra
```

Esto se traduce en el modelo de datos como la tabla `precios_insumo` que ya existe, donde cada insumo puede tener múltiples registros de precio por proveedor, y el sistema usa el proveedor seleccionado por el médico para el cálculo de costos.

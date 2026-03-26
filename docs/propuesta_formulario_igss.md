# Propuesta Definitiva: Formulario IGSS de Vigilancia Sarampion/Rubeola

**Fecha:** 2026-03-26
**Fuentes analizadas:** Ficha MSPAS 2026 (PDF, ~120 campos), GoData Guatemala API, EPIWEB MSPAS, Formulario IGSS actual (formSchema.js)
**Objetivo:** Determinar la disposicion de CADA campo del PDF MSPAS para el contexto IGSS

---

## Contexto Institucional IGSS

El IGSS opera hospitales y clinicas del Seguro Social. A diferencia del MSPAS:

- **Siempre** es "Seguro Social (IGSS)", nunca "Privado"
- **No tiene** estructura DAS/DMS propia, pero puede inferirla del departamento de residencia del paciente
- **No realiza** investigacion domiciliaria (eso lo hacen los equipos de campo del MSPAS)
- **No realiza** BAI/BAC comunitaria ni vacunacion de bloqueo/barrido (eso es MSPAS)
- **Si tiene** laboratorio propio con resultados detallados (IgG, IgM, RT-PCR)
- **Si tiene** numero de afiliacion como identificador unico
- **Si rastrea** datos de empleado IGSS (riesgo ocupacional)

---

## 1. TABLA MAESTRA -- Cada campo del PDF con propuesta IGSS

### Leyenda de Propuestas

| Codigo | Significado |
|--------|-------------|
| **MOSTRAR-OBL** | Mostrar en formulario, obligatorio |
| **MOSTRAR-OPC** | Mostrar en formulario, opcional |
| **HARDCODEAR** | Valor fijo, no requiere input del usuario |
| **AUTO-CALCULAR** | Se deriva automaticamente de otros campos |
| **INFERIR** | Se deduce de otro campo con tabla de mapeo |
| **OCULTAR** | No aplica para IGSS, no mostrar |

---

### Header -- Diagnostico de Sospecha

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| H1 | Sarampion (checkbox) | check | -- | `diagnostico_de_sospecha_` = "SARAMPION" | `diagnostico_sospecha` | **MOSTRAR-OBL** | Usuario selecciona; checkbox multiple |
| H2 | Rubeola (checkbox) | check | -- | `diagnostico_de_sospecha_` = "RUBEOLA" | `diagnostico_sospecha` | **MOSTRAR-OBL** | Parte del mismo checkbox group |
| H3 | Dengue (checkbox) | check | -- | `diagnostico_de_sospecha_` = "DENGUE" | `diagnostico_sospecha` | **MOSTRAR-OBL** | Parte del mismo checkbox group |
| H4 | Otra Arbovirosis | check+text | -- | `diagnostico_de_sospecha_` + `especifique` | `diagnostico_sospecha` + `diagnostico_sospecha_otro` | **MOSTRAR-OPC** | + campo especifique condicional |
| H5 | Otra febril exantematica | check+text | -- | `diagnostico_de_sospecha_` + `especifique_` | `diagnostico_sospecha` + `diagnostico_sospecha_otro` | **MOSTRAR-OPC** | + campo especifique condicional |
| H6 | Caso altamente sospechoso de Sarampion | check | -- | `caso_altamente_sospechoso_de_sarampion` | `diagnostico_sospecha` | **MOSTRAR-OPC** | Solo si se selecciona Sarampion |

**Nota IGSS:** Ademas del diagnostico de sospecha, el IGSS registra el diagnostico CIE-10 especifico (`diagnostico_registrado` = B05x/B06x) que no existe en el PDF MSPAS.

---

### Seccion 1: Unidad Notificadora

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 1.1 | Fecha de Notificacion | fecha | -- | `fecha_de_notificacion` (REQ) | `fecha_notificacion` | **MOSTRAR-OBL** | Fecha en que se notifica el caso |
| 1.2 | Direccion de Area de Salud (DAS) | select | 29 DAS | `direccion_de_area_de_salud` (REQ) | -- (nuevo) | **INFERIR** | Se deduce de `departamento_residencia` (ver tabla Seccion 4) |
| 1.3 | Distrito Municipal de Salud (DMS) | select cascading | ~340 DMS | `distrito_municipal_de_salud_dms*` (REQ) | -- (nuevo) | **INFERIR** | Se deduce de `municipio_residencia` via catalogo MSPAS |
| 1.4 | Servicio de Salud (nombre) | texto | -- | `servicio_de_salud_*` | `unidad_medica` | **HARDCODEAR** | = nombre de la unidad medica IGSS seleccionada |
| 1.5 | Fecha de Consulta | fecha | -- | `fecha_de_consulta` | `fecha_registro_diagnostico` | **MOSTRAR-OBL** | Fecha en que se atendio al paciente |
| 1.6 | Fecha de investigacion domiciliaria | fecha | -- | `fecha_de_investigacion_domiciliaria` | `fecha_visita_domiciliaria` | **OCULTAR** | IGSS no realiza investigacion de campo; si MSPAS la hace, se puede registrar opcionalmente |
| 1.7 | Nombre de quien investiga | texto | -- | `nombre_de_quien_investiga` | `nom_responsable` | **HARDCODEAR** | = responsable de notificacion IGSS |
| 1.8 | Cargo de quien investiga | texto | -- | `cargo_de_quien_investiga` | `cargo_responsable` | **HARDCODEAR** | = cargo del responsable IGSS |
| 1.9 | Telefono | numerico | -- | `telefono` | `telefono_responsable` | **MOSTRAR-OPC** | Telefono del responsable |
| 1.10 | Correo electronico | texto | -- | `correo_electronico` | `correo_responsable` | **MOSTRAR-OPC** | Correo del responsable |
| 1.11 | Seguro Social (IGSS) checkbox | check | SI/NO | `otro_establecimiento` = "Seguro Social (IGSS)" | `es_seguro_social` | **HARDCODEAR** | Siempre "SI" -- IGSS es Seguro Social por definicion |
| 1.12 | Especifique establecimiento IGSS | texto | -- | `especifique_establecimiento` | `unidad_medica` | **HARDCODEAR** | = nombre de la unidad medica seleccionada |
| 1.13 | Establecimiento Privado checkbox | check | SI/NO | `otro_establecimiento` = "ESTABLECIMIENTO PRIVADO" | `establecimiento_privado` | **HARDCODEAR** | Siempre "NO" -- IGSS nunca es privado |
| 1.14 | Especifique establecimiento privado | texto | -- | `especifique_privado` | -- | **HARDCODEAR** | Siempre vacio |
| 1.15 | Fuente de Notificacion | checkboxes | Servicio de Salud, Privada, Laboratorio, Comunidad, Busqueda Activa Institucional, Busqueda Activa Comunitaria, Busqueda Activa Laboratorial, Investigacion de Contactos, Otro | `fuente_de_notificacion_` | `fuente_notificacion` | **MOSTRAR-OBL** | Opciones relevantes para IGSS: Servicio de Salud, Laboratorio, Busqueda Activa Institucional, Auto Notificacion, Defuncion, Otra |
| 1.16 | Especifique fuente (si Otro) | texto | -- | `especifique_fuente` | `fuente_notificacion_otra` | **MOSTRAR-OPC** | Solo si fuente = "Otra" |

**Campos IGSS adicionales (no en PDF MSPAS):**

| # | Campo | IGSS field_id | Propuesta | Justificacion |
|---|-------|--------------|-----------|---------------|
| 1.E1 | Diagnostico Registrado (CIE-10) | `diagnostico_registrado` | **MOSTRAR-OBL** | Codigo CIE-10 del sistema IGSS |
| 1.E2 | Codigo CIE-10 | `codigo_cie10` | **AUTO-CALCULAR** | Se deriva del diagnostico seleccionado |
| 1.E3 | Servicio que Reporta | `servicio_reporta` | **MOSTRAR-OPC** | Emergencia/Consulta Externa/Encamamiento |
| 1.E4 | Semana Epidemiologica | `semana_epidemiologica` | **AUTO-CALCULAR** | Se calcula de fecha_notificacion (CDC/MMWR) |
| 1.E5 | Enviaron Ficha? | `envio_ficha` | **MOSTRAR-OPC** | Tracking interno IGSS |

---

### Seccion 2: Informacion del Paciente

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 2.1 | Codigo de Identificacion (DPI/Pasaporte/Otro) | select | DPI, PASAPORTE, OTRO | `codigo_unico_de_identificacion_dpi_pasaporte_otro` | `tipo_identificacion` | **MOSTRAR-OPC** | Tipo de documento |
| 2.2 | No. de DPI | numerico | -- | `no_de_dpi` | `numero_identificacion` | **MOSTRAR-OPC** | Numero del documento; se envia al campo GoData segun tipo |
| 2.3 | No. de Pasaporte | texto | -- | `no_de_pasaporte` | `numero_identificacion` | **MOSTRAR-OPC** | Mismo campo, switch segun tipo_identificacion |
| 2.4 | Especifique (si Otro doc) | texto | -- | `especifique_cui` | `numero_identificacion` | **MOSTRAR-OPC** | Mismo campo, texto libre si tipo=OTRO |
| 2.5 | Primer Nombre | texto | -- | `firstName` (REQ) | `nombres` | **MOSTRAR-OBL** | Nombre(s) del paciente |
| 2.6 | Segundo Nombre | texto | -- | `middleName` | (incluido en `nombres`) | **MOSTRAR-OBL** | IGSS captura nombres completos en un solo campo |
| 2.7 | Primer Apellido | texto | -- | `lastName` (REQ) | `apellidos` | **MOSTRAR-OBL** | Apellido(s) del paciente |
| 2.8 | Segundo Apellido | texto | -- | (incluido en `lastName`) | (incluido en `apellidos`) | **MOSTRAR-OBL** | IGSS captura apellidos completos en un solo campo |
| 2.9 | Sexo | radio | Masculino/Femenino | `gender` (REQ) | `sexo` | **MOSTRAR-OBL** | M/F |
| 2.10 | Fecha de Nacimiento | fecha | -- | `ageDob.dob` | `fecha_nacimiento` | **MOSTRAR-OBL** | Fecha de nacimiento |
| 2.11 | Edad Anos | numerico | -- | `ageDob.age.years` | `edad_anios` | **AUTO-CALCULAR** | De fecha_nacimiento |
| 2.12 | Edad Meses | numerico | -- | `ageDob.age.months` | `edad_meses` | **AUTO-CALCULAR** | De fecha_nacimiento |
| 2.13 | Edad Dias | numerico | -- | -- | `edad_dias` | **AUTO-CALCULAR** | De fecha_nacimiento |
| 2.14 | Nombre del Tutor/Encargado | texto | -- | `nombre_del_tutor_` | `nombre_encargado` | **MOSTRAR-OBL** | Obligatorio para menores; aplica a todos en IGSS |
| 2.15 | Parentesco del Tutor | texto | -- | `parentesco_` | `parentesco_tutor` | **MOSTRAR-OPC** | Madre/Padre/Abuelo/Otro |
| 2.16 | Tipo ID Tutor (DPI/Pasaporte/Otro) | select | DPI, PASAPORTE, OTRO | `codigo_unico_de_identificacion_dpi_pasaporte_otro_` | `tipo_id_tutor` | **MOSTRAR-OPC** | Documento del encargado |
| 2.17 | No. DPI Tutor | numerico | -- | `no_de_dpi_` | `numero_id_tutor` | **MOSTRAR-OPC** | Numero ID del encargado |
| 2.18 | No. Pasaporte Tutor | texto | -- | `no_de_pasaporte_` | `numero_id_tutor` | **MOSTRAR-OPC** | Mismo campo, switch segun tipo |
| 2.19 | Especifique doc Tutor | texto | -- | `especifique_doc` | `numero_id_tutor` | **MOSTRAR-OPC** | Mismo campo |
| 2.20 | Pueblo/Etnia | select | LADINO, MAYA, GARIFUNA, XINCA, DESCONOCIDO | `pueblo` | `pueblo_etnia` | **MOSTRAR-OBL** | Requerido por EPIWEB |
| 2.21 | Comunidad Linguistica | select | 23 comunidades mayas | `comunidad_linguistica` | `comunidad_linguistica` | **MOSTRAR-OPC** | Solo si pueblo=MAYA |
| 2.22 | Extranjero | radio | SI/NO | `extranjero_` | -- | **INFERIR** | Se deduce de pais_residencia != GUATEMALA |
| 2.23 | Migrante | radio | SI/NO | `migrante` | `es_migrante` | **MOSTRAR-OPC** | |
| 2.24 | Ocupacion | select/texto | catalogo MSPAS | `ocupacion_` | `ocupacion` | **MOSTRAR-OBL** | Catalogo MSPAS de ocupaciones |
| 2.25 | Escolaridad | select | NINGUNA, PRE-PRIMARIA, PRIMARIA, BASICOS, DIVERSIFICADO, UNIVERSITARIO, POST GRADO, DESCONOCIDA, NO APLICA | `escolaridad_` | `escolaridad` | **MOSTRAR-OBL** | Requerido por EPIWEB |
| 2.26 | Telefono del Paciente | numerico | -- | `telefono_` | `telefono_paciente` | **MOSTRAR-OPC** | |
| 2.27 | Pais de Residencia | select | GUATEMALA/OTRO | `pais_de_residencia_` (REQ) | `pais_residencia` | **MOSTRAR-OBL** | Default: GUATEMALA. Requerido por GoData |
| 2.28 | Especifique pais (si otro) | texto | -- | `especifique_pais` (REQ si otro) | `pais_residencia` | **MOSTRAR-OPC** | Solo si pais != GUATEMALA |
| 2.29 | Departamento de Residencia | select | 22 deptos | `departamento_de_residencia_` (REQ) | `departamento_residencia` | **MOSTRAR-OBL** | Requerido en todos los sistemas |
| 2.30 | Municipio de Residencia | select cascading | por depto | `municipio_de_residencia_*` (REQ) | `municipio_residencia` | **MOSTRAR-OBL** | Cascading desde departamento |
| 2.31 | Lugar Poblado | select/texto | -- | `lugar_poblado_` | `poblado` | **MOSTRAR-OPC** | Cascading desde municipio |
| 2.32 | Direccion de Residencia | texto | -- | `direccion_de_residencia_` | `direccion_exacta` | **MOSTRAR-OPC** | Texto libre |

**Campos IGSS adicionales (no en PDF MSPAS):**

| # | Campo | IGSS field_id | Propuesta | Justificacion |
|---|-------|--------------|-----------|---------------|
| 2.E1 | Numero de Afiliacion | `afiliacion` | **MOSTRAR-OBL** | Identificador unico del paciente en IGSS |
| 2.E2 | Telefono del Encargado | `telefono_encargado` | **MOSTRAR-OPC** | Contacto adicional |

---

### Seccion 2-bis: Embarazo (Subseccion del PDF, Tab separado en IGSS)

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 2B.1 | Embarazada | radio | SI/NO | `pregnancyStatus` (campo estandar) | `esta_embarazada` | **MOSTRAR-OBL** | Condicional: solo si sexo=F. Opciones: SI/NO/N-A |
| 2B.2 | Lactando | radio | SI/NO | -- | `lactando` | **MOSTRAR-OPC** | Condicional: solo si sexo=F |
| 2B.3 | Semanas de Embarazo | numerico | -- | -- | `semanas_embarazo` | **MOSTRAR-OPC** | Condicional: si embarazada=SI |
| 2B.4 | Trimestre | select | 1/2/3 | -- | `trimestre_embarazo` | **AUTO-CALCULAR** | = ceil(semanas_embarazo / 13) |
| 2B.5 | Fecha Probable de Parto | fecha | -- | -- | `fecha_probable_parto` | **MOSTRAR-OPC** | Condicional: si embarazada=SI |
| 2B.6 | Vacuna en Embarazo | radio | SI/NO | -- | `vacuna_embarazada` | **MOSTRAR-OPC** | Condicional: si embarazada=SI |
| 2B.7 | Fecha Vacunacion Embarazada | fecha | -- | -- | `fecha_vacunacion_embarazada` | **MOSTRAR-OPC** | Condicional: si vacuna_embarazada=SI |

---

### Seccion 3: Antecedentes Medicos y de Vacunacion

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 3.1 | Paciente vacunado contra Sarampion | radio | SI, NO, VERBAL, DESCONOCIDO | `paciente_vacunado_` (REQ) | `vacunado` | **MOSTRAR-OBL** | SI/NO/DESCONOCIDO. GoData tiene opcion " VERBAL" (espacio al inicio) |
| 3.2 | Tipo de vacuna recibida | multiple | SPR, SR | `tipo_de_vacuna_recibida_` | (derivado de `dosis_spr`, `dosis_sr`, `dosis_sprv`) | **MOSTRAR-OPC** | IGSS separa en 3 vacunas: SPR, SR, SPRV |
| 3.3 | Numero de dosis SPR | numerico | -- | `numero_de_dosis` | `dosis_spr` | **MOSTRAR-OPC** | Condicional: si vacunado=SI |
| 3.4 | Fecha ultima dosis SPR | fecha | -- | `fecha_de_la_ultima_dosis` | `fecha_ultima_spr` | **MOSTRAR-OPC** | Condicional: si vacunado=SI |
| 3.5 | Numero de dosis SR | numerico | -- | `numero_de_dosis_` | `dosis_sr` | **MOSTRAR-OPC** | Condicional: si vacunado=SI. GoData tiene variable separada |
| 3.6 | Fecha ultima dosis SR | fecha | -- | `fecha_de_la_ultima_dosis_` | `fecha_ultima_sr` | **MOSTRAR-OPC** | Condicional: si vacunado=SI |
| 3.7 | Numero de dosis SPRV | numerico | -- | -- | `dosis_sprv` | **MOSTRAR-OPC** | Exclusivo IGSS (formato 2026); no existe en GoData |
| 3.8 | Fecha ultima dosis SPRV | fecha | -- | -- | `fecha_ultima_sprv` | **MOSTRAR-OPC** | Exclusivo IGSS |
| 3.9 | Fuente de informacion sobre vacunacion | select | Carne de Vacunacion, SIGSA 5a Cuaderno, SIGSA 5B Otros Grupos, Registro Unico Vacunacion, Verbal | `fuente_de_la_informacion_sobre_la_vacunacion_` | `fuente_info_vacuna` | **MOSTRAR-OPC** | Condicional: si vacunado=SI |
| 3.10 | Vacunacion en el sector | select | MSPAS, IGSS, PRIVADO | `vacunacion_en_el_sector_` | `sector_vacunacion` | **MOSTRAR-OPC** | Condicional: si vacunado=SI |
| 3.11 | Antecedentes medicos | radio | SI, NO, DESCONOCIDO | `antecedentes_medicos_` | `tiene_antecedentes_medicos` | **MOSTRAR-OPC** | |
| 3.12 | Especifique: Desnutricion | check/select | DESNUTRICION | `especifique_ant` = "DESNUTRICION" | `antecedente_desnutricion` | **MOSTRAR-OPC** | Condicional: si antecedentes=SI |
| 3.13 | Especifique: Inmunocompromiso | check/select | INMUNOCOMPROMISO | `especifique_ant` = "INMUNOCOMPROMISO" | `antecedente_inmunocompromiso` | **MOSTRAR-OPC** | Condicional: si antecedentes=SI |
| 3.14 | Especifique: Enfermedad Cronica | check/select | ENFERMEDAD CRONICA | `especifique_ant` = "ENFERMEDAD CRONICA" | `antecedente_enfermedad_cronica` | **MOSTRAR-OPC** | Condicional: si antecedentes=SI |
| 3.15 | Especifique: Otro antecedente | texto | -- | `especifique_A` | `antecedentes_medicos_detalle` | **MOSTRAR-OPC** | Texto libre para detalles adicionales |

---

### Seccion 4: Datos Clinicos

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 4.1 | Fecha de inicio de sintomas | fecha | -- | `fecha_de_inicio_de_sintomas_` | `fecha_inicio_sintomas` | **MOSTRAR-OBL** | Fecha de onset |
| 4.2 | Fecha de inicio de fiebre | fecha | -- | `fecha_de_inicio_de_fiebre_` | `fecha_inicio_fiebre` | **MOSTRAR-OBL** | |
| 4.3 | Fecha de inicio de exantema/rash | fecha | -- | `fecha_de_inicio_de_exantema_rash_` (REQ) | `fecha_inicio_erupcion` | **MOSTRAR-OBL** | Requerido por GoData |
| 4.4 | Sitio de inicio de erupcion | select | Retroauricular, Cara, Cuello, Torax, Otro | -- | `sitio_inicio_erupcion` | **MOSTRAR-OBL** | Requerido por EPIWEB |
| 4.5 | Sintomas presente | radio | SI/NO | `sintomas_` | (derivado de signos individuales) | **AUTO-CALCULAR** | SI si cualquier signo es SI |
| 4.6 | Fiebre | radio | SI/NO/DESCONOCIDO | `que_sintomas_` incluye "Fiebre" | `signo_fiebre` | **MOSTRAR-OBL** | Radio SI/NO/DESCONOCIDO |
| 4.7 | Exantema maculopapular | radio | SI/NO/DESCONOCIDO | `que_sintomas_` incluye "Exantema" | `signo_exantema` | **MOSTRAR-OBL** | |
| 4.8 | Manchas de Koplik | radio | SI/NO/DESCONOCIDO | `que_sintomas_` incluye "Manchas de Koplik" | `signo_manchas_koplik` | **MOSTRAR-OPC** | Dificil de evaluar clinicamente; ni GoData ni EPIWEB lo requieren |
| 4.9 | Tos | radio | SI/NO/DESCONOCIDO | `que_sintomas_` incluye "Tos" | `signo_tos` | **MOSTRAR-OBL** | Requerido para triaje clinico |
| 4.10 | Conjuntivitis | radio | SI/NO/DESCONOCIDO | `que_sintomas_` incluye "Conjuntivitis" | `signo_conjuntivitis` | **MOSTRAR-OBL** | Criterio diagnostico clave |
| 4.11 | Coriza (catarro nasal) | radio | SI/NO/DESCONOCIDO | `que_sintomas_` incluye "Coriza" | `signo_coriza` | **MOSTRAR-OBL** | Criterio diagnostico clave |
| 4.12 | Adenopatias (ganglios inflamados) | radio | SI/NO/DESCONOCIDO | `que_sintomas_` incluye "Adenopatias" | `signo_adenopatias` | **MOSTRAR-OPC** | No critico para diagnostico de sarampion |
| 4.13 | Artralgia/Artritis | radio | SI/NO/DESCONOCIDO | `que_sintomas_` incluye "Artralgia / Artritis" | `signo_artralgia` | **MOSTRAR-OPC** | Mas relevante para rubeola |
| 4.14 | Temperatura C | numerico | -- | `temp_c` | `temperatura_celsius` | **MOSTRAR-OPC** | Valor numerico en grados |
| 4.15 | Hospitalizacion | radio | SI, NO, DESCONOCIDO | `hospitalizacion_` | `hospitalizado` | **MOSTRAR-OBL** | |
| 4.16 | Nombre del Hospital | texto | -- | `nombre_del_hospital_` | `hosp_nombre` | **MOSTRAR-OBL** | Condicional: si hospitalizado=SI |
| 4.17 | Fecha de Hospitalizacion | fecha | -- | `fecha_de_hospitalizacion_` | `hosp_fecha` | **MOSTRAR-OBL** | Condicional: si hospitalizado=SI |
| 4.18 | No. Registro Medico | texto | -- | -- | `no_registro_medico` | **MOSTRAR-OBL** | Condicional: si hospitalizado=SI (campo IGSS) |
| 4.19 | Complicaciones | radio | SI, NO, DESCONOCIDO | `complicaciones_` | `tiene_complicaciones` | **MOSTRAR-OPC** | |
| 4.20 | Neumonia | radio/check | -- | `especifique_complicaciones_` incluye "NEUMONIA" | `comp_neumonia` | **MOSTRAR-OPC** | Condicional: si complicaciones=SI |
| 4.21 | Encefalitis | radio/check | -- | `especifique_complicaciones_` incluye "ENCEFALITIS" | `comp_encefalitis` | **MOSTRAR-OPC** | Condicional: si complicaciones=SI |
| 4.22 | Diarrea | radio/check | -- | `especifique_complicaciones_` incluye "DIARREA" | `comp_diarrea` | **MOSTRAR-OPC** | Condicional: si complicaciones=SI |
| 4.23 | Trombocitopenia | radio/check | -- | `especifique_complicaciones_` incluye "TROMBOCITOPENIA" | `comp_trombocitopenia` | **MOSTRAR-OPC** | Condicional: si complicaciones=SI |
| 4.24 | Otitis Media Aguda | radio/check | -- | `especifique_complicaciones_` incluye "OTITIS MEDIA AGUDA" | `comp_otitis` | **MOSTRAR-OPC** | Condicional: si complicaciones=SI |
| 4.25 | Ceguera | radio/check | -- | `especifique_complicaciones_` incluye "CEGUERA" | `comp_ceguera` | **MOSTRAR-OPC** | Condicional: si complicaciones=SI |
| 4.26 | Otra complicacion | texto | -- | `especique` (sic en GoData) | `comp_otra_texto` | **MOSTRAR-OPC** | Texto libre; condicional: si complicaciones=SI |
| 4.27 | Aislamiento respiratorio | radio | SI, NO, DESCONOCIDO | `aislamiento_respiratorio` | `aislamiento_respiratorio` | **MOSTRAR-OPC** | IGSS si realiza aislamiento en hospitales |
| 4.28 | Fecha de aislamiento | fecha | -- | `fecha_de_aislamiento` | `fecha_aislamiento` | **MOSTRAR-OPC** | Condicional: si aislamiento=SI |

**Campos IGSS adicionales (no en PDF MSPAS):**

| # | Campo | IGSS field_id | Propuesta | Justificacion |
|---|-------|--------------|-----------|---------------|
| 4.E1 | Fecha de Captacion | `fecha_captacion` | **MOSTRAR-OBL** | Fecha en que se capta el caso (EPIWEB la requiere) |
| 4.E2 | Sitio inicio erupcion otro | `sitio_inicio_erupcion_otro` | **MOSTRAR-OPC** | Si sitio=Otro |
| 4.E3 | Asintomatico | `asintomatico` | **MOSTRAR-OPC** | Solo IGSS; redundante si se llenan signos |
| 4.E4 | Condicion de Egreso | `condicion_egreso` | **MOSTRAR-OPC** | Si hospitalizado=SI |
| 4.E5 | Fecha de Egreso | `fecha_egreso` | **MOSTRAR-OPC** | Si hospitalizado=SI |
| 4.E6 | Fecha de Defuncion | `fecha_defuncion` | **MOSTRAR-OBL** | Condicional: si egreso=MUERTO |
| 4.E7 | Medico que Certifica | `medico_certifica_defuncion` | **MOSTRAR-OPC** | Condicional: si egreso=MUERTO |
| 4.E8 | Motivo de Consulta | `motivo_consulta` | **MOSTRAR-OPC** | Texto libre, observaciones clinicas |

---

### Seccion 5: Factores de Riesgo

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 5.1 | Existe caso en municipio | radio | Si, No, Desconocido | `Existe_caso_en_muni` | `caso_sospechoso_comunidad_3m` | **MOSTRAR-OBL** | Caso sospechoso en comunidad/municipio en ultimos 3 meses |
| 5.2 | Tuvo contacto con caso sospechoso/confirmado | radio | Si, No, Desconocido | `tuvo_contacto_con_un_caso_sospechoso_o_confirmado` | `contacto_sospechoso_7_23` | **MOSTRAR-OBL** | 7-23 dias antes del inicio de erupcion |
| 5.3 | Viajo durante los 7-23 dias previos | radio | Si, No | `viajo_durante_los_7_23_dias` | `viajo_7_23_previo` | **MOSTRAR-OBL** | |
| 5.4 | Pais/Departamento/Municipio de viaje | select+texto | GUATEMALA/OTRO + depto + municipio | `pais_departamento_y_municipio`, `departamento`, `municipio` | `viaje_pais`, `viaje_departamento`, `viaje_municipio` | **MOSTRAR-OPC** | Condicional: si viajo=SI |
| 5.5 | Fecha de salida (viaje) | fecha | -- | `fecha_de_salida_viaje` | `viaje_fecha_salida` | **MOSTRAR-OPC** | Condicional: si viajo=SI |
| 5.6 | Fecha de entrada/regreso (viaje) | fecha | -- | `fecha_de_entrada_viaje` | `viaje_fecha_entrada` | **MOSTRAR-OPC** | Condicional: si viajo=SI |
| 5.7 | Familiar viajo al exterior | radio | Si, No | `alguna_persona_de_su_casa_ha_viajado_al_exterior` | `familiar_viajo_exterior` | **MOSTRAR-OPC** | |
| 5.8 | Fecha de retorno del familiar | fecha | -- | `fecha_de_retorno` | `familiar_fecha_retorno` | **MOSTRAR-OPC** | Condicional: si familiar_viajo=SI |
| 5.9 | Contacto con embarazada | radio | Si, No, Desconocido | `el_paciente_estuvo_en_contacto_con_una_mujer_embarazada1` | `contacto_embarazada` | **MOSTRAR-OPC** | |
| 5.10 | Fuente posible de contagio | multiple | Contacto en el hogar, Institucion Educativa, Espacio Publico, Evento Masivo, Transporte Internacional, Servicio de Salud, Comunidad, Desconocido, Otro | `fuente_posible_de_contagio1` | `fuente_posible_contagio` | **MOSTRAR-OPC** | Select con opciones GoData exactas |

**Campo IGSS adicional:**

| # | Campo | IGSS field_id | Propuesta | Justificacion |
|---|-------|--------------|-----------|---------------|
| 5.E1 | Contacto enfermo catarro/erupcion | `contacto_enfermo_catarro` | **MOSTRAR-OPC** | Campo EPIWEB; util para triaje |

---

### Seccion 6: Acciones de Respuesta

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 6.1 | Se realizo BAI | radio | SI(1), NO(2) | `se_realizo_busqueda_activa_institucional_de_casos_bai` | `bai_realizada` | **MOSTRAR-OPC** | IGSS puede hacer BAI dentro de sus instalaciones |
| 6.2 | No. casos sospechosos BAI | numerico | -- | `numero_de_casos_sospechosos_identificados_en_bai` | `bai_casos_sospechosos` | **MOSTRAR-OPC** | Condicional: si BAI=SI |
| 6.3 | Se realizo BAC | radio | SI(1), NO(2) | `se_realizo_busqueda_activa_comunitaria_de_casos_bac` | `bac_realizada` | **OCULTAR** | IGSS no realiza busqueda comunitaria; eso es MSPAS |
| 6.4 | No. casos sospechosos BAC | numerico | -- | `numero_de_casos_sospechosos_identificados_en_bac` | `bac_casos_sospechosos` | **OCULTAR** | Dependiente del 6.3 |
| 6.5 | Vacunacion de bloqueo | radio | SI(1), NO(2) | `hubo_vacunacion_de_bloqueo` | `vacunacion_bloqueo` | **OCULTAR** | IGSS no hace vacunacion de bloqueo; eso es MSPAS campo |
| 6.6 | Vacunacion con barrido documentado | radio | SI(1), NO(2) | `hubo_vacunacion_con_barrido_documentado` | `vacunacion_barrido` | **OCULTAR** | IGSS no hace vacunacion de barrido |
| 6.7 | Monitoreo rapido de vacunacion | radio | SI(1), NO(2) | `se_realizo_monitoreo_rapido_de_vacunacion` | `monitoreo_rapido_vacunacion` | **OCULTAR** | Actividad de campo MSPAS |
| 6.8 | Se administro Vitamina A | radio | SI(1), NO(2), N/A(3) | `se_le_administro_vitamina_a` | `vitamina_a_administrada` | **MOSTRAR-OPC** | IGSS si administra Vitamina A en hospital |
| 6.9 | No. dosis Vitamina A | numerico | -- | `numero_de_dosis_de_vitamina_a_recibidas` | `vitamina_a_dosis` | **MOSTRAR-OPC** | Condicional: si vitamina_a=SI |
| 6.10 | Por que no se realizaron acciones | texto | -- | `por_que_no_acciones_respuesta` | -- | **OCULTAR** | No aplica; IGSS no es responsable de acciones de campo |

**Nota:** Los campos BAC, vacunacion de bloqueo/barrido y monitoreo rapido se mantienen en la BD para compatibilidad con GoData, pero se ocultan del formulario porque no son actividades del IGSS. Al sincronizar con GoData, se envian como "2" (NO) o vacios.

---

### Seccion 7: Laboratorio

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 7.1 | Se recolecto muestra | radio | SI/NO | (lab-results separados en GoData) | `recolecto_muestra` | **MOSTRAR-OBL** | |
| 7.2 | Tipo de muestra: Suero | check | -- | `sampleType` | `muestra_suero` | **MOSTRAR-OPC** | Condicional: si recolecto=SI |
| 7.3 | Fecha recoleccion suero | fecha | -- | `dateSampleTaken` | `muestra_suero_fecha` | **MOSTRAR-OPC** | Condicional: si suero=SI |
| 7.4 | Tipo de muestra: Hisopado nasofaringeo | check | -- | `sampleType` | `muestra_hisopado` | **MOSTRAR-OPC** | Condicional: si recolecto=SI |
| 7.5 | Fecha recoleccion hisopado | fecha | -- | `dateSampleTaken` | `muestra_hisopado_fecha` | **MOSTRAR-OPC** | Condicional: si hisopado=SI |
| 7.6 | Tipo de muestra: Orina | check | -- | `sampleType` | `muestra_orina` | **MOSTRAR-OPC** | Condicional: si recolecto=SI |
| 7.7 | Fecha recoleccion orina | fecha | -- | `dateSampleTaken` | `muestra_orina_fecha` | **MOSTRAR-OPC** | Condicional: si orina=SI |
| 7.8 | Antigeno (que se busca) | select | Sarampion, Rubeola, Dengue, Otros | `testedFor` | `antigeno_prueba` | **MOSTRAR-OBL** | Condicional: si recolecto=SI |
| 7.9 | Resultado de prueba | select | Positivo, Negativo, Muestra Inadecuada, Indeterminada | `result` (REQ en lab-results) | `resultado_prueba` | **MOSTRAR-OBL** | Condicional: si recolecto=SI |
| 7.10 | Fecha recepcion en laboratorio | fecha | -- | `dateSampleDelivered` | `fecha_recepcion_laboratorio` | **MOSTRAR-OPC** | |
| 7.11 | Fecha de resultado | fecha | -- | `dateOfResult` | `fecha_resultado_laboratorio` | **MOSTRAR-OPC** | |
| 7.12 | Resultado secuenciacion/genotipo | texto | -- | `sequence[resultId]` | `secuenciacion_resultado` | **MOSTRAR-OPC** | Genotipificacion genomica |
| 7.13 | Fecha secuenciacion | fecha | -- | `sequence[dateResult]` | `secuenciacion_fecha` | **MOSTRAR-OPC** | |

**Campos IGSS adicionales de laboratorio (no en PDF MSPAS):**

| # | Campo | IGSS field_id | Propuesta | Justificacion |
|---|-------|--------------|-----------|---------------|
| 7.E1 | Motivo no recoleccion | `motivo_no_recoleccion` | **MOSTRAR-OPC** | Si recolecto=NO |
| 7.E2 | Otra muestra | `muestra_otra` + `muestra_otra_descripcion` + `muestra_otra_fecha` | **MOSTRAR-OPC** | Para muestras no estandar |
| 7.E3 | Antigeno otro | `antigeno_otro` | **MOSTRAR-OPC** | Si antigeno=Otros |
| 7.E4 | IgG Cualitativo | `resultado_igg_cualitativo` | **MOSTRAR-OPC** | Lab IGSS: REACTIVO/NO REACTIVO/INDETERMINADO |
| 7.E5 | IgG Numerico | `resultado_igg_numerico` | **MOSTRAR-OPC** | Valor cuantitativo |
| 7.E6 | IgM Cualitativo | `resultado_igm_cualitativo` | **MOSTRAR-OPC** | Lab IGSS |
| 7.E7 | IgM Numerico | `resultado_igm_numerico` | **MOSTRAR-OPC** | Valor cuantitativo |
| 7.E8 | RT-PCR Orina | `resultado_pcr_orina` | **MOSTRAR-OPC** | Lab IGSS |
| 7.E9 | RT-PCR Hisopado | `resultado_pcr_hisopado` | **MOSTRAR-OPC** | Lab IGSS |
| 7.E10 | Motivo no 3 muestras | `motivo_no_3_muestras` | **MOSTRAR-OPC** | Control de calidad muestreo |
| 7.E11 | Matriz lab detallada (JSON) | `lab_muestras_json` | **MOSTRAR-OPC** | Formato 2026 con multiples muestras |

---

### Seccion 8: Clasificacion Final

| # | Campo PDF | Tipo | Opciones PDF | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-------------|-----------|--------------|----------------|-------------|
| 8.1 | Clasificacion (header pendiente/clasificado) | select | CLASIFICADO, PENDIENTE(2) | `clasificacion` | (derivado de `clasificacion_caso`) | **AUTO-CALCULAR** | Si clasificacion_caso != SOSPECHOSO/PENDIENTE => "CLASIFICADO", sino "2" |
| 8.2 | Clasificacion Final | select | Confirmado Sarampion(1), Confirmado Rubeola(2), Descartado(3), Pendiente(5) | `clasificacion_final` | `clasificacion_caso` | **MOSTRAR-OBL** | IGSS tiene opciones expandidas: SOSPECHOSO, CONFIRMADO SARAMPION, CONFIRMADO RUBEOLA, DESCARTADO, PENDIENTE, NO CUMPLE DEFINICION, CLINICO, FALSO, ERROR DIAGNOSTICO, SUSPENDIDO |
| 8.3 | Criterio de confirmacion (Sarampion) | select | Laboratorio(LABSR), Nexo Epi(NE), Clinico(CX) | `criterio_de_confirmacion_sarampion` | `criterio_confirmacion` | **MOSTRAR-OPC** | Condicional: si clasificacion=CONFIRMADO SARAMPION |
| 8.4 | Criterio de confirmacion (Rubeola) | select | Laboratorio(LABRB), Nexo Epi(NERB), Clinico(CXRB) | `criterio_de_confirmacion_rubeola` | `criterio_confirmacion` | **MOSTRAR-OPC** | Condicional: si clasificacion=CONFIRMADO RUBEOLA |
| 8.5 | Criterio para descartar el caso | select | Laboratorio(LAB), Reaccion Vacunal(RVAC), Clinico(CX2), Otro(OTRO) | `criterio_para_descartar_el_caso` | `criterio_descarte` | **MOSTRAR-OPC** | Condicional: si clasificacion=DESCARTADO. IGSS tiene opciones expandidas |
| 8.6 | Especifique criterio descarte (si Otro) | texto | -- | `especifiqueX` | -- (nuevo campo necesario) | **MOSTRAR-OPC** | Condicional: si criterio_descarte=Otro |
| 8.7 | Contacto de otro caso | radio | SI, NO | `contacto_de_otro_caso` | `contacto_otro_caso` | **MOSTRAR-OPC** | |
| 8.8 | Fuente de infeccion de casos confirmados | select | Importado(1), Relacionado importacion(2), Endemico(3), Fuente desconocida(4) | `fuente_de_infeccion_de_los_casos_confirmados` | `fuente_infeccion` | **MOSTRAR-OPC** | Condicional: si confirmado |
| 8.9 | Pais de importacion | texto | -- | `importado_pais_de_importacion` | `pais_importacion` | **MOSTRAR-OPC** | Condicional: si fuente=Importado |
| 8.10 | Caso analizado por | multiple | CONAPI(1), DEGR(2), Comision Nacional(3), Otro(4) | `caso_analizado_por` | `caso_analizado_por` | **MOSTRAR-OPC** | |
| 8.11 | Especifique (si analizado por Otro) | texto | -- | `especifique_otro_clasificacion` | `caso_analizado_por_otro` | **MOSTRAR-OPC** | Condicional: si analizado_por=Otro |
| 8.12 | Fecha de clasificacion | fecha | -- | `fecha_de_clasificacion` | `fecha_clasificacion_final` | **MOSTRAR-OPC** | |
| 8.13 | Condicion final del paciente | select | Recuperado(1), Con Secuelas(2), Fallecido(3), Desconocido(4) | `condicion_final_del_paciente` | `condicion_final_paciente` | **MOSTRAR-OPC** | |
| 8.14 | Fecha de defuncion | fecha | -- | `fecha_de_defuncion` | `fecha_defuncion` | **MOSTRAR-OPC** | Condicional: si condicion=Fallecido. Nota: tambien se mapea al campo estandar `dateOfOutcome` de GoData |
| 8.15 | Causa de muerte segun certificado | texto | -- | `causa_de_muerte_segun_certificado_de_defuncion` | `causa_muerte_certificado` | **MOSTRAR-OPC** | Condicional: si condicion=Fallecido |

**Campos IGSS adicionales:**

| # | Campo | IGSS field_id | Propuesta | Justificacion |
|---|-------|--------------|-----------|---------------|
| 8.E1 | No. de Contactos Directos | `contactos_directos` | **MOSTRAR-OPC** | Seguimiento de contactos IGSS |
| 8.E2 | Detalle contacto otro caso | `contacto_otro_caso_detalle` | **MOSTRAR-OPC** | Texto libre; condicional si contacto=SI |
| 8.E3 | Responsable de Clasificacion | `responsable_clasificacion` | **MOSTRAR-OPC** | Quien clasifica el caso |
| 8.E4 | Observaciones | `observaciones` | **MOSTRAR-OPC** | Texto libre general |

---

### Seccion sin numero en PDF: Lugares Visitados y Rutas de Desplazamiento

| # | Campo PDF | Tipo | GoData var | IGSS field_id | Propuesta IGSS | Valor/Logica |
|---|-----------|------|-----------|--------------|----------------|-------------|
| R.1 | Lugares visitados (header) | radio | `lugares_visitados_y_rutas_de_desplazamiento_del_caso` | -- | **OCULTAR** | Rastreo de movimientos es tarea de investigacion de campo MSPAS |
| R.2 | Sitio/Ruta 1 | texto | `sitio_ruta_de_desplazamiento_1` | -- | **OCULTAR** | Idem |
| R.3 | Direccion Lugar 1 | texto | `direccion_del_lugar_y_rutas_de_desplazamiento_1` | -- | **OCULTAR** | Idem |
| R.4 | Fecha visita Lugar 1 | fecha | `fecha_en_que_visito_el_lugar_ruta_1` | -- | **OCULTAR** | Idem |
| R.5 | Tipo abordaje Lugar 1 | multiple | `tipo_de_abordaje_realizado_1` (Bloqueo, Barrido, etc.) | -- | **OCULTAR** | Actividad MSPAS de campo |
| R.6 | Fecha abordaje Lugar 1 | fecha | `fecha_de_abordaje_1` | -- | **OCULTAR** | Idem |
| R.7-R.12 | Sitio/Ruta 2 (mismos 6 campos) | -- | `*_2` | -- | **OCULTAR** | Idem |

**Nota:** Estos 12 campos de rutas de desplazamiento son exclusivamente para investigacion epidemiologica de campo que el MSPAS realiza. El IGSS no participa en esta fase de la investigacion. Si en el futuro se necesitara, se puede agregar como seccion expandible.

---

### Seccion IGSS exclusiva: Datos de Empleado IGSS

| # | Campo | IGSS field_id | Propuesta | Justificacion |
|---|-------|--------------|-----------|---------------|
| I.1 | Es empleado del Seguro Social | `es_empleado_igss` | **MOSTRAR-OBL** | Critico para vigilancia de riesgo ocupacional |
| I.2 | Unidad Medica donde trabaja | `unidad_medica_trabaja` | **MOSTRAR-OPC** | Condicional: si es_empleado=SI |
| I.3 | Puesto que desempena | `puesto_desempena` | **MOSTRAR-OPC** | Condicional: si es_empleado=SI |
| I.4 | Subgerencia IGSS | `subgerencia_igss` | **MOSTRAR-OPC** | Cascading 4 niveles del organigrama IGSS |
| I.5 | Direccion IGSS | `direccion_igss` | **MOSTRAR-OPC** | Cascading desde subgerencia |
| I.6 | Departamento IGSS | `departamento_igss` | **MOSTRAR-OPC** | Cascading desde direccion |
| I.7 | Seccion IGSS | `seccion_igss` | **MOSTRAR-OPC** | Cascading desde departamento |

---

## 2. RESUMEN DE CONTEO

| Categoria | Campos PDF MSPAS | Campos IGSS extra | Total |
|-----------|-----------------|-------------------|-------|
| **MOSTRAR obligatorio** | 22 | 7 | **29** |
| **MOSTRAR opcional** | 47 | 25 | **72** |
| **HARDCODEAR** | 7 | 0 | **7** |
| **AUTO-CALCULAR** | 5 | 3 | **8** |
| **INFERIR** | 3 | 0 | **3** |
| **OCULTAR** | 18 | 0 | **18** |
| **Total campos PDF analizados** | **102** | -- | -- |
| **Total campos en formulario IGSS** | -- | -- | **137** |

### Desglose de campos OCULTAR (18)

| Campo | Razon |
|-------|-------|
| Fecha investigacion domiciliaria (1.6) | IGSS no hace investigacion de campo |
| BAC realizada (6.3) | Busqueda comunitaria es MSPAS |
| BAC casos sospechosos (6.4) | Dependiente de BAC |
| Vacunacion de bloqueo (6.5) | Actividad de campo MSPAS |
| Vacunacion de barrido (6.6) | Actividad de campo MSPAS |
| Monitoreo rapido vacunacion (6.7) | Actividad de campo MSPAS |
| Por que no acciones (6.10) | No aplica a IGSS |
| Lugares visitados header (R.1) | Investigacion de campo MSPAS |
| Sitio/Ruta 1 (R.2) | Investigacion de campo |
| Direccion Lugar 1 (R.3) | Investigacion de campo |
| Fecha visita Lugar 1 (R.4) | Investigacion de campo |
| Tipo abordaje Lugar 1 (R.5) | Investigacion de campo |
| Fecha abordaje Lugar 1 (R.6) | Investigacion de campo |
| Sitio/Ruta 2 (R.7) | Investigacion de campo |
| Direccion Lugar 2 (R.8) | Investigacion de campo |
| Fecha visita Lugar 2 (R.9) | Investigacion de campo |
| Tipo abordaje Lugar 2 (R.10) | Investigacion de campo |
| Fecha abordaje Lugar 2 (R.11) | Investigacion de campo |

---

## 3. CAMPOS HARDCODEADOS (lista completa)

| # | Campo PDF | Valor fijo IGSS | GoData destino | Logica |
|---|-----------|----------------|---------------|--------|
| 1 | Seguro Social (IGSS) | SI | `otro_establecimiento` = "Seguro Social (IGSS)" | Siempre; IGSS es Seguro Social |
| 2 | Establecimiento Privado | NO | No se envia (o vacio) | Siempre; IGSS nunca es privado |
| 3 | Especifique establecimiento privado | (vacio) | `especifique_privado` = null | Nunca aplica |
| 4 | Servicio de Salud | = `unidad_medica` seleccionada | `servicio_de_salud_*` (variable por DAS) | Se envia el nombre de la unidad medica IGSS |
| 5 | Nombre quien investiga | = `nom_responsable` | `nombre_de_quien_investiga` | El responsable IGSS es quien investiga |
| 6 | Cargo quien investiga | = `cargo_responsable` | `cargo_de_quien_investiga` | Idem |
| 7 | Especifique establecimiento IGSS | = `unidad_medica` | `especifique_establecimiento` | Nombre de la unidad medica |

---

## 4. CAMPOS INFERIDOS (lista completa con logica)

| # | Campo destino | Derivable desde | Logica de inferencia |
|---|--------------|----------------|---------------------|
| 1 | **DAS (Direccion de Area de Salud)** | `departamento_residencia` | Mapeo directo excepto Guatemala que tiene 4 DAS. Regla: si depto=GUATEMALA, por defecto usar "GUATEMALA CENTRAL" (el usuario puede cambiar). Resto de departamentos: nombre del depto = nombre del DAS, excepto: QUICHE incluye DAS IXCAN e IXIL (mapear a "QUICHE" por defecto), PETEN incluye DAS PETEN NORTE, PETEN SUR OCCIDENTE, PETEN SUR ORIENTE (mapear a "PETEN NORTE" por defecto). |
| 2 | **DMS (Distrito Municipal de Salud)** | `municipio_residencia` | Buscar en catalogo GoData: para cada DAS, hay una variable cascadeada `distrito_municipal_de_salud_dms*` que contiene la lista de municipios. El municipio de residencia se mapea al DMS correspondiente. |
| 3 | **Extranjero** | `pais_residencia` | Si pais_residencia != "GUATEMALA" entonces extranjero = "SI", sino "NO" |
| 4 | **Edad (anos/meses/dias)** | `fecha_nacimiento` | Ya implementado como auto-calculo en el formulario |
| 5 | **Semana epidemiologica** | `fecha_notificacion` | Calendario CDC/MMWR (domingo-sabado). Ya implementado |
| 6 | **Trimestre embarazo** | `semanas_embarazo` | = ceil(semanas / 13). Ya implementado |
| 7 | **Codigo CIE-10** | `diagnostico_registrado` | Mapeo via `diagnosticosMap`. Ya implementado |
| 8 | **Sintomas presente (header GoData)** | signos individuales | "SI" si al menos un signo es "SI" |
| 9 | **Clasificacion header GoData** | `clasificacion_caso` | Si != SOSPECHOSO/PENDIENTE => "CLASIFICADO", sino "2" (pendiente en GoData) |

### Tabla de mapeo DAS completa

| Departamento de Residencia | DAS (GoData) | Notas |
|---------------------------|-------------|-------|
| ALTA VERAPAZ | ALTA VERAPAZ | 1:1 |
| BAJA VERAPAZ | BAJA VERAPAZ | 1:1 |
| CHIMALTENANGO | CHIMALTENANGO | 1:1 |
| CHIQUIMULA | CHIQUIMULA | 1:1 |
| EL PROGRESO | EL PROGRESO | 1:1 |
| ESCUINTLA | ESCUINTLA | 1:1 |
| **GUATEMALA** | **GUATEMALA CENTRAL** | Default. Opciones: GUATEMALA CENTRAL, GUATEMALA NOR OCCIDENTE, GUATEMALA NOR ORIENTE, GUATEMALA SUR |
| HUEHUETENANGO | HUEHUETENANGO | 1:1 |
| IZABAL | IZABAL | 1:1 |
| JALAPA | JALAPA | 1:1 |
| JUTIAPA | JUTIAPA | 1:1 |
| **PETEN** | **PETEN NORTE** | Default. Opciones: PETEN NORTE, PETEN SUR OCCIDENTE, PETEN SUR ORIENTE |
| **QUICHE** | **QUICHE** | Default. Opciones: QUICHE, IXCAN, IXIL |
| QUETZALTENANGO | QUETZALTENANGO | 1:1 |
| RETALHULEU | RETALHULEU | 1:1 |
| SACATEPEQUEZ | SACATEPEQUEZ | 1:1 |
| SAN MARCOS | SAN MARCOS | 1:1 |
| SANTA ROSA | SANTA ROSA | 1:1 |
| SOLOLA | SOLOLA | 1:1 |
| SUCHITEPEQUEZ | SUCHITEPEQUEZ | 1:1 |
| TOTONICAPAN | TOTONICAPAN | 1:1 |
| ZACAPA | ZACAPA | 1:1 |

**Importante:** Para Guatemala, Peten y Quiche, el formulario debe mostrar un sub-selector que permita al usuario elegir la DAS correcta cuando el departamento tiene multiples opciones. El default es la DAS mas comun.

---

## 5. PROPUESTA FINAL DE TABS

Basado en el analisis campo por campo, la estructura de 9 tabs del formulario IGSS se mantiene con los siguientes ajustes:

### Tab 1: Datos Generales (22 campos visibles)

| Seccion | Campos |
|---------|--------|
| Diagnostico | `diagnostico_registrado`, `codigo_cie10` (auto), `diagnostico_sospecha` (checkboxes), `diagnostico_sospecha_otro` |
| Unidad Notificadora | `unidad_medica`, `unidad_medica_otra` |
| Fechas | `fecha_notificacion`, `fecha_registro_diagnostico` (OPC), `semana_epidemiologica` (auto) |
| Servicio | `servicio_reporta` (OPC) |
| Responsable | `nom_responsable`, `cargo_responsable`, `telefono_responsable` (OPC), `correo_responsable` (OPC) |
| Tracking | `envio_ficha` (OPC) |
| Investigacion | `fuente_notificacion`, `fuente_notificacion_otra` (condicional) |
| Ocultos/hardcoded | `es_seguro_social` = SI, `establecimiento_privado` = NO, `establecimiento_privado_nombre` = vacio |

**Cambios respecto al formulario actual:**
- `fecha_registro_diagnostico`: REQ -> OPC (solo IGSS interno)
- `servicio_reporta`: REQ -> OPC (ni GoData ni EPIWEB lo requieren)
- `envio_ficha`: REQ -> OPC (solo tracking interno)
- Agregar campo `fecha_visita_domiciliaria` como OPC (actualmente existe pero propuesto OCULTAR; mantener OPC por si MSPAS lo llena)

### Tab 2: Datos del Paciente (24 campos visibles)

| Seccion | Campos |
|---------|--------|
| Identificacion | `afiliacion`, `tipo_identificacion` (OPC), `numero_identificacion` (OPC) |
| Nombre | `nombres`, `apellidos` |
| Datos basicos | `sexo`, `fecha_nacimiento`, `edad_anios` (auto), `edad_meses` (auto), `edad_dias` (auto) |
| Sociodemograficos | `pueblo_etnia`, `comunidad_linguistica` (OPC), `es_migrante` (OPC), `ocupacion`, `escolaridad` |
| Residencia | `pais_residencia` (OBL, default GUATEMALA), `departamento_residencia`, `municipio_residencia`, `poblado` (OPC), `direccion_exacta` (OPC) |
| Encargado | `nombre_encargado`, `parentesco_tutor` (OPC), `tipo_id_tutor` (OPC), `numero_id_tutor` (OPC), `telefono_paciente` (OPC), `telefono_encargado` (OPC) |

**Cambios respecto al formulario actual:**
- `pais_residencia`: OPC -> OBL (GoData lo requiere)

### Tab 3: Embarazo (7 campos, condicional sexo=F)

Sin cambios. Todos los campos son condicionales y correctamente configurados.

| Campos | `esta_embarazada` (OBL si F), `lactando` (OPC), `semanas_embarazo` (OPC), `trimestre_embarazo` (auto), `fecha_probable_parto` (OPC), `vacuna_embarazada` (OPC), `fecha_vacunacion_embarazada` (OPC) |

**Cambio:** `semanas_embarazo`: REQ -> OPC (EPIWEB no lo requiere).

### Tab 4: Antecedentes y Vacunacion (15 campos visibles)

| Seccion | Campos |
|---------|--------|
| Vacunacion | `vacunado` (OBL), `fuente_info_vacuna` (OPC), `sector_vacunacion` (OPC) |
| SPR | `dosis_spr` (OPC), `fecha_ultima_spr` (OPC) |
| SR | `dosis_sr` (OPC), `fecha_ultima_sr` (OPC) |
| SPRV | `dosis_sprv` (OPC), `fecha_ultima_sprv` (OPC) |
| Antecedentes | `tiene_antecedentes_medicos` (OPC), `antecedentes_medicos_detalle` (OPC), `antecedente_desnutricion` (OPC), `antecedente_inmunocompromiso` (OPC), `antecedente_enfermedad_cronica` (OPC) |

**Cambio:** `fuente_info_vacuna`: REQ -> OPC (simplificar; GoData no lo requiere).

### Tab 5: Datos Clinicos (28 campos visibles)

| Seccion | Campos |
|---------|--------|
| Conocimiento | `fecha_inicio_sintomas` (OBL), `fecha_captacion` (OBL) |
| Exposicion | `fecha_inicio_erupcion` (OBL), `sitio_inicio_erupcion` (OBL), `sitio_inicio_erupcion_otro`, `fecha_inicio_fiebre` (OBL), `temperatura_celsius` (OPC) |
| Signos/Sintomas | `signo_fiebre` (OBL), `signo_exantema` (OBL), `signo_manchas_koplik` (OPC), `signo_tos` (OBL), `signo_conjuntivitis` (OBL), `signo_coriza` (OBL), `signo_adenopatias` (OPC), `signo_artralgia` (OPC), `asintomatico` (OPC) |
| Hospitalizacion | `hospitalizado` (OBL), `hosp_nombre`, `hosp_fecha`, `no_registro_medico`, `condicion_egreso` (OPC), `fecha_egreso` (OPC), `fecha_defuncion`, `medico_certifica_defuncion` (OPC) |
| Observaciones | `motivo_consulta` (OPC) |
| Complicaciones | `tiene_complicaciones` (OPC), `comp_neumonia`..`comp_ceguera`, `comp_otra_texto` |
| Aislamiento | `aislamiento_respiratorio` (OPC), `fecha_aislamiento` (OPC) |

**Cambios respecto al formulario actual:**
- `signo_manchas_koplik`: REQ -> OPC (dificil de evaluar clinicamente)
- `signo_adenopatias`: REQ -> OPC (no critico para sarampion)
- `signo_artralgia`: REQ -> OPC (mas relevante para rubeola)
- `asintomatico`: REQ -> OPC (redundante con signos individuales)

### Tab 6: Factores de Riesgo (13 campos visibles)

Sin cambios significativos. Los campos estan bien configurados.

| Campos | `contacto_sospechoso_7_23` (OBL), `caso_sospechoso_comunidad_3m` (OBL), `viajo_7_23_previo` (OBL), `viaje_pais` (OPC), `viaje_departamento` (OPC), `viaje_municipio` (OPC), `viaje_fecha_salida` (OPC), `viaje_fecha_entrada` (OPC), `familiar_viajo_exterior` (OPC), `familiar_fecha_retorno` (OPC), `contacto_enfermo_catarro` (OPC), `contacto_embarazada` (OPC), `fuente_posible_contagio` (OPC) |

### Tab 7: Acciones de Respuesta (4 campos visibles, 5 ocultos)

| Seccion | Campos |
|---------|--------|
| Busqueda Activa | `bai_realizada` (OPC), `bai_casos_sospechosos` (OPC, condicional) |
| Vitamina A | `vitamina_a_administrada` (OPC), `vitamina_a_dosis` (OPC, condicional) |
| **OCULTOS** | `bac_realizada`, `bac_casos_sospechosos`, `vacunacion_bloqueo`, `vacunacion_barrido`, `monitoreo_rapido_vacunacion` |

**Cambios respecto al formulario actual:**
- Ocultar BAC, vacunacion bloqueo/barrido, monitoreo rapido (no son actividades IGSS)
- Mantenerlos en la BD para compatibilidad con GoData (se envian como NO/vacio)

### Tab 8: Laboratorio (20 campos visibles)

Sin cambios significativos. La seccion de laboratorio es una fortaleza del IGSS.

**Cambios:**
- `muestra_suero`: REQ -> OPC (EPIWEB usa checkboxes opcionales)
- `muestra_hisopado`: REQ -> OPC
- `muestra_orina`: REQ -> OPC

### Tab 9: Clasificacion y Datos IGSS (20 campos visibles)

Sin cambios significativos.

| Seccion | Campos |
|---------|--------|
| Clasificacion | `contactos_directos` (OPC), `clasificacion_caso` (OBL), `criterio_confirmacion` (OPC), `criterio_descarte` (OPC), `fuente_infeccion` (OPC), `pais_importacion` (OPC), `contacto_otro_caso` (OPC), `contacto_otro_caso_detalle` (OPC), `caso_analizado_por` (OPC), `caso_analizado_por_otro` (OPC), `fecha_clasificacion_final` (OPC), `responsable_clasificacion` (OPC) |
| Condicion Final | `condicion_final_paciente` (OPC), `causa_muerte_certificado` (OPC) |
| Observaciones | `observaciones` (OPC) |
| Datos IGSS | `es_empleado_igss` (OBL), `unidad_medica_trabaja` (OPC), `puesto_desempena` (OPC), `subgerencia_igss` (OPC), `direccion_igss` (OPC), `departamento_igss` (OPC), `seccion_igss` (OPC) |

---

## 6. DISCREPANCIAS GoData vs PDF y Resoluciones

### 6.1 Opciones con acentos (GoData requiere, nuestro codigo quita)

| Campo | Nuestro valor (sin acentos) | GoData espera (con acentos) | Resolucion |
|-------|---------------------------|---------------------------|------------|
| diagnostico_de_sospecha_ | SARAMPION | SARAMPION | Preservar acentos; no usar `_godata_text()` en opciones SINGLE_ANSWER |
| diagnostico_de_sospecha_ | RUBEOLA | RUBEOLA | Idem |
| direccion_de_area_de_salud | IXCAN | IXCAN | Idem |
| direccion_de_area_de_salud | PETEN NORTE | PETEN NORTE | Idem |
| direccion_de_area_de_salud | QUICHE | QUICHE | Idem |
| direccion_de_area_de_salud | SACATEPEQUEZ | SACATEPEQUEZ | Idem |
| direccion_de_area_de_salud | SOLOLA | SOLOLA | Idem |
| direccion_de_area_de_salud | SUCHITEPEQUEZ | SUCHITEPEQUEZ | Idem |
| departamento_de_residencia_ | (7 deptos) | (con acentos) | Idem |
| escolaridad_ | BASICOS | BASICOS | Idem |
| fuente_de_notificacion_ | BUSQUEDA ACTIVA * | BUSQUEDA ACTIVA * | Idem |
| especifique_ant | DESNUTRICION | DESNUTRICION | Idem |
| especifique_ant | ENFERMEDAD CRONICA | ENFERMEDAD CRONICA | Idem |
| especifique_complicaciones_ | NEUMONIA | NEUMONIA | Idem |
| pueblo | GARIFUNA | GARIFUNA | Idem |

**Resolucion global:** Crear funcion `_godata_option(text)` que solo hace `.upper().strip()` SIN quitar acentos. Usar para todos los campos de opcion. Mantener `_godata_text()` solo para campos de texto libre.

### 6.2 Etiquetas de sintomas (GoData vs nuestro mapeo)

| Nuestro label | GoData label correcto | Resolucion |
|---------------|----------------------|------------|
| Adenopatias/ Ganglios inflamados | Adenopatias | Usar label GoData exacto |
| Artralgia/ Dolor articular | Artralgia / Artritis | Usar label GoData exacto |

### 6.3 Etiquetas de complicaciones

| Nuestro label | GoData label correcto | Resolucion |
|---------------|----------------------|------------|
| NEUMONIA | NEUMONIA | Preservar acento |
| OTITIS MEDIA | OTITIS MEDIA AGUDA | Agregar "AGUDA" |

### 6.4 Fuente posible de contagio

| Nuestro label | GoData label correcto | Resolucion |
|---------------|----------------------|------------|
| Hogar | Contacto en el hogar | Ya corregido en formSchema.js |
| Espacio publico | Espacio Publico | Ya corregido |
| (faltante) | Institucion Educativa | Ya agregado |
| (faltante) | Evento Masivo | Ya agregado |
| (faltante) | Transporte Internacional | Ya agregado |

### 6.5 Variable de Servicio de Salud (26 de 29 incorrectos)

La variable GoData `servicio_de_salud_*` es cascadeada por DAS. Solo 3 de 29 estan correctamente mapeados en el backend. Se debe corregir el `_SERVICIO_SALUD_VARIABLE_MAP` completo con los valores auditados del API GoData (ver tabla en godata_campo_por_campo.md seccion 2.1).

### 6.6 Clasificacion pendiente

| Campo | Nuestro valor | GoData valor | Resolucion |
|-------|--------------|-------------|------------|
| `clasificacion` (header) | "PENDIENTE" | "2" | Enviar "2" para pendiente, "CLASIFICADO" para clasificado |

### 6.7 Factores de riesgo: capitalizacion mixta

GoData usa "Si"/"No"/"Desconocido" (primera mayuscula) en seccion de factores de riesgo, pero "SI"/"NO" en otras secciones. El mapeo debe respetar la capitalizacion exacta por campo.

### 6.8 Vacunado: opcion VERBAL con espacio

GoData tiene la opcion `" VERBAL"` (con espacio al inicio) para `paciente_vacunado_`. Nuestro formulario tiene "DESCONOCIDO" en su lugar. El mapeo debe considerar que "VERBAL" en GoData equivale a que el paciente dice estar vacunado pero no tiene comprobante.

**Resolucion:** Agregar opcion "VERBAL" al formulario IGSS como cuarta opcion (SI/NO/VERBAL/DESCONOCIDO), o mapear la fuente de informacion "Verbal" como indicador.

---

## 7. RESUMEN DE CAMBIOS RECOMENDADOS AL FORMULARIO ACTUAL

### 7.1 Campos a pasar de REQ a OPC (11 campos)

| Campo | Razon | Ahorro estimado |
|-------|-------|----------------|
| `fecha_registro_diagnostico` | Solo IGSS interno | ~5 seg/caso |
| `servicio_reporta` | Ni GoData ni EPIWEB lo requieren | ~5 seg/caso |
| `envio_ficha` | Solo tracking interno | ~3 seg/caso |
| `fuente_info_vacuna` | GoData no lo requiere | ~5 seg/caso |
| `signo_manchas_koplik` | Dificil de evaluar, no requerido externamente | ~5 seg/caso |
| `signo_adenopatias` | No critico para diagnostico | ~3 seg/caso |
| `signo_artralgia` | Mas relevante para rubeola | ~3 seg/caso |
| `asintomatico` | Redundante con signos | ~3 seg/caso |
| `muestra_suero` | EPIWEB usa checkboxes opcionales | ~3 seg/caso |
| `muestra_hisopado` | Idem | ~3 seg/caso |
| `muestra_orina` | Idem | ~3 seg/caso |

**Ahorro total estimado: ~41 segundos por caso**

### 7.2 Campos a pasar de OPC a OBL (1 campo)

| Campo | Razon |
|-------|-------|
| `pais_residencia` | GoData lo requiere; default GUATEMALA ya existe |

### 7.3 Campos a OCULTAR del formulario (7 campos, mantener en BD)

| Campo | Razon |
|-------|-------|
| `bac_realizada` | Busqueda comunitaria es MSPAS |
| `bac_casos_sospechosos` | Dependiente |
| `vacunacion_bloqueo` | Actividad de campo MSPAS |
| `vacunacion_barrido` | Actividad de campo MSPAS |
| `monitoreo_rapido_vacunacion` | Actividad de campo MSPAS |
| `fecha_visita_domiciliaria` | IGSS no hace investigacion de campo |
| `fecha_inicio_investigacion` | Idem |

### 7.4 Campos nuevos a agregar (0 campos UI, 2 campos logica backend)

| Campo | Tipo | Destino | Logica |
|-------|------|---------|--------|
| DAS (auto-derivado) | inferido | GoData `direccion_de_area_de_salud` | De `departamento_residencia` via tabla de mapeo |
| DMS (auto-derivado) | inferido | GoData `distrito_municipal_de_salud_dms*` | De `municipio_residencia` via catalogo MSPAS |

**Nota:** No se agregan campos nuevos al formulario visible. DAS y DMS se calculan automaticamente en el backend al sincronizar con GoData.

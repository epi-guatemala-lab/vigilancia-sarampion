# Comparacion Tres Vias: React Form vs MSPAS 2026 PDF vs GoData Guatemala

**Fecha**: 2026-03-26
**Fuentes**:
- **React Form**: `/tmp/vigilancia-sarampion/src/config/formSchema.js` (186 fields, 9 tabs)
- **MSPAS PDF**: Ficha de Investigacion Epidemiologica Sarampion/Rubeola 2026 (Doc 4), reconstructed from plan
- **GoData**: Outbreak "Taller Sarampion" en `godataguatemala.mspas.gob.gt` (questionnaire + standard fields)

---

## 1. Resumen Estadistico

| Metrica | Cantidad |
|---------|----------|
| Campos totales analizados (conceptos unicos) | 148 |
| OK (alineados en las 3 fuentes) | 62 |
| PARTIAL (existe en 2 de 3) | 38 |
| MISMATCH (existe en 3 pero opciones difieren) | 19 |
| MISSING_FORM (no en React, si en PDF/GoData) | 8 |
| MISSING_GODATA (en React, no en GoData) | 14 |
| MISSING_PDF (en React, no en PDF 2026) | 7 |
| IGSS-only (campos exclusivos IGSS, no aplica a otras fuentes) | 16 |

### Discrepancias de Opciones Criticas: 14

---

## 2. Tabla Completa Tres Vias

### SECCION 1: DIAGNOSTICO DE SOSPECHA

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 1 | Diagnostico registrado CIE-10 | `diagnostico_registrado` | select (16 opts B05x/B06x) | Encabezado ficha | N/A (no directo) | MISSING_GODATA | GoData no tiene campo CIE-10, usa diagnostico_sospecha |
| 2 | Codigo CIE-10 (auto) | `codigo_cie10` | text readonly | N/A | N/A | IGSS-only | Campo interno IGSS |
| 3 | Diagnostico de sospecha | `diagnostico_sospecha` | checkbox (6 opts) | Header checkboxes | `diagnostico_de_sospecha_` (single select, 5 opts) | **MISMATCH** | Ver Discrepancia D1 |
| 4 | Especifique sospecha | `diagnostico_sospecha_otro` | text | Especifique | `especifique` / `especifique_` | OK | |

### SECCION 2: DATOS DE LA UNIDAD NOTIFICADORA

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 5 | Fecha de notificacion | `fecha_notificacion` | date | SI | `dateOfReporting` (std) + `fecha_de_notificacion` (qA) | OK | |
| 6 | Fecha registro diagnostico | `fecha_registro_diagnostico` | date | Fecha de consulta | `fecha_de_consulta` (qA) | OK | Mismo concepto, nombre distinto |
| 7 | Semana epidemiologica | `semana_epidemiologica` | number (auto) | Implícito | N/A (calculada) | PARTIAL | GoData no la almacena explicitamente |
| 8 | Unidad medica que reporta | `unidad_medica` | select (IGSS units) | N/A (IGSS specific) | N/A | IGSS-only | |
| 9 | Unidad medica otra | `unidad_medica_otra` | text | N/A | N/A | IGSS-only | |
| 10 | Area de salud MSPAS (DDRISS) | N/A (no en form) | -- | DDRISS (29 areas) | `direccion_de_area_de_salud` (29 opts) | **MISSING_FORM** | Ver Discrepancia D2 |
| 11 | Distrito municipal de salud | N/A (no en form) | -- | DMS (per area) | `distrito_municipal_de_salud_dms*` (cascading) | **MISSING_FORM** | Ver Discrepancia D2 |
| 12 | Servicio de salud MSPAS | N/A (no en form) | -- | Servicio de salud (text) | `servicio_de_salud*` (text) | **MISSING_FORM** | Ver Discrepancia D2 |
| 13 | Servicio que reporta | `servicio_reporta` | select (4 opts) | N/A | N/A | IGSS-only | EMERGENCIA/CONSULTA EXT/ENCAMAMIENTO/OTRO |
| 14 | Responsable notificacion | `nom_responsable` | text | Nombre quien investiga | `nombre_de_quien_investiga` (qA) | OK | |
| 15 | Cargo responsable | `cargo_responsable` | text | Cargo | `cargo_de_quien_investiga` (qA) | OK | |
| 16 | Telefono responsable | `telefono_responsable` | phone | Telefono | `telefono` (qA) | OK | |
| 17 | Correo responsable | `correo_responsable` | text | Correo | `correo_electronico` (qA) | OK | |
| 18 | Envio ficha | `envio_ficha` | radio SI/NO | N/A | N/A | IGSS-only | |
| 19 | Seguro Social (IGSS) | `es_seguro_social` | radio hidden | Seguro Social checkbox | `otro_establecimiento` = "Seguro Social (IGSS)" | OK | Auto-set, hidden |
| 20 | Establecimiento privado | `establecimiento_privado` | radio hidden | Establecimiento privado checkbox | `otro_establecimiento` = "ESTABLECIMIENTO PRIVADO" | OK | Auto-set, hidden |
| 21 | Nombre est. privado | `establecimiento_privado_nombre` | text hidden | Especifique | `especifique_privado` (qA) | OK | |
| 22 | Fuente de notificacion | `fuente_notificacion` | select (11 opts) | 9 opciones | `fuente_de_notificacion_` (9 opts) | **MISMATCH** | Ver Discrepancia D3 |
| 23 | Fuente notificacion otra | `fuente_notificacion_otra` | text | Especifique | `especifique_fuente` (qA) | OK | |
| 24 | Fecha visita domiciliaria | `fecha_visita_domiciliaria` | date | SI | `fecha_de_investigacion_domiciliaria` (qA) | OK | |
| 25 | Fecha inicio investigacion | `fecha_inicio_investigacion` | date | N/A | N/A | IGSS-only | |
| 26 | Busqueda activa | `busqueda_activa` | select (3 opts) | N/A | N/A | IGSS-only | Retrospectiva/Comunidad/Otras |

### SECCION 3: INFORMACION DEL PACIENTE

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 27 | Numero afiliacion | `afiliacion` | text | N/A | N/A | IGSS-only | |
| 28 | Tipo identificacion | `tipo_identificacion` | select DPI/PASAPORTE/OTRO | SI | `codigo_unico_de_identificacion_dpi_pasaporte_otro` (3 opts) | OK | |
| 29 | Numero identificacion | `numero_identificacion` | text | SI | `no_de_dpi` / `no_de_pasaporte` / `especifique_cui` (sub-preguntas) | **MISMATCH** | GoData split por tipo, React unificado. Ver D4 |
| 30 | Nombres | `nombres` | text | SI | `firstName` (std) | OK | |
| 31 | Apellidos | `apellidos` | text | SI | `lastName` (std) | OK | |
| 32 | Segundo nombre | N/A | -- | N/A | `middleName` (std) | MISSING_FORM | GoData tiene middleName |
| 33 | Sexo | `sexo` | radio M/F | SI | `gender` MALE/FEMALE (std) | OK | Mapeo directo |
| 34 | Fecha nacimiento | `fecha_nacimiento` | date | SI | `dob` (std) | OK | |
| 35 | Edad en anios | `edad_anios` | number (auto) | SI | `age.years` (std) | OK | |
| 36 | Edad en meses | `edad_meses` | number (auto) | SI | `age.months` (std) | OK | |
| 37 | Edad en dias | `edad_dias` | number (auto) | SI | N/A | MISSING_GODATA | GoData no tiene campo dias |
| 38 | Pueblo / Etnia | `pueblo_etnia` | select (7 opts) | SI (5 opts) | `pueblo` (5 opts) | **MISMATCH** | Ver Discrepancia D5 |
| 39 | Comunidad linguistica | `comunidad_linguistica` | text | SI | `comunidad_linguistica` (select 23 opts) | **MISMATCH** | React=text libre, GoData=select con 23 etnias mayas. Ver D6 |
| 40 | Es extranjero | N/A | -- | SI | `extranjero_` SI/NO | **MISSING_FORM** | GoData y PDF tienen campo Extranjero separado |
| 41 | Es migrante | `es_migrante` | radio SI/NO | SI | `migrante` SI/NO | OK | |
| 42 | Ocupacion | `ocupacion` | select (441 opts MSPAS) | SI | `ocupacion_` (text libre) | **MISMATCH** | React=select con catalogo EPIWEB, GoData=text libre. Ver D7 |
| 43 | Escolaridad | `escolaridad` | select (17 opts) | SI | `escolaridad_` (9 opts) | **MISMATCH** | Ver Discrepancia D8 |
| 44 | Telefono paciente | `telefono_paciente` | phone | SI | `telefono_` (qA numeric) | OK | |
| 45 | Pais residencia | `pais_residencia` | text (default GUATEMALA) | SI | `pais_de_residencia_` (GUATEMALA/OTRO) | **MISMATCH** | React=text libre, GoData=select 2 opts. Ver D9 |
| 46 | Departamento residencia | `departamento_residencia` | select (22 deptos) | SI | `departamento_de_residencia_` (22 deptos) | OK | Mismos 22 departamentos |
| 47 | Municipio residencia | `municipio_residencia` | select (cascading) | SI | `municipio_de_residencia_*` (cascading per depto) | OK | |
| 48 | Poblado / Localidad | `poblado` | select (cascading) | SI | `lugar_poblado_` (text libre) | **MISMATCH** | React=select cascading, GoData=text libre |
| 49 | Direccion exacta | `direccion_exacta` | textarea | SI | `direccion_de_residencia_` (text) | OK | |
| 50 | Nombre encargado/tutor | `nombre_encargado` | text | SI | `nombre_del_tutor_` (SI/NO gate) | OK | GoData tiene gate "Tiene tutor?" |
| 51 | Parentesco tutor | `parentesco_tutor` | select (6 opts) | SI | `parentesco_` (text libre) | **MISMATCH** | React=select, GoData=text. Ver D10 |
| 52 | Tipo ID tutor | `tipo_id_tutor` | select DPI/PASAPORTE/OTRO | SI | `codigo_unico_de_identificacion_dpi_pasaporte_otro_` (3 opts) | OK | |
| 53 | Numero ID tutor | `numero_id_tutor` | text | SI | `no_de_dpi_` / `no_de_pasaporte_` / `especifique_doc` | OK | Same split pattern as patient |
| 54 | Telefono encargado | `telefono_encargado` | phone | N/A | N/A | IGSS-only | |
| 55 | Nombre tutor (tiene tutor gate) | N/A | -- | N/A | `nombre_del_tutor_` SI/NO then sub-q | PARTIAL | GoData has gate, React shows field always |

### SECCION 4: EMBARAZO

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 56 | Esta embarazada | `esta_embarazada` | radio SI/NO/N/A | SI | `pregnancyStatus` (std ref_data) | OK | |
| 57 | Lactando | `lactando` | radio SI/NO | N/A | N/A | MISSING_PDF | Campo IGSS/React only |
| 58 | Semanas embarazo | `semanas_embarazo` | number | SI | N/A (no directo) | MISSING_GODATA | |
| 59 | Trimestre embarazo | `trimestre_embarazo` | select 1/2/3 (auto) | SI (trimestre checkbox) | N/A | MISSING_GODATA | |
| 60 | Fecha probable parto | `fecha_probable_parto` | date | N/A | N/A | MISSING_PDF | Campo React only |
| 61 | Vacuna en embarazada | `vacuna_embarazada` | select SI/NO/NS/NA | N/A | N/A | MISSING_PDF | |
| 62 | Fecha vacunacion embarazada | `fecha_vacunacion_embarazada` | date | N/A | N/A | MISSING_PDF | |

### SECCION 5: ANTECEDENTES Y VACUNACION

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 63 | Paciente vacunado | `vacunado` | radio SI/NO/DESCONOCIDO | SI/NO/DESCONOCIDO | `paciente_vacunado_` SI/NO/VERBAL/DESCONOCIDO | **MISMATCH** | Ver Discrepancia D11 |
| 64 | Fuente info vacunacion | `fuente_info_vacuna` | select (5 opts) | 4 opts | `fuente_de_la_informacion_sobre_la_vacunacion_` (4 opts) | **MISMATCH** | Ver Discrepancia D12 |
| 65 | Sector vacunacion | `sector_vacunacion` | select MSPAS/IGSS/Privado | SI | `vacunacion_en_el_sector_` MSPAS/IGSS/PRIVADO | OK | |
| 66 | Tipo vacuna recibida | N/A (split por tipo) | -- | SPR/SR checkboxes | `tipo_de_vacuna_recibida_` multi-select SPR/SR | **MISMATCH** | React split en campos, GoData multi-select. Ver D13 |
| 67 | Dosis SPR | `dosis_spr` | select 1/2/3/Mas/NR | SI | `numero_de_dosis` (numeric, sub-q de SPR) | OK | Conceptualmente alineado |
| 68 | Fecha ultima SPR | `fecha_ultima_spr` | date | SI | `fecha_de_la_ultima_dosis` (date, sub-q de SPR) | OK | |
| 69 | Dosis SR | `dosis_sr` | select 1/2/3/Mas/NR | SI | `numero_de_dosis_` (numeric, sub-q de SR) | OK | |
| 70 | Fecha ultima SR | `fecha_ultima_sr` | date | SI | `fecha_de_la_ultima_dosis_` (date, sub-q de SR) | OK | |
| 71 | Dosis SPRV | `dosis_sprv` | select 1/2/3/Mas/NR | SI | N/A | **MISSING_GODATA** | GoData no tiene SPRV |
| 72 | Fecha ultima SPRV | `fecha_ultima_sprv` | date | SI | N/A | **MISSING_GODATA** | |
| 73 | Tipo vacuna (legacy) | `tipo_vacuna` | select hidden | EPIWEB legacy | N/A | IGSS-only | backward-compat |
| 74 | Num dosis (legacy) | `numero_dosis_spr` | select hidden | EPIWEB legacy | N/A | IGSS-only | |
| 75 | Fecha ult dosis (legacy) | `fecha_ultima_dosis` | date hidden | EPIWEB legacy | N/A | IGSS-only | |
| 76 | Observaciones vacuna | `observaciones_vacuna` | text hidden | N/A | N/A | IGSS-only | |
| 77 | Antecedentes medicos | `tiene_antecedentes_medicos` | radio SI/NO/DESC | SI/NO/DESCONOCIDO | `antecedentes_medicos_` SI/NO/DESCONOCIDO | OK | |
| 78 | Detalle antecedentes | `antecedentes_medicos_detalle` | text | Especifique | N/A (GoData usa checkboxes) | **MISMATCH** | React=text libre, GoData=select con sub-opts |
| 79 | Desnutricion | `antecedente_desnutricion` | radio SI/NO | Checkbox | `especifique_ant` = "DESNUTRICION" (checkbox) | OK | Different UI, same concept |
| 80 | Inmunocompromiso | `antecedente_inmunocompromiso` | radio SI/NO | Checkbox | `especifique_ant` = "INMUNOCOMPROMISO" | OK | |
| 81 | Enfermedad cronica | `antecedente_enfermedad_cronica` | radio SI/NO | Checkbox | `especifique_ant` = "ENFERMEDAD CRONICA" | OK | |
| 82 | Otro antecedente | N/A (covered by detalle) | -- | Otro + especifique | `especifique_ant` = "OTRO" + `especifique_A` (text) | PARTIAL | React has free text, GoData has OTRO option |

### SECCION 6: DATOS CLINICOS

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 83 | Fecha inicio sintomas | `fecha_inicio_sintomas` | date | SI | `fecha_de_inicio_de_sintomas_` (qA) + `dateOfOnset` (std) | OK | |
| 84 | Fecha captacion | `fecha_captacion` | date | N/A | N/A | IGSS-only | |
| 85 | Fecha inicio erupcion | `fecha_inicio_erupcion` | date | SI | `fecha_de_inicio_de_exantema_rash_` (qA) | OK | |
| 86 | Sitio inicio erupcion | `sitio_inicio_erupcion` | select (5 opts) | N/A | N/A | MISSING_PDF | MISSING_GODATA. Campo IGSS/EPIWEB only |
| 87 | Sitio erupcion otro | `sitio_inicio_erupcion_otro` | text | N/A | N/A | IGSS-only | |
| 88 | Fecha inicio fiebre | `fecha_inicio_fiebre` | date | SI | `fecha_de_inicio_de_fiebre_` (qA) | OK | |
| 89 | Temperatura C | `temperatura_celsius` | text | SI | `temp_c` (numeric, sub-q de Fiebre) | OK | |
| 90 | Sintomas gate | N/A (individual fields) | -- | N/A | `sintomas_` SI/NO | **MISSING_FORM** | GoData tiene gate "Sintomas SI/NO" antes de listar |
| 91 | Fiebre | `signo_fiebre` | radio SI/NO/DESC | SI | `que_sintomas_` includes "Fiebre" | **MISMATCH** | React=3-radio per sign, GoData=multi-select. Ver D14 |
| 92 | Exantema | `signo_exantema` | radio SI/NO/DESC | SI | `que_sintomas_` includes "Exantema/Rash" | **MISMATCH** | Same D14 |
| 93 | Manchas de Koplik | `signo_manchas_koplik` | radio SI/NO/DESC | SI | `que_sintomas_` includes "Manchas de Koplik" | **MISMATCH** | Same D14 |
| 94 | Tos | `signo_tos` | radio SI/NO/DESC | SI | `que_sintomas_` includes "Tos" | **MISMATCH** | Same D14 |
| 95 | Conjuntivitis | `signo_conjuntivitis` | radio SI/NO/DESC | SI | `que_sintomas_` includes "Conjuntivitis" | **MISMATCH** | Same D14 |
| 96 | Coriza/catarro | `signo_coriza` | radio SI/NO/DESC | SI | `que_sintomas_` includes "Coriza / Catarro" | **MISMATCH** | Same D14 |
| 97 | Adenopatias | `signo_adenopatias` | radio SI/NO/DESC | SI | `que_sintomas_` includes "Adenopatias" | **MISMATCH** | Same D14 |
| 98 | Artralgia | `signo_artralgia` | radio SI/NO/DESC | SI | `que_sintomas_` includes "Artralgia / Artritis" | **MISMATCH** | Same D14 |
| 99 | Asintomatico | `asintomatico` | radio SI/NO/DESC | N/A | N/A | MISSING_PDF | IGSS-only |
| 100 | Hospitalizado | `hospitalizado` | radio SI/NO/DESC | SI/NO/DESCONOCIDO | `hospitalizacion_` SI/NO/DESCONOCIDO | OK | |
| 101 | Nombre hospital | `hosp_nombre` | text | SI | `nombre_del_hospital_` (text) | OK | |
| 102 | Fecha hospitalizacion | `hosp_fecha` | date | SI | `fecha_de_hospitalizacion_` (date) | OK | |
| 103 | No. registro medico | `no_registro_medico` | text | N/A | N/A | IGSS-only | |
| 104 | Condicion egreso hosp | `condicion_egreso` | select MEJORADO/GRAVE/MUERTO | N/A | N/A | IGSS-only | Diferente de condicion_final_paciente |
| 105 | Fecha egreso | `fecha_egreso` | date | N/A | N/A | IGSS-only | |
| 106 | Fecha defuncion (hosp) | `fecha_defuncion` | date | SI | `fecha_de_defuncion` (qA, under clasificacion) | PARTIAL | React in Tab 5, GoData in clasificacion |
| 107 | Medico certifica defuncion | `medico_certifica_defuncion` | text | N/A | N/A | IGSS-only | |
| 108 | Motivo consulta | `motivo_consulta` | textarea | N/A | N/A | IGSS-only | |
| 109 | Tiene complicaciones | `tiene_complicaciones` | radio SI/NO/DESC | SI/NO/DESCONOCIDO | `complicaciones_` SI/NO/DESCONOCIDO | OK | |
| 110 | Neumonia | `comp_neumonia` | radio SI/NO | Checkbox | `especifique_complicaciones_` includes "NEUMONIA" | OK | Different UI, same concept |
| 111 | Encefalitis | `comp_encefalitis` | radio SI/NO | Checkbox | `especifique_complicaciones_` includes "ENCEFALITIS" | OK | |
| 112 | Diarrea | `comp_diarrea` | radio SI/NO | Checkbox | `especifique_complicaciones_` includes "DIARREA" | OK | |
| 113 | Trombocitopenia | `comp_trombocitopenia` | radio SI/NO | Checkbox | `especifique_complicaciones_` includes "TROMBOCITOPENIA" | OK | |
| 114 | Otitis | `comp_otitis` | radio SI/NO | Checkbox | `especifique_complicaciones_` includes "OTITIS MEDIA AGUDA" | OK | GoData dice "OTITIS MEDIA AGUDA", React dice "Otitis" |
| 115 | Ceguera | `comp_ceguera` | radio SI/NO | Checkbox | `especifique_complicaciones_` includes "CEGUERA" | OK | |
| 116 | Otra complicacion | `comp_otra_texto` | text | Otra + especifique | `especifique_complicaciones_` = "OTRA" + `especique` (text) | OK | |
| 117 | Aislamiento respiratorio | `aislamiento_respiratorio` | radio SI/NO/DESC | SI/NO/DESCONOCIDO | `aislamiento_respiratorio` SI/NO/DESCONOCIDO | OK | |
| 118 | Fecha aislamiento | `fecha_aislamiento` | date | SI | `fecha_de_aislamiento` (date) | OK | |

### SECCION 7: FACTORES DE RIESGO

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 119 | Contacto sospechoso 7-23d | `contacto_sospechoso_7_23` | radio SI/NO/DESC | SI/NO/DESCONOCIDO | `tuvo_contacto_con_un_caso_sospechoso_o_confirmado` Si/No/Desconocido | OK | GoData dice "caso sospechoso O CONFIRMADO" |
| 120 | Caso en comunidad 3m | `caso_sospechoso_comunidad_3m` | radio SI/NO/DESC | SI/NO/DESCONOCIDO | `Existe_caso_en_muni` Si/No/Desconocido | OK | GoData dice "CONFIRMADO" no "sospechoso" |
| 121 | Viajo 7-23 dias | `viajo_7_23_previo` | radio SI/NO | SI/NO | `viajo_durante_los_7_23_dias` Si/No | OK | React missing DESCONOCIDO. GoData also just Si/No |
| 122 | Pais viaje | `viaje_pais` | text | SI | `pais_departamento_y_municipio` GUATEMALA/OTRO | **MISMATCH** | React=text libre, GoData=select+cascade. Ver D9 |
| 123 | Departamento viaje | `viaje_departamento` | text | SI | `departamento` (select 22 deptos, sub-q) | **MISMATCH** | React=text, GoData=select |
| 124 | Municipio viaje | `viaje_municipio` | text | SI | `municipio` (text libre) | OK | Both text |
| 125 | Fecha salida viaje | `viaje_fecha_salida` | date | SI | `fecha_de_salida_viaje` (date) | OK | |
| 126 | Fecha entrada viaje | `viaje_fecha_entrada` | date | SI | `fecha_de_entrada_viaje` (date) | OK | |
| 127 | Destino viaje (legacy) | `destino_viaje` | text hidden | EPIWEB legacy | N/A | IGSS-only | |
| 128 | Familiar viajo exterior | `familiar_viajo_exterior` | radio SI/NO | SI | `alguna_persona_de_su_casa_ha_viajado_al_exterior` Si/No | OK | |
| 129 | Fecha retorno familiar | `familiar_fecha_retorno` | date | SI | `fecha_de_retorno` (date) | OK | |
| 130 | Contacto enfermo catarro | `contacto_enfermo_catarro` | radio SI/NO | N/A | N/A | IGSS-only | Campo EPIWEB legacy |
| 131 | Contacto embarazada | `contacto_embarazada` | radio SI/NO/DESC | SI/NO/DESCONOCIDO | `el_paciente_estuvo_en_contacto_con_una_mujer_embarazada1` Si/No/Desconocido | OK | |
| 132 | Fuente posible contagio | `fuente_posible_contagio` | select (9 opts) | SI | `fuente_posible_de_contagio1` multi-select (9 opts) | **MISMATCH** | React=single select, GoData=multi-select |
| 133 | Otra fuente contagio | `fuente_contagio_otro` | text | Especifique | `otro_especifique` (text) | OK | |

### SECCION 8: ACCIONES DE RESPUESTA

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 134 | BAI realizada | `bai_realizada` | radio SI/NO | SI | `se_realizo_busqueda_activa_institucional_de_casos_bai` 1=Si/2=No | OK | GoData usa codes 1/2 |
| 135 | BAI casos sospechosos | `bai_casos_sospechosos` | number | SI | `numero_de_casos_sospechosos_identificados_en_bai` (numeric) | OK | |
| 136 | BAC realizada | `bac_realizada` | radio SI/NO | SI | `se_realizo_busqueda_activa_comunitaria_de_casos_bac` 1=Si/2=No | OK | |
| 137 | BAC casos sospechosos | `bac_casos_sospechosos` | number | SI | `numero_de_casos_sospechosos_identificados_en_bac` (numeric) | OK | |
| 138 | Vacunacion bloqueo | `vacunacion_bloqueo` | radio SI/NO | SI | `hubo_vacunacion_de_bloqueo` 1=Si/2=No | OK | |
| 139 | Monitoreo rapido vacunacion | `monitoreo_rapido_vacunacion` | radio SI/NO | SI | `se_realizo_monitoreo_rapido_de_vacunacion` 1=Si/2=No | OK | |
| 140 | Vacunacion barrido | `vacunacion_barrido` | radio SI/NO | SI | `hubo_vacunacion_con_barrido_documentado` 1=Si/2=No | OK | |
| 141 | Vitamina A administrada | `vitamina_a_administrada` | radio SI/NO/DESC | SI/NO/Desconocido | `se_le_administro_vitamina_a` 1=Si/2=No/3=Desconocido | OK | |
| 142 | Vitamina A dosis | `vitamina_a_dosis` | select 1/2/3/4+/Desc | SI (numero) | `numero_de_dosis_de_vitamina_a_recibidas` (numeric) | OK | React select vs GoData numeric |
| 143 | Acciones NO gate | N/A | -- | N/A | `acciones_de_respuesta` SI/NO gate + `por_que_no_acciones_respuesta` | **MISSING_FORM** | GoData tiene gate y campo "por que no" |
| 144 | Lugares visitados/rutas | N/A | -- | SI (tabla rutas) | `lugares_visitados_y_rutas_de_desplazamiento_del_caso` (full section) | **MISSING_FORM** | Ver Discrepancia D15 |

### SECCION 9: LABORATORIO

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 145 | Recolecto muestra | `recolecto_muestra` | radio SI/NO | SI | N/A (directo) | PARTIAL | GoData maneja lab-results via API endpoint separado |
| 146 | Motivo no recoleccion | `motivo_no_recoleccion` | text | SI | N/A | MISSING_GODATA | |
| 147 | Muestra suero | `muestra_suero` | radio SI/NO | SI | Lab-results API (sampleType=SERUM) | PARTIAL | |
| 148 | Fecha suero | `muestra_suero_fecha` | date | SI | Lab-results API (dateSampleTaken) | PARTIAL | |
| 149 | Muestra hisopado | `muestra_hisopado` | radio SI/NO | SI | Lab-results API (sampleType=THROAT_SWAB) | PARTIAL | |
| 150 | Fecha hisopado | `muestra_hisopado_fecha` | date | SI | Lab-results API | PARTIAL | |
| 151 | Muestra orina | `muestra_orina` | radio SI/NO | SI | Lab-results API (sampleType=URINE) | PARTIAL | |
| 152 | Fecha orina | `muestra_orina_fecha` | date | SI | Lab-results API | PARTIAL | |
| 153 | Muestra otra | `muestra_otra` | radio SI/NO | SI | Lab-results API | PARTIAL | |
| 154 | Desc otra muestra | `muestra_otra_descripcion` | text | SI | Lab-results API | PARTIAL | |
| 155 | Fecha otra muestra | `muestra_otra_fecha` | date | SI | Lab-results API | PARTIAL | |
| 156 | Antigeno | `antigeno_prueba` | select 4 opts | SI | Lab-results (testedFor) | PARTIAL | |
| 157 | Antigeno otro | `antigeno_otro` | text | N/A | N/A | IGSS-only | |
| 158 | Resultado prueba | `resultado_prueba` | select 4 opts | SI | Lab-results (result) | PARTIAL | React: Neg/Pos/Inadecuada/Indet |
| 159 | Fecha recepcion lab | `fecha_recepcion_laboratorio` | date | SI | Lab-results (dateSampleDelivered) | PARTIAL | |
| 160 | Fecha resultado lab | `fecha_resultado_laboratorio` | date | SI | Lab-results (dateOfResult) | PARTIAL | |
| 161 | IgG cualitativo | `resultado_igg_cualitativo` | select 5 opts | SI (matriz) | Lab-results | PARTIAL | |
| 162 | IgG numerico | `resultado_igg_numerico` | text | N/A | N/A | IGSS-only | |
| 163 | IgM cualitativo | `resultado_igm_cualitativo` | select 5 opts | SI (matriz) | Lab-results | PARTIAL | |
| 164 | IgM numerico | `resultado_igm_numerico` | text | N/A | N/A | IGSS-only | |
| 165 | PCR orina | `resultado_pcr_orina` | select 4 opts | SI | Lab-results | PARTIAL | |
| 166 | PCR hisopado | `resultado_pcr_hisopado` | select 4 opts | SI | Lab-results | PARTIAL | |
| 167 | Motivo no 3 muestras | `motivo_no_3_muestras` | text | SI | N/A | MISSING_GODATA | |
| 168 | Lab muestras JSON | `lab_muestras_json` | lab_matrix | SI (tabla detallada) | Lab-results API | PARTIAL | Different structure |
| 169 | Secuenciacion resultado | `secuenciacion_resultado` | text | SI | Lab-results (sequence) | PARTIAL | |
| 170 | Secuenciacion fecha | `secuenciacion_fecha` | date | SI | Lab-results (dateSampleSent) | PARTIAL | |

### SECCION 10: CLASIFICACION

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 171 | Contactos directos | `contactos_directos` | number | N/A | N/A | IGSS-only | |
| 172 | Clasificacion caso | `clasificacion_caso` | select (10 opts) | 4 opts principales | `clasificacion` CLASIFICADO/"2" + `clasificacion_final` (4 opts) | **MISMATCH** | Ver Discrepancia D16 |
| 173 | Criterio confirmacion | `criterio_confirmacion` | select Lab/Nexo/Clinico | SI | `criterio_de_confirmacion_sarampion` LABSR/NE/CX + rubeola variant | OK | GoData split by disease |
| 174 | Criterio descarte | `criterio_descarte` | select (8 opts) | SI | `criterio_para_descartar_el_caso` LAB/RVAC/CX2/OTRO | **MISMATCH** | Ver Discrepancia D17 |
| 175 | Fuente infeccion | `fuente_infeccion` | select (4 opts) | SI | `fuente_de_infeccion_de_los_casos_confirmados` 1-4 | OK | Mismas opciones |
| 176 | Pais importacion | `pais_importacion` | text | SI | `importado_pais_de_importacion` / `pais_de_importacion` | OK | GoData duplicate for opt 1 and 2 |
| 177 | Contacto otro caso | `contacto_otro_caso` | radio SI/NO | SI | `contacto_de_otro_caso` SI/NO | OK | |
| 178 | Detalle contacto otro caso | `contacto_otro_caso_detalle` | text | Especifique | N/A | MISSING_GODATA | |
| 179 | Caso analizado por | `caso_analizado_por` | select (4 opts) | SI | `caso_analizado_por` multi-select 1=CONAPI/2=DEGR/3=COMISION/4=OTRO | **MISMATCH** | React=single, GoData=multi-select |
| 180 | Caso analizado por otro | `caso_analizado_por_otro` | text | Especifique | `especifique_otro_clasificacion` (text) | OK | |
| 181 | Fecha clasificacion final | `fecha_clasificacion_final` | date | SI | `fecha_de_clasificacion` (date) | OK | |
| 182 | Responsable clasificacion | `responsable_clasificacion` | text | SI | N/A | MISSING_GODATA | |
| 183 | Condicion final paciente | `condicion_final_paciente` | select Recup/Secuelas/Fallec/Desc | SI | `condicion_final_del_paciente` 1-4 | OK | |
| 184 | Causa muerte certificado | `causa_muerte_certificado` | text | SI | `causa_de_muerte_segun_certificado_de_defuncion` (text) | OK | |
| 185 | Observaciones | `observaciones` | textarea | SI | N/A | MISSING_GODATA | |

### SECCION 11: DATOS IGSS (React Tab 9, exclusivos)

| # | Concepto | React (field ID) | React Type | MSPAS PDF | GoData Variable | Status | Notas |
|---|----------|-----------------|------------|-----------|-----------------|--------|-------|
| 186 | Es empleado IGSS | `es_empleado_igss` | radio SI/NO | N/A | N/A | IGSS-only | |
| 187 | Unidad medica trabaja | `unidad_medica_trabaja` | select | N/A | N/A | IGSS-only | |
| 188 | Puesto desempena | `puesto_desempena` | text | N/A | N/A | IGSS-only | |
| 189 | Subgerencia IGSS | `subgerencia_igss` | select cascading | N/A | N/A | IGSS-only | |
| 190 | Subgerencia otra | `subgerencia_igss_otra` | text | N/A | N/A | IGSS-only | |
| 191 | Direccion IGSS | `direccion_igss` | select cascading | N/A | N/A | IGSS-only | |
| 192 | Direccion otra | `direccion_igss_otra` | text | N/A | N/A | IGSS-only | |
| 193 | Departamento IGSS | `departamento_igss` | select cascading | N/A | N/A | IGSS-only | |
| 194 | Departamento otro | `departamento_igss_otro` | text | N/A | N/A | IGSS-only | |
| 195 | Seccion IGSS | `seccion_igss` | select cascading | N/A | N/A | IGSS-only | |
| 196 | Seccion otra | `seccion_igss_otra` | text | N/A | N/A | IGSS-only | |

---

## 3. Discrepancias de Opciones Detalladas

### D1: Diagnostico de Sospecha

| Sistema | Opciones |
|---------|----------|
| **React** | Sarampion, Rubeola, Dengue, Otra Arbovirosis, Otra febril exantematica, Caso altamente sospechoso de Sarampion |
| **MSPAS PDF** | Sarampion, Rubeola, Dengue, Otro Arbovirosis, Otro febril exantematica (checkboxes) + Caso altamente sospechoso |
| **GoData** | SARAMPION, RUBEOLA, DENGUE, OTRO ARBOVIROSIS, OTRO FEBRIL EXANTEMATICA (single-select, 5 opts) |

**Discrepancias**:
- React es `checkbox` (multi-select), GoData es `single-select` -- **No se puede seleccionar multiples en GoData**
- "Caso altamente sospechoso" es opcion independiente en React, pero sub-pregunta en GoData (solo aparece si SARAMPION)
- **Accion**: Cambiar React a single-select con sub-pregunta para "altamente sospechoso" O aceptar la diferencia y mapear primer seleccion a GoData

### D2: Area de Salud MSPAS / DDRISS / DMS

| Sistema | Campo |
|---------|-------|
| **React** | NO EXISTE |
| **MSPAS PDF** | DDRISS (29 areas) + DMS (cascading) + Servicio de Salud (text) |
| **GoData** | `direccion_de_area_de_salud` (29 opts) + `distrito_municipal_de_salud_dms*` (cascading per area) + `servicio_de_salud*` (text) |

**Discrepancias**:
- React no tiene estos 3 campos (area_salud, distrito, servicio_salud MSPAS)
- Plan los menciona como `area_salud_mspas`, `distrito_salud_mspas`, `servicio_salud_mspas` pero NO estan implementados en formSchema.js
- **Accion CRITICA**: Agregar 3 campos cascading al Tab 1. GoData tiene 29 DDRISS (no 22 departamentos): incluye Guatemala split en 4, Peten en 3, Ixcan, Ixil separados

### D3: Fuente de Notificacion

| # | React | MSPAS PDF | GoData |
|---|-------|-----------|--------|
| 1 | Servicio de Salud | Servicio de Salud | SERVICIO DE SALUD |
| 2 | Privada | N/A | N/A |
| 3 | Laboratorio | Laboratorio | LABORATORIO |
| 4 | Comunidad | Caso reportado por la comunidad | CASO REPORTADO POR LA COMUNIDAD |
| 5 | Busqueda Activa Institucional | Busqueda Activa Institucional | BUSQUEDA ACTIVA INSTITUCIONAL |
| 6 | Busqueda Activa Comunitaria | Busqueda Activa Comunitaria | BUSQUEDA ACTIVA COMUNITARIA |
| 7 | Busqueda Activa Laboratorial | Busqueda Activa Laboratorial | BUSQUEDA ACTIVA LABORATORIAL |
| 8 | Investigacion de Contactos | Investigacion de Contactos | INVESTIGACION DE CONTACTOS |
| 9 | Auto Notificacion | Auto Notificacion por Numero Gratuito | AUTO NOTIFICACION POR NUMERO GRATUITO |
| 10 | Defuncion | N/A | N/A |
| 11 | Otra | Otro | OTRO |

**Discrepancias**:
- "Privada" solo en React -- ni PDF ni GoData la tienen
- "Defuncion" solo en React -- ni PDF ni GoData
- "Auto Notificacion" en React es corto, GoData dice "POR NUMERO GRATUITO"
- "Comunidad" vs "CASO REPORTADO POR LA COMUNIDAD" -- naming difference
- **Accion**: Remover "Privada" (se cubre con establecimiento_privado flag). Remover "Defuncion" o moverla. Alinear texto de "Auto Notificacion" con GoData

### D4: Numero de Identificacion Split

| Sistema | Estructura |
|---------|-----------|
| **React** | `numero_identificacion` campo unico de texto |
| **GoData** | Sub-preguntas separadas: `no_de_dpi` (numeric), `no_de_pasaporte` (text), `especifique_cui` (text) |

**Accion**: React puede mantener campo unificado. El mapeo GoData debe enrutar al sub-campo correcto segun `tipo_identificacion`

### D5: Pueblo / Etnia

| # | React (etniasOptions) | MSPAS PDF | GoData |
|---|----------------------|-----------|--------|
| 1 | Maya | Maya | MAYA |
| 2 | Ladino / Mestizo | Ladino | LADINO |
| 3 | Garifuna | Garifuna | GARIFUNA |
| 4 | Xinca | Xinca | XINCA |
| 5 | Otros | N/A | N/A |
| 6 | Extranjero | N/A | N/A |
| 7 | Desconocido | Desconocido | DESCONOCIDO |

**Discrepancias**:
- React tiene "Otros" y "Extranjero" que GoData/PDF no tienen
- React dice "Ladino / Mestizo", GoData/PDF dice "LADINO"
- **Accion**: Alinear a 5 opciones MSPAS. Mapear "Otros"/"Extranjero" a "DESCONOCIDO" en GoData

### D6: Comunidad Linguistica

| Sistema | Tipo | Opciones |
|---------|------|----------|
| **React** | text libre | N/A |
| **GoData** | select | 23 opciones (Achi, Akateka, Awakateka, Ch'orti', Chalchiteka, Chuj, Itza', Ixil, Jakalteka, Kaqchikel, K'iche', Mam, Mopan, Poqomam, Pocomchi', Q'anjob'al, Q'eqchi', Sakapulteka, Sipakapensa, Tektiteka, Tz'utujil, Uspanteka, No indica) |

**Accion**: Convertir React a select con las 23 comunidades mayas de GoData. Mas preciso y permite mapeo directo

### D7: Ocupacion

| Sistema | Tipo | Opciones |
|---------|------|----------|
| **React** | select | 441 opciones (catalogo MSPAS EPIWEB) |
| **GoData** | text libre | N/A |

**Accion**: Mantener React con select (mejor para EPIWEB). Mapear a text para GoData

### D8: Escolaridad

| # | React (17 opts) | GoData (9 opts) |
|---|----------------|-----------------|
| 1 | Ninguna | NINGUNO |
| 2 | Primaria Incompleta | -- |
| 3 | Primaria Completa | -- |
| 4 | Primaria | PRIMARIA |
| 5 | Secundaria Incompleta | -- |
| 6 | Secundaria Completa | -- |
| 7 | Secundaria | BASICOS |
| 8 | Diversificado Incompleto | -- |
| 9 | Diversificado Completo | -- |
| 10 | Diversificado | DIVERSIFICADO |
| 11 | Universitaria Incompleta | -- |
| 12 | Universitaria Completa | -- |
| 13 | Universitario | UNIVERSIDAD |
| 14 | Postgrado | -- |
| 15 | Alfabeto | -- |
| 16 | Analfabeto | -- |
| 17 | No aplica | NO APLICA |
| -- | -- | PRE PRIMARIA |
| -- | -- | OTRO |
| -- | -- | NO INDICA |

**Discrepancias**:
- React tiene granularidad (Completa/Incompleta) que GoData no tiene
- GoData tiene "PRE PRIMARIA", "OTRO", "NO INDICA" que React no tiene
- React tiene "Postgrado", "Alfabeto", "Analfabeto" que GoData no tiene
- GoData dice "BASICOS" donde React dice "Secundaria"
- **Accion**: React mantiene opciones EPIWEB. Mapeo GoData: Primaria*/Completa/Incompleta -> PRIMARIA, Secundaria* -> BASICOS, etc.

### D9: Pais de Residencia / Viaje

| Sistema | Tipo |
|---------|------|
| **React** | text libre (default GUATEMALA) |
| **GoData** | select: GUATEMALA / OTRO (con especifique) |

**Accion**: Considerar cambiar React a select GUATEMALA/OTRO con campo especifique para mejor mapeo

### D10: Parentesco Tutor

| Sistema | Tipo | Opciones |
|---------|------|----------|
| **React** | select | Madre, Padre, Abuelo/a, Tio/a, Hermano/a, Otro |
| **GoData** | text libre | N/A |

**Accion**: Mantener React select, mapear a text para GoData

### D11: Paciente Vacunado

| # | React | GoData |
|---|-------|--------|
| 1 | SI | SI |
| 2 | NO | NO |
| 3 | DESCONOCIDO | DESCONOCIDO |
| 4 | -- | VERBAL |

**Discrepancia**: GoData tiene "VERBAL" como opcion de vacunado (= sin carne, info verbal). React no tiene esta opcion.
**Accion**: Agregar "VERBAL" como opcion en React, o mapear "DESCONOCIDO" -> "VERBAL" cuando fuente_info_vacuna = "Verbal"

### D12: Fuente Informacion Vacunacion

| # | React (5 opts) | GoData (4 opts) |
|---|----------------|-----------------|
| 1 | Carne de Vacunacion | CARNE DE VACUNACION |
| 2 | SIGSA 5a Cuaderno | SIGSA 5A CUADERNO |
| 3 | SIGSA 5B Otros Grupos | SIGSA 5B OTROS GRUPOS |
| 4 | Registro Unico de Vacunacion | REGISTRO UNICO DE VACUNACION |
| 5 | Verbal | -- |

**Discrepancia**: React tiene "Verbal" que GoData no tiene (GoData usa VERBAL como opcion de `paciente_vacunado_` en vez)
**Accion**: Cuando React fuente="Verbal", mapear GoData paciente_vacunado="VERBAL"

### D13: Tipo Vacuna -- SPRV Missing en GoData

| Vacuna | React | PDF | GoData |
|--------|-------|-----|--------|
| SPR | `dosis_spr` + `fecha_ultima_spr` | SI | `tipo_de_vacuna_recibida_` = "SPR..." + sub-q dosis/fecha |
| SR | `dosis_sr` + `fecha_ultima_sr` | SI | `tipo_de_vacuna_recibida_` = "SR..." + sub-q dosis/fecha |
| SPRV | `dosis_sprv` + `fecha_ultima_sprv` | SI | **NO EXISTE** |

**Discrepancia**: GoData no tiene SPRV (Sarampion Paperas Rubeola Varicela). Solo SPR y SR.
**Accion**: Agregar nota que SPRV no se puede sincronizar a GoData. Mantener en React/BD

### D14: Signos y Sintomas -- Estructura Fundamental Diferente

| Sistema | Estructura |
|---------|-----------|
| **React** | 8 campos radio individuales (SI/NO/DESCONOCIDO cada uno) |
| **MSPAS PDF** | Checkboxes individuales + lista |
| **GoData** | Gate `sintomas_` SI/NO, luego `que_sintomas_` multi-select (8 opts) |

**Discrepancias**:
- GoData usa multi-select (solo se marcan los presentes) -- no tiene "NO" ni "DESCONOCIDO" per symptom
- React tiene "DESCONOCIDO" per symptom que GoData no puede representar
- GoData tiene gate "Sintomas SI/NO" que React no tiene

**Mapeo necesario**:
- React signo_X = "SI" -> incluir en array que_sintomas_
- React signo_X = "NO" -> excluir de array
- React signo_X = "DESCONOCIDO" -> excluir de array (pierde informacion)
- Si todos "NO" -> GoData sintomas_ = "NO"
- Si al menos uno "SI" -> GoData sintomas_ = "SI" + array de los que son SI

### D15: Lugares Visitados y Rutas de Desplazamiento -- SECCION COMPLETA AUSENTE

| Campo GoData | Existe en React | Existe en PDF |
|--------------|-----------------|---------------|
| `lugares_visitados_y_rutas_de_desplazamiento_del_caso` (SE INVESTIGO/NO/DESC) | NO | SI |
| `sitio_ruta_de_desplazamiento_1` (text) | NO | SI |
| `direccion_del_lugar_y_rutas_de_desplazamiento_1` (text) | NO | SI |
| `fecha_en_que_visito_el_lugar_ruta_1` (date) | NO | SI |
| `tipo_de_abordaje_realizado_1` (multi: BLOQUEO/BARRIDO/BAC/BAI) | NO | SI |
| `fecha_de_abordaje_1` (date) | NO | SI |
| Campos _2 (duplicado para segundo lugar) | NO | SI |

**Accion CRITICA**: Agregar seccion completa de "Lugares Visitados" al formulario React. Minimo 2 slots de lugar con: sitio, direccion, fecha visita, tipo abordaje (multi-select), fecha abordaje.

### D16: Clasificacion Final

| # | React (10 opts) | GoData | PDF |
|---|----------------|--------|-----|
| 1 | SOSPECHOSO | N/A (case.classification = SUSPECT) | N/A |
| 2 | CONFIRMADO SARAMPION | clasificacion_final = "1" (Sarampion) | Sarampion |
| 3 | CONFIRMADO RUBEOLA | clasificacion_final = "2" (Rubeola) | Rubeola |
| 4 | DESCARTADO | clasificacion_final = "3" (Descartado) | Descartado |
| 5 | PENDIENTE | clasificacion = "2" (PENDIENTE) | Pendiente |
| 6 | NO CUMPLE DEFINICION | clasificacion_final = "5" (No cumple) | No cumple |
| 7 | CLINICO | N/A | N/A |
| 8 | FALSO | N/A | N/A |
| 9 | ERROR DIAGNOSTICO | N/A | N/A |
| 10 | SUSPENDIDO | N/A | N/A |

**Discrepancias**:
- GoData tiene estructura de 2 niveles (CLASIFICADO/PENDIENTE -> sub-opcion)
- React opts 7-10 (CLINICO, FALSO, ERROR DX, SUSPENDIDO) son IGSS-only, no existen en GoData ni PDF
- GoData gate "CLASIFICADO" = ya se clasifico. React no tiene esta distincion
- **Accion**: Mapeo: SOSPECHOSO/PENDIENTE -> GoData "2" (pendiente). CONFIRMADO*/DESCARTADO/NO CUMPLE -> GoData "CLASIFICADO" + sub-opcion. CLINICO/FALSO/ERROR/SUSPENDIDO -> no enviar a GoData

### D17: Criterio para Descartar

| # | React (8 opts) | GoData (4 opts) | PDF |
|---|----------------|-----------------|-----|
| 1 | Laboratorial | LAB | Laboratorial |
| 2 | Reaccion Vacunal | RVAC | Relacionado con Vacuna |
| 3 | Dengue | OTRO | N/A |
| 4 | Parvovirus B19 | OTRO | N/A |
| 5 | Herpes 6 | OTRO | N/A |
| 6 | Reaccion Alergica | OTRO | N/A |
| 7 | Otro Diagnostico | OTRO | N/A |
| 8 | Clinico | CX2 | Clinico |

**Discrepancias**:
- GoData solo tiene 4 opciones (LAB/RVAC/CX2/OTRO) -- no desglosa por enfermedad
- React tiene 8 opciones mas granulares (Dengue, Parvovirus, Herpes, Alergica) que GoData agrupa en OTRO
- PDF 2026 solo tiene Laboratorial/Relacionado Vacuna/Clinico (3 opciones)
- **Accion**: React mantiene 8 opts. Mapeo GoData: Dengue/Parvovirus/Herpes/Alergica/Otro Dx -> "OTRO" + especifique texto

---

## 4. Resumen de Acciones Prioritarias

### PRIORIDAD 1 (Bloquean sincronizacion GoData)

| # | Accion | Esfuerzo | Archivos |
|---|--------|----------|----------|
| A1 | Agregar campos DDRISS/DMS/Servicio de Salud MSPAS (cascading, 29 areas) | Alto | formSchema.js, database.py |
| A2 | Agregar seccion "Lugares Visitados y Rutas de Desplazamiento" (2 slots) | Medio | formSchema.js, FormPage.jsx, database.py |
| A3 | Implementar mapeo sintomas: 8 radios individuales -> multi-select GoData | Medio | godata_field_map.py |
| A4 | Implementar mapeo clasificacion: 10 opts React -> 2-level GoData | Medio | godata_field_map.py |

### PRIORIDAD 2 (Datos inconsistentes entre sistemas)

| # | Accion | Esfuerzo |
|---|--------|----------|
| B1 | Cambiar `diagnostico_sospecha` de checkbox a single-select + sub-pregunta "altamente sospechoso" | Bajo |
| B2 | Agregar campo `es_extranjero` (SI/NO) -- falta en React, existe en GoData y PDF | Bajo |
| B3 | Agregar "VERBAL" como opcion de `vacunado` o documentar mapping logic | Bajo |
| B4 | Convertir `comunidad_linguistica` de text a select (23 comunidades mayas) | Bajo |
| B5 | Cambiar `fuente_posible_contagio` de single-select a multi-select (GoData es multi) | Bajo |
| B6 | Agregar gate "Acciones de respuesta SI/NO" + campo "por que no" | Bajo |
| B7 | Agregar `middleName` (segundo nombre) -- GoData standard field | Bajo |

### PRIORIDAD 3 (Cosmeticas / alineacion de texto)

| # | Accion |
|---|--------|
| C1 | Alinear texto "Auto Notificacion" -> "Auto Notificacion por Numero Gratuito" |
| C2 | Alinear "Comunidad" -> "Caso Reportado por la Comunidad" |
| C3 | Remover "Privada" y "Defuncion" de fuente_notificacion (no en PDF/GoData) |
| C4 | Alinear etnia "Ladino / Mestizo" -> "Ladino" (per MSPAS/GoData) |
| C5 | Documentar que SPRV no existe en GoData (solo SPR/SR) |
| C6 | Documentar que GoData criterio_descarte solo tiene 4 opts vs 8 en React |

---

## 5. Campos GoData sin Equivalente en React (Completos)

| GoData Variable | Seccion | Tipo | Descripcion |
|----------------|---------|------|-------------|
| `middleName` | Standard | string | Segundo nombre |
| `extranjero_` | Paciente | SI/NO | Es extranjero |
| `sintomas_` gate | Clinicos | SI/NO | Gate antes de listar sintomas |
| `acciones_de_respuesta` gate | Respuesta | SI/NO | Gate + "por que no" |
| `por_que_no_acciones_respuesta` | Respuesta | text | Razon de no acciones |
| `lugares_visitados_*` (12 sub-campos) | Rutas | varios | Seccion completa de rutas/desplazamiento |
| `riskLevel` | Standard | ref_data | Nivel de riesgo |
| `visualId` | Standard | auto | ID visual (SR-NNNN) |

---

## 6. Campos React sin Equivalente en GoData ni PDF (IGSS-only, 16 campos)

Estos campos son exclusivos del IGSS y no necesitan mapeo:

`diagnostico_registrado`, `codigo_cie10`, `afiliacion`, `unidad_medica`, `unidad_medica_otra`, `servicio_reporta`, `envio_ficha`, `fecha_inicio_investigacion`, `busqueda_activa`, `busqueda_activa_otra`, `fecha_captacion`, `no_registro_medico`, `condicion_egreso` (hosp), `fecha_egreso`, `medico_certifica_defuncion`, `motivo_consulta`, `contactos_directos`, `es_empleado_igss` + 8 campos organizacionales IGSS

# GoData Guatemala: Auditoría Campo por Campo

**Fecha:** 2026-03-26
**Outbreak ID:** ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19
**Fuente:** API GoData Guatemala (godataguatemala.mspas.gob.gt)
**Archivo de mapeo:** `backend/godata_field_map.py`

---

## Resumen Ejecutivo

| Categoría | Cantidad |
|-----------|----------|
| Campos estándar del caso | 10 configurados, 6 mandatory |
| Campos de cuestionario (conceptuales, sin contar variantes cascadeadas) | ~85 |
| Campos REQUIRED en cuestionario | 59 (mayoría son variantes cascadeadas de DMS/municipio) |
| **BUGS CRÍTICOS encontrados** | **5** |
| Campos mapeados correctamente | ~65 |
| Campos con valor incorrecto | ~12 |
| Campos no mapeados (GoData espera, no enviamos) | ~15 |
| Campos extra (enviamos, GoData no tiene) | 0 |

### Los 5 Bugs Críticos

1. **ACCENT STRIPPING mata los option values** -- `_godata_text()` quita acentos pero GoData requiere acentos en: SARAMPIÓN, RUBÉOLA, IXCÁN, PETÉN, QUICHÉ, SACATEPÉQUEZ, SOLOLÁ, SUCHITEPÉQUEZ, BÚSQUEDA ACTIVA, etc.
2. **Servicio de Salud variable mapping incorrecto** -- Nuestro mapa tiene ~12 variables equivocadas (ej: ESCUINTLA debería ser `servicio_de_salud_` pero tenemos `servicio_de_salud_5`).
3. **DAS→DMS lookup falla para Guatemala** -- No manejamos 4 DAS de Guatemala como entidades separadas en `direccion_de_area_de_salud`.
4. **Addresses/documents arrays vacíos en casos enviados** -- Los 5 casos existentes tienen arrays vacíos, pero nuestro código SÍ los genera. Posible que el endpoint los rechace silenciosamente o que el envío de prueba no incluyó estos campos.
5. **Section header `clasificacion` valor "PENDIENTE" no existe** -- GoData tiene "CLASIFICADO" y "2" (pendiente). Enviamos "PENDIENTE" como texto.

---

## Sección 1: Campos Estándar del Caso

Fuente: `visibleAndMandatoryFields.cases` del outbreak config.

| Campo GoData | Mandatory | Visible | Nuestro DB column | Mapped? | Notas |
|---|---|---|---|---|---|
| `firstName` | **SI** | SI | `nombres` | MAPPED | `_godata_text()` quita acentos -- OK para nombres |
| `middleName` | NO | SI | -- | NOT MAPPED | GoData lo acepta, no lo enviamos. Harmless. |
| `lastName` | **SI** | SI | `apellidos` | MAPPED | OK |
| `gender` | **SI** | SI | `sexo` | MAPPED | Via GENDER_MAP. OK. |
| `ageDob` | NO | SI | `edad_anios`, `edad_meses`, `fecha_nacimiento` | MAPPED | `age.years` + `age.months` + `dob`. OK. |
| `dateOfOnset` | **SI** | SI | `fecha_inicio_sintomas` | MAPPED | ISO format. OK. |
| `dateOfReporting` | **SI** | SI | `fecha_notificacion` | MAPPED | ISO format. OK. |
| `followUp[status]` | NO | SI | -- | NOT MAPPED | Follow-up tracking. No lo necesitamos. |
| `visualId` | **SI** | SI | `registro_id` | MAPPED | OK. |
| `pregnancyStatus` | -- | SI | `esta_embarazada`, `trimestre_embarazo` | MAPPED | OK con LNG refs correctos. |

### Campos estándar adicionales que nuestro código envía:

| Campo | Nuestro mapeo | Status |
|---|---|---|
| `classification` | Via CLASSIFICATION_MAP | MAPPED -- OK |
| `outcomeId` | Via OUTCOME_MAP | MAPPED -- OK |
| `dateOfOutcome` | `fecha_defuncion` | MAPPED -- OK |
| `occupation` | `ocupacion` | MAPPED -- pero `_godata_text()` quita acentos innecesariamente |
| `isDateOfReportingApproximate` | Hardcoded `False` | MAPPED -- OK |
| `documents` | `tipo_identificacion` + `numero_identificacion` + `afiliacion` | MAPPED -- pero arrays vacíos en casos reales (ver bug 4) |
| `addresses` | `pais_residencia`, `municipio_residencia`, `direccion_exacta`, etc. | MAPPED -- pero arrays vacíos en casos reales |
| `dateRanges` | hospitalización + aislamiento | MAPPED -- pero arrays vacíos en casos reales |
| `vaccinesReceived` | -- | **NOT MAPPED** -- no enviamos este array estándar (usamos solo questionnaire) |

---

## Sección 2: Campos del Cuestionario (por sección)

### 2.0 Diagnóstico de Sospecha
**Categoría:** FICHA_EPIDEMIOLOGICA_DE_VIGILANCIA_DE_SARAMPION_RUBEOLA

| Variable GoData | Req | Tipo | Opciones GoData | Nuestro DB column | Status | Problema |
|---|---|---|---|---|---|---|
| `diagnostico_de_sospecha_` | opt | SINGLE | SARAMPIÓN, RUBÉOLA, DENGUE, OTRO ARBOVIROSIS, OTRO FEBRIL EXANTEMÁTICA | `diagnostico_sospecha` | **WRONG VALUE** | Enviamos "SARAMPION" (sin acento), GoData espera "SARAMPIÓN" (con acento) |
| `caso_altamente_sospechoso_de_sarampion` | opt | SINGLE | SI, NO | -- | **NOT MAPPED** | Solo aparece cuando dx=SARAMPIÓN. No lo enviamos. |
| `especifique` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Solo si dx=OTRO ARBOVIROSIS. Low priority. |
| `especifique_` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Solo si dx=OTRO FEBRIL EXANTEMÁTICA. Low priority. |

### 2.1 Datos de la Unidad Notificadora
**Categoría:** DATOS_DE_LA_UNIDAD_NOTIFICADORA

| Variable GoData | Req | Tipo | Opciones | Nuestro DB | Status | Problema |
|---|---|---|---|---|---|---|
| `fecha_de_notificacion` | **REQ** | SINGLE | "Fecha de Notificación" | Hardcoded | MAPPED | Enviamos "Fecha de Notificacion" (sin acento), GoData espera "Fecha de Notificación" |
| `direccion_de_area_de_salud` | **REQ** | SINGLE | 29 DAS (con acentos) | `departamento_das` / `departamento_residencia` | **WRONG VALUE** | Quitamos acentos con `_godata_text()`. IXCÁN->IXCAN, PETÉN->PETEN, etc. |
| `distrito_municipal_de_salud_dms*` (29 vars) | **REQ** | SINGLE | Municipios por DAS | `distrito_salud` / `municipio_residencia` | MAPPED | Variable cascadeada correcta. Pero valor sin acentos. |
| `servicio_de_salud*` (29 vars) | opt | FREE_TEXT | -- | `servicio_salud_mspas` / `unidad_medica` | **WRONG VARIABLE** | Ver tabla de errores abajo |
| `fecha_de_consulta` | opt | DATE | -- | `fecha_registro_diagnostico` / `fecha_consulta` | MAPPED | OK |
| `fecha_de_investigacion_domiciliaria` | opt | DATE | -- | `fecha_visita_domiciliaria` | MAPPED | OK |
| `nombre_de_quien_investiga` | opt | FREE_TEXT | -- | `nombre_investigador` | MAPPED | OK |
| `cargo_de_quien_investiga` | opt | FREE_TEXT | -- | `cargo_investigador` | MAPPED | OK |
| `telefono` | opt | NUMERIC | -- | `telefono_investigador` | MAPPED | OK |
| `correo_electronico` | opt | FREE_TEXT | -- | `correo_investigador` | MAPPED | OK |
| `otro_establecimiento` | opt | SINGLE | "Seguro Social (IGSS)", "ESTABLECIMIENTO PRIVADO" | `es_seguro_social` / `unidad_medica` | MAPPED | OK |
| `especifique_establecimiento` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Sub de "Seguro Social (IGSS)". Podríamos enviar nombre unidad IGSS. |
| `especifique_privado` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Sub de "ESTABLECIMIENTO PRIVADO". Low priority. |
| `fuente_de_notificacion_` | opt | SINGLE | 9 opciones (con acentos) | `fuente_notificacion` | **WRONG VALUE** | Nuestro mapa quita acentos: "BUSQUEDA" vs "BÚSQUEDA". Solo "SERVICIO DE SALUD" y "LABORATORIO" y "OTRO" funcionan. |
| `especifique_fuente` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Sub de fuente="OTRO". Low priority. |

#### Errores en Servicio de Salud Variable Mapping

| DAS | Variable correcta (GoData) | Variable nuestra | Error? |
|---|---|---|---|
| ALTA VERAPAZ | `servicio_de_salud` | `servicio_de_salud` | OK |
| BAJA VERAPAZ | `servicio_de_salud_1` | `servicio_de_salud_1` | OK |
| CHIMALTENANGO | `servicio_de_salud_2` | `servicio_de_salud_2` | OK |
| CHIQUIMULA | `servicio_de_salud_3` | `servicio_de_salud_CH` | **WRONG** |
| EL PROGRESO | `servicio_de_salud_4` | `servicio_de_salud_3` | **WRONG** |
| ESCUINTLA | `servicio_de_salud_` | `servicio_de_salud_5` | **WRONG** |
| GUATEMALA CENTRAL | `servicio_de_salud_5` | `servicio_de_salud_7` | **WRONG** |
| GUATEMALA NOR OCCIDENTE | `servicio_de_salud_6` | -- (uses GUATEMALA) | **WRONG** |
| GUATEMALA NOR ORIENTE | `servicio_de_salud_7` | -- (uses GUATEMALA) | **WRONG** |
| GUATEMALA SUR | `servicio_de_salud_8` | -- (uses GUATEMALA) | **WRONG** |
| HUEHUETENANGO | `servicio_de_salud_9` | `servicio_de_salud_8` | **WRONG** |
| IXCÁN | `servicio_de_salud_10` | `servicio_de_salud_9` | **WRONG** |
| IXIL | `servicio_de_salud_11` | `servicio_de_salud_10` | **WRONG** |
| IZABAL | `servicio_de_salud_12` | `servicio_de_salud_11` | **WRONG** |
| JALAPA | `servicio_de_salud_13` | `servicio_de_salud_12` | **WRONG** |
| JUTIAPA | `servicio_de_salud_14` | `servicio_de_salud_13` | **WRONG** |
| PETÉN NORTE | `servicio_de_salud_15` | `servicio_de_salud_14` | **WRONG** |
| PETÉN SUR OCCIDENTE | `servicio_de_salud_18` | `servicio_de_salud_15` | **WRONG** |
| PETÉN SUR ORIENTE | `servicio_de_salud_19` | `servicio_de_salud_16` | **WRONG** |
| QUETZALTENANGO | `servicio_de_salud_20` | `servicio_de_salud_17` | **WRONG** |
| QUICHÉ | `servicio_de_salud_22` | `servicio_de_salud_18` | **WRONG** |
| RETALHULEU | `servicio_de_salud_23` | `servicio_de_salud_19` | **WRONG** |
| SACATEPÉQUEZ | `servicio_de_salud_24` | `servicio_de_salud_20` | **WRONG** |
| SAN MARCOS | `servicio_de_salud_25` | `servicio_de_salud_21` | **WRONG** |
| SANTA ROSA | `servicio_de_salud_26` | `servicio_de_salud_22` | **WRONG** |
| SOLOLÁ | `servicio_de_salud_27` | `servicio_de_salud_23` | **WRONG** |
| SUCHITEPÉQUEZ | `servicio_de_salud_28` | `servicio_de_salud_24` | **WRONG** |
| TOTONICAPAN | `servicio_de_salud_30` | `servicio_de_salud_25` | **WRONG** |
| ZACAPA | `servicio_de_salud_31` | `servicio_de_salud_26` | **WRONG** |

**Solo 3 de 29 son correctos.** Los otros 26 envían el dato a la variable equivocada.

### 2.2 Información del Paciente
**Categoría:** INFORMACION_DEL_PACIENTE

| Variable GoData | Req | Tipo | Opciones | Nuestro DB | Status | Problema |
|---|---|---|---|---|---|---|
| `informacion_del_paciente` | opt | SINGLE (header) | "DATOS GENERALES" | Hardcoded | MAPPED | OK |
| `codigo_unico_de_identificacion_dpi_pasaporte_otro` | opt | SINGLE | DPI, PASAPORTE, OTRO | `tipo_identificacion` | MAPPED | OK |
| `no_de_dpi` | opt | NUMERIC | -- | `numero_identificacion` | MAPPED | OK |
| `no_de_pasaporte` | opt | FREE_TEXT | -- | -- | **PARTIALLY** | Solo mapeamos `no_de_dpi`, no switch por tipo |
| `especifique_cui` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Sub de tipo=OTRO |
| `nombre_del_tutor_` | opt | SINGLE | SI, NO | `nombre_encargado` (presencia) | MAPPED | OK |
| `parentesco_` | opt | FREE_TEXT | -- | `parentesco_encargado` | MAPPED | OK |
| `codigo_unico_de_identificacion_dpi_pasaporte_otro_` (tutor) | opt | SINGLE | DPI, PASAPORTE, OTRO | -- | NOT MAPPED | Doc del tutor |
| `no_de_dpi_` (tutor) | opt | NUMERIC | -- | -- | NOT MAPPED | DPI del tutor |
| `no_de_pasaporte_` (tutor) | opt | FREE_TEXT | -- | -- | NOT MAPPED | Pasaporte tutor |
| `especifique_doc` (tutor) | opt | FREE_TEXT | -- | -- | NOT MAPPED | Otro doc tutor |
| `pueblo` | opt | SINGLE | LADINO, MAYA, GARÍFUNA, XINCA, DESCONOCIDO | `pueblo` / `etnia` | **WRONG VALUE** | Quitamos acentos: "GARIFUNA" vs "GARÍFUNA" |
| `comunidad_linguistica` | opt | SINGLE | 23 opciones (con acentos/apóstrofes) | -- | **NOT MAPPED** | Sub de pueblo=MAYA. Valores como "K'iche'", "Q'eqchi'" |
| `extranjero_` | opt | SINGLE | SI, NO | `es_extranjero` | MAPPED | OK |
| `migrante` | opt | SINGLE | SI, NO | `es_migrante` | MAPPED | OK |
| `ocupacion_` | opt | FREE_TEXT | -- | `ocupacion` | MAPPED | Accents stripped pero es free text, OK |
| `escolaridad_` | opt | SINGLE | 9 opciones (con acentos) | `escolaridad` | **WRONG VALUE** | "BASICOS" vs "BÁSICOS". Solo valores sin acento funcionan. |
| `telefono_` | opt | NUMERIC | -- | `telefono_paciente` | MAPPED | OK |
| `pais_de_residencia_` | **REQ** | SINGLE | GUATEMALA, OTRO | `pais_residencia` | MAPPED | OK (no acentos en opciones) |
| `especifique_pais` | **REQ** | FREE_TEXT | -- | -- | NOT MAPPED | Sub de pais=OTRO. Debería mapear nombre del país. |
| `departamento_de_residencia_` | **REQ** | SINGLE | 22 deptos (con acentos) | `departamento_residencia` | **WRONG VALUE** | Quitamos acentos: "QUICHE" vs "QUICHÉ", "SOLOLA" vs "SOLOLÁ", "PETEN" vs "PETÉN" |
| `municipio_de_residencia*` (22 vars) | **REQ** | SINGLE | Municipios por depto | `municipio_residencia` | MAPPED | Variable cascadeada correcta. Valores sin acentos en su mayoría. |
| `direccion_de_residencia_` | opt | FREE_TEXT | -- | `direccion_exacta` | MAPPED | Free text, OK |
| `lugar_poblado_` | opt | FREE_TEXT | -- | `poblado` / `lugar_poblado` | MAPPED | Free text, OK |

### 2.3 Antecedentes Médicos y de Vacunación
**Categoría:** ANTECEDENTES_MEDICOS_Y_DE_VACUNACION

| Variable GoData | Req | Tipo | Opciones | Nuestro DB | Status | Problema |
|---|---|---|---|---|---|---|
| `antecedentes_medicos_y_de_vacunacion` | **REQ** | SINGLE (header) | "ANTECEDENTES MEDICOS Y DE VACUNACIÓN" | Hardcoded | MAPPED | Enviamos "ANTECEDENTES MEDICOS Y DE VACUNACION" (sin ó). GoData espera con acento. |
| `paciente_vacunado_` | **REQ** | SINGLE | SI, NO, ` VERBAL`, DESCONOCIDO | `vacunado` | MAPPED | Nota: " VERBAL" tiene espacio al inicio en GoData. Nuestro mapa no lo maneja. |
| `tipo_de_vacuna_recibida_` | opt | MULTIPLE | "SPR – Sarampión Paperas Rubéola", "SR – Sarampión Rubéola" | `tipo_vacuna` | **WRONG VALUE** | Enviamos "SPR \u2013 Sarampión Paperas Rubéola" (en dash), GoData usa "SPR – Sarampión Paperas Rubéola" (en dash). Verificar si el caracter es igual. |
| `numero_de_dosis` | opt | NUMERIC | -- | `numero_dosis_spr` / `numero_dosis` | MAPPED | SPR dosis. OK. |
| `fecha_de_la_ultima_dosis` | opt | DATE | -- | `fecha_ultima_dosis` / `fecha_ultima_spr` | MAPPED | SPR fecha. OK. |
| `numero_de_dosis_` | opt | NUMERIC | -- | -- | **NOT MAPPED** | SR dosis (diferente variable!). Solo mapeamos SPR. |
| `fecha_de_la_ultima_dosis_` | opt | DATE | -- | -- | **NOT MAPPED** | SR fecha ultima dosis. Solo mapeamos SPR. |
| `fuente_de_la_informacion_sobre_la_vacunacion_` | opt | SINGLE | 4 opciones (con acentos) | `fuente_info_vacuna` | **WRONG VALUE** | "CARNE DE VACUNACION" vs "CARNÉ DE VACUNACIÓN". Nuestro mapa produce el valor correcto CON acentos pero `_godata_text()` luego los quita. No -- en realidad no pasamos por `_godata_text()` aquí. Revisar. |
| `vacunacion_en_el_sector_` | opt | SINGLE | MSPAS, IGSS, PRIVADO | `sector_vacunacion` | MAPPED | OK (sin acentos) |
| `antecedentes_medicos_` | opt | SINGLE | SI, NO, DESCONOCIDO | `tiene_antecedentes_medicos` | MAPPED | OK |
| `especifique_ant` | opt | SINGLE | DESNUTRICIÓN, INMUNOCOMPROMISO, ENFERMEDAD CRÓNICA, OTRO | `antecedentes_medicos_detalle` | **WRONG VALUE** | Opciones GoData tienen acentos: "DESNUTRICIÓN", "ENFERMEDAD CRÓNICA". Enviamos sin acentos. |
| `especifique_A` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Sub de antecedente=OTRO. Low priority. |

### 2.4 Datos Clínicos
**Categoría:** DATOS_CLINICOS

| Variable GoData | Req | Tipo | Opciones | Nuestro DB | Status | Problema |
|---|---|---|---|---|---|---|
| `datos_clinicos` | opt | SINGLE (header) | "DATOS CLÍNICOS" | Hardcoded | MAPPED | Enviamos "DATOS CLINICOS" sin acento. GoData tiene "DATOS CLÍNICOS". |
| `fecha_de_inicio_de_sintomas_` | opt | DATE | -- | `fecha_inicio_sintomas` | MAPPED | OK |
| `fecha_de_inicio_de_fiebre_` | opt | DATE | -- | `fecha_inicio_fiebre` | MAPPED | OK |
| `fecha_de_inicio_de_exantema_rash_` | **REQ** | DATE | -- | `fecha_inicio_erupcion` / `fecha_inicio_exantema` | MAPPED | OK |
| `sintomas_` | opt | SINGLE | SI, NO | Lógica basada en signos | MAPPED | OK |
| `que_sintomas_` | opt | MULTIPLE | 8 opciones | Campos `signo_*` individuales | **WRONG VALUES** | "Adenopatías/ Ganglios inflamados" vs GoData "Adenopatías". "Artralgia/ Dolor articular" vs GoData "Artralgia / Artritis". |
| `temp_c` | opt | NUMERIC | -- | `temperatura_celsius` | MAPPED | OK |
| `hospitalizacion_` | opt | SINGLE | SI, NO, DESCONOCIDO | `hospitalizado` | MAPPED | OK (sin DESCONOCIDO en nuestro map) |
| `nombre_del_hospital_` | opt | FREE_TEXT | -- | `hosp_nombre` | MAPPED | OK |
| `fecha_de_hospitalizacion_` | opt | DATE | -- | `hosp_fecha` | MAPPED | OK |
| `complicaciones_` | opt | SINGLE | SI, NO, DESCONOCIDO | `tiene_complicaciones` | MAPPED | OK |
| `especifique_complicaciones_` | opt | MULTIPLE | 7 opciones (con acentos) | `comp_*` campos | **WRONG VALUES** | Enviamos "NEUMONIA" vs GoData "NEUMONÍA". "OTITIS MEDIA" vs "OTITIS MEDIA AGUDA". |
| `especique` (sic) | opt | FREE_TEXT | -- | `comp_otra_texto` | NOT MAPPED | Sub de comp=OTRA. Debería ir aquí en vez de en el array. |
| `aislamiento_respiratorio` | opt | SINGLE | SI, NO, DESCONOCIDO | `aislamiento_respiratorio` | MAPPED | OK |
| `fecha_de_aislamiento` | opt | DATE | -- | `fecha_aislamiento` | MAPPED | OK |

### 2.5 Factores de Riesgo
**Categoría:** EXPOSURE_RISK

| Variable GoData | Req | Tipo | Opciones | Nuestro DB | Status | Problema |
|---|---|---|---|---|---|---|
| `factores_de_riesgo` | opt | SINGLE | Si, No, DESCONOCIDO | Lógica basada en `viajo_7_23_previo` | **WRONG LOGIC** | Solo seteamos "Si" cuando viajó. Debería reflejar si hay CUALQUIER factor. Además: GoData usa "Si"/"No" (minúscula), no "SI"/"NO". |
| `Existe_caso_en_muni` | opt | SINGLE | Si, No, Desconocido | `caso_sospechoso_comunidad_3m` | MAPPED | OK -- valores exactos "Si"/"No"/"Desconocido" |
| `tuvo_contacto_con_un_caso_sospechoso_o_confirmado` | opt | SINGLE | Si, No, Desconocido | `contacto_caso_sospechoso` | MAPPED | OK |
| `viajo_durante_los_7_23_dias` | opt | SINGLE | Si, No | `viajo_7_23_previo` | MAPPED | OK |
| `pais_departamento_y_municipio` | opt | SINGLE | GUATEMALA, OTRO | `viaje_pais` / `viaje_departamento` | **WRONG VALUE** | Cuando es Guatemala, enviamos el depto en texto. GoData espera "GUATEMALA" como opción y luego `departamento` sub-campo. |
| `departamento` | opt | SINGLE | 22 deptos | `viaje_departamento` | **NOT MAPPED** as sub-field | Solo se mapea dentro de `pais_departamento_y_municipio` |
| `municipio` | opt | FREE_TEXT | -- | `viaje_municipio` | MAPPED | OK |
| `especifique_pais1` | opt | FREE_TEXT | -- | `viaje_pais` | MAPPED | OK (cuando pais != Guatemala) |
| `fecha_de_salida_viaje` | opt | DATE | -- | `viaje_fecha_salida` | MAPPED | OK |
| `fecha_de_entrada_viaje` | opt | DATE | -- | `viaje_fecha_entrada` / `viaje_fecha_regreso` | MAPPED | OK |
| `alguna_persona_de_su_casa_ha_viajado_al_exterior` | opt | SINGLE | Si, No | `familiar_viajo_exterior` | MAPPED | OK |
| `fecha_de_retorno` | opt | DATE | -- | -- | **NOT MAPPED** | Sub de familiar viajó=Si |
| `el_paciente_estuvo_en_contacto_con_una_mujer_embarazada1` | opt | SINGLE | Si, No, Desconocido | `contacto_embarazada` | MAPPED | OK |
| `fuente_posible_de_contagio1` | opt | MULTIPLE | 9 opciones (mixed case) | `fuente_posible_contagio` | **WRONG VALUES** | GoData: "Contacto en el hogar", "Institución Educativa", "Espacio Público", "Evento Masivo", "Transporte Internacional". Nuestro mapa: "Hogar", "Servicio de Salud", "Comunidad", etc. |

### 2.6 Acciones de Respuesta
**Categoría:** ACCIONES_DE_RESPUESTA

| Variable GoData | Req | Tipo | Opciones | Nuestro DB | Status | Problema |
|---|---|---|---|---|---|---|
| `acciones_de_respuesta` | opt | SINGLE | SI, NO | Lógica conjunta | MAPPED | Cuando NO hay acciones enviamos `[{}]` (vacío) en vez de "NO" |
| `se_realizo_busqueda_activa_institucional_de_casos_bai` | opt | SINGLE | 1, 2 | `bai_realizada` | MAPPED | OK (1=SI, 2=NO) |
| `numero_de_casos_sospechosos_identificados_en_bai` | opt | NUMERIC | -- | `bai_casos_sospechosos` | MAPPED | OK |
| `se_realizo_busqueda_activa_comunitaria_de_casos_bac` | opt | SINGLE | 1, 2 | `bac_realizada` | MAPPED | OK |
| `numero_de_casos_sospechosos_identificados_en_bac` | opt | NUMERIC | -- | `bac_casos_sospechosos` | MAPPED | OK |
| `hubo_vacunacion_de_bloqueo` | opt | SINGLE | 1, 2 | `vacunacion_bloqueo` | MAPPED | OK |
| `hubo_vacunacion_con_barrido_documentado` | opt | SINGLE | 1, 2 | `vacunacion_barrido` | MAPPED | OK |
| `se_realizo_monitoreo_rapido_de_vacunacion` | opt | SINGLE | 1, 2 | `monitoreo_rapido_vacunacion` | MAPPED | OK |
| `se_le_administro_vitamina_a` | opt | SINGLE | 1, 2, 3 | `vitamina_a` | MAPPED | OK |
| `numero_de_dosis_de_vitamina_a_recibidas` | opt | NUMERIC | -- | `vitamina_a_dosis` | MAPPED | OK |
| `por_que_no_acciones_respuesta` | opt | FREE_TEXT | -- | -- | **NOT MAPPED** | Sub de acciones=NO. Razón de no hacer acciones. |

### 2.7 Clasificación
**Categoría:** OUTCOME_STATUS

| Variable GoData | Req | Tipo | Opciones | Nuestro DB | Status | Problema |
|---|---|---|---|---|---|---|
| `clasificacion` | opt | SINGLE | CLASIFICADO, 2 | `clasificacion_caso` | **WRONG VALUE** | Enviamos "PENDIENTE" como texto. GoData espera "2" para pendiente. |
| `clasificacion_final` | opt | SINGLE | 1, 2, 3, 5 | Via `_CLASIFICACION_FINAL_MAP` | MAPPED | OK |
| `criterio_de_confirmacion_sarampion` | opt | SINGLE | LABSR, NE, CX | `criterio_confirmacion` | MAPPED | OK |
| `criterio_de_confirmacion_rubeola` | opt | SINGLE | LABRB, NERB, CXRB | `criterio_confirmacion` | MAPPED | OK |
| `criterio_para_descartar_el_caso` | opt | SINGLE | LAB, RVAC, CX2, OTRO | `criterio_descarte` | MAPPED | OK (nota: nuestro var name es `criterio_de_descarte` pero GoData es `criterio_para_descartar_el_caso`) |
| `especifiqueX` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Sub de descarte=OTRO |
| `contacto_de_otro_caso` | opt | SINGLE | SI, NO | `contacto_otro_caso` | MAPPED | OK |
| `fuente_de_infeccion_de_los_casos_confirmados` | opt | SINGLE | 1, 2, 3, 4 | `fuente_infeccion` | MAPPED | OK |
| `importado_pais_de_importacion` | opt | FREE_TEXT | -- | `pais_importacion` | MAPPED | OK |
| `pais_de_importacion` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Parece duplicado de `importado_pais_de_importacion` (diferente sub-trigger) |
| `caso_analizado_por` | opt | MULTIPLE | 1, 2, 3, 4 | `caso_analizado_por` | MAPPED | OK |
| `especifique_otro_clasificacion` | opt | FREE_TEXT | -- | -- | NOT MAPPED | Sub de analizado=4(Otro) |
| `fecha_de_clasificacion` | opt | DATE | -- | `fecha_clasificacion_final` / `fecha_clasificacion` | MAPPED | OK |
| `condicion_final_del_paciente` | opt | SINGLE | 1, 2, 3, 4 | `condicion_final_paciente` / `condicion_egreso` | MAPPED | OK |
| `fecha_de_defuncion` | opt | DATE | -- | `fecha_defuncion` | **NOT MAPPED in QA** | Solo se mapea en standard `dateOfOutcome`, no en questionnaire. |
| `causa_de_muerte_segun_certificado_de_defuncion` | opt | FREE_TEXT | -- | -- | NOT MAPPED | |

### 2.8 Lugares Visitados y Rutas de Desplazamiento
**Categoría:** RECENT_TRAVEL

| Variable GoData | Req | Tipo | Opciones | Nuestro DB | Status | Problema |
|---|---|---|---|---|---|---|
| `lugares_visitados_y_rutas_de_desplazamiento_del_caso` | opt | SINGLE | 1, 2, DESCONOCIDO | -- | **NOT MAPPED** | No enviamos este campo. |
| `sitio_ruta_de_desplazamiento_1` | opt | FREE_TEXT | -- | -- | NOT MAPPED | |
| `direccion_del_lugar_y_rutas_de_desplazamiento_1` | opt | FREE_TEXT | -- | -- | NOT MAPPED | |
| `fecha_en_que_visito_el_lugar_ruta_1` | opt | DATE | -- | -- | NOT MAPPED | |
| `tipo_de_abordaje_realizado_1` | opt | MULTIPLE | BLOQUEO, BARRIDO, 3, 4 | -- | NOT MAPPED | |
| `fecha_de_abordaje_1` | opt | DATE | -- | -- | NOT MAPPED | |
| `sitio_ruta_de_desplazamiento_2` | opt | FREE_TEXT | -- | -- | NOT MAPPED | |
| `direccion_del_lugar_y_rutas_de_desplazamiento_2` | opt | FREE_TEXT | -- | -- | NOT MAPPED | |
| `fecha_en_que_visito_el_lugar_ruta_2` | opt | DATE | -- | -- | NOT MAPPED | |
| `tipo_de_abordaje_realizado_2` | opt | MULTIPLE | 1, 2, 3, 4 | -- | NOT MAPPED | |
| `fecha_de_abordaje_2` | opt | DATE | -- | -- | NOT MAPPED | |

---

## Sección 3: Análisis de Brechas

### 3.1 BUG CRÍTICO: Accent Stripping

**El problema más grave.** La función `_godata_text()` llama a `_strip_accents()` que elimina TODOS los acentos. Pero GoData Guatemala usa valores con acentos como opciones de respuesta.

**Campos afectados donde el valor NO matcheará en GoData:**

| Campo | Enviamos | GoData espera |
|---|---|---|
| `diagnostico_de_sospecha_` | SARAMPION | SARAMPIÓN |
| `diagnostico_de_sospecha_` | RUBEOLA | RUBÉOLA |
| `direccion_de_area_de_salud` | IXCAN | IXCÁN |
| `direccion_de_area_de_salud` | PETEN NORTE | PETÉN NORTE |
| `direccion_de_area_de_salud` | QUICHE | QUICHÉ |
| `direccion_de_area_de_salud` | SACATEPEQUEZ | SACATEPÉQUEZ |
| `direccion_de_area_de_salud` | SOLOLA | SOLOLÁ |
| `direccion_de_area_de_salud` | SUCHITEPEQUEZ | SUCHITEPÉQUEZ |
| `departamento_de_residencia_` | (mismo problema para 7 departamentos) | |
| `escolaridad_` | BASICOS | BÁSICOS |
| `fuente_de_notificacion_` | BUSQUEDA ACTIVA * | BÚSQUEDA ACTIVA * |
| `fuente_de_notificacion_` | INVESTIGACION DE CONTACTOS | INVESTIGACIÓN DE CONTACTOS |
| `especifique_ant` | DESNUTRICION | DESNUTRICIÓN |
| `especifique_ant` | ENFERMEDAD CRONICA | ENFERMEDAD CRÓNICA |
| `especifique_complicaciones_` | NEUMONIA | NEUMONÍA |
| `pueblo` | GARIFUNA | GARÍFUNA |

**Fix:** No usar `_godata_text()` para valores de opciones SINGLE_ANSWER. Solo usar `.upper()` preservando acentos. `_strip_accents()` solo debe usarse para FREE_TEXT donde no importa.

### 3.2 Servicio de Salud Variable Map (26 de 29 incorrectos)

Ver tabla completa en sección 2.1. La numeración en nuestro `_SERVICIO_SALUD_VARIABLE_MAP` no coincide con la del template GoData.

### 3.3 Symptom Label Mismatches

| Nuestro label | GoData label correcto |
|---|---|
| `Adenopatías/ Ganglios inflamados` | `Adenopatías` |
| `Artralgia/ Dolor articular` | `Artralgia / Artritis` |

### 3.4 Complication Label Mismatches

| Nuestro label | GoData label correcto |
|---|---|
| `NEUMONIA` | `NEUMONÍA` |
| `OTITIS MEDIA` | `OTITIS MEDIA AGUDA` |

### 3.5 Fuente Posible de Contagio Mismatches

| Nuestro label | GoData label correcto |
|---|---|
| `Hogar` | `Contacto en el hogar` |
| `Espacio público` | `Espacio Público` |
| No mapeado | `Institución Educativa` |
| No mapeado | `Evento Masivo` |
| No mapeado | `Transporte Internacional` |

### 3.6 Campos NOT MAPPED (GoData tiene, no enviamos)

**Prioridad Alta (aparecen en casos reales):**
- `caso_altamente_sospechoso_de_sarampion` -- Todos los casos reales lo tienen
- `comunidad_linguistica` -- Caso 5 lo llena (K'iche')
- Sección 8 completa: Lugares visitados y rutas de desplazamiento -- Caso 5 lo llena

**Prioridad Media:**
- `numero_de_dosis_` / `fecha_de_la_ultima_dosis_` (dosis SR, no SPR)
- `especifique_establecimiento` (nombre del establecimiento IGSS)
- `fecha_de_retorno` (familiar que viajó)
- `fecha_de_defuncion` en QA (además de standard `dateOfOutcome`)
- `causa_de_muerte_segun_certificado_de_defuncion`
- `por_que_no_acciones_respuesta`

**Prioridad Baja:**
- `especifique` / `especifique_` (especificar dx otro)
- `especifique_fuente` (fuente notificación otro)
- `especifique_cui` (doc otro tipo)
- Documentos del tutor (DPI, pasaporte, otro)
- `especifique_A` (antecedente otro)
- `especifiqueX` (descarte otro)
- `especifique_otro_clasificacion` (analizado por otro)
- `pais_de_importacion` (2do campo de país importación)

### 3.7 Valores vacíos `[{}]` en lugar de omitir

Nuestro código envía `[{}]` (array con dict vacío) para campos sin valor. En los casos reales de GoData, se usa `[{}]` para campos sin valor. **Esto parece aceptable y consistente con el comportamiento de GoData.**

---

## Sección 4: Análisis de Uso de Campos (5 casos existentes)

### Campos que TODOS los 5 casos tienen:
- `fecha_de_notificacion` (header)
- `antecedentes_medicos_y_de_vacunacion` (header)
- `direccion_de_area_de_salud`
- `distrito_municipal_de_salud_dms*`
- `paciente_vacunado_`
- `que_sintomas_`
- `sintomas_`
- Standard: `firstName`, `lastName`, `gender`, `dateOfReporting`, `dateOfOnset`, `dob`, `age`

### Campos que 4 de 5 casos tienen:
- `diagnostico_de_sospecha_` = "SARAMPIÓN" (todos menos caso 1)
- `caso_altamente_sospechoso_de_sarampion` = "SI" (todos menos caso 1)
- `datos_clinicos` (header)
- `informacion_del_paciente` (header)
- `fecha_de_inicio_de_sintomas_`
- `fecha_de_inicio_de_fiebre_`
- `fecha_de_inicio_de_exantema_rash_`
- `fecha_de_consulta`

### Campos que 3 de 5 casos tienen:
- `departamento_de_residencia_`
- `municipio_de_residencia*`
- `pais_de_residencia_`
- `direccion_de_residencia_`
- `lugar_poblado_`
- `codigo_unico_de_identificacion_dpi_pasaporte_otro`
- `no_de_dpi`
- `escolaridad_`
- `ocupacion_`
- `pueblo`
- `nombre_de_quien_investiga`
- `correo_electronico`
- `servicio_de_salud_*`
- `fuente_de_notificacion_`
- `acciones_de_respuesta` con sub-campos

### Campos que solo 1-2 casos tienen:
- `comunidad_linguistica` (solo caso 5, Maya K'iche')
- `especifique_ant` (2 casos: ENFERMEDAD CRÓNICA)
- `fuente_de_la_informacion_sobre_la_vacunacion_` (1 caso)
- `tipo_de_vacuna_recibida_` con valores (2 casos)
- Sección de rutas de desplazamiento (solo caso 5)
- `clasificacion_final`, `criterio_de_confirmacion_*` (solo caso 1)

### Campos que NINGÚN caso tiene:
- `vaccinesReceived` (standard array)
- `documents` (standard array)
- `addresses` (standard array)
- `dateRanges` (standard array)
- `fecha_de_defuncion` / `causa_de_muerte`
- `pais_de_importacion`

**Observación importante:** Los arrays estándar (`addresses`, `documents`, `dateRanges`, `vaccinesReceived`) están VACÍOS en todos los 5 casos. Esto sugiere que GoData Guatemala no usa estos campos estándar y pone todo en el cuestionario. Nuestro código genera estos arrays pero probablemente son ignorados por la API o la UI de GoData.

---

## Sección 5: Recomendaciones (ordenadas por prioridad)

### P0 - Crítico (rompe la integración)

1. **Eliminar accent stripping de valores de opciones.** Crear nueva función `_godata_option(text)` que solo hace `.upper().strip()` SIN quitar acentos. Usarla para todos los campos SINGLE_ANSWER y MULTIPLE_ANSWERS. Mantener `_godata_text()` solo para FREE_TEXT y nombres.

2. **Corregir `_SERVICIO_SALUD_VARIABLE_MAP` completo.** Reemplazar con valores correctos del template GoData:
   ```python
   _SERVICIO_SALUD_VARIABLE_MAP = {
       "ALTA VERAPAZ": "servicio_de_salud",
       "BAJA VERAPAZ": "servicio_de_salud_1",
       "CHIMALTENANGO": "servicio_de_salud_2",
       "CHIQUIMULA": "servicio_de_salud_3",
       "EL PROGRESO": "servicio_de_salud_4",
       "ESCUINTLA": "servicio_de_salud_",
       "GUATEMALA CENTRAL": "servicio_de_salud_5",
       "GUATEMALA NOR OCCIDENTE": "servicio_de_salud_6",
       "GUATEMALA NOR ORIENTE": "servicio_de_salud_7",
       "GUATEMALA SUR": "servicio_de_salud_8",
       "HUEHUETENANGO": "servicio_de_salud_9",
       "IXCÁN": "servicio_de_salud_10",
       "IXIL": "servicio_de_salud_11",
       "IZABAL": "servicio_de_salud_12",
       "JALAPA": "servicio_de_salud_13",
       "JUTIAPA": "servicio_de_salud_14",
       "PETÉN NORTE": "servicio_de_salud_15",
       "PETÉN SUR OCCIDENTE": "servicio_de_salud_18",
       "PETÉN SUR ORIENTE": "servicio_de_salud_19",
       "QUETZALTENANGO": "servicio_de_salud_20",
       "QUICHÉ": "servicio_de_salud_22",
       "RETALHULEU": "servicio_de_salud_23",
       "SACATEPÉQUEZ": "servicio_de_salud_24",
       "SAN MARCOS": "servicio_de_salud_25",
       "SANTA ROSA": "servicio_de_salud_26",
       "SOLOLÁ": "servicio_de_salud_27",
       "SUCHITEPÉQUEZ": "servicio_de_salud_28",
       "TOTONICAPAN": "servicio_de_salud_30",
       "ZACAPA": "servicio_de_salud_31",
   }
   ```

3. **Corregir `_DMS_VARIABLE_MAP` keys para usar acentos** y manejar las 4 DAS de Guatemala como entradas separadas (GUATEMALA CENTRAL, GUATEMALA NOR OCCIDENTE, GUATEMALA NOR ORIENTE, GUATEMALA SUR).

4. **Corregir `clasificacion` valor pendiente:** Enviar "2" en vez de "PENDIENTE".

### P1 - Alto (datos incorrectos pero no rompe)

5. **Corregir symptom labels:**
   - `"signo_adenopatias": "Adenopatías"` (no "Adenopatías/ Ganglios inflamados")
   - `"signo_artralgia": "Artralgia / Artritis"` (no "Artralgia/ Dolor articular")

6. **Corregir complication labels:**
   - `"comp_neumonia": "NEUMONÍA"` (con acento)
   - `"comp_otitis": "OTITIS MEDIA AGUDA"` (no "OTITIS MEDIA")

7. **Corregir fuente_posible_de_contagio1 labels:**
   - Usar valores exactos de GoData: "Contacto en el hogar", "Institución Educativa", "Espacio Público", "Evento Masivo", "Transporte Internacional"

8. **Corregir acciones_de_respuesta cuando NO:** Enviar `_qa_val("NO")` en vez de `[{}]`.

9. **Corregir header values con acentos:**
   - `fecha_de_notificacion` = "Fecha de Notificación" (con ó)
   - `antecedentes_medicos_y_de_vacunacion` = "ANTECEDENTES MEDICOS Y DE VACUNACIÓN" (con ó)

### P2 - Medio (campos faltantes)

10. **Mapear `caso_altamente_sospechoso_de_sarampion`:** Siempre "SI" cuando dx=SARAMPIÓN.

11. **Mapear `comunidad_linguistica`:** Agregar campo `comunidad_linguistica` a BD y mapearlo.

12. **Separar dosis SPR vs SR:** `numero_de_dosis` es para SPR, `numero_de_dosis_` es para SR. Actualmente solo mapeamos uno.

13. **Mapear sección Rutas de Desplazamiento:** Campos opcionales pero usados por operadores.

14. **Mapear `fecha_de_defuncion` y `causa_de_muerte` en QA** (además del standard field).

### P3 - Bajo (nice to have)

15. Switch `no_de_dpi` / `no_de_pasaporte` según `tipo_identificacion`.
16. Mapear documentos del tutor.
17. Mapear `especifique_establecimiento` con nombre de unidad IGSS.
18. Mapear campos "especifique" para opciones "OTRO".
19. Mapear `fecha_de_retorno` del familiar que viajó.
20. Considerar NO enviar arrays estándar (`addresses`, `documents`, `dateRanges`) ya que GoData Guatemala no los usa.

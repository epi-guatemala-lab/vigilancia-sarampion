# GoData Guatemala API - Documentacion Completa

**URL Base**: `https://godataguatemala.mspas.gob.gt/api`
**Fecha de exploracion**: 2026-03-27
**Cuenta usada**: practica4@gmail.com (rol limitado)

---

## 1. Autenticacion

### OAuth2 Token
```bash
TOKEN=$(curl -s -X POST "https://godataguatemala.mspas.gob.gt/api/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"practica4@gmail.com","password":"sarampion123456"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
```

**Respuesta**:
```json
{
  "token_type": "bearer",
  "expires_in": 600,
  "access_token": "<64-char-token>"
}
```

**IMPORTANTE**: El token se pasa como **query parameter** `?access_token=TOKEN`, NO como header Bearer.
El token expira en 600 segundos (10 minutos). Renovar antes de cada bloque de requests.

---

## 2. Endpoints Accesibles y No Accesibles

### Accesibles (practica4@gmail.com)

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/api/oauth/token` | POST | Autenticacion |
| `/api/outbreaks` | GET | Lista de brotes |
| `/api/outbreaks/{id}` | GET | Detalle de brote |
| `/api/outbreaks/{id}/cases` | GET | Casos del brote |
| `/api/outbreaks/{id}/cases/count` | GET | Conteo de casos |
| `/api/outbreaks/{id}/cases/{caseId}/lab-results` | GET | Resultados lab por caso |
| `/api/outbreaks/{id}/contacts` | GET | Contactos |
| `/api/outbreaks/{id}/events` | GET | Eventos |
| `/api/outbreaks/{id}/follow-ups` | GET | Seguimientos |
| `/api/outbreaks/{id}/relationships` | GET | Relaciones caso-contacto |
| `/api/outbreaks/{id}/relationships/count` | GET | Conteo relaciones |
| `/api/outbreaks/{id}/clusters` | GET | Clusters |
| `/api/outbreaks/{id}/cases/export` | GET | Exportar casos (async) |
| `/api/reference-data` | GET | Datos de referencia |
| `/api/locations` | GET | Ubicaciones |
| `/api/locations/hierarchical` | GET | Arbol jerarquico |
| `/api/languages` | GET | Idiomas |
| `/api/teams` | GET | Equipos |
| `/api/roles` | GET | Roles |
| `/api/export-logs` | GET | Historial de exportaciones |
| `/api/icons` | GET | Iconos |

### NO Accesibles (requieren permisos adicionales)

| Endpoint | Error | Permiso requerido |
|----------|-------|-------------------|
| `/api/system-settings/version` | 401 Invalid API Key | (bug? no acepta token) |
| `/api/system-settings` | 403 | system_settings_view |
| `/api/users` | 403 | user_list |
| `/api/users/me` | 403 | user_view |
| `/api/audit-logs` | 403 | audit_log_list |
| `/api/devices` | 403 | device_list |
| `/api/outbreaks/{id}/cases` | 401 (POST) | case_create (esta cuenta es solo lectura) |

---

## 3. Brotes (Outbreaks)

### Unico brote disponible

| Campo | Valor |
|-------|-------|
| **ID** | `ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19` |
| **Nombre** | Taller Sarampion |
| **Enfermedad** | `LNG_REFERENCE_DATA_CATEGORY_DISEASE_MEASLES` |
| **Pais** | Guatemala |
| **Fecha inicio** | 2025-12-15 |
| **Fecha fin** | 2027-12-31 |
| **Case ID Mask** | SR-9999 |
| **Contact ID Mask** | CO-9999 |
| **Event ID Mask** | EV-9999 |
| **Periodo seguimiento** | 21 dias |
| **Frecuencia seguimiento** | 1 vez/dia |
| **Periodo largo entre onset** | 14 dias |
| **Contacto de contacto activo** | Si |
| **Follow-up de casos** | No |
| **Ubicaciones asignadas** | 535 |

### Campos visibles y obligatorios (Casos)

| Campo | Visible | Obligatorio |
|-------|---------|-------------|
| firstName | Si | Si |
| middleName | Si | No |
| lastName | Si | Si |
| gender | Si | Si |
| ageDob | Si | No |
| dateOfOnset | Si | Si |
| dateOfReporting | Si | Si |
| visualId | Si | Si |
| pregnancyStatus | Si | No |

---

## 4. Casos (7 en total)

| Visual ID | Nombre | Genero | Edad | Onset | Classification |
|-----------|--------|--------|------|-------|----------------|
| SR-0001 | MARIA SONIA CAPETILLO LERA | F | 62 | 2026-03-23 | Sin clasificar |
| SR-0002 | BENJAMIN CONTRERAS ESTRADA | M | 68 | 2026-03-22 | Sin clasificar |
| SR-0003 | KATERIN RAMOS | F | 2 | 2026-03-23 | Sin clasificar |
| (sin ID) | PRUEBA TEST AUTOMATICO | M | 36 | 2026-03-25 | Sospechoso |
| (sin ID) | PRUEBA TEST AUTOMATICO | M | 36 | 2026-03-25 | Sospechoso |
| SR-0005 | CARMEN VALLADARES SORIA | F | 50 | 2026-03-21 | Sin clasificar |
| SR-0004 | Gregorio velasquez | M | 64 | 2026-03-24 | Sin clasificar |

### Estructura de un caso (campos top-level)

```
id, visualId, outbreakId, firstName, middleName, lastName
gender, age {years, months}, dob
classification, classificationHistory[]
dateOfOnset, dateOfReporting, isDateOfReportingApproximate
addresses[], documents[], dateRanges[], vaccinesReceived[]
questionnaireAnswers {}
followUp {originalStartDate, startDate, endDate, status}
pregnancyStatus, occupation, riskLevel, outcomeId
numberOfContacts, numberOfExposures, hasRelationships
wasContact, wasContactOfContact
duplicateKeys {name[]}
safeBurial, transferRefused
usualPlaceOfResidenceLocationId
createdAt, createdBy, updatedAt, updatedBy, createdOn, deleted
```

### Filtrado de casos via API

```bash
# Por clasificacion
?filter={"where":{"classification":"LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT"}}

# Proyeccion de campos
?filter={"fields":["id","firstName","lastName","visualId","classification","dateOfOnset"]}

# Limite
?filter={"limit":100}

# Combinado
?filter={"limit":100,"where":{"classification":"..."},"fields":["id","firstName"]}
```

---

## 5. Cuestionario de Investigacion de Caso (Template)

### Estructura jeraquica completa (9 secciones principales)

#### 5.1. Diagnostico de sospecha
- Variable: `diagnostico_de_sospecha_`
- Tipo: SINGLE_ANSWER
- Opciones: SARAMPION, RUBEOLA, DENGUE, OTRO ARBOVIROSIS, OTRO FEBRIL EXANTEMATICA
- Sub-pregunta (si SARAMPION): `caso_altamente_sospechoso_de_sarampion` (SI/NO)

#### 5.2. Fecha de notificacion (DATOS UNIDAD NOTIFICADORA) *REQUERIDO*
- Variable: `fecha_de_notificacion`
- Sub-preguntas cascada:
  - `direccion_de_area_de_salud` *REQUERIDO* -> 29 DAS de Guatemala
  - `distrito_municipal_de_salud_dms*` *REQUERIDO* -> DMS por DAS (variables dinamicas con sufijo numerico)
  - `servicio_de_salud_*` -> texto libre
  - `fecha_de_consulta` -> datetime
  - `fecha_de_investigacion_domiciliaria` -> datetime
  - `nombre_de_quien_investiga` -> texto
  - `cargo_de_quien_investiga` -> texto
  - `telefono` -> numerico
  - `correo_electronico` -> texto
  - `otro_establecimiento` -> Seguro Social (IGSS) / ESTABLECIMIENTO PRIVADO
  - `fuente_de_notificacion_` -> SERVICIO DE SALUD, LABORATORIO, BUSQUEDA ACTIVA INSTITUCIONAL/COMUNITARIA/LABORATORIAL, INVESTIGACION DE CONTACTOS, CASO REPORTADO POR COMUNIDAD, AUTO NOTIFICACION, OTRO

**NOTA CRITICA**: Cada DAS tiene una variable de DMS con sufijo numerico diferente:
- Alta Verapaz -> `distrito_municipal_de_salud_dms`
- Baja Verapaz -> `distrito_municipal_de_salud_dms_`
- Chimaltenango -> `distrito_municipal_de_salud_dms_CHI`
- Chiquimula -> `distrito_municipal_de_salud_dms_CH`
- El Progreso -> `distrito_municipal_de_salud_dms1`
- Escuintla -> `distrito_municipal_de_salud_dms3`
- Guatemala Central -> `distrito_municipal_de_salud_dms4`
- Guatemala Nor Occidente -> `distrito_municipal_de_salud_dms5`
- Guatemala Nor Oriente -> `distrito_municipal_de_salud_dms6`
- Guatemala Sur -> `distrito_municipal_de_salud_dms7`
- Huehuetenango -> `distrito_municipal_de_salud_dms8`
- Ixcan -> `distrito_municipal_de_salud_dms9`
- Ixil -> `distrito_municipal_de_salud_dms10`
- Izabal -> `distrito_municipal_de_salud_dms11`
- Jalapa -> `distrito_municipal_de_salud_dms12`
- Jutiapa -> `distrito_municipal_de_salud_dms13`
- Peten Norte -> `distrito_municipal_de_salud_dms14`
- Peten Sur Occidente -> `distrito_municipal_de_salud_dms15`
- Peten Sur Oriente -> `distrito_municipal_de_salud_dms16`
- Quetzaltenango -> `distrito_municipal_de_salud_dms17`
- Quiche -> `distrito_municipal_de_salud_dms18`
- Retalhuleu -> `distrito_municipal_de_salud_dms19`
- Sacatepequez -> `distrito_municipal_de_salud_dms20`
- San Marcos -> `distrito_municipal_de_salud_dms21`
- Santa Rosa -> `distrito_municipal_de_salud_dms22`
- Solola -> `distrito_municipal_de_salud_dms23`
- Suchitepequez -> `distrito_municipal_de_salud_dms24`
- Totonicapan -> `distrito_municipal_de_salud_dms25`
- Zacapa -> `distrito_municipal_de_salud_dms26`

Mismo patron para `servicio_de_salud_*` (sufijos 1-31).

#### 5.3. Informacion del paciente (DATOS GENERALES)
- `codigo_unico_de_identificacion_dpi_pasaporte_otro` -> DPI/PASAPORTE/OTRO
  - `no_de_dpi` (numerico)
  - `no_de_pasaporte` (texto)
- `nombre_del_tutor_` -> SI/NO (con sub-preguntas de parentesco y documento)
- `pueblo` -> LADINO, MAYA (con `comunidad_linguistica` 23 opciones), GARIFUNA, XINCA, DESCONOCIDO
- `extranjero_` -> SI/NO
- `migrante` -> SI/NO
- `ocupacion_` -> texto libre
- `escolaridad_` -> NO APLICA, PRE PRIMARIA, PRIMARIA, BASICOS, DIVERSIFICADO, UNIVERSIDAD, NINGUNO, OTRO, NO INDICA
- `telefono_` -> numerico
- `pais_de_residencia_` *REQUERIDO* -> GUATEMALA (con cascada departamento -> municipio) / OTRO
  - `departamento_de_residencia_` *REQUERIDO* -> 22 departamentos
  - `municipio_de_residencia*` *REQUERIDO* -> municipios por departamento (variables con sufijo numerico)
- `direccion_de_residencia_` -> texto
- `lugar_poblado_` -> texto

**NOTA**: Las variables de municipio tienen sufijos numericos por departamento:
- Alta Verapaz -> `municipio_de_residencia_`
- Baja Verapaz -> `municipio_de_residencia1`
- ... hasta `municipio_de_residencia21` (Zacapa)

#### 5.4. Antecedentes medicos y de vacunacion *REQUERIDO*
- `paciente_vacunado_` *REQUERIDO* -> SI, NO, VERBAL, DESCONOCIDO
  - Si SI:
    - `tipo_de_vacuna_recibida_` [MULTIPLE] -> SPR / SR
      - Para cada una: `numero_de_dosis` (numerico) y `fecha_de_la_ultima_dosis` (fecha)
    - `fuente_de_la_informacion_sobre_la_vacunacion_` -> CARNE DE VACUNACION, SIGSA 5A CUADERNO, SIGSA 5B OTROS GRUPOS, REGISTRO UNICO DE VACUNACION
    - `vacunacion_en_el_sector_` -> MSPAS, IGSS, PRIVADO
- `antecedentes_medicos_` -> SI/NO/DESCONOCIDO
  - Si SI: `especifique_ant` -> DESNUTRICION, INMUNOCOMPROMISO, ENFERMEDAD CRONICA, OTRO

#### 5.5. Datos clinicos
- `fecha_de_inicio_de_sintomas_` -> datetime
- `fecha_de_inicio_de_fiebre_` -> datetime
- `fecha_de_inicio_de_exantema_rash_` *REQUERIDO* -> datetime
- `sintomas_` -> SI/NO
  - Si SI: `que_sintomas_` [MULTIPLE] -> Fiebre (con `temp_c`), Coriza/Catarro, Exantema/Rash, Manchas de Koplik, Tos, Artralgia/Artritis, Conjuntivitis, Adenopatias
- `hospitalizacion_` -> SI/NO/DESCONOCIDO
  - Si SI: `nombre_del_hospital_` (texto), `fecha_de_hospitalizacion_` (fecha)
- `complicaciones_` -> SI/NO/DESCONOCIDO
  - Si SI: `especifique_complicaciones_` [MULTIPLE] -> NEUMONIA, ENCEFALITIS, DIARREA, TROMBOCITOPENIA, OTITIS MEDIA AGUDA, CEGUERA, OTRA
- `aislamiento_respiratorio` -> SI/NO/DESCONOCIDO
  - Si SI: `fecha_de_aislamiento` (fecha)

#### 5.6. Factores de riesgo
- Si/No/DESCONOCIDO
- Sub-preguntas (si SI):
  - `Existe_caso_en_muni` -> Si/No/Desconocido
  - `tuvo_contacto_con_un_caso_sospechoso_o_confirmado` -> Si/No/Desconocido
  - `viajo_durante_los_7_23_dias` -> Si/No
    - Si SI: pais/departamento/municipio + fechas salida/entrada
  - `alguna_persona_de_su_casa_ha_viajado_al_exterior` -> Si/No
  - `el_paciente_estuvo_en_contacto_con_una_mujer_embarazada1` -> Si/No/Desconocido
  - `fuente_posible_de_contagio1` [MULTIPLE] -> Contacto en hogar, Servicio de Salud, Institucion Educativa, Espacio Publico, Comunidad, Evento Masivo, Transporte Internacional, Desconocido, Otro

#### 5.7. Acciones de respuesta
- SI/NO
- Si SI:
  - `se_realizo_busqueda_activa_institucional_de_casos_bai` -> 1/2 (Si/No)
    - Si 1: `numero_de_casos_sospechosos_identificados_en_bai` (numerico)
  - `se_realizo_busqueda_activa_comunitaria_de_casos_bac` -> 1/2
    - Si 1: `numero_de_casos_sospechosos_identificados_en_bac` (numerico)
  - `hubo_vacunacion_de_bloqueo` -> 1/2
  - `hubo_vacunacion_con_barrido_documentado` -> 1/2
  - `se_realizo_monitoreo_rapido_de_vacunacion` -> 1/2
  - `se_le_administro_vitamina_a` -> 1/2/3
    - Si 1: `numero_de_dosis_de_vitamina_a_recibidas` (numerico)
- Si NO: `por_que_no_acciones_respuesta` (texto)

#### 5.8. Clasificacion
- `clasificacion_final`:
  - 1 = Confirmado Sarampion -> `criterio_de_confirmacion_sarampion` (LABSR, NE, CX)
  - 2 = Confirmado Rubeola -> `criterio_de_confirmacion_rubeola` (LABRB, NERB, CXRB)
  - 3 = Descartado -> `criterio_para_descartar_el_caso` (LAB, RVAC, CX2, OTRO)
  - 5 = (otro valor, pendiente?)
- `contacto_de_otro_caso` -> SI/NO
- `fuente_de_infeccion_de_los_casos_confirmados`:
  - 1 = Importado (con pais)
  - 2 = Relacionado con importacion (con pais)
  - 3 = Endemico
  - 4 = Desconocido
- `caso_analizado_por` [MULTIPLE] -> 1, 2, 3, 4 (OTRO con especificar)
- `fecha_de_clasificacion` -> datetime
- `condicion_final_del_paciente`:
  - 1 = Vivo
  - 2 = (otra condicion)
  - 3 = Fallecido (con `fecha_de_defuncion`, `causa_de_muerte_segun_certificado_de_defuncion`)
  - 4 = (otra condicion)

#### 5.9. Lugares visitados y rutas de desplazamiento
- Hasta 2 sitios:
  - `sitio_ruta_de_desplazamiento_1/2` -> texto
  - `direccion_del_lugar_y_rutas_de_desplazamiento_1/2` -> texto
  - `fecha_en_que_visito_el_lugar_ruta_1/2` -> datetime
  - `tipo_de_abordaje_realizado_1/2` [MULTIPLE] -> BLOQUEO, BARRIDO, 3, 4
  - `fecha_de_abordaje_1/2` -> datetime

---

## 6. Template de Investigacion de Contactos (5 campos)

| Variable | Tipo | Opciones |
|----------|------|----------|
| `visita_a_de_investigacion_de_contactos_directos` | SINGLE | 1, 2 |
| `fecha_de_investigacion_de_contactos_directos` | DATETIME | - |
| `antecedente_vacunal_sr_o_spr` | SINGLE | 1, 2, 3, 4 |
| `signos_segun_definicion_de_caso` | MULTIPLE | 1, 2, 3 |
| `contacto_vacunado_durante_la_investigacion` | SINGLE | 1, 2 |

**Template de seguimiento de contactos**: Vacio (0 campos).

---

## 7. Datos de Referencia (496 items, 36 categorias)

### 7.1. Clasificacion de casos
| Valor | Activo |
|-------|--------|
| CONFIRMADO_POR_NEXO | Si |
| CONFIRMED | Si |
| NOT_A_CASE_DISCARDED | Si |
| PROBABLE | Si |
| SUSPECT | Si |
| SOSPECHOSO_DESCARTADO | No |
| SOSPECHOSO_E | No |

### 7.2. Genero
- FEMALE
- MALE

### 7.3. Desenlace (Outcome)
- ALIVE
- DECEASED
- RECOVERED

### 7.4. Enfermedades configuradas
COVID-19, Resp. Aguda, Colera, Ebola, Influenza, Leptospirosis, Marburg, **SARAMPION (MEASLES)**, MERS-CoV, Mpox, Peste, **RUBEOLA**, Fiebre Amarilla

### 7.5. Tipos de laboratorio
| Tipo de test | Activo |
|--------------|--------|
| AVIDEZ_RUBEOLA | Si |
| IG_C_OR_IG_M | Si |
| OTHER | Si |
| PCR | Si |
| RT_PCR | Si |
| SEROLOGIA_AVIDEZ | Si |
| SEROLOGIA_IG_G | Si |
| SEROLOGIA_IG_G_RUBEOLA | Si |
| SEROLOGIA_IG_M_RUBEOLA | Si |

### 7.6. Resultados de laboratorio
| Resultado | Activo |
|-----------|--------|
| ALTA | Si |
| BAJA | Si |
| INVALIDO | Si |
| MUESTRA_INADECUADA | Si |
| NEGATIVE | Si |
| NO_FUE_PROCESADA | Si |
| POSITIVE | Si |

### 7.7. Tipos de muestra (activos)
- HISOPADO_NASOFARINGEO
- SERUM
- URINE

### 7.8. Vacunas
- SPR (Sarampion-Paperas-Rubeola)
- SPRV
- SR (Sarampion-Rubeola)

### 7.9. Estado de vacunacion
- NOT_VACCINATED
- VACCINATED

### 7.10. Instituciones (35 items)
29 DAS departamentales + GENERIC, HOSPITAL_PRIVADO, **IGSS**, PRUEBA_PILOTO, PRUEBA_PILOTO_MSPAS, USUARIOS_PARA_ENTRENAMIENTO_MSPAS

### 7.11. Ocupaciones (24 items)
ALBANIL, BUTCHER, CALL_CENTER, CHILD, CIVIL_SERVANT, DEPENDIENTE_DE_TIENDA, FARMER, FORESTRY, HEALTH_CARE_WORKER, HEALTH_LABORATORY_WORKER, HOTELERIA, HOTELERIA_RESTAURANTE, LIMPIEZA_DOMESTICA, MAQUILA, MINING, OFICINA, OTHER, RELIGIOUS_LEADER, STUDENT, TAXI_DRIVER, TEACHER, TRADITIONAL_HEALER (inactivo), UNKNOWN, WORKING_WITH_ANIMALS (inactivo)

### 7.12. Estado de embarazo
DESCONOCIDO, NONE, NOT_PREGNANT, NO_APLICA, NO_SABE, YES_FIRST/SECOND/THIRD_TRIMESTER, YES_TRIMESTER_UNKNOWN

### 7.13. Tipo de exposicion (activos)
COMUNITARIO, FAMILIAR, MIGRANTE, OTHER, VUELO

### 7.14. Nivel de certeza / tipo de contacto (activos)
BRINDA_ATENCION_SIN_EPP, CONTACTO_CERCANO_MENOS_DE_1_5_MTS, DOMICILIAR, ESCOLAR, INSTITUCIONES_DE_CUIDADO, LABORAL, REUNION_SOCIAL, VIVE_EN_EL_MISMO_LUGAR

### 7.15. Estado seguimiento diario (activos)
INFO_RASTREO_INCOMPLETA, MISSED, NOT_ATTEMPTED, NOT_PERFORMED, NO_RESPONDIO, RECHAZO_SEGUIMIENTO, SEEN_NOT_OK, SEEN_OK

### 7.16. Laboratorio
- Nombre lab: LABORATORIO_NACIONAL_DE_SALUD_LNS
- Resultado secuencia: VARIANTE_A

---

## 8. Ubicaciones (803 nodos, 782 en arbol jerarquico)

### Jerarquia
```
Guatemala (Admin Level 0) - 1 nodo
  ├── 22 Departamentos (Admin Level 1) + ~21 duplicados DAS
  │     Nota: hay 43 items en Level 1 porque existen dos jerarquias paralelas
  ├── 83 DAS/Distritos (Admin Level 2)
  ├── 354 Municipios (Admin Level 3)
  └── 322 DMS (Admin Level 4)
```

### Departamentos (Level 1)
Alta Verapaz, Baja Verapaz, Chimaltenango, Chiquimula, El Progreso, Escuintla, Guatemala, Huehuetenango, Izabal, Jalapa, Jutiapa, Peten, Quetzaltenango, Quiche, Retalhuleu, Sacatepequez, San Marcos, Santa Rosa, Solola, Suchitepequez, Totonicapan, Zacapa

### IDs de ubicacion clave
| Ubicacion | ID |
|-----------|-----|
| Guatemala (pais) | `65c6cd0f-0be1-4848-9c0e-d4f422fc61ea` |
| Guatemala (depto) | `1` |
| Escuintla | `5` |
| Quiche | `14` (Ixcan/Ixil dentro) |
| Alta Verapaz | `16` |
| DAS Guatemala Central | `278` |
| DAS Guatemala Nor-Occidente | `203` |
| DAS Guatemala Nor-Oriente | `202` |
| DAS Guatemala Sur | `204` |

---

## 9. Equipos (53 equipos)

Organizados por DAS, con equipos de vigilancia y rastreo separados:

| Equipo | Miembros | DAS/Ubicacion |
|--------|----------|---------------|
| DAS Quetzaltenango | 63 | 212 |
| DAS Huehuetenango | 55 | 216 |
| Rastreo - DAS Guatemala Central | 47 | 278 |
| Rastreo - DAS Quetzaltenango | 43 | 212 |
| Rastreo - DAS Chiquimula | 38 | 224 |
| DAS Retalhuleu | 29 | 214 |
| Rastreo - DAS Retalhuleu | 24 | 214 |
| DAS Chimaltenango | 23 | 207 |
| DAS Jalapa | 23 | 225 |
| DAS Baja Verapaz | 22 | 219 |
| Rastreo - DAS Escuintla | 21 | 208 |
| DAS Quiche | 19 | 217 |
| Rastreo - DAS Guatemala Nororiente | 19 | 202 |
| Rastreo - DAS Chimaltenango | 20 | 207 |
| DAS Escuintla | 17 | 208 |
| DAS Izabal | 17 | 222 |
| DAS Totonicapan | 16 | 211 |
| DAS Sacatepequez | 16 | 206 |
| DAS Zacapa | 12 | 223 |
| ... (33 mas) | | |

**Equipos especiales**: Administradores (3), Rastreo - OPS (4), Rastreo - Kawok (3), Rastreo - Bomberos (11), Rastreo - Municipalidad de Guatemala (5)

---

## 10. Roles (20 roles)

| Rol | Permisos |
|-----|----------|
| Digitador Sarampion | 106 |
| Epidemiologo | 125 |
| Digitador | 99 |
| Data viewer | 67 |
| Visualizador | 68 |
| Contact tracer | 41 |
| Contact tracing coordinator | 41 |
| LABORATORIO NACIONAL SARAMPION | 28 |
| Data exporter | 26 |
| Epidemiologist | 19 |
| Contact of Contact - all permissions | 11 |
| Usuarios | 10 |
| System administrator | 8 |
| Default minimum backup access | 7 |
| Reference data manager | 5 |
| Outbreaks and templates administrator | 4 |
| User manager | 3 |
| Language manager | 2 |
| Help content manager | 2 |
| Laboratory data manager | 25 |

---

## 11. Idiomas

| ID | Nombre | Solo lectura |
|----|--------|-------------|
| `arabic` | Arabe | Si |
| `d86b2070-fad9-4699-8be9-a8ae5cc0edd2` | **Espanol GTRC** | No |
| `english_us` | English | Si |
| `french_fr` | Francais | Si |
| `portuguese_pt` | Portugues | Si |
| `russian_ru` | Ruso | Si |
| `spanish_es` | Espanol | Si |

**Espanol GTRC** es la traduccion personalizada de Guatemala (editable).

---

## 12. Resultados de Laboratorio

### Configuracion lab-results (campos visibles)
| Campo | Obligatorio |
|-------|-------------|
| sampleIdentifier | No |
| dateSampleTaken | **Si** |
| dateSampleDelivered | No |
| dateTesting | No |
| dateOfResult | No |
| labName | No |
| sampleType | No |
| testType | No |
| result | **Si** |
| testedFor | No |
| status | No |
| quantitativeResult | No |
| notes | No |
| sequence[hasSequence] | No |
| sequence[dateSampleSent] | No |
| sequence[labId] | No |
| sequence[dateResult] | No |
| sequence[resultId] | No |

**Estado actual**: 0 resultados de laboratorio en los 7 casos existentes.

---

## 13. Exportacion

### Endpoint de exportacion asincrona
```bash
# Iniciar exportacion
GET /api/outbreaks/{id}/cases/export?access_token=TOKEN
# Respuesta: {"exportLogId": "uuid"}

# Verificar estado
GET /api/export-logs?access_token=TOKEN
# Buscar por ID el log con status=LNG_SYNC_STATUS_SUCCESS
```

El historial muestra exportaciones exitosas previas de: cases, followUps.

---

## 14. Limitaciones y Restricciones

### Cuenta practica4@gmail.com

1. **Solo lectura**: No puede crear, modificar ni eliminar casos, contactos, ni eventos (401 Authorization Required en POST)
2. **Sin acceso a usuarios**: No puede listar ni ver usuarios del sistema
3. **Sin acceso a audit logs**: No puede ver historial de auditorias
4. **Sin acceso a system settings**: No puede ver version ni configuracion del sistema
5. **Sin acceso a devices**: No puede gestionar dispositivos moviles
6. **Token corto**: 600 segundos (10 min) de vida

### Limitaciones del sistema

1. **Un solo brote**: Solo existe "Taller Sarampion" — es un ambiente de entrenamiento/practica
2. **7 casos de prueba**: Datos de taller, no datos reales de produccion
3. **Variables con sufijos numericos**: El template usa variables como `distrito_municipal_de_salud_dms4`, `municipio_de_residencia13`, etc. donde el sufijo numerico depende del DAS/departamento seleccionado en la cascada. Esto complica la extraccion programatica.
4. **Valores 1/2/3 sin etiqueta**: Muchas opciones en clasificacion y acciones usan valores numericos (1=Si, 2=No, etc.) sin label legible
5. **Ubicaciones duplicadas**: Hay dos jerarquias paralelas de departamentos (una con IDs numericos, otra con UUIDs)

---

## 15. Recomendaciones para Integracion IGSS

### 15.1. Lectura de datos (consulta periodica)
```python
# Patron recomendado para sync IGSS
def sync_godata_cases():
    token = get_fresh_token()
    outbreak_id = "ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19"

    # Obtener todos los casos con campos necesarios
    cases = get_cases(outbreak_id, token, fields=[
        "id", "visualId", "firstName", "middleName", "lastName",
        "gender", "age", "dob", "dateOfOnset", "dateOfReporting",
        "classification", "outcomeId", "addresses",
        "questionnaireAnswers", "createdAt", "updatedAt"
    ])

    for case in cases:
        qa = case.get("questionnaireAnswers", {})
        # Extraer campos del cuestionario
        dx = extract_value(qa, "diagnostico_de_sospecha_")
        das = extract_value(qa, "direccion_de_area_de_salud")
        vacunado = extract_value(qa, "paciente_vacunado_")
        sintomas = extract_values(qa, "que_sintomas_")  # lista
        clasificacion = extract_value(qa, "clasificacion_final")
        # ... mapear a esquema IGSS
```

### 15.2. Extraccion de valores del cuestionario
```python
def extract_value(qa, key):
    """Extrae valor simple de questionnaireAnswers de GoData."""
    entry = qa.get(key, [{}])
    if isinstance(entry, list) and entry:
        return entry[0].get("value")
    return None

def extract_values(qa, key):
    """Extrae lista de valores (MULTIPLE_ANSWERS)."""
    entry = qa.get(key, [{}])
    if isinstance(entry, list) and entry:
        val = entry[0].get("value")
        if isinstance(val, list):
            return val
    return []
```

### 15.3. Mapeo de DAS/DMS
Problema: Las variables de DMS tienen sufijos numericos diferentes por DAS. Solucion:

```python
# Mapear DAS -> variable de DMS
DAS_TO_DMS_VAR = {
    "ALTA VERAPAZ": "distrito_municipal_de_salud_dms",
    "BAJA VERAPAZ": "distrito_municipal_de_salud_dms_",
    "CHIMALTENANGO": "distrito_municipal_de_salud_dms_CHI",
    "CHIQUIMULA": "distrito_municipal_de_salud_dms_CH",
    "EL PROGRESO": "distrito_municipal_de_salud_dms1",
    "ESCUINTLA": "distrito_municipal_de_salud_dms3",
    "GUATEMALA CENTRAL": "distrito_municipal_de_salud_dms4",
    "GUATEMALA NOR OCCIDENTE": "distrito_municipal_de_salud_dms5",
    "GUATEMALA NOR ORIENTE": "distrito_municipal_de_salud_dms6",
    "GUATEMALA SUR": "distrito_municipal_de_salud_dms7",
    "HUEHUETENANGO": "distrito_municipal_de_salud_dms8",
    "IXCÁN": "distrito_municipal_de_salud_dms9",
    "IXIL": "distrito_municipal_de_salud_dms10",
    "IZABAL": "distrito_municipal_de_salud_dms11",
    "JALAPA": "distrito_municipal_de_salud_dms12",
    "JUTIAPA": "distrito_municipal_de_salud_dms13",
    "PETÉN NORTE": "distrito_municipal_de_salud_dms14",
    "PETÉN SUR OCCIDENTE": "distrito_municipal_de_salud_dms15",
    "PETÉN SUR ORIENTE": "distrito_municipal_de_salud_dms16",
    "QUETZALTENANGO": "distrito_municipal_de_salud_dms17",
    "QUICHÉ": "distrito_municipal_de_salud_dms18",
    "RETALHULEU": "distrito_municipal_de_salud_dms19",
    "SACATEPÉQUEZ": "distrito_municipal_de_salud_dms20",
    "SAN MARCOS": "distrito_municipal_de_salud_dms21",
    "SANTA ROSA": "distrito_municipal_de_salud_dms22",
    "SOLOLÁ": "distrito_municipal_de_salud_dms23",
    "SUCHITEPÉQUEZ": "distrito_municipal_de_salud_dms24",
    "TOTONICAPÁN": "distrito_municipal_de_salud_dms25",
    "ZACAPA": "distrito_municipal_de_salud_dms26",
}

# Similar para municipio de residencia
DEPTO_TO_MUNI_VAR = {
    "ALTA VERAPAZ": "municipio_de_residencia_",
    "BAJA VERAPAZ": "municipio_de_residencia1",
    "CHIMALTENANGO": "municipio_de_residencia2",
    "CHIQUIMULA": "municipio_de_residencia3",
    "EL PROGRESO": "municipio_de_residencia4",
    "ESCUINTLA": "municipio_de_residencia5",
    "GUATEMALA": "municipio_de_residencia6",
    "HUEHUETENANGO": "municipio_de_residencia7",
    "IZABAL": "municipio_de_residencia8",
    "JALAPA": "municipio_de_residencia9",
    "JUTIAPA": "municipio_de_residencia10",
    "PETÉN": "municipio_de_residencia11",
    "QUETZALTENANGO": "municipio_de_residencia12",
    "QUICHÉ": "municipio_de_residencia13",
    "RETALHULEU": "municipio_de_residencia14",
    "SACATEPÉQUEZ": "municipio_de_residencia15",
    "SAN MARCOS": "municipio_de_residencia16",
    "SANTA ROSA": "municipio_de_residencia17",
    "SOLOLÁ": "municipio_de_residencia18",
    "SUCHITEPÉQUEZ": "municipio_de_residencia19",
    "TOTONICAPÁN": "municipio_de_residencia20",
    "ZACAPA": "municipio_de_residencia21",
}
```

### 15.4. Para crear casos (requiere cuenta con permisos)
```python
# Payload minimo para crear un caso
case_payload = {
    "firstName": "NOMBRE",
    "lastName": "APELLIDO",
    "gender": "LNG_REFERENCE_DATA_CATEGORY_GENDER_MALE",
    "dateOfOnset": "2026-03-25T00:00:00.000Z",
    "dateOfReporting": "2026-03-27T00:00:00.000Z",
    "classification": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT",
    "age": {"years": 36, "months": 0},
    "addresses": [{
        "typeId": "LNG_REFERENCE_DATA_CATEGORY_ADDRESS_TYPE_USUAL_PLACE_OF_RESIDENCE",
        "locationId": "1",  # ID de ubicacion
        "addressLine1": "Direccion"
    }],
    "questionnaireAnswers": {
        "diagnostico_de_sospecha_": [{"value": "SARAMPIÓN"}],
        "fecha_de_notificacion": [{"value": "Fecha de Notificación"}],
        "direccion_de_area_de_salud": [{"value": "GUATEMALA CENTRAL"}],
        # ... demas campos
    }
}

# POST /api/outbreaks/{id}/cases?access_token=TOKEN
```

### 15.5. Permisos necesarios para integracion completa
La cuenta actual (practica4@gmail.com) es insuficiente. Se necesita una cuenta con rol "Digitador Sarampion" (106 permisos) o "Epidemiologo" (125 permisos) que incluya:
- `case_create` para crear casos
- `case_modify` para actualizar
- `lab_result_create` para registrar resultados
- `contact_create` para crear contactos

### 15.6. Estrategia de sync recomendada
1. **Polling cada 15 min**: GET casos con filtro `updatedAt > last_sync`
2. **Deduplicacion**: Usar `visualId` (SR-XXXX) como clave unica
3. **Mapeo de referencia**: Precargar y cachear `/api/reference-data` (cambia poco)
4. **Ubicaciones**: Precargar `/api/locations/hierarchical` una vez
5. **Token refresh**: Renovar token cada 8 min (expira a los 10)

---

## 16. Hallazgos Criticos de la Exploracion API (2026-03-27)

### 16.1. Doble sistema de clasificacion
GoData Guatemala tiene DOS sistemas de clasificacion que deben setearse por separado:

1. **`case.classification`** (campo estandar GoData) — Usado por dashboards, filtros y reportes nativos de GoData. Si no se setea, el caso aparece como "Sin clasificar" en la UI.
2. **`questionnaireAnswers.clasificacion_final`** (cuestionario personalizado Guatemala) — Codigos numericos (1=Sarampion, 2=Rubeola, 3=Descartado, 5=Pendiente).

**Los 5 casos reales existentes (SR-0001 a SR-0005) tienen `classification=null`** porque los operadores guatemaltecos solo llenan el cuestionario pero no setean el campo estandar. Esto es un problema de entrenamiento, no de la API.

**Nuestro codigo setea AMBOS** en `godata_field_map.py:map_record_to_godata()`.

### 16.2. outcomeId nunca seteado
Similar a classification, el campo `outcomeId` (condicion final del paciente) no esta seteado en ninguno de los 7 casos existentes. Los operadores solo llenan `condicion_final_del_paciente` en el cuestionario.

Nuestro codigo setea ambos: `case.outcomeId` (estandar) y `qa.condicion_final_del_paciente` (cuestionario).

### 16.3. Import mappings disponibles
Guatemala tiene 3 templates de importacion configurados:
- **`plantilla contactos W`** — importacion de contactos
- **`Laboratorio_recoded`** — importacion de casos
- **`plantilla laboratorio - W`** — importacion de datos de laboratorio

Estos podrian usarse para importacion masiva via `/api/outbreaks/{id}/cases/import` en lugar de llamadas individuales POST.

### 16.4. Endpoint per-classification count
```
GET /api/outbreaks/{id}/cases/per-classification/count
```
Retorna conteo de casos agrupados por clasificacion. Util para dashboard sin descargar todos los casos.

### 16.5. Idioma "Espanol GTRC"
- ID: `d86b2070-fad9-4699-8be9-a8ae5cc0edd2`
- Es la traduccion personalizada de Guatemala (editable, no read-only)
- Contiene todas las traducciones del cuestionario en espanol
- Los otros idiomas (english_us, spanish_es, etc.) son read-only

### 16.6. Follow-ups, events, relationships vacios
Todos los endpoints de rastreo de contactos existen y son accesibles pero no contienen datos:
- 0 contactos, 0 eventos, 0 seguimientos, 0 relaciones
- Estas features son para rastreo de contactos que Guatemala aun no usa en este brote de entrenamiento

### 16.7. Cero resultados de laboratorio
Ninguno de los 7 casos tiene lab-results registrados via la API de laboratorio. Los datos de laboratorio solo existen dentro del cuestionario (`questionnaireAnswers`).

Nuestro codigo envia resultados de laboratorio SEPARADAMENTE via POST `/cases/{id}/lab-results`, lo cual es correcto y complementa los datos del cuestionario.

### 16.8. Validacion server-side inexistente
GoData acepta **cualquier payload** sin validar campos obligatorios, formatos de fecha, ni valores de referencia. Un POST con `{"firstName": ""}` es aceptado sin error.

Por esto, implementamos `validate_godata_payload()` en `godata_field_map.py` para validacion client-side antes del envio.

---

## Archivos JSON de referencia

Todos los datos crudos estan guardados en `/tmp/godata_api_exploration/`:
- `outbreaks.json` (1 MB) - Brote completo con templates
- `cases.json` (44 KB) - 7 casos con cuestionarios
- `reference_data.json` (300 KB) - 496 items de referencia
- `locations.json` (526 KB) - 803 ubicaciones
- `teams.json` (62 KB) - 53 equipos
- `templates.json` (708 KB) - Templates de investigacion
- `languages.json` (2 KB) - 7 idiomas
- `contacts.json` - Vacio (0 contactos)
- `events.json` - Vacio (0 eventos)
- `followups.json` - Vacio (0 seguimientos)
- `relationships.json` - Vacio (0 relaciones)
- `lab_results.json` - Vacio (0 resultados)
